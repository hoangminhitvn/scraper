from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.link import Link
from scrapy.utils.python import unique
from urlparse import urlparse, urljoin


"""
Custom Link extractor that allow extract link from text, javascript, html
"""

class RegexLinkExtractor(LxmlLinkExtractor):

    def extract_links(self, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        url_info = urlparse(response.url)
        base_url = balloon_spider.base_url
        if base_url and len(base_url.strip()) == 0:
            base_url = "%s://%s" % (url_info.scheme, url_info.netloc)
        all_links = []
        if self.allow_res:
            for allow_re in self.allow_res:
                all_links = all_links + allow_re.findall(response.body)
        ## run process value see #LxmlParserLinkExtractor
        all_links = [self.link_extractor.process_attr(url) for url in all_links if self.link_extractor.process_attr(url) is not None]
        all_links = [Link(urljoin(base_url, url), "") for url in all_links]
        return unique(all_links)



