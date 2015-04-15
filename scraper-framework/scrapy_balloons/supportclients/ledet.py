import re
import pdb
import json
class ledet:
    start = 1
    event_url = "https://www.ledet.com/events?course_ids=%s&page_for_branch=1&page_for_online=1&page_for_primary=1&per_page_for_branch=10000&per_page_for_online=10000&per_page_for_primary=10000#primary_anchor"

    @classmethod
    def request_events(self, response):
        course_id = (response.url).split('courses/')[1]

        if course_id:
            course_id = course_id
            url = ledet.event_url % (course_id)
        else:
            return None
        return {'url': url}



