from scrapy_balloons.utils.html_string import html_to_text


class vrayart:
    @classmethod
    def description(cls, response):
        data = response.xpath("//div[@itemprop='description']/div//text()").re("\\w.*")

        desc = []
        for i in data:
            desc.append(i.lower().capitalize())

        if 'What this Training Include?' in response.body:
            result = html_to_text(desc).split('What this Training Include?')[0]
        elif 'How it Works' in response.body:
            result = html_to_text(desc).split('How it Works')[0]
        elif 'Just like in this Example:' in response.body:
            result = html_to_text(desc).split('Just like in this Example:')[0]
        elif 'your personal practice.' in response.body:
            result = html_to_text(desc).split('This training consist from:')[0]
        elif 'The Most effective Photoshop' in response.body:
            result = html_to_text(desc).split('The Most effective Photoshop')[0]
        else:
            result = html_to_text(desc).split('Comments')[0]

        return result


    @classmethod
    def not_in_english(cls,response):
        detect_key = response.xpath("//div[@class='course_title']/h1//text()").extract()
        try:
            # import pdb
            # pdb.set_trace()
            title = str(detect_key[0])
            return False
        except:
            return True