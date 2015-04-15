# -*- coding: utf-8 -*-
from __future__ import division
import pdb, traceback
from datetime import date
import datetime, time
import dateutil.parser as date_parser
from scrapy_balloons.constant import *
from scrapy_balloons.utils.basefunctions import *
from datetime import timedelta


def tz(value):
    value = normalize_space(value) if isinstance(value, unicode) else value
    r = re.search(ALL_TIME_ZONE, value, re.I)
    return r.group(0) if r else "?"


def duration_display(value):
    value = int(value)
    seconds_by_day = 8 * 3600
    seconds_by_week = seconds_by_day * 5
    seconds_by_hour = 3600
    msg = ""
    weeks = int(value / seconds_by_week)
    days = int((value - weeks * seconds_by_week) / seconds_by_day)
    hours = int((value - weeks * seconds_by_week - days * seconds_by_day) / seconds_by_hour)
    minutes = int((value - weeks * seconds_by_week - days * seconds_by_day - hours * seconds_by_hour) / 60)
    seconds = value % 60
    list = [{weeks: " %s weeks" % weeks}, {days: " %s days" % days}, {hours: " %s hours" % hours},
            {minutes: " %s minutes" % minutes},
            {seconds: " %s seconds" % seconds}]
    for i in list:
        k = i.keys()[0]
        if k == 1:
            msg += i[k].replace('s', '')
        elif k != 0:
            msg += i[k]

    if "second" in msg:
        return msg.strip()
    else:
        return msg.replace('econd', 'second').strip()

def string_to_second(value_raw):
    try:
        """
        1 -- only convert to low case and use the pattern pre-predefined to match
        Any new pattern will be added here.
        """
        value_raw_low = value_raw.lower().strip()
        patterns = \
            {
                "(\d+:\d+.*(am|pm))": "minus_times_to_seconds(result.group(1))",  # "November 8, 2014 - 2:00PM - 5:00PM
            }
        for k, v in patterns.iteritems():
            result = re.search(k, value_raw_low)
            if result:
                return eval(v)
        """
        2 -- clean the data by extract only alphabet and numeric character abd  split by integer
        and use the pattern pre-predefined to match. Any new pattern will be added here.
        """
        value = clean_date_time_data(value_raw)
        patterns = \
            [
                # jan 12 2014 oct 12 2014
                {"^\w+ \d{1,2} \d{4} \w+ \d{1,2} \d{4}$": "minus_dates_to_seconds(result.group(0))"},
                # 1 2 3 | 2 3 (hour minute second or minute second)
                {"(\d+ ){1,2}\d+$": "hours_minutes_to_seconds(result.group(0))"},
                # 3 months
                {"^(\d+\.?\d*) months?$": "months_to_seconds(float(result.group(1)))"},
                # 1 h|hour|hours,
                {"^(\d+\.?\d*) h(?:(?:ou)?rs?)?$": "float(result.group(1))*3600"},
                #1 weeks 2 days
                {
                    "^(\d+\.?\d*) w(?:eeks?)? (\d+\.?\d*) (?:days?)": "float(result.group(1))*144000 + float(result.group(2))*28800"},
                # 2 weeks ,one week has 5 days
                {"^(\d+\.?\d*) w(?:eeks?)?$": "float(result.group(1))*144000"},
                # 109 m|min|minute|minutes
                {"^(\d+\.?\d*) m(?:(?:in(?:(?:ute)?s?)?)?)?$": "float(result.group(1))*60"},
                # 1 h 10 s
                {
                    "^(\d+\.?\d*) h(?:(?:ou)?rs?)? (\d+\.?\d*) (?:(?:s)|(?:sec)|(?:second)|(?:seconds))?$": "float(result.group(1))*3600 + float(result.group(2))"},
                #1 h 2 s
                {"^(\d+\.?\d*) (?:(?:s)|(?:sec)|(?:second)|(?:seconds))?$": "float(result.group(1))"},
                #1 s|sec|second|seconds
                {
                    "^(\d+\.?\d*) h(?:(?:ou)?rs?)? (\d+\.?\d*) m(?:(?:in(?:(?:ute)?s?)?)?)?$": "float(result.group(1))*3600 +float(result.group(2))*60"},
                # 1h 2m
                {
                    "^(\d+\.?\d*) m(?:(?:in(?:(?:ute)?s?)?)?)? (\d+\.?\d*) (?:(?:s)|(?:sec)|(?:second)|(?:seconds))?$": "float(result.group(1))*60 +float(result.group(2))"},
                # 1 m 20s
                {
                    "^(\d+\.?\d*) h(?:(?:ou)?rs?)? (\d+\.?\d*) m(?:(?:in(?:(?:ute)?s?)?)?)? (\d+\.?\d*) (?:(?:s)|(?:sec)|(?:second)|(?:seconds))?$": "float(result.group(1))*3600 +float(result.group(2))*60 + float(result.group(3))"},
                #1 h 2 p 30 s
                {
                    "^(\d+\.?\d*) d(?:ays?)? (\d+\.?\d*) h(?:(?:ou)?rs?)?": "float(result.group(1))*28800+float(result.group(2))*3600"},
                # 1 day
                {"^(\d+\.?\d*) d(?:ays?)?$": "float(result.group(1))*28800"},
                # 8am 10 am
                {".*\d+.*(am|pm).*\d+.*(am|pm).*": "minus_times_to_seconds(value)"},
                # 1 hrs 1 min
                {
                    "^(\d+\.?\d*) hrs? (\d+\.?\d*) m(?:(?:in(?:(?:ute)?s?)?)?)?$": "float(result.group(1))*3600 +float(result.group(2))*60"},
                #'7 hrs
                {"^(\d+\.?\d*) hrs?$": "float(result.group(1))*3600"}  #'7 hrs
            ]
        for p in patterns:
            key = p.keys()[0]
            result = re.search(key, value)
            if result:
                return eval(p[key])
        return None
    except:
        return None


