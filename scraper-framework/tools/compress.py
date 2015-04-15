import argparse
import csv
import json
import unicodedata
import sys
from os import path
import os
import traceback
import time
import re
import gzip
def get_simple_name(value):
        """
        input  skillup_config.json
        or input skillup.json
        or input skillup_product_list_99922.json
        return skillup
        """
        result = re.search("(\w+)_config\.json", value)
        result = result if result else re.search("(\w+)\.json", value)
        result = result if result else re.search("(\w+)_product_list_\d+\.gz", value)
        if result:
            return result.group(1)
        else:
            return None


def compress(file_path, output):
        try:
            f_inside_out_path = None
            if '.gz' not in output:
                if not os.path.exists(output):
                    os.makedirs(output)
                simple_name = get_simple_name(file_path)
                compress_name = "%s_product_list_%s.gz" % (simple_name, int(time.time()))
                f_out_path = "%s/%s" % (output, compress_name)
            else:
                f_out_path = output
            f_original_path = f_out_path.replace('.gz','.json.gz')
            f_in = open(file_path, 'rb')
            f_out = gzip.open(f_original_path, 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            os.rename(f_original_path,f_out_path)
            print "Compress from %s to %s : Successfully" % (file_path, f_out_path)
        except:
            print "Compress from %s to %s : Failed " % (get_simple_name(file_path), compress_name)
            traceback.print_exc()
            return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputPath',  help='path to input json file. [Required]')
    parser.add_argument('-o', '--outputPath',  help='path to output csv file. [Optional]')

    input_path = parser.parse_args().inputPath
    output_path = parser.parse_args().outputPath

    if os.path.isdir(input_path):
        output_path = output_path if output_path else  'compress'
        for file_name in os.listdir(input_path):
            file_path = os.path.join(input_path,file_name)
            compress(file_path,output_path)




