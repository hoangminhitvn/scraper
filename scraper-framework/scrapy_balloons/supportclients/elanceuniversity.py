import json
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.html_string import html_to_text
from scrapy_balloons.utils.datetimefunctions import *
import pdb


class elanceuniversity:
    """
    Custom callback function.
    Step1 : try to make the next request if necessary
    Step2 : Do mapping courses from response to the product json
    """

    api_url = "https://www.elance.com/q/eol_university/search?terms[]=%s"

    @classmethod
    def parse_product(cls, response):
        #pdb.set_trace()
        index = int(re.search(".*=(\d+)", response.url).group(1))
        next_index = index + 1
        next_url = elanceuniversity.api_url % (next_index)
        origin_products = []
        try:
            origin_products = json.loads(response.body)['nodes']
        except:
            print "There is no courses in the response, got the limit"
        if origin_products:
            print "total courses %s " % (len(origin_products))
            request = Request(url=next_url, callback=elanceuniversity.parse_product)
            results = [request]
            results += elanceuniversity.convert_products(origin_products)
            for result in results:
                yield result
        else:
            yield None


    @classmethod
    def convert_products(self, origin_products):
        from scrapy_balloons.spiders.balloon import balloon_spider

        results = []
        for data in origin_products:
            try:
                product = balloon_spider.create_new_product()
                product['name'] = data['title']
                product['product_image_url'] = data['video_thumbnail']
                product['description'] = html_to_text(data['body'][0]['value'])
                product['product_url'] = urljoin("https://www.elance.com/", data['url'])
                product['duration_display'] = data['video_duration']['hms_labeled']
                product['duration_filter'] = duration_filter(data['video_duration']['hms_labeled'])
                results.append(product)
            except:
                traceback.print_exc()
        return results