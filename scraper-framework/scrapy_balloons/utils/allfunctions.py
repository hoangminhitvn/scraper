import json, re, traceback, time
from langdetect import detect
from scrapy import log
from scrapy import FormRequest, Request, Selector
from scrapy.utils.python import unique
from urlparse import urljoin
import os
import tempfile
import urllib2
import signal
import HTMLParser
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor as lxml
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.html import TextResponse
from scrapy.shell import inspect_response
from scrapy.selector.unified import SelectorList
from scrapy.utils.response import open_in_browser
from scrapy_balloons.items import *
from scrapy_balloons.constant import *
from scrapy_balloons.stats import StatsCollector
from scrapy_balloons.utils.locationfunctions import *
from scrapy_balloons.utils.html_string import *
from scrapy_balloons.utils.prixfunctions import *
from scrapy_balloons.utils.datetimefunctions import *
from scrapy_balloons.utils.locationfunctions import *
from scrapy_balloons.linksextractors import RegexLinkExtractor as lrgl
# from scrapy_balloons.supportclients.netcom import *
# from scrapy_balloons.supportclients.howdesignuniversity import *
# from scrapy_balloons.supportclients.classondemand import *
# # from scrapy_balloons.supportclients.udemy import *
# from scrapy_balloons.supportclients.hubspot import *
# from scrapy_balloons.supportclients.coursehorse import *
# # from scrapy_balloons.supportclients.skillshare import *
# from scrapy_balloons.supportclients.learnnowonline import *
# from scrapy_balloons.supportclients.cfpa import *
# from scrapy_balloons.supportclients.ed2go import *
# from scrapy_balloons.supportclients.evisors import *
# from scrapy_balloons.supportclients.elanceuniversity import *
# from scrapy_balloons.supportclients.simplilearn import *
# from scrapy_balloons.supportclients.filtered import *
# from scrapy_balloons.supportclients.ledet import *
# from scrapy_balloons.supportclients.learnable import *
# from scrapy_balloons.supportclients.checkpointlearning import *
# from scrapy_balloons.supportclients.junipernetworks import *
# from scrapy_balloons.supportclients.informanagement import *
# from scrapy_balloons.supportclients.writersonlineworkshops import *
# from scrapy_balloons.supportclients.pluralsight import *
# from scrapy_balloons.supportclients.lynda import *
# from scrapy_balloons.supportclients.thegreatcourses import *
# from scrapy_balloons.supportclients.edx import *
# from scrapy_balloons.supportclients.writersonlineworkshops import *
# from scrapy_balloons.supportclients.thegreatcourses import *
# from scrapy_balloons.supportclients.codeschool import *
# from scrapy_balloons.supportclients.alison import *
# from scrapy_balloons.supportclients.redhattraining import *
from scrapy_balloons.selenium_api import SeleniumApi as slm
# from scrapy_balloons.supportclients.pimsleur import *
from scrapy_balloons.utils.convertfunctions import *
# from scrapy_balloons.supportclients.google_university import *
# from scrapy_balloons.supportclients.jer_online import *
# from scrapy_balloons.supportclients.coursera import *
# from scrapy_balloons.supportclients.cmivfx import *
# from scrapy_balloons.supportclients.magoosh import *
# from scrapy_balloons.supportclients.zeitgeistminds import *
# from scrapy_balloons.supportclients.cadmasters import *
# from scrapy_balloons.supportclients.salesforce import *
# from scrapy_balloons.supportclients.knowledgecity import *
# from scrapy_balloons.supportclients.udacity import *
# from scrapy_balloons.supportclients.lingq import *
# from scrapy_balloons.supportclients.f5 import *
# from scrapy_balloons.supportclients.marketfy import *
# from scrapy_balloons.supportclients.bignerdranch import *
# from scrapy_balloons.supportclients.speaklanguages import *
# from scrapy_balloons.supportclients.careeracademy import *
# from scrapy_balloons.supportclients.aws import *
# from scrapy_balloons.supportclients.compuworks import *
# from scrapy_balloons.supportclients.seobook import *
# from scrapy_balloons.supportclients.packtpub import *
# from scrapy_balloons.supportclients.edureka import *
# from scrapy_balloons.supportclients.goskills import *
# from scrapy_balloons.supportclients.greycampus import *
# from scrapy_balloons.supportclients.ingram_micro import *
# from scrapy_balloons.supportclients.hbr import *
# from scrapy_balloons.supportclients.vrayschool import *
# from scrapy_balloons.supportclients.vrayart import *
from scrapy_balloons.supportclients.ebay import *

def mapping(value, mappings):
    for k in mappings:
        if contains_ignore_case(value, mappings[k]):
            return k
    return None\


def contains_ignore_case(v, l):
    return v.lower() in [k.lower() for k in l]


def is_existed_in_mapping(value, mappings):
    for k in mappings:
        if contains_ignore_case(value, mappings[k]):
            return True
    return False


def next_fields(fields, level):
    items = {}
    for (k, v) in fields.iteritems():
        if contains(v, 'level'):
            if v['level'] != level:
                fieldsToFields = {}
                if v['level'] in items:
                    fieldsToFields = items[v['level']]
                fieldsToFields[k] = v
                items[v['level']] = fieldsToFields
    return items


def append_to_list(l, data, unique=True):
    l.extend(data) if isinstance(data, list) else l.append(data)
    l = list(set(l)) if unique else l
    return l


"""
return list[selector]
"""


def get_selector(html, field):
    """
    html : Selector or HtmlResponse
    execute the xpath config if existed in field
    """
    try:
        selector = html
        if not ( isinstance(html, Selector) or isinstance(html, SelectorList)):
            selector = Selector(html)
        if contains(field, 'css'):
            selector = selector.css(field['css'])
        if contains(field, 'xpath'):
            #xpath can be a multiple
            selector = xpath(selector, field['xpath'])
        return selector
    except:
        return None


def get_process_type(data):
    if contains(data, 'type'):
        if type(eval(data['type'])) is list:
            return 'list'
        else:
            return 'object'
    elif contains(data, ['xpath', 'css', 're', 'python', 'selenium_function']):
        return 'abstract'
    elif isinstance(data, str):
        return "str"
    elif isinstance(data, unicode):
        return 'unicode'
    elif isinstance(data, int):
        return "int"
    else:
        return None



"""
    # convert to product_type defined by balloon
    # input : product_type

"""
def product_type_id(product_type):
    product_type_analysed = mapping(product_type, PROD_TYPE_MAPPING)
    if product_type_analysed:
        result = PROD_TYPE_NAME_ID[product_type_analysed] if product_type_analysed in PROD_TYPE_NAME_ID.keys() else None
        return result
    return None

def difficulty(value):
    if value:
        value = mapping(value,PROD_DIFFICULTY)
        if value:
            return value
        else:
            log.msg("The product difficulty don't match with the following values : Beginner, Intermediate, Advanced",log.WARNING)
    return None






def view(data):
    if isinstance(data, HtmlResponse) or isinstance(data, TextResponse):
        open_in_browser(data)
    elif isinstance(data, Selector):
        open_in_browser(TextResponse(url="",encoding='utf-8', body=data.extract(), request=None))
    elif isinstance(data, SelectorList):
        content = ""
        for i in data:
            content += "%s <br>" % (i.extract())
        open_in_browser(TextResponse(url="",encoding='utf-8', body=content, request=None))
    else:
        open_in_browser(TextResponse(url="",encoding='utf-8', body=str(data), request=None))












