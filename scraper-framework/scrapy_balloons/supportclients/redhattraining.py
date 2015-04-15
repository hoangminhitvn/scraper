import pdb
from scrapy_balloons.utils.basefunctions import normalize_space
class redhattraining:


    @classmethod
    def product_events(self,data,response):
        locations=normalize_space(response.xpath("//select[@id='training-method-461']//option/text()").extract())
        for index,item in enumerate(data):
            item['location_name'] = locations[index]
        return data
