from scrapy_balloons.utils.allfunctions import *
import pdb


class speaklanguages:
    @classmethod
    def speak(self, data):
        url = []
        data = data if isinstance(data, list) else [data]
        if data:
            for i in range(len(data)):
                image_item = urljoin('http:', data[i])
                url.append(image_item)
            return url
        else:
            print "Not field product_image_url"