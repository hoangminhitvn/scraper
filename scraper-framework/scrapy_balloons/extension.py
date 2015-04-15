import os
from scrapy import log
from scrapy import signals
from scrapy_balloons.services import DataService
class OverrideSettings(object):
    """
    all key and value in the settings object below will be read and update to spider settings (settings.py)
    Here is example in config file :
    "settings": {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_balloons.useragent.RandomUserAgentMiddleware":500
        },
        "DOWNLOAD_DELAY": 5
    }
    """
    @classmethod
    def from_crawler(cls, crawler):
        try:
            # it's only here to be able to get the output file name, try to delete the file if existed
            op_file = crawler.settings.attributes['FEED_URI'].value
            if op_file and os.path.exists(op_file):
                os.remove(op_file)
                log.msg("Delete the output file %s : Successful" %(op_file),level=log.INFO)
        except OSError:
            log.msg("Delete the output file %s : Failed" %(op_file),level=log.INFO)
            pass
        spider = crawler._spider
        if hasattr(spider, 'config'):
            settings = spider.config.settings
            spider_fields = ['handle_httpstatus_list']
            for k, v in settings.iteritems():
                if k in spider_fields:
                    # attribute for spider
                    setattr(spider, k, v)
                else:
                    # attribute for spider setting
                    current_value = crawler.settings.get(k)
                    if isinstance(current_value,dict):
                        # if the type is dict, need update value from config file
                        crawler.settings.get(k).update(v)
                    else:
                        #todo check other type if needed
                        crawler.settings.set(k, v)

class HandleOnClose(object):

    @classmethod
    def from_crawler(self, crawler):
        crawler.signals.connect(HandleOnClose.spider_closed, signal=signals.spider_closed)

    @classmethod
    def spider_closed(self, spider):
        DataService(spider).handle_on_close()
        spider.log("closed spider %s" % spider.name)

