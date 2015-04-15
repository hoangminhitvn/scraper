__author__ = 'hoangminh'
import json
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.datetimefunctions import *


class knowledgecity:
    """
    Step 1: Create request from 'id' on list_course_id
    Step 2: Parse courses

    """
    list_course_id = "http://www.knowledgecity.com/jsonStrings/kcity/courses/courses.json?ver=88a"
    course_api = "http://www.knowledgecity.com/jsonStrings/kcity/courses/courseJsonsEn/"

    @classmethod
    def get_link_course(cls, response):
        # pdb.set_trace()
        ids_course = json.loads(response.body).keys()
        for id_course in ids_course:
            url_course = "http://www.knowledgecity.com/jsonStrings/kcity/courses/courseJsonsEn/%s.json" % id_course

            yield Request(url=url_course, callback=knowledgecity.get_info_course)

    @classmethod
    def get_info_course(cls, response):
        data_json = json.loads(response.body)

        from scrapy_balloons.spiders.balloon import balloon_spider

        output = balloon_spider.create_new_product()

        # Get product url
        prod_url_1 = "http://www.knowledgecity.com/%s" %data_json['id']
        prod_url_2 = data_json['title']
        prod_url = prod_url_1 + '-' + prod_url_2
        output['product_url'] = prod_url.replace(' ','-')

        output['name'] = data_json['title']
        output['product_type_id'] = data_json['id']
        output['description'] = data_json['description']
        output['toc'] = data_json['chapters']
        output['duration_display'] = data_json['trt']
        output['duration_filter'] = duration_filter(data_json['trt'])

        # authors = []
        # author = Author()
        #
        # author['name'] = data_json['author']
        # author['bio'] = None
        # author['link'] = None
        # author['image'] = None
        #
        # authors.append(author)
        #
        # output['authors'] = authors

        return output


