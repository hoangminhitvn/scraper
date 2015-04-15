# -*- coding: utf-8 -*-

# Scrapy settings for scrapy_balloons project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#


BOT_NAME = 'scrapy_balloons'

SPIDER_MODULES = ['scrapy_balloons.spiders']
NEWSPIDER_MODULE = 'scrapy_balloons.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_balloons (+http://www.yourdomain.com)'
#COOKIES_DEBUG = True
ITEM_PIPELINES = {
    'scrapy_balloons.interceptors.PostInterceptor': 100,
    'scrapy_balloons.pipelines.ModifyProduct': 300,
    'scrapy_balloons.filters.PostFilters': 400,
    'scrapy_balloons.filters.StatsFilters': 500,

}


CONCURRENT_REQUESTS = 50
CONCURRENT_REQUESTS_PER_DOMAIN = 30
DOWNLOADER_MIDDLEWARES = {
    'scrapy_balloons.middlewares.EncodeUtf8Response': 100,
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware': 1000,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    #'scrapy_balloons.useragent.RandomUserAgentMiddleware' :400
}
EXTENSIONS = {
    'scrapy_balloons.extension.OverrideSettings': 500,
    'scrapy_balloons.extension.HandleOnClose': 2000,
}

S3_BUCKET = 'test-skilledup-products/test_upload'
S3_ACCESS_KEY = 'AKIAJ35FIFXQ5SLKT25A'
S3_SECRET_KEY = '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'
S3_ENDPOINT = 's3-us-west-1.amazonaws.com'


# DOWNLOAD_DELAY = 1

DOWNLOADER_CLIENTCONTEXTFACTORY = 'scrapy_balloons.contextfactory.CustomClientContextFactory'

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
