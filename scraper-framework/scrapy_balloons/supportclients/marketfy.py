from scrapy_balloons.utils.basefunctions import *
import re
import pdb


class marketfy:
    start = 1

    @classmethod
    def request_comments(self, response):
        url = None
        # first request
        if 'review' not in response.url:
            # first time
            url = "%sreviews/?page=%s" % (response.url, marketfy.start)
        else:
            # check if need next page or end page
            is_has_next_page = response.xpath("//li[@class='disabled']/a[./@title='Next Page']")
            if is_has_next_page != []:
                current_page = int(re.search('page=(\d+)', response.url).group(1))
                next_page = current_page + 1
                url = re.sub('page=(\d+)', 'page=%s' % (next_page), response.url)
            else:
                return None
        print url
        return {'url': url, 'next_request': 'marketfy.request_comments'}