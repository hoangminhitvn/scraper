import re
from subprocess import call
import traceback
import json
def get_simple_name(value):
    result = re.search("(\w+)_config\.json", value)
    result = result if result else re.search("(\w+)\.json", value)
    result = result if result else re.search("(\w+)_product_list_\d+\.gz", value)
    if result:
        return result.group(1)
    else:
        return None

def get_simple_names(file_name):
    result = []
    with open(file_name, 'r') as file_from:
        for line in file_from:
            name = get_simple_name(line)
            if name:
                result.append(name)
    return result

def get_config(simple_name):
    try:
        file_name = "../config/%s_config.json"%(simple_name)
        with open(file_name,'r') as input_file:
            return json.load(input_file)
    except:
        print simple_name
        return None


def get_configs(file_path):
    names = get_simple_names(file_path)
    results = []
    for name in names:
        config = get_config(name)
        if config:
            config['config_file'] = '%s_config.json'%(name)
            results.append(config)
    return results



if __name__ == "__main__":
    providers = get_configs('test1.txt')
    for p in providers:
        fields = p['output_config']['fields']
        print fields['provider_id']


