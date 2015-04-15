import argparse
import csv
import json
import os
import os.path
import parser
import traceback
import time
from datetime import timedelta
import datetime

from run_all import GlobalSummary


def parse_json(path_file):
    with open(path_file) as input_file:
        try:
            json_v = json.load(input_file)
        except:
            print "Error to read %s " % (path_file)


def get_all_ids_by_status(summaries, status_list):
    def is_exist_in_providers(id, providers):
        for p in providers:
            if p.provider_id == id:
                return True
        return False

    def id_exist_in_all_summaries(id, status_list, summaries):
        for s in summaries:
            all_providers = []
            for status in status_list:
                if status == 'OK':
                    all_providers += s.provider_success
                elif status == 'KO':
                    all_providers += s.provider_failed
            if is_exist_in_providers(id, all_providers) is False:
                return False
        return True

    all_ids = []
    # get all_ids
    for s in summaries:
        all_providers = s.provider_success + s.provider_failed + s.provider_running
        for p in all_providers:
            if hasattr(p, 'provider_id') and p.provider_id not in all_ids and p.status in status_list:
                all_ids.append(p.provider_id)
    orders_ids = sorted(all_ids, key=lambda id: id_exist_in_all_summaries(id, status_list, summaries), reverse=True)
    return orders_ids


def get_config_filename(provider_id, summaries):
    for s in summaries:
        all_providers = s.provider_success + s.provider_failed + s.provider_running
        for p in all_providers:
            if hasattr(p, 'provider_id') and p.provider_id == provider_id:
                return p.config_file_name
    return ""


def time_display(sec):
    sec = timedelta(seconds=int(sec))
    d = datetime.datetime(1, 1, 1) + sec
    data = [
        {"%d days" % (d.day - 1): d.day - 1},
        {"%d hours" % (d.hour ): d.hour},
        {"%d min" % (d.minute): d.minute},
        {"%d sec" % (d.second): d.second}
    ]
    result = ""
    for item in data:
        if item.values()[0] != 0:
            result = result + ' ' + item.keys()[0]
    result = ' '.join(result.split()).strip()
    return result


def get_value(id, field_name, providers):
    for p in providers:
        if p.provider_id == id:
            return p.__dict__[field_name]
    return None


def time_to_string(value):
    return time.strftime('%d-%m-%Y', time.localtime(value))


def statistic_all_rerun_to_csv(summaries, output_path):
    # order summaries by date
    summaries = sorted(summaries, key=lambda x: x.start_time, reverse=False)
    try:
        with open(output_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # Part 1 : Overview
            row1 = ["Overview"]
            row2 = ["Date", "-"] + [time_to_string(i.start_time) for i in summaries]
            row3 = ["Total courses", "-"] + [i.course_total_count for i in summaries]
            row4 = ["Total successful providers", "-"] + [i.provider_success_count for i in summaries]
            row5 = ["Total uploaded providers", "-"] + [i.provider_uploaded_count for i in summaries]
            row6 = ["Total failed providers", "-"] + [i.provider_failed_count for i in summaries]
            row7 = ["Total running providers", "-"] + [i.provider_running_count for i in summaries]
            row8 = ["Total time ", "-"] + [time_display(i.spent_time) for i in summaries]
            part1 = [row1, row2, row3, row4, row5, row6, row7, row8]
            for row in part1:
                csvwriter.writerow(row)

            # Part 2 : Detail Success Providers
            csvwriter.writerow([])
            csvwriter.writerow([])
            ids_OK = get_all_ids_by_status(summaries, ['OK'])
            row8 = ["Detail Successful Providers"]
            row9 = ["Provider_id", "Config File Name"] + ["Courses Number" for i in range(len(summaries))]
            csvwriter.writerow(row8)
            csvwriter.writerow(row9)
            for id in ids_OK:
                row = [id]
                # get the config name
                config_file_name = get_config_filename(id, summaries)
                row.append(config_file_name)
                for s in summaries:
                    v = get_value(id, 'courses_total', s.provider_success)
                    row.append(v)
                csvwriter.writerow(row)

            # Part 2 : Detail Failed Providers
            csvwriter.writerow([])
            csvwriter.writerow([])
            ids_KO = get_all_ids_by_status(summaries, ['KO', 'ITEM_SCRAPED_NOT_GROW_UP'])
            row8 = ["Detail Failed Providers"]
            row9 = ["Provider_id", "Config File Name"] + ["Status/Notes" for i in range(len(summaries))]
            csvwriter.writerow(row8)
            csvwriter.writerow(row9)
            for id in ids_KO:
                row = [id]
                config_file_name = get_config_filename(id, summaries)
                row.append(config_file_name)
                for s in summaries:
                    status = get_value(id, 'status', s.provider_failed)
                    message = get_value(id, 'message', s.provider_failed)
                    value = status if message is None else "%s // %s" % (status, message)
                    row.append(value)
                csvwriter.writerow(row)
            csvfile.close()
        return True
    except:
        return None
        traceback.print_exc()
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFolder', default='none',
                        help='path to folder that contains all summaries [Required]')
    parser.add_argument('-o', '--outputFile', default='summary_all.csv', help='path to output file [Required]')
    input_folder = parser.parse_args().inputFolder
    output_path = parser.parse_args().outputFile
    summaries = []
    for file_name in os.listdir(input_folder):
        full_path = os.path.realpath(os.path.join(input_folder, file_name))
        summary = GlobalSummary.load_from_json_file(full_path)
        if summary:
            summaries.append(summary)
    statistic_all_rerun_to_csv(summaries, output_path)
    print "Final report is write to %s " % (output_path)





