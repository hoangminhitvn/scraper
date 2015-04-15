from scrapy_balloons.utils.allfunctions import *


class TestRuleSpider(CrawlSpider):
    name = "rules"
    start_urls = ["http://www.ebay.co.uk/sch/Fancy-Dress-Period-Costume-/163147/i.html?LH_ItemCondition=1000%7C1500&LH_PrefLoc=1&_ipg=200&rt=nc"]
    cpt = 0
    rules = [
        Rule(lxml(allow=('.*',),restrict_xpaths=("//td[@class='pages']/a")), follow=True, callback='passCat'),
        Rule(lxml(allow=('.*',),restrict_xpaths=("//*[@id='GalleryViewInner']/li//div[@class='imgWr']/a")), callback='parse_product')
    ]
    cpt = 0

    def parse_product(self, response):
        self.cpt += 1
        print self.cpt
        print response.url
        # print self.cpt
        return None

    def passCat(self, response):
        print "passFollows------------------"
        self.cpt += 1
        print self.cpt
        print response.url
        return None
