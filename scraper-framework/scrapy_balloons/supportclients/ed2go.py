from scrapy_balloons.utils.datetimefunctions import convert_date_special
from scrapy_balloons.utils.basefunctions import normalize_space
import copy
class ed2go:

    @classmethod
    def set_start_date(self,data, field, selector, response,source):
        dates = selector.xpath("./div[contains(.,'Start Dates:')]/strong/text()").extract()[0]
        dates = [convert_date_special(normalize_space(date)) for date in dates.split(',')]
        results =[]
        for date in dates:
            item = copy.deepcopy(data[0])
            item['start_date_local'] = date
            results.append(item)
        return results