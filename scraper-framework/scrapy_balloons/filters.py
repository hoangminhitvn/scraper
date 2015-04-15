from scrapy_balloons.spiders.balloon import *
from scrapy.exceptions import DropItem
import traceback


class PostFilters(object):
    """
    Validate item before export feedly
    Example from config file :

    "post_filters": {
      "filters_not": [
        {
          "python": "'http://www.tradingacademy.com/education/' == item['product_url']"
        }
      ]
    }
    """
    def process_item(self, item, spider):
        if spider.config.post_filters:
            result = True
            try:
                if 'filters' in spider.config.post_filters:
                    for filter in spider.config.post_filters['filters']:
                        ## if found one return False, ignore this item
                        if eval(filter['python']) == False:
                            result = False
                if 'filters_not' in spider.config.post_filters:
                    for filter_not in spider.config.post_filters['filters_not']:
                        ## if found one True, ignore this item
                        if eval(filter_not['python']) == True:
                            result = False
            except:
                pass
            if result == False:
                raise DropItem
        return item


class StatsFilters(object):
    def process_item(self, item, spider):
        def inc_value_(prefix, item, fields):
            fields = get_attr(fields, 'fields')
            if item and fields and isinstance(fields, dict):
                for k in fields.keys():
                    if not isinstance(fields[k], unicode):
                        if isinstance(item, dict):
                            collector.inc_value("%s.%s" % (prefix, k), item[k])
                        elif isinstance(item, list):
                            for sub_item in item:
                                collector.inc_value("%s.%s" % (prefix, k), sub_item[k])

        try:
            collector = spider.collector
            fields = get_attr(spider.config.output, 'fields')
            if fields and isinstance(fields, dict):
                for k in fields.keys():
                    if k == 'instructors':
                        inc_value_('instructors', item['instructors'], fields[k])
                    elif k == 'publishers':
                        inc_value_('publishers', item['publishers'], fields[k])
                    elif k == 'certificates':
                        inc_value_('certificates', item['certificates'], fields[k])
                    elif k == 'authors':
                        inc_value_('authors', item['authors'], fields[k])
                    elif k == 'ProductRating':
                        inc_value_('ProductRating', item['ProductRating'], fields[k])
                    if not isinstance(fields[k], unicode):
                        collector.inc_value(k, item[k])
        except:
            traceback.print_exc()
            raise DropItem
        return item
