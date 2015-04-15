from scrapy_balloons.utils.prixfunctions import *
from scrapy.selector import Selector
from urlparse import urljoin
import re
import pdb


class greycampus:
    api_url = "http://www.greycampus.com/getworkshops?page=%s"
    cpt = 0
    unique_course_urls = []

    @classmethod
    def parse_cat(self, response):
        from scrapy_balloons.spiders.balloon import balloon_spider

        pager = int(re.search('\\d+', response.url).group(0))
        next_pager = pager + 1
        next_url = self.api_url % next_pager
        try:
            url_courses = Selector(response=response).xpath(
                "//body/div[contains(@class,'item')]//h3//a/@href").extract()
        except:
            print "There is no courses in the response, got the limit"
        if url_courses:
            request = Request(url=next_url, callback=greycampus.parse_cat)
            results = [request]
            for result in results:
                yield result
            for url_course in url_courses:
                url_course_join = urljoin('http://www.greycampus.com', url_course)
                if url_course_join not in greycampus.unique_course_urls:
                    greycampus.unique_course_urls.append(url_course_join)
                    print "start request %s" % (url_course_join)
                    yield balloon_spider.start_download(url_course_join, response)
            print len(results)
        else:
            yield None

    @classmethod
    def parse_course(self, response):
        print "callback %s" % (response.url)