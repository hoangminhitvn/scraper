import urllib
from scrapy_balloons.items import *
from scrapy.http.response.html import HtmlResponse
from scrapy_balloons.utils.html_string import html_to_text
from scrapy_balloons.utils.datetimefunctions import *
from random import randint


class ingram_micro:


    box_url = []
    desc_api = 'https://www.im-plus.be/site/?tc=LoadTrainingDetails&trainingid=%s'

    @classmethod
    def parse(cls, response):

        from scrapy_balloons.spiders.balloon import balloon_spider
        data = response.xpath("//table[@class='training_table']//tr[@bgcolor]")

        def events(selector):

            event = ProductEvent()
            event['language'] = 'eng',
            event['price_currency'] = 'EUR'

            price = selector.xpath("./td[7]//text()").re("\\d.*")
            if price:
                event['price_display_float'] =  html_to_text(price[0])
            else:
                event['price_display_float'] = '0'

            location = selector.xpath("./td[5]/text()[1]").extract()[0]
            event['location_display'] = html_to_text(location)

            start_date = selector.xpath("substring-before(concat(./td[1]/text()[2],' ',./td[5]/i/text()),'-')").extract()[0]
            event['start_date_local'] = convert_date(start_date)

            return event

        # course_dict = {}
        title = []
        results = []

        for d in data:
            name = d.xpath("./td[@class='trainingtitle']//text()").extract()[0]
            print name
            if name not in title:
                try:
                    output = balloon_spider.create_new_product()

                    output['name'] = name

                    description = d.xpath("./td[@class='trainingtitle']/span/@rel-tid").extract()
                    output['description'] = ingram_micro.get_desc(description[0])

                    price = d.xpath("./td[7]//text()").re("\\d.*")
                    if price:
                        output['price_display_float'] =  html_to_text(price[0])
                    else:
                        output['price_display_float'] = '0'

                    start_date = d.xpath("substring-before(concat(./td[1]/text()[2],' ',./td[5]/i/text()),'-')").extract()[0]
                    output['start_date_local'] = convert_date(start_date)

                    location = d.xpath("./td[5]/text()[1]").extract()[0]
                    output['location_display'] = html_to_text(location)
                    output['product_events'] = events(d)

                    output['product_url'] = "%s#%s" %(response.url,len(results) + 1)
                    # pdb.set_trace()
                    title.append(name)
                    results.append(output)
                except:
                    pass

            else:
                for i in results:
                    if name in i['name']:
                        prod_events = []
                        old_event = i['product_events']
                        new_events = events(d)
                        prod_events.append(old_event)
                        prod_events.append(new_events)

                        i['product_events'] = prod_events
                    else:
                        pass

        return results



    @classmethod
    def get_desc(cls, value):
        try:
            # Step 1
            url_desc = ingram_micro.desc_api % (value)
            # Step 2
            data = urllib.urlopen(url_desc)
            response = HtmlResponse(url=url_desc, body=data.read())

            data = None
            all_xpath = [
                "substring-before(//div[@class='training_details_content'],'Language')",
                "substring-before(//div[@class='training_details_content'],'Please bring your')",
                "//div[@class='training_details_content']/p/text()",
                "//div[@class='training_details_content']/div[1]/text()",
                "//div[@class='training_details_content']/span/text()",
                "//div[@class='training_details_content']//text()"
            ]

            for xpath in all_xpath:
                data = response.xpath(xpath).extract()
                desc = html_to_text(data)
                if desc:
                    return desc

            return None

        except:
            pass

    def get_prod_id(self, value):
        if 'Webinar' in value:
            return "4"
        else:
            return "1"


