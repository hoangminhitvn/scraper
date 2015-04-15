from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.html import TextResponse


class EncodeUtf8Response(object):
    """A downloader middleware to force utf8 encoding for all responses."""

    def process_response(self, request, response, spider):
        """
        TextResponse will be not applied by RuleExtractor. Need convert to HtmlResponse
        """
        body = response.body_as_unicode().encode('utf8') if hasattr(response,'body_as_unicode') else response.body
        if response.status != 200 and hasattr(spider, 'suspect_requests'):
            spider.suspect_requests.append("%s  %s \n" % (response.status, response.url))
        if isinstance(response, TextResponse):
            return HtmlResponse(url=response.url, body=body,request=response.request, status=response.status,headers=response.headers)
        else:
            return response.replace(body=body)


    def process_exception(self, request, exception, spider):
        print "---------process_exception----------------------------------------------"
        print request
        print exception
        print spider


