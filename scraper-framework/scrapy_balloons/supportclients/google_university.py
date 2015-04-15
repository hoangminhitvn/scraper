from urlparse import urljoin


class google_university:
    @classmethod
    def set_product_url(self, item, spider):
        if item['product_url'] == 'https://developers.google.com/university/courses/mobile':
            response = spider.resources_ext[item['product_url']]
            courses = response.xpath("//div[@class='course-listing']//a")
            for c in courses:
                if item['name'] == c.xpath('./text()').extract()[0]:
                    item['product_url'] = urljoin('https://developers.google.com/university/courses/',
                                                  c.xpath('./@href').extract()[0])

