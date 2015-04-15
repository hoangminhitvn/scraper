import pdb
from scrapy_balloons.utils.allfunctions import *

class ebay:

    @classmethod
    def address(cls, value):
        result = []
        for i in value:
            result.append(i[::-1] + ', ')
        return html_to_text(result)
        # print html_to_text(value)
        # print value
        # pdb.set_trace()
