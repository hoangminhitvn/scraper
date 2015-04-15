import json, urllib
import pdb
import re

class hubspot:
    list_reposne = []
    list_url=["https://api.hubapi.com/library/v1/assets/page?options=%7B%22pageSize%22%3A8%7D"]
    name = ''
    @classmethod
    def extract_next_url_cat(cls, value):
        if 'true' in value:
            option = re.search("(\"lastDate.*)}",value).group(1)
            url = "https://api.hubapi.com/library/v1/assets/page?options={%s}"%(option)
            if url not in hubspot.list_url:
                hubspot.list_url.append(url)
            return url

        #value : containsMore":true,"lastDate":1421211600000,"lastTitle":"Demand Generation Benchmarks Report"}
        #https://js.hubspot.com/library/v1/assets/page

    @classmethod
    def hubspot_img(cls, value):
        all_url = hubspot.list_url
        check_value = str(value)
        if check_value:
            for start_url in all_url:
                # pdb.set_trace()
                response_img = urllib.urlopen(start_url)
                data_img = json.loads(response_img.read())
                for data in data_img['assets']:
                    if check_value == data['url']:
                        product_image_url = data['imageUrl']
                        hubspot.name = data['title']
                        print "product_image_url: ", product_image_url
                        print "name: ", hubspot.name
                        return product_image_url
        else:
            return None

    @classmethod
    def hubspot_title(cls, value):
        check_value = str(value)
        if check_value:
            return hubspot.name
        else:
            return None
