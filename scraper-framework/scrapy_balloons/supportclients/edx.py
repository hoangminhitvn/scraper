import json
from scrapy_balloons.items import ProductRating

class edx:
    # url_pattern = "https://www.coursetalk.com/widgets/review/long/edx/%s"

    @classmethod
    def extract_links_parse(self, value):
        link_parse = value.replace('\\','')
        return link_parse


    @classmethod
    def not_in_english(cls,response):
        detect_key = response.xpath("//*[@class='course-detail-title']/text()").extract()
        try:
            # import pdb
            # pdb.set_trace()
            title = str(detect_key[0])
            return False
        except:
            return True

    # @classmethod
    # def get_data_comment_rating(self, response):
    #     code = response.xpath("//div[@id='ct-read-review-widget']/@data-course").extract()
    #     if code:
    #         return edx.url_pattern % (code[0])
    #     else:
    #         return None
    #
    #
    # @classmethod
    # def create_comment_rating(cls, response):
    #     json_data = json.loads(response.body)
    #     reviews = json_data['reviews']
    #     result = []
    #     for review in reviews:
    #         pr = ProductRating()
    #         pr['overall_rating'] = review['rating']/2
    #         pr['username'] = review['author']
    #         pr['review'] = review['body']
    #         result.append(pr)
    #     return result