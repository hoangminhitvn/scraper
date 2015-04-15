import time
from scrapy_balloons.utils.seleniumfunctions import *
from scrapy.http import HtmlResponse


class curious:
    @classmethod
    def process_request(request, spider):
        driver = spider.driver
        driver.get(request.url)
        while (True):
            try:
                driver.find_element_by_xpath("//a[contains(./div,'View More Courses')]").click()
                time.sleep(1)
            except:

                spider._requests_to_follow(HtmlResponse(request.url, encoding='utf-8', body=driver.page_source.encode('utf-8')))
                break





