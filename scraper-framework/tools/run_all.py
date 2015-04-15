from __future__ import division
import argparse
import csv
import mimetypes
import smtplib
import re
import sys
import shutil
import tinys3
import time
from subprocess import call
from multiprocessing import Pool, Manager
from os import path
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText


sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from statistic_reports import *
from scrapy_balloons.stats.stats_collector import *
from scrapy_balloons.constant import *
from scrapy_balloons.utils.basefunctions import object_to_json
from scrapy_balloons.utils.datetimefunctions import time_display

MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = '587'
MAIL_FROM = 'scraper.skilledup@gmail.com'
MAIL_PASS = 'Teslavietnam2015'

# S3 CREDENTIAL
S3_ACCESS_KEY = 'AKIAJ35FIFXQ5SLKT25A'
S3_SECRET_KEY = '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'
S3_ENDPOINT = 's3-us-west-1.amazonaws.com'
S3_REPORTS_BUCKET = "test-skilledup-products"
S3_REPORTS_FOLDER = "rerun_all_reports"

TIME_NOTIFICATION_BY_EMAIL = 36000
TIMEOUT_SCRAPER = 64800 # 18h

COMPRESS_NAME = 'compress'
LOGS_NAME = 'logs'
OUTPUT_NAME = 'output'
SUMMARY_JSON_NAME = "rerun_%s.json" % (time.strftime('%Hh%Mm_%d_%m_%Y'))
SUMMARY_CSV_NAME = SUMMARY_JSON_NAME.replace('json', 'csv')
LISTENER_KILL_SIGNAL = 'KILL'
STATISTIC_ALL_RERUN_CSV_FILE = 'statistic_all_rerun.csv'


def get_simple_name(value):
    """
    input  skillup_config.json
    or input skillup.json
    or input skillup_product_list_99922.json
    return skillup
    """
    result = re.search("(\w+)_config\.json", value)
    result = result if result else re.search("(\w+)\.json", value)
    result = result if result else re.search("(\w+)_product_list_\d+\.gz", value)
    if result:
        return result.group(1)
    else:
        return None


def get_providers(file_name):
    result = []
    with open(file_name, 'r') as file_from:
        for line in file_from:
            name = get_simple_name(line)
            if name:
                result.append(name)
    return result


def create_output_folder(folder):
    if not folder:
        op_folder = int(time.time())
        os.makedirs(op_folder)
        folder = op_folder
    elif not os.path.exists(folder):
        os.makedirs(folder)
    logs = os.path.join(folder, LOGS_NAME)
    json_products = os.path.join(folder, OUTPUT_NAME)
    compress = os.path.join(folder, COMPRESS_NAME)
    if not os.path.exists(logs):
        os.makedirs(logs)
    if not os.path.exists(json_products):
        os.makedirs(json_products)
    if not os.path.exists(compress):
        os.makedirs(compress)
    return folder


def get_output_json_name(input):
    """
    # get_output_json_name(input) => str. Get the output file name from the config file name
    input  example :  skillfeed_config.json.
    return : skillfeed.json
    """
    return input.split("/")[len(input.split("/")) - 1].replace("_config", "")


