from scrapy_balloons.items import *
from scrapy_balloons.utils.datetimefunctions import *
import demjson
import re

class salesforce:
    """

    """

    @classmethod
    def get_event(cls, response, item):
        data=re.search("classCfgs:(.*),filters",response.body,re.S).group(1)

        events = demjson.decode(data)
        from scrapy_balloons.spiders.balloon import balloon_spider

        output = balloon_spider.create_new_product()

        product_events = []

        for event in events:
            prod_event = ProductEvent()
            prod_event['langauge'] = 'eng'
            prod_event['location_display'] = event['location']

            start_time = event['start']
            prod_event['start_date_local'] = epoch_time_to_date(start_time)

            end_time = event['end']
            prod_event['end_date_local'] = epoch_time_to_date(end_time)

            prod_event['duration_display'] = item['duration_display']
            prod_event['duration_filter'] = item['duration_filter']

            prod_event['price_currency'] = 'USD'
            prod_event['price_display_float'] = item['price_display_float']

            product_events.append(prod_event)

            output['product_events'] = product_events

        return output