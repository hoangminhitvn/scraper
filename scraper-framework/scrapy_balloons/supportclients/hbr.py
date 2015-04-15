import json, urllib, re
import pdb

class hbr:
    list_reposne = []
    list_url=["https://hbr.org/service/search/more-results/1/10?format=json&N=4294967060"]
    name = ''
    @classmethod
    def extract_next_url_cat(cls, value):
        if '200' in value:
            try:
                option = re.search("number\" : (\d+)", value).group(1)
                if int(option) < 301:
                    next_page = str(int(option) + 1)
                    url = "https://hbr.org/service/search/more-results/%s/10?format=json&N=4294967060"%(next_page)
                    return url
                else:
                    pass
            except:
                pass