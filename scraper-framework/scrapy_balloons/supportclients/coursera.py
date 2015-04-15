import json
from scrapy_balloons.items import *
from scrapy_balloons.utils.basefunctions import get_by_curl
from scrapy_balloons.utils.html_string import html_to_text
from scrapy_balloons.utils.datetimefunctions import *

class coursera:
    """
    Step 1: Get info courses and instructors from api
    Step 2: Build courses
    """
    instructors_url = "https://www.coursera.org/api/instructors.v1?fields=firstName,lastName,bio,photo,shortName,profileId,middleName,prefixName,shortName,suffixName"
    courses_data = []
    events = []
    instructors_data = dict()
    courses_detail_data = dict()


    @classmethod
    def get_courses(cls, response):
        url = "https://www.coursera.org/api/courses.v1?fields=categories,certificates,description,display,instructorIds,membershipIds,partnerIds,partnerLogo,photoUrl,previewLink,primaryLanguages,specializations,subtitleLanguages,v1Details,workload,memberships.v1(vcMembershipId),partners.v1(classLogo,homeLink,links,logo,name,shortName),v1Details.v1(aboutTheCourse,courseFormat,courseSyllabus,faq,readings,recommendedBackground,sessionIds,videos),v1Sessions.v1(active,dbEndDate,durationString,hasSigTrack,instructorIds,selfStudy,startDay,startMonth,startYear,vcDetails),instructors.v1(firstName,fullName,lastName,middleName,partnerIds,partners,photo,prefixName,profileId,shortName,suffixName),languages.v1(englishName),specializations.v1(logo,name,partnerIds,shortName)&includes=categories,instructorIds,membershipIds,partnerIds,primaryLanguages,specializations,subtitleLanguages,v1Details,memberships.v1(vcMembershipId),v1Details.v1(sessionIds),v1Sessions.v1(instructorIds,vcDetails),instructors.v1(partnerIds),specializations.v1(partnerIds)"
        data = get_by_curl(url)
        source = json.loads(data)
        coursera.events = source['linked']['v1Sessions.v1']
        coursera.courses_data = source['elements']
        for detail in source['linked']['v1Details.v1']:
            coursera.courses_detail_data[detail['id']] = detail

        instructors_response = get_by_curl(coursera.instructors_url)
        return coursera.get_instructors(instructors_response)



    @classmethod
    def get_instructors(cls, response):
        instructors = json.loads(response)['elements']
        for ins in instructors:
            coursera.instructors_data[ins['id']] = ins
        return coursera.build_course()

    @classmethod
    def get_events_by_courseid(cls, id):
        return [event for event in coursera.events if event['courseId'] == id]

    @classmethod
    def find_instructors(self, ids):
        return [coursera.instructors_data[id] for id in ids]


    @classmethod
    def build_course(cls):
        from scrapy_balloons.spiders.balloon import balloon_spider

        courses_data = coursera.courses_data if balloon_spider.limit == -1 else coursera.courses_data[
                                                                                :balloon_spider.limit]
        for data in courses_data:
            if 'en' in data['primaryLanguages']:
                output = balloon_spider.create_new_product()
                output['name'] = html_to_text(data['name'])
                output['product_url'] = 'https://www.coursera.org/course/' + data['slug']
                output['description'] = html_to_text(data['description'])
                output['product_image_url'] = data['photoUrl']
                duration_week = data['workload']
                # instructors
                ins_course = []
                if 'instructorIds' in data:
                    ins_data = coursera.find_instructors(data['instructorIds'])
                    for in_data in ins_data:
                        instructor = Instructor()
                        instructor['name'] = "%s %s %s" % (
                        get_attr(in_data, 'firstName'), get_attr(in_data, 'middleName'), get_attr(in_data, 'lastName'))
                        instructor['bio'] = html_to_text(get_attr(in_data, 'bio'))
                        instructor['image'] = get_attr(in_data, 'photo')
                        instructor['link'] = 'https://www.coursera.org/instructor/~' + in_data['profileId'] if contains(
                            in_data, 'profileId') else None
                        ins_course.append(instructor)

                # product events
                course_events = coursera.get_events_by_courseid(data['id'])
                if course_events:
                    product_events = []
                    for event_data in course_events:
                        event = ProductEvent()
                        event['language'] = 'eng'
                        start_time = "%s %s %s" % (get_attr(event_data, 'startDay'), get_attr(event_data, 'startMonth'),
                                                   get_attr(event_data, 'startYear'))
                        event['start_date_local'] = convert_date(start_time)
                        if contains(event_data, 'dbEndDate'):
                            end_time = event_data['dbEndDate']
                            event['end_date_local'] = epoch_time_to_date(end_time / 1000)
                        event['duration_display'] = event_data['durationString']
                        event['duration_filter'] = duration_filter(event_data['durationString'])
                        product_events.append(event)
                        output['product_events'] = product_events

                else:
                    output['language'] = 'eng'
                    output['duration_display'] = duration_week.encode('ascii', 'ignore')
                    if 'hours/week' in output['duration_display']:
                        if '-' in output['duration_display']:
                            output['duration_filter'] = duration_filter(
                                output['duration_display'].split('-')[0] + ' hours')
                        else:
                            output['duration_filter'] = duration_filter(output['duration_display'].split('/')[0])

                    elif ' hours ' in output['duration_display']:
                        if '-' in output['duration_display']:
                            output['duration_filter'] = duration_filter(
                                output['duration_display'].split(' hours ')[0].split('-')[0] + ' hours')
                        else:
                            output['duration_filter'] = duration_filter(
                                output['duration_display'].split(' hours ')[0] + ' hours')
                    else:
                        None
                    output['instructors'] = ins_course

                courses_detail = get_attr(coursera.courses_detail_data, data['id'])
                if courses_detail:
                    output['toc'] = get_attr(courses_detail, 'aboutTheCourse')
                    videos = get_attr(courses_detail, 'videos')
                    if videos and len(videos) > 0:
                        output['product_video_url'] = videos[0]['source']
                    else:
                        # pdb.set_trace()
                        output['product_video_url'] = None
                output['language'] = 'eng'
                yield output

