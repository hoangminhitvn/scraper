import json
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.datetimefunctions import *
from urlparse import urljoin


class pluralsight:
    """
    Custom callback function.
    Step1 : try to make the next request if necessary
    Step2 : Do mapping courses from response to the product json
    """
    courses_id_seen = set()
    courses_caches = dict()
    base_url = "http://www.pluralsight.com/"
    tag_url = "http://www.pluralsight.com/data/tags/search//1?pageSize=10000"
    courses_by_tag_url = "http://www.pluralsight.com/data/courses/tags?id=%s&pageSize=%s"
    tags_by_course_id_url = "http://www.pluralsight.com/data/course/relationships/%s"
    course_content_url = "http://www.pluralsight.com/data/course/content/%s"
    course_info_url = "http://www.pluralsight.com/data/course/%s"
    course_author_url = "http://www.pluralsight.com/data/course/authors/%s"
    course_all_urls = [course_content_url, course_info_url, course_author_url, tags_by_course_id_url]
    limit = -1
    price_info_url = "http://www.pluralsight.com/data/pricing/business"
    price = None

    @classmethod
    def parse(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        pluralsight.limit = balloon_spider.limit
        print "parse  %s" % (response)
        print "Call %s" % (pluralsight.tag_url)
        tags_request = Request(url=pluralsight.tag_url, callback=pluralsight.parse_tags)
        price_request = Request(url=pluralsight.price_info_url, callback=pluralsight.parse_price)
        requests = [tags_request, price_request]
        for r in requests:
            yield r


    @classmethod
    def parse_price(cls, response):
        json_data = json.loads(response.body)
        pluralsight.price = json_data['basicPrice']


    @classmethod
    def parse_tags(cls, response):
        print "parse_tags  %s" % (response)
        tags = json.loads(response.body)['tagsForCurrentPage']
        tags = [tag for tag in tags if tag['numberOfCourses'] > 0]
        tags = tags[:2]
        for tag in tags:
            if not pluralsight.is_limit() and tag['numberOfCourses'] > 0:
                url = pluralsight.courses_by_tag_url % (tag['name'], tag['numberOfCourses'])
                print "Call %s" % (url)
                yield Request(url=url, callback=pluralsight.parse_courses)

    @classmethod
    def parse_courses(cls, response):
        items = json.loads(response.body)['courses']
        print "parse_courses  %s" % (response)
        print "get %s courses" % (len(items))
        ids = [item['name'] for item in items if item['name'] not in pluralsight.courses_id_seen]
        for id in ids:
            pluralsight.courses_id_seen.add(id)
            for url_pattern in pluralsight.course_all_urls:
                if not pluralsight.is_limit():
                    url = url_pattern % (id)
                    print "parse_course Call url %s" % (url)
                    yield Request(url=url, callback=pluralsight.parse_part_course, meta={'id': id})

    @classmethod
    def is_limit(cls):
        if pluralsight.limit != -1 and len(pluralsight.courses_id_seen) > pluralsight.limit:
            return True
        return False

    @classmethod
    def parse_part_course(cls, response):
        print "parse_part_course get response %s" % (response)
        id = response.meta['id']
        if id not in pluralsight.courses_caches:
            pluralsight.courses_caches[id] = [response]
        else:
            pluralsight.courses_caches[id].append(response)
        if len(pluralsight.courses_caches[id]) == 4:
            course = pluralsight.create_course(id)
            del pluralsight.courses_caches[id]
            return course

    @classmethod
    def create_course(self, id):
        from scrapy_balloons.spiders.balloon import balloon_spider
        product = balloon_spider.create_new_product()
        data = pluralsight.courses_caches[id]
        product['product_url'] = urljoin(pluralsight.base_url, 'courses/%s' % (id))
        product['price_display_float'] = float_to_string(pluralsight.price)
        product['price_currency'] = 'USD'
        for r in data:
            json_data = json.loads(r.body)
            if 'data/course/content' in r.url:
                # example see : http://www.pluralsight.com/data/course/content/clickonce-deployment-fundamentals
                product['toc'] = json_data
            elif 'data/course/authors' in r.url:
                # see http://www.pluralsight.com/data/course/authors/clickonce-deployment-fundamentals
                authors = []
                for data in json_data:
                    author = Author()
                    author['name'] = data['fullName']
                    author['link'] = urljoin(pluralsight.base_url, 'author', data['authorHandle'])
                    author['bio'] = data['longBio']
                    author['image'] = data['largeImageUrl'].replace('//', '')
                    authors.append(author)
                product['authors'] = authors
            elif 'data/course/relationships' in r.url:
                prod_keywords = [item['name'] for item in json_data['tags']]
                product['prod_keywords'] = prod_keywords
            else:
                # see http://www.pluralsight.com/data/course/clickonce-deployment-fundamentals
                product['name'] = json_data['title']
                product['description'] = json_data['description']
                product['short_desc'] = json_data['shortDescription']
                product['difficulty'] = json_data['level']
                product['published_date'] = convert_date(json_data['releaseDate'])
                product['duration_filter'] = duration_filter(json_data['duration'])
                product['duration_display'] = pluralsight.duration_display(json_data['duration'])
                rating_data = json_data['courseRating']
                rating = ProductRating()
                rating['pub_status'] = 'L'
                rating['overall_rating'] = str(int(round(rating_data['rating'])))
                rating['rating_only'] = '1'
                product['ProductRating'] = rating
        return product


    @classmethod
    def duration_display(cls, value):
        try:
            # input 02:22:28
            # return 2 h 22 m
            value = value.split(':')
            return "%s h %s m" % (int(value[0]), int(value[1]))
        except:
            print "Error to convert duration_display %s" % (value)
            return None







