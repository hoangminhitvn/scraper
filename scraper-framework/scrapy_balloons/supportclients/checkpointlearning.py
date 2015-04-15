import re
import pdb
import json
class checkpointlearning:
    start = 1
    size = 1
    page_url = "https://checkpointlearning.thomsonreuters.com/CourseFinder/Search?pageNumber=%s"

    @classmethod
    def extract_links_cat(self, value):
        page_number = re.search("\d+",value)
        if page_number:
            return checkpointlearning.page_url%(page_number.group(0))
        else:
            return None

    @classmethod
    def get_duration_value(self, response):
        duration_data = response.xpath("//div[contains(./span/text(), 'NASBA Field of Study')]//td[3]/text()").re("\\d+.?\\d+")

        total = sum(float(i) for i in duration_data)
        return str(total) + ' hours'