class GlobalSummary:
    def __init__(self):
        self.start_time = int(time.time())
        self.end_time = 0
        self.spent_time = 0
        self.provider_success = []
        self.provider_failed = []
        self.provider_running = []
        self.provider_running_count = 0
        self.provider_success_count = 0
        self.provider_uploaded_count = 0
        self.provider_failed_count = 0
        self.provider_total_count = 0
        self.percent_provider_success = 0
        self.percent_provider_failed = 0
        self.course_total_count = 0
        self.size_total = 0

    @classmethod
    def load_from_json_file(cls, file_name):
        try:
            if os.path.isfile(file_name):
                with open(file_name, 'r') as json_file:
                    return GlobalSummary.load_from_json_value(json.load(json_file))
        except:
            print "GlobalSummary load from file %s : Failed" % (file_name)
            return None


    @classmethod
    def load_from_json_value(cls, value):
        try:
            summary = GlobalSummary()
            #pdb.set_trace()
            for k, v in value.iteritems():
                if k in ['provider_success', 'provider_failed', 'provider_running']:
                    providers = []
                    for item in v:
                        providers.append(StatsCollector.load_from_json(json_value=item))
                        #providers = sorted(providers, key=lambda k: k.status)
                    setattr(summary, k, providers)
                else:
                    setattr(summary, k, v)
            return summary
        except:
            traceback.print_exc()
            print "GlobalSummary load from json value Failed"
            return None


    def put_collector(self, collector):
        if collector.status == SUCCESS_STATUS:
            self.provider_success.append(collector)
            self.remove(self.provider_running, collector)
        elif collector.status == RUNNING_STATUS:
            self.provider_running.append(collector)
        else:
            self.provider_failed.append(collector)
            self.remove(self.provider_running, collector)

    def remove(self, item_list, item_remove):
        for item in item_list:
            if item.config_file_name == item_remove.config_file_name:
                item_list.remove(item)
                return

    def reset(self):
        self.provider_success_count = 0
        self.provider_failed_count = 0
        self.provider_running_count = 0
        self.provider_uploaded_count = 0
        self.provider_total_count = 0
        self.percent_provider_success = 0
        self.percent_provider_failed = 0
        self.course_total_count = 0
        self.size_total = 0

    def update_timeout_status(self):
        # when a provider take too long time to be finished,
        # if we stop the scraped process we need update the summary
        for index, p in enumerate(self.provider_running):
            p.status = FAILED_STATUS
            p.message = 'Exception Timeout %s ' % (TIMEOUT_SCRAPER)
            self.provider_failed.append(p)
        self.provider_running = []
        self.update()


    def update(self):
        self.reset()
        self.provider_success_count = len(self.provider_success)
        self.provider_failed_count = len(self.provider_failed)
        self.provider_running_count = len(self.provider_running)
        self.provider_total_count = self.provider_success_count + self.provider_failed_count
        for p in self.provider_success:
            if p.compress_file:
                self.size_total += p.compress_file.size
            if p.s3_info and p.s3_info.uploaded == 'Yes':
                self.provider_uploaded_count += 1
            self.course_total_count += p.courses_total
        if self.provider_total_count != 0:
            self.percent_provider_success = float(
                "{0:.2f}".format(self.provider_success_count / self.provider_total_count))
            self.percent_provider_failed = float(
                "{0:.2f}".format(self.provider_failed_count / self.provider_total_count))
        self.end_time = int(time.time())
        self.spent_time = self.end_time - self.start_time

    def write_to_json(self, output_file):
        with open(output_file, 'wb') as jsonfile:
            json.dump(self.to_json(), jsonfile)
            jsonfile.close()

    def to_json(self):
        return object_to_json(self)


    def write_to_csv(self, output_file):
        csvfile = open(output_file, 'wb')
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['Provider Success Total', self.provider_success_count])
        csvwriter.writerow(['Provider Uploaded Total', self.provider_uploaded_count])
        csvwriter.writerow(['Provider Failed Total', self.provider_failed_count])
        csvwriter.writerow(['Provider Total', self.provider_total_count])
        csvwriter.writerow(['Percent Provider Success', self.percent_provider_success])
        csvwriter.writerow(['Provider Running Total', self.provider_running_count])
        csvwriter.writerow(['Courses Total ', self.course_total_count])
        csvwriter.writerow(['Time Spent', time_display(self.spent_time)])
        cols = ['provider_id', 'config_file_name', 'courses_total', 'execution_time_display',
                'status', 's3_info', 'message']
        cols_meta = ['PROVIDER_ID', 'CONFIG FILE NAME ', 'COURSES TOTAL ', 'TIME EXECUTION',
                     'STATUS', 'UPLOADED_S3', 'MESSAGE']
        csvwriter.writerow('')
        csvwriter.writerow('')
        csvwriter.writerow(cols_meta)
        provider_total = self.provider_success + self.provider_failed + self.provider_running
        for item in provider_total:
            fields_value = []
            for col in cols:
                try:

                    if col == 's3_info' and item.s3_info:
                        if item.s3_info:
                            fields_value.append(item.s3_info.uploaded)
                        else:
                            fields_value.append('No')
                    else:
                        value = getattr(item, col)
                        fields_value.append(value)
                except:
                    print "Missing field %s" % (col)
                    print item.__dict__
                    fields_value.append("")
            csvwriter.writerow(fields_value)
        csvfile.close()