def hours_minutes_to_seconds(value):
    # "1 2 3" | "2 3" (hour minute second or minute second)
    # todo add  more separator here
    v = value.split()
    sum = 0
    exp = len(v) - 1
    for idx, val in enumerate(v):
        sum += int(val) * (60 ** exp)
        exp -= 1
    return sum


def months_to_seconds(value):
    return value * 30 * (5 / 7) * 8 * 3600


def duration_filter(data):
    return sum_duration(data)


def sum_duration(data):
    if data:
        try:

            if isinstance(data, list):
                sum = 0
                for i in data:
                    sum += string_to_second(i)
                return int(sum)
            else:
                data = string_to_second(data)
                return int(data) if data is not None else None
        except:
            traceback.print_exc()
            return None
    else:
        return None


def convert_date_(value, fIn, fOut):
    """
    convert by datetime api
    """
    try:
        value = datetime.datetime.strptime(value, fIn)
        value = value.strftime(fOut)
        return value
    except:
        return None


"""
    convert a date string to a format defined
"""


def convert_date(input_value, **kwargs):
    try:
        # Step 1
        value = re.sub('[^A-Za-z0-9.]+', ' ', input_value).strip()
        patterns_callbacks = \
            {
                "(.*)ago$": "time_ago_to_seconds(result.group(1))"
            }
        for k, v in patterns_callbacks.iteritems():
            result = re.search(k, value, re.I)
            if result:
                return remove_date_time_null(eval(v))
        # Step 2
        value = re.sub('[^A-Za-z0-9]+', ' ', input_value).strip()
        # see https://docs.python.org/2/library/datetime.html
        #format {"patters":"example value"}
        # May 04 2015 8 30 am
        formats = {
            "%I %M%p %b %d %Y": "6 00pm Dec 2 2014",
            "%I %M %p %b %d %Y": "6 00 pm Dec 2 2014",
            "%d %B %Y %I %M%p": "22 October 2014 6 00pm",
            "%d %B %Y %I %M %p": "19 February 2015 4:00 PM",
            "%d %B %Y %H %M": "7 September 2015 9 00",
            "%d %B %Y %I %M": "22 October 2014 6 00",
            "%d %b %Y %H %M": "22 Oct 2014 6 00",
            "%b %d %Y at %I %M %p": "Oct 17 2014 at 1 45 PM",
            "%b %d %Y %I %M%p": "Oct 17 2014 1 45PM",
            "%b %d %Y %I %M %p": "Oct 17 2014 1 45 PM",
            "%B %d %Y %I %M %p": "September 30 2014 11 59 AM",
            "%Y %m %d %H %M %S": "2014 12 19 10 00 00",
            "%Y %b %d %H %M": "2015 Jan 28 5 30",
            "%m %d %Y %I %M %p": "2/10/2015 9:00 am",
            "%d %m %Y %H %M": "01 04 2015 16 00"

        }
        # custom patterns
        for i in formats:
            r = convert_date_(value, i, DATE_FORMAT)
            if r:
                return remove_date_time_null(r)
        # Step 3
        value = date_parser.parse(input_value, ignoretz=True)
        return remove_date_time_null(value.strftime(DATE_FORMAT))
    except:
        return None


