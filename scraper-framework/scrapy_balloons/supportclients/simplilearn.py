import re
import pdb
from scrapy_balloons.items import ProductRating
from scrapy_balloons.utils.basefunctions import get_attr
import json
class simplilearn:
    start = 0
    size = 10
    review_url = "http://www.simplilearn.com/api/v1?method=loadMoreReviews&course_id=%s&skip=%s"
    duration_url = "http://www.simplilearn.com/api/v1?method=getCoursePreviewData&course_id=%s"

    @classmethod
    def request_comments(self, response):
        if 'loadMoreReviews' not in response.url:
            course_id = response.xpath("//form[@id='frmOnlineCourses']//div[contains(@class, 'price')][1]//button/@ng-click").re("\\d+")
            if course_id:
                course_id = course_id[0]
            elif response.xpath("//div[@class='no_clas_foound']//button/@ng-click").re("\\d+"):
                course_id = response.xpath("//div[@class='no_clas_foound']//button/@ng-click").re("\\d+")[0]
            url = simplilearn.review_url % (course_id, simplilearn.start)
        # check if need to make the next request
        elif response.body.strip() != '[]':
            skip_current = int(re.search('skip=(\d+)', response.url).group(1))
            next_skip = skip_current + simplilearn.size
            url = re.sub('skip=\d+', 'skip=%s' % (next_skip), response.url)
        else:
            return None
        return {'url': url, 'next_request': 'simplilearn.request_comments'}

    @classmethod
    def product_rating(cls, source):
        ratings = []
        source = get_attr(source,'1_1')
        if source:
            source = source if source and isinstance(source,list) else [source]
            for response in source:
                rating_list = json.loads(response.body)
                for data in rating_list:
                    rating = ProductRating()
                    rating['username'] = data['personName']
                    rating['review'] = data['content']
                    rating['overall_rating'] = data['rating']
                    ratings.append(rating)
        return ratings

    @classmethod
    def request_duration(self, response):
        course_id = response.xpath("//form[@id='frmOnlineCourses']//div[contains(@class, 'price')][1]//button/@ng-click").re("\\d+")
        if course_id:
            course_id = course_id[0]
            url = simplilearn.duration_url % (course_id)
        elif response.xpath("//div[@class='no_clas_foound']//button/@ng-click").re("\\d+"):
            course_id = response.xpath("//div[@class='no_clas_foound']//button/@ng-click").re("\\d+")[0]
            url = simplilearn.duration_url % (course_id)
        else:
            return None
        return {'url': url}

    @classmethod
    def get_duration(cls, source):
        source = get_attr(source, '1_2')
        if source:
            source = source if source and isinstance(source, list) else [source]
            for response in source:
                content = json.loads(response.body)['content']
                keys = content.keys()
                if len(keys) == 0:
                    return None
                elif len(keys) == 1:
                    duration=0
                    childSection = content[keys[0]]['childSection']
                    for data in childSection:
                        duration += data['seconds']
                    return duration
                elif len(keys) > 1:
                    duration=0
                    all_key = content.keys()
                    for key in all_key:
                        childSection = content[key]['childSection']
                        for data in childSection:
                            duration += data['seconds']
                        return duration
                else:
                    return None


