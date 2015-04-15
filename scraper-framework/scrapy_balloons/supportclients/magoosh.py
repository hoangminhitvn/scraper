from scrapy_balloons.items import *
from scrapy import Request
import pdb
import re

class magoosh:
    size = 1
    review_link = 'https://%s.magoosh.com/testimonials?page=1'

    @classmethod
    def get_review_link(cls, response):
        keygen = str(re.search('//(\w+)', response.url).group(1))
        if 'testimonials' not in response.url:
            url = magoosh.review_link % (keygen)
            exit_link = response.xpath("//div[@class='section']/div[@class='row']")
        elif response.xpath("//div[@class='pagination']/ul/li[@class='last next']/a"):
            page_current = int(re.search('page=(\d+)', response.url).group(1))
            page_skip = page_current + magoosh.size
            url = re.sub('page=\d+', 'page=%s' % (page_skip), response.url)
        else:
            return None
        return {'url': url, 'next_request': 'magoosh.get_review_link'}