def time_ago_to_seconds(time_string):
    value = clean_date_time_data(time_string)
    result = None
    patterns = \
        [
            # 2 years
            {"^(\d+\.?\d*) years?$": "float(result.group(1))*86400*365"},
            # 3 months
            {"^(\d+\.?\d*) months?$": "float(result.group(1))*86400*30"},
            # 1 weeks
            {"^(\d+\.?\d*) w(?:eeks?)?$": "float(result.group(1))*86400*7"},
            # 1 day
            {"^(\d+\.?\d*) d(?:ays?)?$": "float(result.group(1))*86400"},
        ]
    for p in patterns:
        key = p.keys()[0]
        result = re.search(key, value)
        if result:
            result = eval(p[key])
            break
    result = string_to_second(time_string) if result is None else result
    epoch_time_milliseconds = int(time.time()) - result
    return time.strftime(DATE_FORMAT, time.localtime(epoch_time_milliseconds))


def epoch_time_to_date(value):
    return time.strftime(DATE_FORMAT, time.localtime(value)) if value else None


def clean_date_time_data(value):
    value = re.sub('[^A-Za-z0-9.]+', ' ', value)
    # split character and number
    value = ' '.join(re.split('(\d+\.?\d*)', value)).lower().strip()
    #split by space
    value = re.sub('[^A-Za-z0-9.]+', ' ', value).strip()
    return value


# calculate the different between two dates
def minus_times_to_seconds(value):
    value = clean_date_time_data(value)
    ##9 am mt 12 pm mt
    # 9 00 am 9 45 am pdt
    try:
        # value  9 00 am 9 45 am pdt
        table = re.findall('(?:\d+)|(?:am)|(?:pm)', value)
        value1 = ' '.join(table[0:int(len(table) / 2)]).strip()
        value2 = ' '.join(table[int(len(table) / 2):len(table)]).strip()
        #1 pm | 1 00 pm
        formats = ["%I %M %p", "%I %p"]
        for format in formats:
            try:
                value1 = datetime.datetime.strptime(value1, format)
                value2 = datetime.datetime.strptime(value2, format)
                if value1:
                    break
            except:
                pass
        total_seconds = (value2 - value1).total_seconds()
        return abs(int(total_seconds))
    except:
        traceback.print_exc()
        return 0


def minus_dates_to_seconds(value):
    # sample value : nov 21 2014 nov 23 2014
    start_date = str_ptime(get_start_date(value))
    end_date = str_ptime(get_end_date(value))
    total_seconds = (end_date - start_date).total_seconds()
    days = total_seconds / (24 * 3600)
    # if days number >5 => multiple by 22/30
    days = (days * 22) / 30 if days > 5 else days
    duration_filter = days * 8 * 3600
    return abs(int(duration_filter))


def str_ptime(value):
    try:
        return datetime.datetime.strptime(value, DATE_FORMAT)
    except:
        return datetime.datetime.strptime(value, DATE_FORMAT_SHORT)


def rm_by_idx(value, index):
    tab = value.split()
    r = [v for i, v in enumerate(tab) if i not in index]
    return ' '.join(r).strip()


