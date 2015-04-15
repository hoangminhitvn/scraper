from scrapy_balloons.utils.allfunctions import *
from urlparse import urljoin
from scrapy_balloons.utils.datetimefunctions import *


class cadmasters:
    caches_name = {}


    @classmethod
    def break_data_level_0(cls, response):
        table = response.xpath("//table[@cellpadding='8' and count(.//tr) >2]")
        if len(table) > 1:
            print "Error xpath main table"
        else:
            data = table.xpath("./tr")
            result = []
            # case 1 : has event
            if len(data) % 3 == 0:
                for i, k in enumerate(data):
                    if i % 3 == 0:
                        course_name = data[i].xpath(".//span[@class='bheader_sm']/a/text()").extract()[0]
                        cadmasters.caches_name[course_name] = data[i].xpath(".//span[@class='bheader_sm']/a/@name").extract()[0]
                        result.append(data[i])
            # case 2 no event
            else:
                for i, k in enumerate(data):
                    if i % 2 == 0:
                        course_name = data[i].xpath(".//span[@class='bheader_sm']/a/text()").extract()[0]
                        cadmasters.caches_name[course_name] = data[i].xpath(".//span[@class='bheader_sm']/a/@name").extract()[0]
                        result.append(data[i])
            return result


    @classmethod
    def set_product_url_product_event(cls,item,spider):
        all_event = spider.pre_run_service.responses_received_by_key['all_events'][0]
        tables = all_event.xpath("//tr/td/table[@cellpadding='4']")
        def get_data_product_event(tables,course_name):
            for table in tables:
                data = table.xpath("./tr[1]/td[1]/text()").extract()
                if data and data[0] == course_name:
                    return table
        product_event  = get_data_product_event(tables,item['name'])
        course_id = cadmasters.caches_name[item['name']]
        item['product_url'] = "%s#%s"%(item['product_url'],course_id)
        print item['product_url']

        if product_event :
            if item['duration_display']:
                # from scrapy_balloons.spiders.balloon import balloon_spider
                # output = balloon_spider.create_new_product()

                prod_events = product_event.xpath(".//tr//a")
                product_events = []
                start_date = None
                for prod_event in prod_events:

                    event = ProductEvent()
                    event['language'] = 'eng'

                    start_time = prod_event.xpath(".//text()").extract()[0]
                    start_date = convert_date(start_time.encode('ascii','ignore') + ' 9:00 am')
                    event['start_date_local'] = start_date

                    event['duration_display'] = item['duration_display']
                    event['duration_filter'] = item['duration_filter']

                    event['price_currency'] = 'USD',
                    event['price_display_float'] = item['price_display_float']

                    product_events.append(event)

                item['product_events'] = product_events
                item['start_date_local'] = start_date







