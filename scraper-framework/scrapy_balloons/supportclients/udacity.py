import json
import pdb
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.prixfunctions import get_price_float
from scrapy_balloons.utils.basefunctions import *
from scrapy_balloons.utils.datetimefunctions import *
# from scrapy_balloons.utils.datetimefunctions import duration_filter
# from scrapy_balloons.items import Instructor


class udacity:
    """
    Step 1: Get course info from api
    Step 2: Get course info from a course

    """
    coursesapi = "https://www.udacity.com/public-api/v0/courses?projection=internal"
    course_url = "https://www.udacity.com/course/"
    output_cache = {}

    @classmethod
    def parse_courses(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider

        json_data = json.loads(response.body)['courses']
        json_data = json_data if balloon_spider.limit == -1 else json_data[:balloon_spider.limit]
        for course in json_data:
            from scrapy_balloons.spiders.balloon import balloon_spider
            # create output
            output = balloon_spider.create_new_product()

            # get info of course
            output['product_url'] = "https://www.udacity.com/course/" + course['key']
            output['name'] = course['title']
            output['product_image_url'] = course['image']
            output['product_video_url'] = course['teaser_video']['youtube_url']
            output['description'] = course['summary']
            output['difficulty'] = difficulty(course['level'])
            output['duration_filter'] = duration_filter(
                str(course['expected_duration']) + course['expected_duration_unit'])
            output['duration_display'] = str(course['expected_duration']) + ' ' + course['expected_duration_unit']
            output['toc'] = course['syllabus']
            output['prerequisites'] = course['required_knowledge']
            output['requirements'] = course['required_knowledge']
            instructors = []

            for ins in course['instructors']:
                instructor = Instructor()
                instructor['name'] = ins['name']
                instructor['bio'] = ins['bio']
                instructor['image'] = ins['image']
                instructor['link'] = None

                instructors.append(instructor)
            output['instructors'] = instructors

            key = output['product_url']
            udacity.output_cache[key] = output
            request = Request(url=key, meta={'key': key}, callback=udacity.parse_price, )
            yield request

    @classmethod
    def parse_price(self, response):
        # pdb.set_trace()
        key = response.meta['key']

        output = udacity.output_cache[key]

        output['price_currency'] = "USD"
        price_float = response.xpath(
            "substring(substring-before(substring-after(//script[contains(.,'amount')],'amount: '),','),1,3)").extract()

        if price_float:
            output['price_display_float'] = get_price_float(price_float)
        else:
            output['price_display_float'] = '0'

        yield output
