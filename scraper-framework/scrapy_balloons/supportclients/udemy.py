import json, re
from scrapy_balloons.utils.basefunctions import *
from scrapy_balloons.items import ProductRating


class udemy:
    # client_secret and client_id will be extracted from headers. These information used to make request to rating api
    # Attention : It should extract from headers from response of start url
    # the headers of other resonse will not contains these information
    client_secret = None
    client_id = None
    rating_api_url = "https://www.udemy.com/api-1.1"

    @classmethod
    def product_rating(self, response):
        if response:
            results = []
            response = response if isinstance(response, list) else [response]
            for response_ in response:
                print response_
                json_value = json.loads(response_.body)
                for rating in json_value['data']:
                    item = ProductRating()
                    item['pub_status'] = 'L'
                    item['rating_only'] = 'L'
                    item['overall_rating'] = get_attr(rating, 'rating')
                    item['review'] = "%s %s" % (get_attr(rating, 'title'), get_attr(rating, 'content'))
                    if contains(rating, 'user'):
                        user = rating['user']
                        item['user_id'] = None
                        try:
                            item['username'] = normalize_space(get_attr(user, 'title'))
                        except:
                            pass
                    results.append(item)
                print len(results)
            return results
        else:
            return []


    @classmethod
    def get_comment_review_resources(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        pageSize = 500
        if udemy.client_secret is None and udemy.client_id is None:
            # get info from the header of start_url
            start_url = balloon_spider.start_urls[0]
            headers = str(balloon_spider.resources_ext[start_url].headers)
            #header = str(response.headers)
            udemy.client_id = re.search('client_id=(\w+)', headers).group(1)
            udemy.client_secret = re.search('client_secret=(\w+)', headers).group(1)
            if udemy.client_id is None and udemy.client_secret is None:
                raise Exception("Client_id and client_secret are None, can't get data for Product Rating")
        full_link = None
        if 'reviews' not in response.url:
            link = response.xpath("//a[contains(.,'SEE MORE REVIEWS') and not(contains(./@stype,'none'))]/@data-href").extract()
            if link:
                href = link[0]
            else:
                # try to create api link
                product_id = response.xpath("//div[@id='curriculum']//table/@data-course-id").extract()[0]
                href = "/courses/%s/reviews" % (product_id)
            full_link = "%s%s?p=%s&pageSize=%s" % (udemy.rating_api_url, href, 1,pageSize) if href else None
        else:
            data = json.loads(response.body)['data']
            if len(data) > 0:
                current_page = int(re.search('p=(\d+)&pageSize', response.url).group(1))
                next_page = current_page + 1
                full_link=re.sub("p=(\d+)","p=%s"%(next_page),response.url)
        if full_link:
            return {'url': full_link,
                    'headers': {'X-Udemy-Client-Id': udemy.client_id, 'X-Udemy-Client-Secret': udemy.client_secret},
                    'next_request': 'udemy.get_comment_review_resources'}
        else:
            return None

    @classmethod
    def not_in_english(cls,response):
        result = False
        #check if contains keywords COURSE DESCRIPTION
        if response.xpath("//b[contains(./text(),'COURSE DESCRIPTION')]"):
            try:
                # if possible convert to ascii => english
                description = str(response.xpath("string(//h2[@class='ci-h'])").extract()[0])
                return False
            except:
                return True
        else:
            return True




