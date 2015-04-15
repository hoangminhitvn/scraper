import re
import pdb
from scrapy_balloons.utils.html_string import *


class careeracademy:
    @classmethod
    def extract_links_follow(self, value):
        link_follow = re.sub(r'\r\n', '', value)
        return link_follow

    @classmethod
    def extract_links_parse(self, value):
        link_parse = re.sub(r' ', '', normalize_space(value))
        return link_parse

    @classmethod
    def certificattion(cls, response):
        keywords = response.xpath(
            "//ul[@id='featuresList']/li[contains(./text(),'Certificate of Completion')]//text()").extract()
        if keywords:
            name = response.xpath("//div[@id='product-detail-div']/h1//text()").extract()
        else:
            None

        return name[0]
