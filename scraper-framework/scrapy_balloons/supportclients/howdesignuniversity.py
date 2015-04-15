import json
from scrapy import Request
from scrapy_balloons.items import *
from scrapy_balloons.utils.html_string import html_to_text
from scrapy_balloons.utils.datetimefunctions import *
# import pdb


class howdesignuniversity:
    """
    Custom callback function.
    Step1 : pasre categories
    Step2 : pasre course
    """
    # start_url = "https://www.howdesignuniversity.com/learn/courseGroups"
    courses_api_url = "https://www.howdesignuniversity.com/learn/courseGroups?slug=%s"
    categories_api_url = "https://www.howdesignuniversity.com/learn/courseGroups"

    #Step 1
    @classmethod
    def parse_categories(cls, response):
        json_data = json.loads(response.body)['courses']
        ids = [course['slug'] for course in json_data]
        for id in ids:
            # if id == 'stefan-mumaw-creative-boot-camp' :
            yield Request(url=howdesignuniversity.courses_api_url % (id), callback=howdesignuniversity.parse_course)

    #Step 2
    @classmethod
    def parse_course(cls, response):

        json_data = json.loads(response.body)

        if json_data['courseGroups']:
            from scrapy_balloons.spiders.balloon import balloon_spider

            output = balloon_spider.create_new_product()

            # get course_groups
            course_groups = get_attr(json_data, 'courseGroups')
            if course_groups and len(course_groups) > 0:
                #get field 'product_image_url'
                if [course_groups[0]['asset']]:
                    output['product_image_url'] = [course_groups[0]['asset']]

                #get name Instructor
                if course_groups[0]['categories']:
                    # instructor_name = [item['value'] for item in course_groups[0]['categories'] if item['label']=='Instructor']
                    for item in course_groups[0]['categories']:
                        if item['label'] == 'Instructor':
                            instructor_name = item['value']
                        else:
                            instructor_name = None
            else:
                instructor_name = None


            # get courseTabs
            coursetabs = get_attr(json_data, 'courseTabs')
            if coursetabs and len(coursetabs) > 0:
                #get description
                if coursetabs[0]['body']:
                    output['description'] = html_to_text(coursetabs[0]['body'])

                #get toc
                if len(coursetabs) > 3:
                    if coursetabs[2]['body']:
                        output['toc'] = coursetabs[2]['body']

            # get profileBlocks
            profileblocks = get_attr(json_data, 'profileBlocks')
            if profileblocks and len(profileblocks) > 0:
                #get bio Instructor
                if profileblocks[0]['bio']:
                    instructor_bio = html_to_text(profileblocks[0]['bio'])
            else:
                instructor_bio = None

            # import pdb
            # pdb.set_trace()
            # get users
            users = get_attr(json_data, 'users')
            if users and len(users) > 0:
                #get image Instructor
                for item in users:
                    if item['asset']:
                        instructor_image = item['asset']
                    else:
                        instructor_image = None
            else:
                instructor_image = None

            # get courses
            courses = get_attr(json_data, 'courses')
            if courses and len(courses) > 0:
                #################################################
                url = courses[0]['slug']
                output['product_url'] = urljoin('https://www.howdesignuniversity.com/courses/', url)
                # get field 'name'
                output['name'] = courses[0]['title']

                #get product_events
                instructors = []
                product_events = []
                if courses[0]['courseEndDate']:
                    event = ProductEvent()

                    event['language'] = 'eng'
                    # get field 'start_date_local'
                    if courses[0]['courseStartDate']:
                        event['start_date_local'] = courses[0]['courseStartDate'].split('T')[0] + ' ' + \
                                                    courses[0]['courseStartDate'].split('T')[1].split('.')[0]
                    elif courses[0]['enrollmentStartDate']:
                        event['start_date_local'] = courses[0]['enrollmentStartDate'].split('T')[0] + ' ' + \
                                                    courses[0]['enrollmentStartDate'].split('T')[1].split('.')[0]

                    # get field 'end_date_local'
                    if courses[0]['courseEndDate']:
                        event['end_date_local'] = courses[0]['courseEndDate'].split('T')[0] + ' ' + \
                                                  courses[0]['courseEndDate'].split('T')[1].split('.')[0]
                    elif courses[0]['enrollmentEndDate']:
                        event['end_date_local'] = courses[0]['enrollmentEndDate'].split('T')[0] + ' ' + \
                                                  courses[0]['enrollmentEndDate'].split('T')[1].split('.')[0]

                    #get price
                    if courses[0]['priceInCents']:
                        event['price_display_float'] = float(
                            str(courses[0]['priceInCents'])[:-2] + '.' + str(courses[0]['priceInCents'])[-2] +
                            str(courses[0]['priceInCents'])[-1])


                    #get instructor
                    instructor = Instructor()

                    instructor['name'] = instructor_name
                    instructor['bio'] = instructor_bio
                    instructor['image'] = instructor_image
                    instructor['link'] = None
                    instructors.append(instructor)

                    event['instructors'] = instructors

                    product_events.append(event)

                else:
                    #get price
                    if courses[0]['priceInCents']:
                        output['price_display_float'] = float(
                            str(courses[0]['priceInCents'])[:-2] + '.' + str(courses[0]['priceInCents'])[-2] +
                            str(courses[0]['priceInCents'])[-1])

                    instructor = Instructor()

                    instructor['name'] = instructor_name
                    instructor['bio'] = instructor_bio
                    instructor['image'] = instructor_image
                    instructor['link'] = None
                    instructors.append(instructor)

                    if instructor_image == None and instructor_bio == None:
                        output['instructors'] = None
                    else:
                        output['instructors'] = instructors

                output['product_events'] = product_events

            return output



