class seobook:
    @classmethod
    def extract_links_cat(self,value):
        link_course = value.split('\'')[1]
        return link_course