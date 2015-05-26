# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class OshcallianzassistanceItem(Item):
    price = Field()
    no_of_adults = Field()
    dependant_children = Field()
    cover_period = Field()

