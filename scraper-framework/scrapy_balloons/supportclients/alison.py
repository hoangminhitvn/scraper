from scrapy_balloons.utils.basefunctions import *
import re
import pdb
from urlparse import urljoin

class alison:
    # Base url
    base_url = "http://alison.com/"

    @classmethod
    def request_comments(self, response):
        last_page = response.xpath("//ul[contains(@class, 'pagination')]/li[last()-1]/a/text()").extract()
        # case 1 : if have pagination
        rating_url = response.url
        if last_page:
            last_page = int(last_page[0])
            urls = [urljoin(rating_url, str(i)) for i in range(1, int(last_page) + 1)]
            return urls
        else:
            return None

