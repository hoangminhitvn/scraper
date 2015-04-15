from scrapy_balloons.utils.allfunctions import *


class lingq:
    courses_page_url = "http://www.lingq.com/api/languages/en/learn-recommendations/?format=json&page=%s&level=1&level=2&level=3&level=4&level=5&level=6&level=7"
    cache_courses = {}

    @classmethod
    def parse(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        limit = balloon_spider.limit
        urls = []
        courses = []
        if 'api' not in response.url:
            url = lingq.courses_page_url % (1)
            urls.append(url)
        else:
            # check data response
            data = json.loads(response.body)
            if len(data) > 0:
                # get the next page
                current_page = int(re.search('page=(\d+)', response.url).group(1))
                url = lingq.courses_page_url % (current_page + 1)
                urls.append(url)
                for sub_data in data:
                    courses.append(lingq.mapping_with_course(sub_data))
                    # no need to get the next page
        stop = False
        for course in courses:
            if limit != -1 and len(lingq.cache_courses) >= limit:
                stop = True
            if stop is False:
                lingq.cache_courses[course['product_url']] = course
                yield Request(url=course['product_url'], callback=lingq.parse_course)
        if stop is False:
            for url in urls:
                yield Request(url=url, callback=lingq.parse)

    @classmethod
    def parse_course(cls, response):
        course = get_attr(lingq.cache_courses, response.url)
        if course:
            del lingq.cache_courses[response.url]
            duration_data = response.xpath("//div[@id='lessons']//div[@class='time']/strong/text()").extract()
            course['duration_filter'] = duration_filter(duration_data)
            return course


    @classmethod
    def mapping_with_course(self, data):
        from scrapy_balloons.spiders.balloon import balloon_spider
        product = balloon_spider.create_new_product()
        product['name'] = get_attr(data, 'title')
        product['description'] = get_attr(data, 'description')
        product['difficulty'] = get_attr(data, 'level').split()[0] if get_attr(data, 'level') else None
        product['partner_prod_id'] = get_attr(data, 'id')
        product['published_date'] = convert_date(get_attr(data, 'pub_date'))
        product['price_display_float'] = get_price_float(get_attr(data, 'price'))
        product['product_url'] = get_attr(data, 'url')
        product['product_image_url'] = get_attr(data, 'image_url')
        kw_data = get_attr(data, 'tags')
        product['prod_keywords'] = kw_data.split(',') if kw_data else None
        product['price_display_float'] = '0'
        return product






