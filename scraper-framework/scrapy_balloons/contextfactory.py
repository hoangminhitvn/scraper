from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory
from OpenSSL.SSL import *



class CustomClientContextFactory(ScrapyClientContextFactory):
    """
    read the ssl method from config file to override the scrapy default method
    Example from config file:

    "ssl":"SSLv23_METHOD",


    """
    def __init__(self):
        #Scrapy uses TLSv1 by default.
        #See https://github.com/scrapy/scrapy/blob/master/scrapy/core/downloader/contextfactory.py#L13
        # TLSv1
        # SSLv23_METHOD
        # SSLv2_METHOD
        # SSLv3_METHOD
        # need try catch here to be able to execute in scrapy shell
        try:
            from scrapy_balloons.spiders.balloon import config
            self.method = eval(config.ssl) if config.ssl else TLSv1_METHOD
        except:
            self.method = TLSv1_METHOD


    