import argparse
import traceback
import csv
import json
import unicodedata
import os
import re
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
                u'price_display_text', u'price_filter',u'space_lock',u'time_lock']

exclude_columns = [
    'raw_html',
    'short_desc',
    'toc'
]
cols = [str(value) for value in prod_columns if value not in exclude_columns]

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

def json_to_csv(input_file,output):
    try:
        output_path = None
        if '.csv'  in output:
            output_path = output
        else:
            simple_name = get_simple_name(input_file)
            output_file="%s.csv"%(simple_name)
            if not os.path.exists(output):
                os.makedirs(output)
            output_path = os.path.join(output,output_file)
        with open(output_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(cols)
            cpt = 0
            with open(input_file) as f:
                all_courses = json.load(f)
                for product in all_courses:
                    cpt +=1
                    #print "Convert course %s"%(cpt)
                    product_fields = []
                    for col in cols:
                        if col in product.keys():
                            if product[col]:
                                col_str = unicodedata.normalize('NFKD', product[col]).encode('ascii', 'ignore') if isinstance(product[col],unicode) else str(product[col])
                                product_fields.append(col_str.replace(',', '.').replace('|', '-'))
                            else:
                                product_fields.append("None")
                    csvwriter.writerow(product_fields)
                f.close()
            csvfile.close()
    except:
        print "convert file %s failed "%(input_file)
        traceback.print_exc()
        pass

      

