import json
from scrapy_balloons.utils.datetimefunctions import *
from scrapy_balloons.utils.html_string import *
from scrapy_balloons.items import Instructor




class skillshare:
    @classmethod
    def video(self,response):
        SS = get_json_value(self,response)
        playerID = str(SS['pageData']['videoPlayerData']['units'][0]['sessions'][0]['playerID'])
        playerKey= SS['pageData']['videoPlayerData']['units'][0]['sessions'][0]['playerKey']
        videoId= SS['pageData']['videoPlayerData']['units'][0]['sessions'][0]['videoId'].replace('bc:','')
        videoLink = "http://c.brightcove.com/services/viewer/federated_f9?&flashID=videoExperience_BC_145&playerID="+playerID+"&playerKey="+playerKey+"&isVid=true&isUI=true&dynamicStreaming=true&htmlFallback=true&%40videoPlayer="+videoId
        return videoLink

    @classmethod
    def description(self,response):
        SS = get_json_value(self,response)
        description = SS['pageData']['sectionData']['description'].replace('<p>','').replace('</p>','')
        description = html_to_text(description)
        return description

    @classmethod
    def prod_keywords(self,response):
        SS = get_json_value(self,response)
        tags = SS['pageData']['sectionData']['tags']
        prod_keywords =[]
        for tag in tags:
            prod_keywords.append(tag['name'])
        return prod_keywords

    @classmethod
    def product_image_url(self,response):
        SS = get_json_value(self,response)
        product_image_url = SS['pageData']['syllabusData']['classImageUrl']
        return product_image_url

    @classmethod
    def published_date(self,response):
        SS = get_json_value(self,response)
        published_date = SS['pageData']['sectionData']['classLaunchDate']
        published_date = convert_date(published_date)
        return published_date

    @classmethod
    def get_response_instructors(self,response):
        SS = get_json_value(self,response)
        classSku = str(SS['parentClassData']['sku'])
        userId = str(SS['pageData']['headerData']['teacher']['uid'])

        url_response = "http://www.skillshare.com/users/renderProfilePopup?userId="+userId+"&classSku="+classSku
        print("================ skillshare url_response=====================================================")
        print(url_response)
        return url_response

    @classmethod
    def instructors(self,response):
        from scrapy.selector import Selector
        from scrapy.http import HtmlResponse
        if response:
            results = []
            json_value = json.loads(response.body)
            body = json_value['content']
            print ("==================skillshare instructor pass=====================")
            selector = Selector(text=body).xpath('//div[@class=\'teacher-overview\']')
            item = Instructor()
            item['name'] = ' '.join(normalize_space(selector.xpath('./h3/text()').extract()))
            item['image'] = Selector(text=body).xpath('//div[@class=\'left\']/div[contains(@class,\'user-img\')]/img/@src').extract()[0]
            item['bio'] = ' '.join(normalize_space(selector.xpath('.//p/text()').extract()))

            results.append(item)

            return results
        else:
            print ("==================skillshare instructor response None=====================")
            # pdb.set_trace()
            return None


def get_json_value(self,response):
    raw_data = response.xpath("//script[contains(.,'var SS =')]").extract()[0]
    raw_data = normalize_space(raw_data)
    #json_value=re.search("var SS = ({.*})(?:;)",raw_data,re.S).group(1)
    json_value= re.search("serverBootstrap:(.*), mixpanel",raw_data,re.S).group(1)
    SS = json.loads(json_value)
    return SS
