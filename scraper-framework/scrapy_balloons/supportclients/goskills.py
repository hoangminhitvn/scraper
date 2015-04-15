from scrapy import Request
from urlparse import urljoin

class goskills:
    @classmethod
    def process_request(cls,url):
        request = Request(urljoin("https://www.goskills.com/", url),)
        request.meta['dont_redirect'] = True
        return request


