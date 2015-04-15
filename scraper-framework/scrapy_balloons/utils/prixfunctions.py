# -*- coding: utf-8 -*-
from scrapy_balloons.utils.basefunctions import *
import locale


def get_price_float(value):
    value = str(normalize_space(str(value)))
    value = re.sub('[^0-9.,]+', '', value)
    if len(value):
        return float_to_string(value)
    else:
        return None


def get_price_currency(value):
    if value:
        #see http://www.xe.com/symbols.php
        #value = re.sub('[\w\d;,.\n<>?;!]','',value).strip()
        # convert from a local symbol currency to international code currency.
        # This way is just a tricky, only use when no have other data than symbol currency
        # see here http://www.xe.com/symbols.php
        #todo add more currency here or use regular
        locales = [
            {'GBP': u'£'},
            {'EUR': u'€'},
            {'USD': u'$'},
            {'BRL': u'R'}
        ]
        for item in locales:
            if item.values()[0] in value:
                return item.keys()[0]
    return None


def get_price_display_text(value):
    value = str(normalize_space(value))
    # check separator:
    dFound = re.search("year|month|12 months|3 months|9 months|two week|week", value, re.I)
    if dFound:
        return "Pricing is for a " + dFound.group(0) + " access"
    else:
        return None


def get_price_info(value):
    #value : $439.000000 USD | $439.000000 USD/a year
    value = str(normalize_space(value))
    patterns = \
        {
            ".*(\$)(\d+\.?\d*)(.*)|(\$)(\d+\.?\d*)(.*)": "{'price_display_float':float_to_string(r.group(2)),'price_currency':get_price_currency(r.group(1))}",
        }
    for k, v in patterns.iteritems():
        r = re.search(k, value)
        if r:
            return eval(v)
    price_display_text = get_price_display_text(value)
    if price_display_text:
        value = value.replace(price_display_text, '')
    price_display_float = get_price_float(value)
    if price_display_float:
        price_currency = get_price_currency(value)
        return {"price_display_float": price_display_float, "price_currency": price_currency}
    else:
        return None


"""
input : list of string or a string. string is a price text as $25
output: the min priceText
"""


def min_price(value):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    if isinstance(value, list):
        temp = []
        for item in value:
            r = re.search("(\d+[,.]?\d*)", item)
            if r:
                temp.append(locale.atof(r.group(1)))
        if temp:
            return min(temp)
        return None
    else:
        return value


