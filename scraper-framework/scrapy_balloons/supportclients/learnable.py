import json
from scrapy_balloons.items import ProductRating
import pdb
from scrapy_balloons.utils.allfunctions import *

class learnable:
    review_rating = "https://learnable.com/api/v1/reviews?id=%s"

    @classmethod
    def get_page_review_rating(self, response):
        review_id = response.xpath("//reviews/@gid").extract()
        if review_id:
            return learnable.review_rating % (review_id[0])
        else:
            return None


    @classmethod
    def get_data_review_rating(cls, response):
        json_data = json.loads(response.body)
        result = []
        for review in json_data:
            pr = ProductRating()
            pr['rating_only'] = "0"
            pr['pub_status'] = "L"
            pr['overall_rating'] = review['score']
            pr['username'] = html_to_text(review['user']['name'])
            pr['review'] = html_to_text(review['blurb'])
            result.append(pr)
        return result
