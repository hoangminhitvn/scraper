from scrapy_balloons.utils.basefunctions import *


class codeschool:
    start=0
    size = 10
    @classmethod
    def request_comments(self, response):
        # first request
        if 'reviews' not in response.url:
            url = "%s/reviews?offset=%s" % (response.url,codeschool.start)
        # check if need to make the next request
        elif len(str(response.body).strip()) > 0:
            pattern_url = re.search("(.*offset=)\d+", response.url).group(1)
            current_offset = int(re.search('offset=(\d+)', response.url).group(1))
            next_offset = current_offset + codeschool.size
            url = "%s%s" % (pattern_url, next_offset)
        else:
            return None
            # finish
        return {'url': url, 'headers': {'X-Requested-With': 'XMLHttpRequest'},
                'next_request': 'codeschool.request_comments'}
