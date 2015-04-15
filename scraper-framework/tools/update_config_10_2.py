import argparse
import csv
import json
import os
import os.path
import pdb
import traceback
import re
from collections import OrderedDict

"""
This file allow to modify each config file from a config folder, and write to new folder
"""

cols = ['provider_id', 'file_name']

parser = argparse.ArgumentParser()
parser.add_argument('-if', '--inputFolder', default='none', help='path to input folder json file. [Required]')
parser.add_argument('-of', '--outputFolder', default='none', help='path to output csv file. [Optional]')

input_folder = parser.parse_args().inputFolder
output_folder = parser.parse_args().outputFolder
results = []

all_key_found = ['base_url', 'start_url', 'levels', 'output_config', 'fields', 'provider_id', 'product_type_id',
                 'language', 'description',
                 'name', 'toc', 'product_events', 'type', 'extractor_rules', 'product_video_url', 'formats',
                 'product_image_url', 'xpath',
                 'price_currency', 'duration_filter', 'price_display_float', 'difficulty', 'duration_display',
                 'requirements', 'certificates',
                 'ProductRating', 'published_date', 'instructors', 'audience', 'authors', 'prerequisites',
                 'prod_keywords',
                 'selenium_config', 'pre_filters', 'publisher',  'partner_prod_id',
                 'end_date_local',
                 'start_date_local', 'price_display_text', 'pub_status', 'post_interceptors', 'pre_run', 'prod_image',
                 'python',
                 'location_city', 'location_name', 'location_display', 'location_state', 'tz', 'post_filters',
                 'product_url',
                 'product_type_name', 'provider_name', 'time_lock', 'space_lock', 'price_filter']
all_keys1 = ['base_url', 'start_url', 'levels',  'selenium_config', 'output_config',
             'pre_run','filters_not','settings']
all_keys2 = ['fields', 'type', 'pre_filters', 'xpath', 'python', 'extractor_rules', 'post_filters', 'post_interceptors']

all_keys3 = ['provider_id', 'product_type_id', 'time_lock', 'space_lock',
             'language', 'description', 'name', 'toc', 'product_events',
             'product_video_url', 'formats', 'product_image_url', 'price_currency', 'duration_filter', 'price_filter',
             'price_display_float',
             'difficulty', 'duration_display', 'requirements', 'certificates', 'ProductRating',
             'published_date', 'instructors', 'audience', 'authors', 'prerequisites', 'prod_keywords', 'publisher',
             'partner_prod_id', 'end_date_local', 'start_date_local', 'price_display_text', 'pub_status',
             'prod_image', 'location_city', 'location_name', 'location_display', 'location_state', 'location_addr',
             'location_country',
             'location_postal', 'tz', 'product_url']


def add_key(result, key):
    if key not in result:
        result.append(key)


def extract_value_by_key(json_v, key):
    if key in json_v:
        return json_v[key]
    else:
        children = [child for child in json_v.values() if isinstance(child, dict)]
        for child in children:
            r = extract_value_by_key(child, key)
            if r:
                return r
    return None


def extract_data(json_v):
    data = {}
    for col in cols:
        data[col] = extract_value_by_key(json_v, col)
    return data


def check_has_key(list1, list2):
    for key in list1:
        if not key in list2:
            if key not in ['short_desc']:
                print "Important Error : must resolve here ---------------------------- Not found key %s" % (key)


def order_json(all_key, json_value):
    output = OrderedDict()
    for k in all_key:
        if k in json_value:
            add_key(all_key_found, k)
            if k == 'output_config':
                output[k] = order_json(all_keys2, json_value[k])
            elif k == 'fields':
                output[k] = order_json(all_keys3, json_value[k])
            else:
                output[k] = json_value[k]
    check_has_key(json_value.keys(), all_key)
    return output


def create_file(path_file, json_value):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_name = re.search("config/(.*)", path_file).group(1)
    file_name = os.path.join(output_folder, file_name)
    json_value = order_json(all_keys1, json_value)
    output_file = open(file_name, 'wb')
    output_file.write(json.dumps(json_value, indent=2))
    #output_file.write(json.dumps(json_value, indent=4))
    output_file.close()


def add_keys(keys, json_value):
    for key in json_value:
        if key not in keys:
            keys.append(str(key))


def remove_fields(obj_dict, fields_name):
    for field_name in fields_name:
        if field_name in obj_dict:
            del obj_dict[field_name]


def parse_json(path_file):
    with open(path_file) as input_file:
        try:
            json_v = json.load(input_file)
            fields = json_v['output_config']['fields']
            fields_to_remove_1 = ['provider_name', 'product_type_name']
            if not isinstance(fields, dict):
                pdb.set_trace()
            remove_fields(fields, fields_to_remove_1)
            create_file(path_file, json_v)
        except:
            traceback.print_exc()
            print "Error to read %s " % (path_file)


for file_name in os.listdir(input_folder):
    full_path = os.path.realpath(os.path.join(input_folder, file_name))
    parse_json(full_path)






