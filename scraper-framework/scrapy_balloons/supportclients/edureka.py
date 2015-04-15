from scrapy_balloons.items import *
from scrapy_balloons.utils.allfunctions import *

class edureka:

    @classmethod
    def start_times(cls, response):

        times = response.xpath("normalize-space(string(//script[contains(.,'start_date')]))").re("if \(time_zone == \'IST\'.{60}")

        for time in times:
            datetime = time.split("'")[5] + ' 2015 ' + time.split("'")[3]
            start_dates = convert_date(datetime)

        return start_dates

    @classmethod
    def product_evemts(cls, response, start_dates):
        xpath_events = response.xpath("//tr[contains(@class,'active')]")

        result = []
        for i, event in xpath_events:
            for j, start_date in start_dates:
                if i == j:
                    item = ProductEvent()

                    item['language'] = 'eng'
                    item['start_date_local'] = start_date

                    item['duration_display'] = event.xpath("./td[2]/text()").extract()
                    item['duration_filter'] = duration_filter(event.xpath("./td[2]/text()").extract())

                    item['price_currency'] = 'USD'





