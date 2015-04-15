from scrapy_balloons.utils.allfunctions import *
from scrapy_balloons.utils.datetimefunctions import *
from datetime import datetime
import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


class zeitgeistminds:
    @classmethod
    def start(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider

        all_course_url = 'https://www.zeitgeistminds.com/zce/video'
        data = zeitgeistminds.curl_url(all_course_url)
        courses_data = re.search(".*\n(.*)", data).group(1)
        courses_data = json.loads(courses_data)
        courses_id = [d['id'] for d in courses_data]
        courses_id = courses_id if balloon_spider.limit == -1 else courses_id[:balloon_spider.limit]
        for id in courses_id:
            # get data detail for a course

            data = zeitgeistminds.curl_url("%s/%s" % (all_course_url, id))
            course_data = re.search(".*\n(.*)", data).group(1)
            course_data = json.loads(course_data)
            product = balloon_spider.create_new_product()
            product['product_url'] = "https://www.zeitgeistminds.com/talk/" + str(get_attr(course_data, 'id')) + "/" + str(get_attr(course_data, 'slug'))
            product['product_image_url'] = get_attr(course_data, 'img_url')
            product['name'] = get_attr(course_data, 'title')
            product['description'] = get_attr(course_data, 'description')
            product['product_video_url'] = "https://www.youtube.com/watch?v=%s" % get_attr(course_data,
                                                                                       'video_id') if get_attr(
                course_data, 'video_id') else None
            product['partner_prod_id'] = get_attr(course_data, 'id')
            product['duration_filter'] = get_attr(course_data, 'duration')
            product['published_date'] = datetime.strptime(str(get_attr(course_data, 'date')),'%b %Y').strftime('%Y - %m')
            yield product


    @classmethod
    def curl_url(self, url):
        print "Get %s" %(url)
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        # For new  PycURL versions:
        #c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()
        body = buffer.getvalue()
        # Body is a string on Python 2 and a byte string on Python 3.
        # If we know the encoding, we can always decode the body and
        # end up with a Unicode string.
        return body



#detail course data
# {"additional_resources": [], "chapters": [], "date": "Sep 2014", "description": "", "duration": 919, "id": 5511102989336576, "img_url": "https://lh5.ggpht.com/okNp5bnJD0mmuXwQio3WflEC3mQU-UliVEhnE8p6GG0a08q34mHK0AgJ-sgJ8TK2S8-HeBJuuPxG9kKUZnE-PX1L2LfNtgZ5fMU", "people": [{"company": "McCaw Professor of Economics, Stanford University", "id": 4981034768662528, "img_url": "https://lh5.ggpht.com/Sa_AYDnof3Z-wwestrzYRZmu8lOJg2y9bvj1bI-WmSAMkp0RwF2-fn4e6-_A7CogQa3VX4P5YHfhw06RiQW--SC6AG4xKLin", "mobile_img_url": "https://lh3.ggpht.com/CYHeih1CcbvIwaYXaSC0JLsqnvQjMYYXgrSZM-nb3Vj369Tcv1mprhBLrVQxadHCkT78UPRd6A2TAzL9awOlGXwIv25JRnzeZ68", "name": "Al Roth", "portrait_img_url": "https://lh3.ggpht.com/wXnIz_EUE498nQosFia5atIBizxUmdVQKn1IPKutJD54rCRKuw2LUQNeoKuX6UQXap7ahVC_lzlMo-RZJKh5QZTOXE1QaieOow", "slug": "al-roth"}], "shorter_version": 6074052942757888, "shorter_version_slug": "the-economic-marketplace-of-the-kidney-transplant-exchange-clip-al-roth", "slug": "the-economic-marketplace-of-the-kidney-transplant-exchange-al-roth", "title": "The Economic Marketplace of the Kidney Transplant Exchange", "video_id": "9j-MmYir2nE"}


