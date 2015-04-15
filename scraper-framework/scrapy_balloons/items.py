from scrapy import Item, Field


class contact_details(Item):
    name = Field()
    address = Field()
    phone_number = Field()
    vat_number = Field()
    email = Field()


class RawHtml(Item):
    link = Field()
    fields = Field()
    source = Field()

class Instructor(Item):
    name = Field()
    bio = Field()
    image = Field()
    link = Field()

class Product(Item):
    product_url = Field()
    short_desc = Field()
    initial_image_url = Field()
    price = Field()
    postage_costs = Field()
    qty_sold = Field()
    image_urls = Field()
    seller_details = Field()
    contact_details = Field()
    instructors = Field()