def get_start_date(value):
    value = normalize_unicode(value)
    value = ' '.join(normalize_space(value)).strip() if isinstance(value, list) else value
    value = ' '.join([i.strip() for i in (re.split('(\d+)', value))]).strip()
    value = re.sub(ALL_TIME_ZONE, '', value)
    value = re.sub('[^A-Za-z0-9]+', ' ', value)
    ## remove time zone
    patterns = \
        {
            #30 Nov 1 Dec 2015
            "(\d{1,2} \w+ \d{1,2} \w+ \d{4})": "convert_date(rm_by_idx(result.group(1),[2,3]))",
            # 19 26 March 2015
            # 12 12 Jun 2015
            "(\d{1,2} \d{1,2} \w+ \d{4})": "convert_date(rm_by_idx(result.group(1),[1]))",
            # May 28 2015 Jun 4 2015 6 PM 9 PM
            "^(\w+ \d{1,2} \d{4} \w+ \d{1,2} \d{4} \d{1,2}? (AM|PM)? \d{1,2}? (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[3,4,5,8,9]))",
            "(\w+ \d{1,2} \d{1,2} \d{4})": "convert_date(rm_by_idx(result.group(1),[2]))",
            "(\w+ \d{1,2} \w+ \d{1,2} \d{4})": "convert_date(rm_by_idx(result.group(1),[2,3]))",
            # 2014 11 25 9 00 am 4 30 pm
            "(\d{4} \d{1,2} \d{1,2} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[6,7,8]))",
            # November 8 2014 2 00 PM 5 00 PM
            "(\w+ \d{1,2} \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[6,7,8]))",
            # Nov 10 14 2014 8 30 AM 4 30 PM ET
            "(\w+ \d{1,2} \d{1,2} \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[2,7,8,9]))",
            # Dec 9 2014 Dec 12 2014 10 30 am 6 30 pm EST UTC 5
            "^(\w+ \d{1,2} \d{4} \w+ \d{1,2} \d{4} \d{1,2} \d{1,2} (am|pm) \d{1,2} \d{1,2} (am|pm))": "convert_date(rm_by_idx(result.group(1),[3,4,5,9,10,11]))",
            # Jan. 28, 5:30-7:30
            "^(\w+ \d{1,2} \d{1,2} \d{1,2} \d{1,2} \d{1,2})$": "convert_date_special(rm_by_idx(result.group(1),[4,5]))",
            # 14 15 May 2015 9 00 17 00
            "^(\d{1,2} \d{1,2} \w+ \d{4} \d{1,2} \d{1,2} \d{1,2} \d{1,2})$": "convert_date(rm_by_idx(result.group(1),[1,6,7]))",
            # 18 19 February 2015 8 00 AM 4 00 PM
            "^(\d{1,2} \d{1,2} \w+ \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[1,7,8,9]))",
            # 29 April 2015 8 00 AM  4 00 PM
            "^(\d{1,2} \w+ \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[6,7,8]))",
            # 29 January 12 February 2015
            "^(\d{1,2} \w+ \d{1,2} \w+ \d{4})$": "convert_date(rm_by_idx(result.group(1),[2,3]))",
            #Mar 23 27 2015 8 30 AM 4 30 PM ET
            "^(\w+ \d{1,2} \d{1,2} \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[2,7,8,9]))",
            # Mar 16 2015 9 AM 5 PM
            "^(\w+ \d{1,2} \d{4} \d{1,2} (AM|PM) \d{1,2} (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[5,6]))",

        }
    for k, v in patterns.iteritems():
        result = re.search(k, value, re.I)
        if result:
            return eval(v)


