import traceback
from langdetect import detect
import unicodedata, re, locale
from  urlparse import urljoin
from scrapy.selector.unified import SelectorList
from scrapy import FormRequest
from scrapy import Request
from scrapy import log
import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


def make_request(data):
    try:
        if isinstance(data, list):
            requests = []
            for d in data:
                requests += make_request(d)
            return requests
        # data is a list of dict or a dict
        elif isinstance(data, dict):
            url = get_attr(data, 'url')
            callback = get_attr(data, 'callback')
            meta = get_attr(data, 'meta', dict())
            dont_filter = get_attr(data, 'dont_filter', True)
            if contains(data, 'formdata'):
                return [FormRequest(url=url, formdata=get_attr(data, 'formdata'), callback=callback, meta=meta,
                                    dont_filter=dont_filter)]
            else:
                return [Request(url=data['url'], callback=callback, meta=meta, dont_filter=dont_filter)]
        else:
            return None
    except:
        log.msg(traceback.format_exc(100), level=log.ERROR)
        log.msg("Exception make request", level=log.ERROR)
        return None


def append_dic(dicFrom, dicTo, override=True):
    for k, v in dicTo.iteritems():
        if not override and k in dicFrom:
            continue
        elif v is not None:
            dicFrom[k] = v
    return dicFrom


"""
clean \n \b a string or a list of string
"""


def normalize_space(value, encode_ascii=True):
    if isinstance(value, list):
        result = []
        for i in value:
            v = normalize_space(i, encode_ascii)
            if v:
                result.append(v)
        return result
    else:
        value = ' '.join(normalize_unicode(value, encode_ascii).split()).strip()
        return value if value and len(value) > 0 else None


def head(list):
    return list[0] if len(list) > 0 else None


def normalize_unicode(value, encode_ascii=True):
    if isinstance(value, unicode):
        if encode_ascii:
            return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        else:
            return unicodedata.normalize('NFKD', value)
    else:
        return value


def xpath(selector, xpathValue):
    if isinstance(xpathValue, dict):
        operator = xpathValue['operator']
        if operator == 'and':
            result = []
            for exp in xpathValue['value']:
                if selector.xpath(exp):
                    result = result + selector.xpath(exp)
            result = clean_selector_null(result)
            return result
        elif operator == 'or':
            return xpath_or(selector, xpathValue['value'])
    elif isinstance(xpathValue, list):
        return xpath_or(selector, xpathValue)
    else:
        return selector.xpath(xpathValue)
    return []


def clean_selector_null(selList):
    result = []
    for item in selList:
        if len(item.extract()) > 0:
            result.append(item)
    return SelectorList(result)


def xpath_or(selector, xpathList):
    for exp in xpathList:
        result = clean_selector_null(selector.xpath(exp))
        if result:
            return result


def extract_data(selector, field=None):
    result = None
    encode_ascii = get_attr(field, 'encode_ascii', True)
    if selector:
        if field:
            if contains(field, 're'):
                try:
                    # first  try to eval re value
                    result = selector.re(eval(field['re']))
                except:
                    result = selector.re(field['re'])
            else:
                result = selector.extract()
        else:
            result = selector.extract()
    if result:
        result = result[0] if len(result) == 1 else result
        return normalize_space(result, encode_ascii)
    else:
        return None


def float_to_string(value):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        value = str(value)
        return str('{0:.2f}'.format(locale.atof(value)))
    except:
        return None

def clean_html(raw_html):
    patterns = [re.compile("<head>.*?</head>", re.DOTALL), re.compile("<footer>.*?</footer>", re.DOTALL)]
    for i in patterns:
        raw_html = i.sub("", raw_html)
    return raw_html


def contains(item, keys):
    try:
        #attention item can be a string
        if not isinstance(item, str) and not isinstance(item, unicode):
            if isinstance(keys, list):
                for key in keys:
                    if key in item:
                        return item[key] is not None
                return False
            else:
                if keys in item:
                    return item[keys] is not None
                else:
                    return False
        else:
            return False
    except:
        return False


