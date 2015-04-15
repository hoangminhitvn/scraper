from __future__ import division
import json
import os
import traceback
import time
import tempfile
import signal
from  scrapy_balloons.constant import *
from scrapy_balloons.utils.basefunctions import get_attr
from scrapy_balloons.utils.basefunctions import object_to_json
from scrapy_balloons.utils.datetimefunctions import time_display





class FieldCollector:
    def __init__(self, field_name=None):
        self.field_name = field_name
        self.count_total = 0
        self.count_null = 0
        self.percent_null = 0


    def inc_total(self):
        self.count_total += 1

    def inc_null(self):
        self.count_null += 1


    @classmethod
    def load_from_json(self, path_file=None, json_value=None):
        try:
            json_value = json.load(open(path_file)) if json_value is None else json_value
            object = FileInfo()
            for (k, v) in json_value.iteritems():
                setattr(object, k, v)
            return object
        except:
            print "FileInfo load from json failed"


class FileInfo:
    def __init__(self, size=0, modified=None, path=None, json_value=None):
        if json_value:
            self.size = get_attr(json_value, 'size')
            self.modified = get_attr(json_value, 'modified')
            self.path = get_attr(json_value, 'path')
        else:
            self.size = size
            self.modified = modified
            self.path = path


class S3Info:
    def __init__(self, compress_file=None, uploaded='No', bucket=None):
        self.compress_file = compress_file
        self.uploaded = uploaded
        self.bucket = bucket

    @classmethod
    def load_from_json(self, json_value=None):
        try:
            object = S3Info()
            for (k, v) in json_value.iteritems():
                setattr(object, k, v)
            return object
        except:
            traceback.print_exc()
            print "S3 Info  load from json failed"


class StatsCollector:
    def __init__(self, spider=None, config_file=None, output_file=None):
        self.fields_collector = []
        self.courses_total = 0
        self.execution_time = 0
        self.execution_time_display = None
        self.status = RUNNING_STATUS
        self.start_time = int(time.time())
        self.execution_time_display = None
        self.scrapy_collector = None
        self.spider = spider
        self.message = None
        self.suspect_requests_count = 0
        self.compress_file = None
        self.json_file = None
        self.s3_info = None
        self.average_percent_null = 0
        config_file = spider.config.config_file_path if config_file is None and spider else config_file
        #init run_all script
        if config_file:
            with open(config_file) as input_file:
                try:

                    json_v = json.load(input_file)
                    fields = json_v['output_config']['fields']
                    # self.provider_id = fields['provider_id']
                    self.config_file_name = config_file.split("/")[len(config_file.split("/")) - 1]
                    self.json_file = {"path": output_file}
                except:
                    traceback.print_exc()
                    print "Error to read file : %s" % (config_file)
                    pass


    @classmethod
    def load_from_json(self, path_file=None, json_value=None):
        try:
            json_value = json.load(open(path_file)) if json_value is None else json_value
            object = StatsCollector()
            for (k, v) in json_value.iteritems():
                if k in ['json_file', 'compress_file'] and v:
                    setattr(object, k, FileInfo(json_value=v))
                elif k == 'fields_collector' and v:
                    if v:
                        result = []
                        for v_ in v:
                            result.append(FieldCollector.load_from_json(json_value=v_))
                        setattr(object, k, result)
                elif k == 's3_info' and v:
                    setattr(object, k, S3Info.load_from_json(json_value=v))
                else:
                    setattr(object, k, v)
            return object
        except:
            traceback.print_exc()
            print "Stat Collector load from json failed json_value  %s  path_file %s" % (json_value, path_file)


    def start(self):
        self.start_time = int(time.time())

    def to_json(self):
        return object_to_json(self, ['spider'])

    def finish(self):
        if self.spider:
            collector = self.spider._crawler.stats
            self.scrapy_collector = json.dumps(collector,
                                               default=lambda o: o.__dict__ if hasattr(o, '__dict__') else None)
            self.end_time = int(time.time())
            self.execution_time = self.end_time - self.start_time
            self.execution_time_display = time_display(self.execution_time)
            self.courses_total = collector._stats[
                'item_scraped_count'] if 'item_scraped_count' in collector._stats else 0
            self.suspect_requests_count = len(self.spider.suspect_requests)
            # calcul the percent null and not null
            if self.courses_total:
                total_percent_null = 0
                for item in self.fields_collector:
                    percent_null = float("{0:.2f}".format(item.count_null / item.count_total))
                    item.percent_null = percent_null
                    total_percent_null += percent_null
                if total_percent_null != 0:
                    self.average_percent_null = float("{0:.2f}".format(total_percent_null / len(self.fields_collector)))
            if self.courses_total > 0 and self.average_percent_null <= PERCENT_FIELD_NULL_MAX:
                self.status = SUCCESS_STATUS
            elif self.average_percent_null > PERCENT_FIELD_NULL_MAX:
                self.status = FAILED_STATUS
                self.message = 'Average percentage of null percent is %s'%(self.average_percent_null)
            elif self.status == ITEM_SCRAPED_NOT_GROW_UP:
                self.status = FAILED_STATUS
                self.message = "The web site is very slowly or there are multiple incorrect requests"
            else:
                self.status = FAILED_STATUS
        else:
            raise Exception("Spider is not found")


    def inc_value(self, key, value):
        collector = self.get_collector(key)
        collector.inc_total()
        if value is None:
            collector.inc_null()

    def get_collector(self, key):
        for item in self.fields_collector:
            if item.field_name == key:
                return item
        item = FieldCollector(key)
        self.fields_collector.append(item)
        return item


    def default_path(self):
        default = "scrapy"
        default_path = os.path.join(tempfile.gettempdir(), default)
        if not os.path.exists(default_path):
            os.makedirs(default_path)
        return os.path.join(default_path, self.summary_name())

    def summary_name(self):
        name = self.config_file_name.replace("_config", "_summary")
        return name


    def get_summary_folder(self):
        return tempfile.gettempdir()


    def item_scraped_must_growing(self, signum, stack):
        if self.status is SUCCESS_STATUS:
            # don't do anything , sleep 1000 s and stop crawler
            time.sleep(1000)
            self.spider._crawler.stop()
        else:
            scrapy_stats_count = self.spider._crawler.stats._stats
            if 'item_scraped_count' in scrapy_stats_count and int(scrapy_stats_count['item_scraped_count']) > 0:
                if self.courses_total == int(scrapy_stats_count['item_scraped_count']):
                    # print "Error : Provider id %s the number of course is not in growing up, will close spider now " % (
                    #     self.provider_id)
                    self.status = ITEM_SCRAPED_NOT_GROW_UP
                    self.spider._crawler.stop()
                else:
                    self.courses_total = scrapy_stats_count['item_scraped_count']
                    signal.alarm(CHECK_ITEM_SCRAPED_COUNT_PERIODIC_TIME)
            else:
                signal.alarm(CHECK_ITEM_SCRAPED_COUNT_PERIODIC_TIME)





