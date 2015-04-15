from __future__ import division
import traceback, re, gzip
import time, os, json
import tinys3
from scrapy_balloons.constant import SUCCESS_STATUS
from scrapy_balloons.utils.convertfunctions import json_to_csv
from scrapy_balloons.stats.stats_collector import FileInfo
from scrapy_balloons.stats.stats_collector import S3Info
from scrapy_balloons.utils.basefunctions import *
from scrapy import log

class DataService:
    """
    allow to compress the output json
    allow send the compress file to s3 bucket
    allow to collect the statistic of output json file see class filters.StatsFilters
    the credential s3 is read from the settings.py file
    """
    def __init__(self, spider):
        self.spider = spider
        self.output_file = spider._crawler.settings.attributes['FEED_URI'].value
        self.S3_ACCESS_KEY = spider._crawler.settings.attributes['S3_ACCESS_KEY'].value
        self.S3_SECRET_KEY = spider._crawler.settings.attributes['S3_SECRET_KEY'].value
        self.S3_ENDPOINT = spider._crawler.settings.attributes['S3_ENDPOINT'].value
        self.S3_BUCKET = spider._crawler.settings.attributes['S3_BUCKET'].value
        if hasattr(self.spider,'s3') and  self.spider.s3:
            self.S3_BUCKET = self.S3_BUCKET if self.spider.s3 == 'default' else self.spider.s3


    def handle_on_close(self):
        compress_file = None
        if hasattr(self.spider,'collector'):
            collector = self.spider.collector
            collector.finish()
            collector.json_file = self.get_info_file(self.output_file)
            if collector.status == SUCCESS_STATUS:
                if self.spider.compress:
                    compress_file = self.compress(self.output_file, self.spider.compress)
                    collector.compress_file = compress_file
                if self.spider.s3:
                    compress_file = compress_file if compress_file else self.compress(self.output_file, './')
                    s3_path = self.S3_BUCKET if self.spider.s3 == 'default' else self.spider.s3
                    s3_info = self.upload_to_s3(compress_file.path, s3_path)
                    collector.s3_info = s3_info
                    collector.compress_file = compress_file
                if self.spider.csv:
                    json_to_csv(self.output_file, self.spider.csv)
        if hasattr(self.spider,'summary') and  self.spider.summary:
            summary_path = self.spider.collector.default_path() if self.spider.summary == 'default' else self.spider.summary
            with open(summary_path, 'wb') as summary_file:
                # Circular reference detected, delete spider
                json.dump(collector.to_json(), summary_file)
                #json.dump(object_to_json(collector,['spider']),summary_file)
                summary_file.close()
                print "Save the summary into the file %s : Successfully" % (summary_path)

    def compress(self, file_path, output):
        try:
            f_inside_out_path = None
            if '.gz' not in output:
                if not os.path.exists(output):
                    os.makedirs(output)
                simple_name = self.get_simple_name(file_path)
                compress_name = "%s_product_list_%s.gz" % (simple_name, int(time.time()))
                f_out_path = "%s/%s" % (output, compress_name)
            else:
                f_out_path = output
            f_original_path = f_out_path.replace('.gz','.json.gz')
            f_in = open(file_path, 'rb')
            f_out = gzip.open(f_original_path, 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            os.rename(f_original_path,f_out_path)
            print "Compress from %s to %s : Successfully" % (file_path, f_out_path)
            return self.get_info_file(f_out_path)
        except:
            print "Compress from %s to %s : Failed " % (self.get_simple_name(file_path), compress_name)
            traceback.print_exc()
            return None

    def get_info_file(self, file_name):
        try:
            stat = os.stat(file_name)
            return FileInfo(size=stat.st_size, modified=int(stat.st_mtime), path=file_name)
        except:
            return FileInfo(path=file_name)

    def get_simple_name(self, value):
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

    def upload_to_s3_(self, file_upload, s3_path):
        temp = file_upload.split('/')
        simple_name = temp[len(temp) - 1:][0]
        try:
            conn = tinys3.Connection(self.S3_ACCESS_KEY, self.S3_SECRET_KEY, tls=True, endpoint=self.S3_ENDPOINT)
            f = open(file_upload, 'rb')
            r = conn.upload(simple_name, f, s3_path)
            if r.reason == 'OK':
                print "Upload file %s to %s : Successfully" % (simple_name, s3_path)
                return S3Info(uploaded='Yes', compress_file=file_upload, bucket=s3_path)
            else:
                msg = "Upload file %s to %s : Failed " % (simple_name, s3_path)
                print msg
                log.msg(msg, level=log.ERROR)
                return S3Info(uploaded='No', compress_file=file_upload, bucket=s3_path)
        except:
            msg = "Upload file %s to %s : Failed " % (simple_name, s3_path)
            print msg
            log.msg(traceback.format_exc(300), level=log.ERROR)
            log.msg(msg, level=log.ERROR)
            return S3Info(uploaded='No', compress_file=file_upload, bucket=s3_path)

    def upload_to_s3(self, file_upload, s3_path):
        retry_number = 3
        for i in range(1, retry_number + 1):
            r = self.upload_to_s3_(file_upload, s3_path)
            if r.uploaded == 'No':
                log.msg("Retry %s times upload the file %s to s3 ", i, file_upload)
                time.sleep(10)
            else:
                return r