def delete_output_json_file_not_finish(summary_path):
    if os.path.isfile(summary_path):
        summary = GlobalSummary.load_from_json_file(file_name=summary_path)
        if summary:
            delete = summary.provider_failed + summary.provider_running
            for p in delete:
                try:
                    name = re.search("(\w+\.json)", p.json_file.path).group(1)
                    file_remove = os.path.join(OUTPUT_JSON_PATH, name)
                    if os.path.exists(file_remove):
                        os.remove(file_remove)
                        print "Delete file %s Successfully" % (file_remove)
                except:
                    traceback.print_exc()
                    print "File %s is not existed " % (file_remove)
                    pass
            summary.provider_failed = []
            summary.provider_running = []
            summary.write_to_json(SUMMARY_JSON_FILE)
            summary.write_to_csv(SUMMARY_CSV_FILE)


def scraper(config_file, queue):
    try:
        # START
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        short_name = get_output_json_name(config_file)
        output_file = os.path.join(OUTPUT_JSON_PATH, short_name)
        #suspect_urls_log = os.path.join(LOGS_PATH, short_name.replace(".json", "_error_urls.log"))
        log_file = os.path.join(LOGS_PATH, short_name.replace(".json", ".log"))
        limit = LIMIT if LIMIT else -1
        #print "Starting : %s " % (config_file)
        command = "scrapy crawl web_scraper -a config_file=%s -s LOG_FILE=%s -o %s -a summary=default -a limit=%s " % (
            config_file, log_file, output_file, limit)
        print command + "\n"
        if S3:
            command = "%s -a compress=%s -a s3=%s" % (command, COMPRESS_PATH, S3)
        collector = StatsCollector(config_file=config_file, output_file=output_file)
        queue.put(collector)
        call(command, shell=True)
        # get data generate from sub process
        summary_path = collector.default_path()
        with open(summary_path) as summary_file:
            json_value = json.load(summary_file)
            collector = StatsCollector.load_from_json(json_value=json_value)
        queue.put(collector)
        return "scrapy from config file %s : OK" % (config_file)
    except:
        traceback.print_exc()
        print "Error when processing the job for %s" % (config_file)
        pass


def get_summary():
    summary = GlobalSummary.load_from_json_file(SUMMARY_JSON_FILE)
    if summary is None:
        summary = GlobalSummary()
        summary.write_to_json(SUMMARY_JSON_FILE)
    return summary


def listener(queue):
    summary = get_summary()
    while 1:
        try:
            m = queue.get()
            if isinstance(m, StatsCollector):
                summary.put_collector(m)
                summary.update()
                summary.write_to_json(SUMMARY_JSON_FILE)
                summary.write_to_csv(SUMMARY_CSV_FILE)
            elif m == "LISTENER_KILL_SIGNAL":
                break
        except:
            traceback.print_exc()
            pass
    queue.close()