def get_end_date(value):
    # split character and number
    value = normalize_unicode(value)
    value = ' '.join(normalize_space(value)).strip() if isinstance(value, list) else value
    value = ' '.join([i.strip() for i in (re.split('(\d+)', value))]).strip()
    value = re.sub(ALL_TIME_ZONE, '', value)
    value = re.sub('[^A-Za-z0-9]+', ' ', value)
    patterns = \
        {
            #30 Nov 1 Dec 2015
            "(\d{1,2} \w+ \d{1,2} \w+ \d{4})": "convert_date(rm_by_idx(result.group(1),[0,1]))",
            # 12 12 Jun 2015
            "(\d{1,2} \d{1,2} \w+ \d{4})": "convert_date(rm_by_idx(result.group(1),[0]))",
            # May 28 2015 Jun 4 2015 6 PM 9 PM
            "^(\w+ \d{1,2} \d{4} \w+ \d{1,2} \d{4} \d{1,2}? (AM|PM)? \d{1,2}? (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[0,1,2,6,7]))",
            "(\w+ \d{1,2} \d{1,2} \d{4})": "convert_date(rm_by_idx(result.group(1),[1]))",
            "(\w+ \d{1,2} \w+ \d{1,2} \d{4})": "convert_date(rm_by_idx(result.group(1),[0,1]))",
            #2014 11 25 9 00 am 4 30 pmfind
            "(\d{4} \d{1,2} \d{1,2} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[3,4,5]))",
            #November 8 2014 2 00 PM 5 00 PM
            "(\w+ \d{1,2} \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[3,4,5]))",
            #Nov 10 14 2014 8 30 AM 4 30 PM ET
            "(\w+ \d{1,2} \d{1,2} \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[1,4,5,6]))",
            #Dec 9 2014 Dec 12 2014 10 30 am 6 30 pm EST UTC 5
            "^(\w+ \d{1,2} \d{4} \w+ \d{1,2} \d{4} \d{1,2} \d{1,2} (am|pm) \d{1,2} \d{1,2} (am|pm))": "convert_date(rm_by_idx(result.group(1),[0,1,2,6,7,8]))",
            #Jan. 28, 5:30-7:30
            "^(\w+ \d{1,2} \d{1,2} \d{1,2} \d{1,2} \d{1,2})$": "convert_date_special(rm_by_idx(result.group(1),[2,3]))",
            #14 15 May 2015 9 00 17 00
            "^(\d{1,2} \d{1,2} \w+ \d{4} \d{1,2} \d{1,2} \d{1,2} \d{1,2})$": "convert_date(rm_by_idx(result.group(1),[0,4,5]))",
            # 18 19 February 2015 8 00 AM 4 00 PM
            "^(\d{1,2} \d{1,2} \w+ \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[0,4,5,6]))",
            # 29 April 2015 8 00 AM  4 00 PM
            "^(\d{1,2} \w+ \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[4,5,6]))",
            # 29 January 12 February 2015
            "^(\d{1,2} \w+ \d{1,2} \w+ \d{4})$": "convert_date(rm_by_idx(result.group(1),[0,1]))",
            #Mar 23 27 2015 8 30 AM 4 30 PM ET
            "^(\w+ \d{1,2} \d{1,2} \d{4} \d{1,2} \d{1,2} (AM|PM) \d{1,2} \d{1,2} (AM|PM))": "convert_date(rm_by_idx(result.group(1),[1,4,5,6]))",
            # Mar 16 2015 9 AM 5 PM
            "^(\w+ \d{1,2} \d{4} \d{1,2} (AM|PM) \d{1,2} (AM|PM))$": "convert_date(rm_by_idx(result.group(1),[3,4]))"
        }
    for k, v in patterns.iteritems():
        result = re.search(k, value, re.I)
        if result:
            return eval(v)


def notnull(value):
    return value is not None and len(value) > 0


def remove_date_time_null(data):
    return data.replace(" 00:00:00", '') if data else data


def convert_date_special(input):
    """
    input : Sample : "1 Jan","1 Jan"
    """
    input = re.sub('[^A-Za-z0-9]+', ' ', input)
    input = ' '.join(input.split()).lower().strip()
    year = date.today().year
    patterns = \
        [
            {"^(\w+ \d{1,2})$": ' "%s %s"%(input,year) '},
            {"^(\d{1,2} \w+)$": ' "%s %s"%(input,year) '},
            {"^(\w+ \d{1,2} \d{1,2} \d{1,2})$": ' "%s %s" %(year,input) '},
        ]
    for p in patterns:
        key = p.keys()[0]
        result = re.search(key, input)
        if result:
            # p.values()[0]
            value = p[key]
            date_final = convert_date(eval(value))
            different = date_parser.parse(date_final) - datetime.datetime.now()
            if different.days <= -180:
                value.replace(str(year), str(year + 1))
                return convert_date(value.replace(str(year), str(year + 1)))
            else:
                return date_final
    return None


def is_expired(data):
    date_convert = convert_date(data)
    try:
        value = datetime.datetime.strptime(convert_date(date_convert), DATE_FORMAT)
    except:
        value = datetime.datetime.strptime(convert_date(date_convert), DATE_FORMAT_SHORT)
    return value.date() < datetime.datetime.today().date()


def time_display(sec):
    sec = timedelta(seconds=int(sec))
    d = datetime.datetime(1, 1, 1) + sec
    data = [
        {"%d days" % (d.day - 1): d.day - 1},
        {"%d hours" % (d.hour ): d.hour},
        {"%d min" % (d.minute): d.minute},
        {"%d sec" % (d.second): d.second}
    ]
    result = ""
    for item in data:
        if item.values()[0] != 0:
            result = result + ' ' + item.keys()[0]
    result = ' '.join(result.split()).strip()
    return result

