import re
import pdb
import json
class junipernetworks:

    page_url = "https://learningportal.juniper.net/juniper/user_activity_info.aspx?id=%s"
    @classmethod
    def extract_links_course(self, value):
        page_number = re.search("activity\((\d+)", value)
        if page_number:
            return junipernetworks.page_url%(page_number.group(1))
        else:
            return None