def init_params():
    global CONFIG_PATH, OUTPUT_PATH, LOGS_PATH, SUMMARY_CSV_FILE, CURRENT_OUTPUT_LIST, FINAL_CONFIG_TO_SCRAPE, \
        PROCESS_NUMBER, SUMMARY_JSON_FILE, ALLOW_FILE_PATH, DENY_FILE_PATH, OUTPUT_JSON_PATH, LIMIT, COMPRESS_PATH, S3, MAIL_TO, CLEAN_OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--config_path', help='folder path where the config files are. [Required]')
    parser.add_argument('-o', '--output_path',
                        help='output folder where the output file will be stored. Without it,current epoch time as folder name  will be created.[Optional]')
    parser.add_argument('-l', '--limit', help='limit the courses number to be scraped for each provider. [Optional]')
    parser.add_argument('-n', '--process_number', default=2, help='number of providers to run in parallel. [Optional]')
    parser.add_argument('-s3', '--s3_path', default=None,
                        help='compress the json output and upload to s3  after finishing  [Optional]')
    parser.add_argument('-a', '--allow', default=None,
                        help='path to text file. Only providers has config file names in this text file will be scraped. [Optional]')
    parser.add_argument('-d', '--deny', default=None,
                        help='path to text file. All providers has config file names in this text will be ignored to be scraped. [Optional]')
    parser.add_argument('-e', '--email', default=None,
                        help='Email address that will receive notifications and report.[Optional]')
    parser.add_argument('-c', '--clean_output', default='no',
                        help='Delete the output folder')

    CONFIG_PATH = parser.parse_args().config_path
    OUTPUT_PATH = parser.parse_args().output_path
    OUTPUT_PATH = OUTPUT_PATH if OUTPUT_PATH else str(int(time.time()))
    PROCESS_NUMBER = int(parser.parse_args().process_number)
    ALLOW_FILE_PATH = parser.parse_args().allow
    DENY_FILE_PATH = parser.parse_args().deny
    LIMIT = parser.parse_args().limit
    MAIL_TO = parser.parse_args().email
    S3 = parser.parse_args().s3_path
    CLEAN_OUTPUT = parser.parse_args().clean_output
    CURRENT_OUTPUT_LIST = []

    # create logs file
    LOGS_PATH = os.path.join(OUTPUT_PATH, LOGS_NAME)
    SUMMARY_CSV_FILE = os.path.join(OUTPUT_PATH, SUMMARY_CSV_NAME)
    SUMMARY_JSON_FILE = os.path.join(OUTPUT_PATH, SUMMARY_JSON_NAME)
    OUTPUT_JSON_PATH = os.path.join(OUTPUT_PATH, OUTPUT_NAME)
    COMPRESS_PATH = os.path.join(OUTPUT_PATH, COMPRESS_NAME)
    ALLOW = get_providers(ALLOW_FILE_PATH) if ALLOW_FILE_PATH else []
    DENY = get_providers(DENY_FILE_PATH) if DENY_FILE_PATH else []
    FINAL_CONFIG_TO_SCRAPE = []
    if not CONFIG_PATH or not os.path.exists(OUTPUT_PATH):
        print parser.print_help()
    if CLEAN_OUTPUT.lower() in ['yes', 'true'] and os.path.exists(OUTPUT_PATH):
        # Delete the output
        shutil.rmtree(OUTPUT_PATH)
        create_output_folder(OUTPUT_PATH)
        print "Delete folder %s : OK" % (OUTPUT_PATH)
    else:
        create_output_folder(OUTPUT_PATH)
        delete_output_json_file_not_finish(SUMMARY_JSON_FILE)
        for output_file in os.listdir(OUTPUT_JSON_PATH):
            if get_simple_name(output_file):
                DENY.append(get_simple_name(output_file))
    for file_name in os.listdir(CONFIG_PATH):
        name = get_simple_name(file_name)
        full_path = os.path.abspath(os.path.join(CONFIG_PATH, file_name))
        if name in ALLOW and name not in DENY:
            FINAL_CONFIG_TO_SCRAPE.append(full_path)
        elif not ALLOW and name not in DENY:
            FINAL_CONFIG_TO_SCRAPE.append(full_path)


