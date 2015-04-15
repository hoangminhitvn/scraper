import pdb
from scrapy_balloons.items import Instructor


class bignerdranch:
    @classmethod
    def set_instructors(cls, data, source):
        if source['1_1'] is None:
            result = []
            res_level1 = source['1']
            names = source['1'].xpath("//p[contains(.,'Instructor(s)')]/a/text()").extract()
            names_unique = list(set(names))
            for name in names_unique:
                instructor = Instructor()
                instructor['name'] = name
                result.append(instructor)
            return result
        else:
            return data


    @classmethod
    def get_instructors_url(cls, data):
        data = data if isinstance(data, list) else [data]
        urls = []
        for url in data:
            if 'about-us' in url:
                if '.html' in url:
                    url = url.replace('.html', '/')
                else:
                    url = url + '/'
                urls.append(url)
        return list(set(urls))





