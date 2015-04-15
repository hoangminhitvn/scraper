from scrapy_balloons.utils.allfunctions import *
from scrapy.http import Request
from scrapy_balloons.items import *
from time import gmtime, strftime
import re


class aws:
    """
    Step 1: Create 1 request from code 'RequestVerificationToken'
    Step 2: Get event's data from response
    """
    api_url = "https://www.aws.training/api/2014/v1/session/anonymous"

    # Step 1
    @classmethod
    def create_request(cls, response):
        code_ev = response.xpath("//input[@id='hiddenAntiForgeryToken']/@value").extract()
        if code_ev:
            course_id = re.search('courseid=(\d+)', response.url).group(1)
            date_range_start = strftime("%Y-%m-%d", gmtime())
            date_range = str(int(date_range_start.split('-')[0]) + 1)
            date_range_end = date_range_start.replace(date_range_start.split('-')[0], date_range)
            """
            body={
              "Page": null,
              "Filters": {
                "CourseId": "4",
                "DateRangeStart": "2015-02-25",
                "DateRangeEnd": "2016-02-25",
                "LanguageId": 2
              }
            }
            """
            body = "{ 'Page': null, 'Filters': { 'CourseId': '%s', 'DateRangeStart': '%s', 'DateRangeEnd': '%s', 'LanguageId': 2} }" % (
            course_id, date_range_start, date_range_end)

            return {'url': aws.api_url, 'method': 'POST', "body": body,
                    'headers': {'Content-Type': 'application/json; charset=UTF-8',
                                'RequestVerificationToken': code_ev[0]}}


    # Step 2
    @classmethod
    def create_events(cls, response):
        events_json = json.loads(response.body)['Sessions']
        results = []
        if events_json:
            for event in events_json:
                item = ProductEvent()
                item['language'] = 'eng'

                # Get duration
                item['duration_display'] = event['DisplayDuration']
                item['duration_filter'] = duration_filter(event['DisplayDuration'])

                # Get start date and end date
                start_date = event['StartDateTime'].replace('T', ' ')
                item['start_date_local'] = convert_date(start_date)

                end_date = event['EndDateTime'].replace('T', ' ')
                item['end_date_local'] = convert_date(end_date)

                # Get location
                item['location_display'] = html_to_text(event['Location']['FormattedAddress'])
                item['location_country'] = html_to_text(event['Location']['City']['Country']['Name'])
                item['location_city'] = html_to_text(event['Location']['City']['Name'])
                item['location_addr'] = html_to_text(event['Location']['FormattedAddress'].split(',')[0])

                # Get time zone
                item['tz'] = event['Location']['TimeZone']['DisplayUtcOffset']

                results.append(item)
            return results





















