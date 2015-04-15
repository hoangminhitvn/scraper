from scrapy_balloons.items import Instructor
from scrapy_balloons.utils.html_string import html_to_text


class informanagement:
    @classmethod
    def get_instructors(self, response, source=None):
        def first_non_null(value):
            if value and isinstance(value, list):
                for i in value:
                    if i and len(i.strip()) > 0:
                        return i
            return None

        table = response.xpath("//table")
        instructors = []
        if table:
            # case 1 : data as table format
            tr1 = table.xpath("//tr[1]")
            tr2 = table.xpath("//tr[2]")
            for i in range(1, len(tr1.xpath(".//td")) + 1):
                instructor = Instructor()
                try:
                    instructor['image'] = tr1.xpath("td[%s]//img/@src" % (i)).extract()[0]
                except:
                    pass
                try:
                    name = first_non_null(tr2.xpath("td[%s]//text()" % (i)).extract())
                    if name is None or len(name.strip()) == 0:
                        name = tr2.xpath("td[%s]//strong/text()" % (i)).extract()[0]
                    instructor['name'] = html_to_text(name)
                except:
                    pass
                instructors.append(instructor)
        else:
            # case 2 : data as  text format
            data = response.xpath(
                "//div[@id='article-content']//b[contains(.,'Speakers')]/following-sibling::b/text() | //div[@id='article-content']//b[contains(.,'Presenter')]/following-sibling::b/text()").extract()
            if not data:
                data = response.xpath(
                    "//div[@id='article-content']//b[contains(.,'PRESENTERS')]/following-sibling::b/text()").extract()
                data = data if len(data) % 2 == 0 else data[0:len(data) - 1]
                data = [v for i, v in enumerate(data) if i % 2 == 0]
            for i in data:
                instructor = Instructor()
                instructor['name'] = html_to_text(i)
                instructors.append(instructor)
        return instructors if instructors else None



















