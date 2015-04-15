import re
class lynda:
    @classmethod
    def extract_links_cat(self,value):
        return re.sub('ajax=\d+|&','',value)