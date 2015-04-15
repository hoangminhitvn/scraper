import datetime
from scrapy_balloons.utils.datetimefunctions import convert_date


class cfpa:
    @classmethod
    def get_url_leve2(self,response, source):
        condition = source['0'].xpath(".//input[@src='images/Register-Now.gif']")
        if condition:
            data =source['0'].xpath("td[2]/a/@href").extract()[0].split('/')
            date = source['0'].xpath("td[1]/strong/text()[1]").extract()[0]
            url = "CourseRegistration.aspx?TempID=%s&CourseID=%s&Place=%s&STDATE=%s" %(data[1],data[2],data[3],datetime.datetime.strptime(convert_date(date),"%Y-%m-%d").strftime('%m/%d/%y'))
            return url
        else:
            return None
