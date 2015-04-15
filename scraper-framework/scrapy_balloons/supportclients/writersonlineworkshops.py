from __future__ import division
import json
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.html_string import html_to_text
from scrapy_balloons.utils.datetimefunctions import *
# import pdb



class writersonlineworkshops:
    """
    Custom callback function.
    Step1 : pasre categories
    Step2 : pasre course
    """
    # start_url = "https://www.howdesignuniversity.com/learn/courseGroups"
    courses_api_url = "https://www.writersonlineworkshops.com/learn/courseGroups?slug=%s"
    categories_api_url = "https://www.writersonlineworkshops.com/learn/courseGroups"

    # Step 1
    @classmethod
    def parse_categories(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        limit = balloon_spider.limit
        json_data = json.loads(response.body)['courseGroups']
        ids = [course['slug'] for course in json_data]
        for index,id in enumerate(ids):
            if limit== -1 or  index < limit:
                yield Request(url=writersonlineworkshops.courses_api_url % (id),
                              callback=writersonlineworkshops.parse_course)

    # Step 2
    @classmethod
    def parse_course(cls, response):
        print response.url
        json_data = json.loads(response.body)
        from scrapy_balloons.spiders.balloon import balloon_spider

        output = balloon_spider.create_new_product()
        # get course_groups
        info = get_attr(json_data, 'courseGroups')[0]
        output['product_image_url'] = info['asset']
        output['name'] = info['title']
        output['product_url'] = urljoin('https://www.writersonlineworkshops.com/courses/', info['slug'])

        # get courseTabs
        course_tabs = get_attr(json_data, 'courseTabs')
        #get description
        for item in course_tabs:
            if 'Overview' in item['label']:
                output['description'] = html_to_text(item['body'])
            #get audience
            elif 'Who Should Take' in item['label']:
                output['audience'] = html_to_text(item['body'])
            #get toc
            elif 'Course Outline' in item['label']:
                output['toc'] = item['body']
        # get courses
        courses = get_attr(json_data, 'courses')
        #################################################
        product_events = []
        has_price = False
        for item in courses:
            if not is_expired(item['courseStartDate']):
                event = ProductEvent()
                event['language'] = 'eng'
                event['start_date_local'] = convert_date(item['courseStartDate'])
                event['end_date_local'] = convert_date(item['courseEndDate'])
                event['price_display_float'] = item['priceInCents'] / 100
                has_price = True
                product_events.append(event)
                output['product_events'] = product_events
        if not has_price and len(courses) > 0:
            event = ProductEvent()
            event['price_display_float'] = item['priceInCents'] / 100
            event['price_currency'] = 'USD'
            product_events.append(event)
            output['product_events'] = product_events
        return output



