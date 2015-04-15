from scrapy_balloons.utils.basefunctions import *
from scrapy_balloons.constant import *


def state(value):
    if value is not None:
        value = normalize_space(value) if isinstance(value, unicode) else value
        r = re.search(All_STATE, value, re.I)
        return r.group(0) if r else None
    else:
        return None


def city(value):
    if value is not None:
        value = normalize_space(value) if isinstance(value, unicode) else value
        r = re.search(ALL_CITY, value, re.I)
        return r.group(0) if r else None
    else:
        return None
