import os,json
import argparse

def is_valid_json(json_path):
    try:
        with open(json_path) as json_file:
            json.load(json_file)
            json_file.close()
            return True
    except:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputPath', help='path to input json file or folder q. [Required]')
    input_path = parser.parse_args().inputPath
    if os.path.isfile(input_path):
        if is_valid_json(input_path) == True:
            print "file %s has the correct json format" % (input_path)
        else:
            print "file %s No JSON object could be decoded" % (input_path)
    elif os.path.isdir(input_path):
        for file_name in os.listdir(input_path):
            if is_valid_json(os.path.join(input_path, file_name)) == False:
                print "file %s : No JSON object could be decoded" % (file_name)



