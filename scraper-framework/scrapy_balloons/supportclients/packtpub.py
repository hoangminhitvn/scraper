import pdb
import re
class packtpub:
    @classmethod
    def extract_links_cat(self,value):
        offset = re.search('\\d+',value).group(0)
        link_create = "/web-development?search=&offset=%s" % offset
        link_full = re.sub('/\\d+',link_create, value)
        return link_full