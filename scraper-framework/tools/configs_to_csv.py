import argparse
import csv
import json
import os
import os.path



cols = ['provider_id','file_name']

parser = argparse.ArgumentParser()
parser.add_argument('-if', '--inputFolder', default='none', help='path to input folder json file. [Required]')
parser.add_argument('-of', '--outputFile', default='none', help='path to output csv file. [Optional]')

input_folder = parser.parse_args().inputFolder
output_file = parser.parse_args().outputFile
output_file = output_file if output_file != 'none' else (input_folder + '.csv').replace('/','')
results = []


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


def parse_json(path_file):
    with open(path_file) as input_file:
        try:
            json_v = json.load(input_file)
            data = extract_data(json_v)
            data['file_name'] = os.path.basename(path_file)
            results.append(data)
        except:
            print "Error to read %s "%(path_file)


for file_name in os.listdir(input_folder):
    full_path =os.path.realpath(os.path.join(input_folder, file_name))
    print full_path
    parse_json(full_path)

with open(output_file,  'wb') as csvfile:
  csvwriter = csv.writer(csvfile,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL )
  csvwriter.writerow(cols)
  for item in results:
      print output_file
      csvwriter.writerow([item[cols[0]],item[cols[1]],item['file_name']])



