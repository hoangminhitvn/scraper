import re
import pdb
from scrapy_balloons.utils.basefunctions import get_attr
import json
class filtered:
    toc_url = "https://filtered.com/api/syllabus/?courseid=%s"

    @classmethod
    def request_toc(self, response):
        if '/syllabus/' not in response.url:
            course_id = response.xpath("//div[contains(@class, 'course-id')]//span/text()").extract()
            if course_id:
                course_id = course_id[0]
                url = filtered.toc_url % (course_id)
            else:
                None
        else:
            return None
        return {'url': url}

    @classmethod
    def toc_field(cls, source):
        toc = []
        source = get_attr(source, '1_1')
        if source:
            source = source if source and isinstance(source,list) else [source]
            for response in source:
                content = json.loads(response.body)['html']
                if content:
                    toc = content
                else:
                    None
        return toc