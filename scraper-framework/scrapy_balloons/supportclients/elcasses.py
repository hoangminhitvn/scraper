from scrapy import Request
from scrapy_balloons.items import *

import re

class eclasses:
    # function calculate rating

    def rating(self, response):
        star = response.xpath("//strong[contains(.,'Rating')]/following-sibling::img/@class//text()")
        int_star = re.search('\d+',star)

        for iteam in int_star:
            total_rating = (sum(int(iteam)) / 20) * 100