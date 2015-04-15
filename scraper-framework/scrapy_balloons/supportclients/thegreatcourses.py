import json, re
from scrapy_balloons.utils.basefunctions import *
from scrapy.http.response.html import HtmlResponse
from scrapy_balloons.utils.html_string import text_to_selector
import re
class thegreatcourses:


    review_api = "https://theteachingcompany.ugc.bazaarvoice.com/%sqa-en_us/%s/reviews.djs?format=embeddedhtml&page=%s"
    @classmethod
    def get_data_rating_reviews(self, response):
        #https://www.thegreatcourses.com:80/courses/music/beethoven-s-piano-sonatas.html?bvrrp=3456/reviews/product/2/7250.htm
        print "go get_data_rating_reviews"
        pages_selector = response.xpath("//span[contains(@class,'BVRRPageLink')]//a")
        last_page = None
        course_id  = None
        api_code = None
        for page in pages_selector:
            try:
                link = page.xpath("@href").extract()[0]
                course_id = re.search("(\d+).htm",link).group(1)
                api_code = re.search("bvrrp=(\d+)",link).group(1)
                last_page = int(page.xpath("text()").extract()[0])
            except:
                pass
        urls  =[]
        if last_page >0:
            for i in range(0,last_page):
                url = thegreatcourses.review_api %(api_code,course_id,i)
                urls.append(url)
        return urls






    @classmethod
    def text_to_html(cls, data):
        result = []
        for r in data:
            if isinstance(r,HtmlResponse) and 'review' in r.url:
                temp=re.search("BVRRSourceID\":\"(.*)\"\},",r.body).group(1)
                #temp =temp.replace("\\r","\r").replace("\\n","\n").replace("\\",'')
                selector = text_to_selector(temp)
                result.append(selector)
            else:
                result.append(r)
        return result




