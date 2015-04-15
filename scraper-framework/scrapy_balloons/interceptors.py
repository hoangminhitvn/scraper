from scrapy_balloons.utils.allfunctions import *
from scrapy_balloons.utils.basefunctions import contains



class PostInterceptor(object):
    """
    data from config file will be a list of python function.
    Each python function receive item object passe in parameter.
    The item object will be modified by these python function
    Example from config file
    "post_interceptors": [
      {
        "python": "item['product_events'] = [event for event in item['product_events'] if event['location_display']]"
      }
    ]
    """

    def process_item(self, item, spider):
        if spider.config.post_interceptors:
            inters = spider.config.post_interceptors if isinstance(spider.config.post_interceptors, list) else [
                spider.config.post_interceptors]
            for inter in inters:
                if not isinstance(inter, dict) or not contains(inter, 'python'):
                    log.msg("Config the interceptor is not correct", level=log.INFO)
                    print "Config for interceptor must be a dict contains 'python' key"
                else:
                    try:
                        exec (inter['python'])
                    except:
                        log.msg("PostInterceptor : impossible exec the python code %s" % (inter['python']),
                                level=log.INFO)
                        pass
        return item
