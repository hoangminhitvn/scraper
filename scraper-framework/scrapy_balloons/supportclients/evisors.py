import json
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.html_string import html_to_text
from scrapy_balloons.utils.datetimefunctions import *
from scrapy_balloons.utils.prixfunctions import *
import re


class evisors:
    """
    Custom callback function.
    Step1 : try to make the next request if necessary
    Step2 : Do mapping courses from response to the product json
    """

    api_url = "https://www.evisors.com/api/webinars/search.json?pagination[page]=%s"

    @classmethod
    def parse_product(cls, response):
        index = int(re.search(".*=(\d+)", response.url).group(1))
        next_index = index + 1
        next_url = evisors.api_url % (next_index)
        origin_products = []
        try:
            origin_products = json.loads(response.body)['data']['results']
        except:
            print "There is no courses in the response, got the limit"
        if origin_products:
            print "total courses %s " % (len(origin_products))
            request = Request(url=next_url, callback=evisors.parse_product)
            results = [request]
            results += evisors.convert_products(origin_products)
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
                product['product_image_url'] = data['image']['l']
                try:
                    video_id = data['freeChapter']['videoID']
                    if video_id:
                        product['product_video_url'] = urljoin("https://www.youtube.com/embed/", video_id)
                    else:
                        product['product_video_url'] = None
                except:
                    pass
                product['description'] = html_to_text(data['description'])
                product['published_date'] = data['date']['date']
                product['tz'] = data['date']['timezone']
                product['product_url'] = urljoin("https://www.evisors.com/", data['url'])
                instructors = []
                for ins in data['presenters']:
                    instructor = Instructor()
                    instructor['name'] = ins['name']
                    instructor['image'] = ins['avatar']['xl']
                    instructor['bio'] = html_to_text(ins['bio'])
                    instructor['link'] = urljoin("https://www.evisors.com/", ins['expert']['url'])
                    instructors.append(instructor)
                product['instructors'] = instructors
                product['price_currency'] = 'USD'
                product['price_display_float'] = get_price_float(data['price'])
                results.append(product)
            except:
                traceback.print_exc()
        return results