def get_attr(item, key, value=None):
    if item and contains(item, key):
        return item[key]
    else:
        return value


def equal_ignore_case(str1, str2):
    return str1.lower() == str2.lower()


def difficulty(value):
    if value:
        levels = ['Beginner', 'Intermediate', 'Expert']
        for l in levels:
            if l.lower() == value.strip().lower():
                return value
    return None


def url_join_list(prefix, urls):
    try:
        results = []
        urls = urls if isinstance(urls, list) else [urls]
        for l in urls:
            l = urljoin(prefix, l) if l else None
            if l:
                results.append(l)
        return results
    except:
        return []


def get_link_youtube(value):
    #//www.youtube.com/embed/DLElzmuhrnY
    #https://www.youtube.com/watch?v=DLElzmuhrnY
    id = re.search("embed/(.*)", value).group(1)
    return "https://www.youtube.com/watch?v=%s" % id
    return value.replace("//", )


def sub_string(value, length):
    if value:
        if length >= len(value):
            return value
        else:
            for i in range(length, len(value)):
                if value[i] == ' ':
                    return value[:i].strip()
        return value
    else:
        return None


def remove_none(value):
    #todo add more type here
    if isinstance(value, list):
        result = []
        for i in value:
            if not is_item_none(i):
                result.append(i)
        return result if result else None
    else:
        return value


def map_to_dict(item):
    if not isinstance(item, dict):
        try:
            return item.__dict__['_values']
        except:
            return item
    else:
        return item


def is_item_none(item):
    result = True
    if item:
        item = map_to_dict(item)
        if isinstance(item, dict):
            for k, v in item.iteritems():
                if v:
                    result = False
                    break
        else:
            return item is None
    return result


def detect_language(value):
    value_language = detect(value)
    #todo add more language mapping here
    patterns = \
        {
            "es": "spa",
            "en": "eng",
            "ru": "rus",
            "fr": "fra",
            "ja": "jpn",
            "zh": "zho"
        }
    for k, v in patterns.iteritems():
        result = re.search(k, value_language, re.IGNORECASE)
        if result:
            return v
    pass


def language(value):
    #todo add more language mapping here
    patterns = \
        {
            "English": "eng",
            "German": "ger",
            "Russian": "rus",
            "French": "fra",
            "Spanish": "spa",
            "Japanese": "jpn",
            "Chinese": "zho"
        }
    for k, v in patterns.iteritems():
        result = re.search(k, value, re.IGNORECASE)
        if result:
            return v


def object_to_json(obj, ignore=[]):
    result = {}
    data = obj.iteritems() if isinstance(obj, dict) else obj.__dict__.iteritems()
    for k, v in data:
        if k not in ignore:
            if isinstance(v, list):
                sub_result = []
                for item in v:
                    sub_result.append(object_to_json(item))
                result[k] = sub_result
            elif hasattr(v, '__dict__'):
                result[k] = v.__dict__
            else:
                result[k] = v
    return result


class SizedDict(dict):
    ''' Sized dictionary without timeout. '''

    def __init__(self, size=1000):
        dict.__init__(self)
        self._maxsize = size
        self._stack = []

    def __setitem__(self, name, value):
        if len(self._stack) >= self._maxsize:
            self.__delitem__(self._stack[0])
            del self._stack[0]
        self._stack.append(name)
        return dict.__setitem__(self, name, value)

    def get(self, name, default=None, do_set=False):
        try:
            return self.__getitem__(name)
        except KeyError:
            if default is not None:
                if do_set:
                    self.__setitem__(name, default)
                return default
            else:
                raise

def get_by_curl(url):
    print "Get %s" %(url)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    # For new  PycURL versions:
    #c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    body = buffer.getvalue()
    # Body is a string on Python 2 and a byte string on Python 3.
    # If we know the encoding, we can always decode the body and
    # end up with a Unicode string.
    return body
