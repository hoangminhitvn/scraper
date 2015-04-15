from scrapy_balloons.spiders.balloon import *

class ModifyProduct(object):
    """
    Here is all custom rules that modify the item object by product json V#
    """
    def process_item(self, item, spider):
        self.execute_custom_rules(item, spider)
        for i in item.fields:
            if item.get(i, None) is None:
                item[i] = None
            else:
                # if i == 'product_events':
                #     self.set_null_if_not_existed(item['product_events'], ProductEvent().fields)
                #     product_events = item['product_events'] if isinstance(item['product_events'], list) else [
                #         item['product_events']]
                #     #for pe in product_events:
                #     #if contains(pe,'instructors'):
                #     #    self.set_null_if_not_existed(pe['instructors'], Instructor().fields)
                if i == 'contact_details':
                    self.set_null_if_not_existed(item['contact_details'], contact_details().fields)
                # if i == 'publishers':
                #     self.set_null_if_not_existedit(item['publishers'], Publisher().fields)
                # if i == 'certificates':
                #     self.set_null_if_not_existed(item['certificates'], Certificate().fields)
                # if i == 'authors':
                #     self.set_null_if_not_existed(item['authors'], Author().fields)
                # if i == 'ProductRating':
                #     self.set_null_if_not_existed(item['ProductRating'], ProductRating().fields)

        return item

    def set_null_if_not_existed(self, data, fields):
        try:
            data = remove_none(data)
            items = data if isinstance(data, list) else [data]
            for item in items:
                for f in fields:
                    if f not in item:
                        item[f] = None
                    elif f in ['link', 'image', 'product_image_url', 'product_video_url'] and item[f]:
                        item[f] = urljoin('http://', item[f]).replace('///', '//')
        except:
            pass


    def execute_custom_rules(self, item, spider):
        if spider.pre_run_service and spider.pre_run_service.price_info:
            append_dic(item, spider.pre_run_service.price_info, False)
        if contains(item, 'product_image_url'):
            item['product_image_url'] = urljoin(BalloonCrawl.base_url, item['product_image_url'])
        # self.set_short_desc(item)
        # self.set_format(item)
        # self.upperKeywords(item)
        # # self.set_pub_status(item)
        # self.set_duration_display(item)
        # #must at the last
        # self.set_product_event(item)
        # self.set_difficulty(item)
        # self.set_price_filter(item)

    # def set_price_filter(self, item):
    #     if get_attr(item, 'price_currency') and get_attr(item, 'price_currency').lower() == 'usd':
    #         if contains(item, 'price_display_float'):
    #             item['price_filter'] = item['price_display_float']
    #     if 'product_events' in item and item['product_events']:
    #         for event in item['product_events']:
    #             if contains(event, 'price_currency') and get_attr(event, 'price_currency').lower() == 'usd' :
    #                 event['price_filter'] = get_attr(event,'price_display_float')
    #
    # def set_difficulty(self, item):
    #     item['difficulty'] = difficulty(get_attr(item, 'difficulty'))
    #
    # # def set_pub_status(self, item):
    # #     item['pub_status'] = 'L'
    #
    # def set_short_desc(self, item):
    #     short = get_attr(item, 'short_desc')
    #     if short is None:
    #         try:
    #             item['short_desc'] = sub_string(item['description'], 500)
    #         except:
    #             pass
    #
    #
    # def set_duration_display(self, product):
    #     try:
    #         events = product['product_events']
    #         for e in events:
    #             if contains(e, 'duration_filter'):
    #                 if "duration_display" not in e:
    #                     e['duration_display'] = duration_display(int(e['duration_filter']))
    #         product['product_events'] = events
    #     except:
    #         pass
    #
    #     try:
    #         if contains(product, "duration_filter"):
    #             duration_filter = int(product["duration_filter"])
    #             if "duration_display" not in product:
    #                 product['duration_display'] = duration_display(duration_filter)
    #     except:
    #         pass
    #
    # def set_format(self, item):
    #     try:
    #         haveFormat = False
    #         if contains(item, 'formats'):
    #             if isinstance(item['formats'], list):
    #                 if len(item['formats']) == 0:
    #                     haveFormat = True
    #             else:
    #                 if len(item['formats'].strip()) == 0:
    #                     haveFormat = True
    #         else:
    #             haveFormat = True
    #         if haveFormat:
    #             if len(item['product_video_url']) > 0:
    #                 item['formats'] = ['video']
    #     except:
    #         pass
    #
    #
    # def upperKeywords(self, item):
    #     try:
    #         item['prod_keywords'] = [x.capitalize() for x in item['prod_keywords']]
    #     except:
    #         pass
    #
    #
    # def set_product_event(self, item):
    #     found = None
    #     try:
    #         found = item['product_events'][0]
    #         for i in item['product_events']:
    #             found = i if float(i['price_display_float']) < float(found['price_display_float']) else found
    #         item = append_dic(item, found)
    #     except:
    #         if found:
    #             item = append_dic(item, found)
    #         pass
    #
    # def set_price_info(self, item, price):
    #     if self.price_info:
    #         append_dic(item, self.price_info, False)

