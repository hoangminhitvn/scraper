import pdb
import copy
from scrapy_balloons.utils.datetimefunctions import *
from scrapy_balloons.utils.html_string import *


class f5:
    @classmethod
    def product_events(self, data, source):
        from scrapy_balloons.spiders.balloon import balloon_spider
        response_events = balloon_spider.pre_run_service.responses_received_by_key['all_events']
        response_events = [event for event in response_events if
                           'course-schedules/schedule-plain.php?courseID' in event.url]
        final_result = []
        def create_product_events(object_clone, url, response):
            result = []
            all_trs = response.xpath("//tr")
            for tr in all_trs:
                all_tds = tr.xpath("./td")
                if len(all_tds) == 4 and all_tds[1].xpath("./a/@href"):
                    if url == all_tds[1].xpath("./a/@href").extract()[0]:
                        item = copy.deepcopy(object_clone)
                        date_text = all_tds[0].xpath('./text()').extract()  # Feb 9-10, 2015
                        date_text = html_to_text(date_text[0]) if date_text else None
                        location_text = all_tds[2].xpath('./text()').extract()  #Montreal, Canada (Scalar Decisions)
                        location_text = html_to_text(location_text[0]) if location_text else None
                        item['start_date_local'] = get_start_date(date_text)
                        item['end_date_local'] = get_end_date(date_text)
                        if location_text :
                            item['location_display'] = location_text
                            if re.search('online', location_text, re.I) is None:
                                city = re.search("(.*),",location_text)
                                item['location_city'] = city.group(1) if city else None
                        result.append(item)
            return result
        for res in response_events:
            event_data = create_product_events(data[0], source['1'].url, res)
            if event_data:
                final_result = final_result + event_data
        final_result = final_result if final_result else data
        return final_result


