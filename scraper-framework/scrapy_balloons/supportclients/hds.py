from scrapy_balloons.utils.datetimefunctions import *
import datetime
import dateutil.parser
import pdb


class hds:
    """
    Convert start date & end date to normal format
    """

    @classmethod
    def get_start_time(cls, response):
        try:
            value_1 = response.xpath("substring-before(./start_date,' ')").extract()
            value_2 = response.xpath("./time/text()").re("\\d+:\\d+")
            value_3 = response.xpath("./time/text()").re("\\d+\\.\\d+")
            if value_2:
                value_input = value_1[0] + ' ' + value_2[0]
                output_start_date = convert_date(value_input)

            elif value_3:
                value_input = value_1[0] + ' ' + value_3[0].replace('.',':')
                output_start_date = convert_date(value_input)

            else:
                value_input = value_1[0]
                output_start_date = convert_date(value_input)

            return output_start_date
        except:
            None

    @classmethod
    def get_end_time(cls, response):
        try:
            value_start_date = response.xpath("substring-before(./start_date,' ')").extract()
            value_duration = response.xpath("./duration/text()").re("\\d+")
            value_end_time_1 = response.xpath("./time/text()").re("\\d+:\\d+")
            value_end_time_2 = response.xpath("./time/text()").re("\\d+.\\d+")

            if value_end_time_1:
                if int(value_end_time_1[1].split(':')[0]) > 10:
                    int_duration = int(value_duration[0]) - 1
                    value_end_date = datetime.datetime.fromtimestamp(
                        int(dateutil.parser.parse(value_start_date[0]).strftime('%s')) + int_duration * 3600 * 24).strftime(
                        '%d %B %Y')
                    output_end_date = convert_date(value_end_date + ' ' + value_end_time_1[1])
                else:
                    value_end_time_2 = value_end_time_1[1] + ' pm'
                    int_duration = int(value_duration[0]) - 1
                    value_end_date = datetime.datetime.fromtimestamp(
                        int(dateutil.parser.parse(value_start_date[0]).strftime('%s')) + int_duration * 3600 * 24).strftime(
                        '%d %B %Y')
                    output_end_date = convert_date(value_end_date + ' ' + value_end_time_2)

            elif value_end_time_2:
                # pdb.set_trace()
                int_duration = int(value_duration[0]) - 1
                value_end_date = datetime.datetime.fromtimestamp(
                    int(dateutil.parser.parse(value_start_date[0]).strftime('%s')) + int_duration * 3600 * 24).strftime(
                    '%d %B %Y')
                output_end_date = convert_date(value_end_date + ' ' + value_end_time_2[1].replace('.',':'))

            else:
                int_duration = int(value_duration[0]) - 1
                value_end_date = datetime.datetime.fromtimestamp(
                    int(dateutil.parser.parse(value_start_date[0]).strftime('%s')) + int_duration * 3600 * 24).strftime(
                    '%d %B %Y')
                output_end_date = convert_date(value_end_date)

            return output_end_date
        except:
            None