def main():
    if MAIL_TO:
        signal.signal(signal.SIGALRM, send_email_by_alarm)
        signal.alarm(TIME_NOTIFICATION_BY_EMAIL)
        send_email_start()
    start_time = int(time.time())
    manager = Manager()
    queue = manager.Queue()
    pool = Pool(PROCESS_NUMBER + 1)
    jobs = []
    pool.apply_async(listener, args=(queue,))
    for config_file in FINAL_CONFIG_TO_SCRAPE:
        job = pool.apply_async(scraper, (config_file, queue))
        jobs.append(job)
    for i, job in enumerate(jobs):
        try:
            result = job.get(TIMEOUT_SCRAPER)
        except:
            print "Job %s failed Timeout %s " % (i, TIMEOUT_SCRAPER)
            pass
    time.sleep(5)
    # update errors for global report
    summary = get_summary()
    summary.update_timeout_status()
    summary.write_to_json(SUMMARY_JSON_FILE)
    summary.write_to_csv(SUMMARY_CSV_FILE)

    # put the summary to s3


    # although all job finished, but for unknown some providers still running
    time.sleep(10)
    queue.put(LISTENER_KILL_SIGNAL)
    pool.close()
    if MAIL_TO:
        send_email_end()

    # get all report from s3:
    if S3:
        conn = s3_conn()
        data = list(conn.list("%s/json" % (S3_REPORTS_FOLDER), S3_REPORTS_BUCKET))
        file_names = [i['key'] for i in data]
        reports = []
        for name in file_names:
            output = conn.get(name, S3_REPORTS_BUCKET)
            value = json.loads(output._content)
            report = GlobalSummary.load_from_json_value(value)
            if report:
                reports.append(report)


                # upload individual report to s3
        s3_report_json_folder = "%s/json" % ( os.path.join(S3_REPORTS_BUCKET, S3_REPORTS_FOLDER))
        s3_report_csv_folder = "%s/csv" % ( os.path.join(S3_REPORTS_BUCKET, S3_REPORTS_FOLDER))
        upload_to_s3(SUMMARY_JSON_FILE, s3_report_json_folder)
        upload_to_s3(SUMMARY_CSV_FILE, s3_report_csv_folder)

        # add the current report
        reports.append(summary)
        path_file_csv = os.path.join(OUTPUT_PATH, STATISTIC_ALL_RERUN_CSV_FILE)
        if statistic_all_rerun_to_csv(reports, path_file_csv):
            upload_to_s3(path_file_csv, os.path.join(S3_REPORTS_BUCKET, S3_REPORTS_FOLDER))


def get_mailer():
    mailer = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    mailer.ehlo()
    mailer.starttls()
    mailer.ehlo()
    mailer.login(MAIL_FROM, MAIL_PASS)
    return mailer


def build_msg(path_file, attachment=True):
    try:
        if attachment:
            base_name = os.path.basename(path_file)
            ctype, encoding = mimetypes.guess_type(path_file)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(path_file, 'rb')
                # Note: we should handle calculating the charset
                msg = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(path_file, 'rb')
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                encoders.encode_base64(msg)
                # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=base_name)
        else:
            fp = open(path_file, 'rb')
            msg = MIMEText(fp.read())
            fp.close()
        return msg
    except:
        return None


def send(msg):
    mailer = get_mailer()
    mailer.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
    mailer.quit()


def send_email_start():
    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO
    msg['Subject'] = 'Skilledup Scraper : The scraper has  started'
    send(msg)


def send_email_current_status():
    print "send_current_status"
    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO
    msg['Subject'] = 'Skilledup Scraper : Current Status of scraper '
    msg.attach(build_msg(SUMMARY_CSV_FILE, attachment=False))
    msg.attach(build_msg(SUMMARY_CSV_FILE, attachment=True))
    msg.attach(build_msg(SUMMARY_JSON_FILE, attachment=True))
    send(msg)


def send_email_end():
    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO
    msg['Subject'] = 'Skilledup Scraper  : The scraper process  has finished'
    msg.attach(build_msg(SUMMARY_CSV_FILE, attachment=False))
    msg.attach(build_msg(SUMMARY_CSV_FILE, attachment=True))
    msg.attach(build_msg(SUMMARY_JSON_FILE, attachment=True))
    send(msg)


def send_email_by_alarm(signum, stack):
    send_email_current_status()
    signal.alarm(TIME_NOTIFICATION_BY_EMAIL)


def s3_conn():
    conn = tinys3.Connection(S3_ACCESS_KEY, S3_SECRET_KEY, tls=True, endpoint=S3_ENDPOINT)
    return conn


def upload_to_s3(file_upload, s3_path):
    temp = file_upload.split('/')
    simple_name = temp[len(temp) - 1:][0]
    try:
        conn = s3_conn()
        f = open(file_upload, 'rb')
        r = conn.upload(simple_name, f, s3_path)
        if r.reason == 'OK':
            print "Upload file %s to s3://%s : Successfully" % (simple_name, s3_path)
        else:
            print "Upload file %s to s3://%s : Failed " % (simple_name, s3_path)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    init_params()
    main()



