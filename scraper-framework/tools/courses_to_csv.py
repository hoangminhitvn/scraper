import argparse
import csv
import json
import unicodedata
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from scrapy_balloons.utils.convertfunctions import *
import pdb

prod_columns = [u'provider_id', u'product_url', u'name', u'description', u'product_video_url', u'formats',
                u'instructors', u'duration_filter',
                u'location_addr', u'start_date_local', u'requirements',
                u'ProductRating', u'duration_display', u'location_city', u'price_currency',
                u'location_name', u'location_country', u'location_postal', u'short_desc', u'partner_prod_id',
                u'certificates', u'toc', u'product_type_id', u'end_date_local', u'location_state',
                u'price_display_float', u'difficulty', u'location_display',
                u'authors', u'tz', u'publisher', u'product_image_url', u'product_events', u'language',
                u'prerequisites', u'prod_keywords', u'audience', u'pub_status', u'published_date', u'raw_html',
                u'price_display_text', u'price_filter']

exclude_columns = [
    #'product_events',
    'raw_html',
    'short_desc',
    'toc'
]
cols = [str(value) for value in prod_columns if value not in exclude_columns]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputPath',  help='path to input json file. [Required]')
    parser.add_argument('-o', '--outputPath',  help='path to output csv file. [Optional]')

    input_path = parser.parse_args().inputPath
    output_path = parser.parse_args().outputPath

    if os.path.isfile(input_path):
        output_path = output_path if output_path else input_path + '.out.csv'
        json_to_csv(input_path, output_path)
        print "File saved to %s" % (output_path)
    elif os.path.isdir(input_path):
        output_path = output_path if output_path else  'csv'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for file_name in os.listdir(input_path):
            input_path_file  = os.path.join(input_path, file_name)
            output_path_file = os.path.join(output_path, file_name + '.out.csv')
            print input_path_file
            print output_path_file
            json_to_csv(input_path_file, output_path_file)


