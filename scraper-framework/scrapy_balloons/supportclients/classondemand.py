from scrapy_balloons.utils.datetimefunctions import *



class classondemand:
    @classmethod
    def duration_filter(self, selector):
        if selector:
            try:
                data = selector.re('\d+\.?\d*.*hrs?.*\d+\.?\d*.*min(?:utes?)?|\d+\.?\d*hrs?|\d+\.?\d*HRS?|\d+\.?\d* hours?.*\d+ min(?:utes?)?|\d+\.?\d* hours?|\d+ min(?:utes?)?|\d+\.?\d*.*hours?')[0].replace('</b>','')
                data = duration_filter(data)
                if data:
                    return data
                else:
                    return self.handleZero(selector)
            except:
                return self.handleZero(selector)
        return None

    @classmethod
    def handleZero(self,selector):
        data = ' '.join(normalize_space(selector.extract())).lower()
        patterns = {
            "(\d+\.?\d*) hrs? (\d+\.?\d*) m(?:(?:in(?:utes?)?)?)?": "float(result.group(1))*3600 +float(result.group(2))*60", # 1 h 2m
            "(\d+\.?\d*) hrs?": "float(result.group(1))*3600",  #'7 hrs
            "(\d+\.?\d*)hrs?\. (\d+\.?\d*).*m(?:(?:ins?)?)?\.": "float(result.group(1))*3600 +float(result.group(2))*60", #1hr 35 mins
        }
        for k, v in patterns.iteritems():
            result = re.search(k, data)
            if result:
                return eval(v)