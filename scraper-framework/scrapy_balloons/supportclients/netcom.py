from scrapy_balloons.utils.prixfunctions import *
from scrapy_balloons.utils.datetimefunctions import *
import re
import copy
from scrapy import Selector


class netcom:
    @classmethod
    def product_events(self, result, field, selector, response, source):
        finalResult = []
        objectclone = result[0]
        sourcelevel1 = source["1"]
        hasViewMoreLink = sourcelevel1.xpath("//a[contains(./text(),'View More Schedules')]/@href")
        if hasViewMoreLink:
            obs1 = response.xpath("//a[contains(@title,'See what is included for this price')]/@onclick").extract()
            obs2 = response.xpath("//td/text()").re(re.compile("\d+:.*", re.S))
            obs2 = normalize_space(obs2)
            for index in range(len(obs1)):
                item = copy.deepcopy(objectclone)
                v1 = re.search(".*ShowHide\((.+?)\).*", normalize_unicode(obs1[index])).group(1).split('\',\'')
                v2 = normalize_space(obs2[index])
                item['tz'] = tz(v2)
                v2 = normalize_space(v2.replace(tz(v2), ""))
                #format "6:00pm Dec 2, 2014"

                startdate = v2 + " " + v1[1]
                matchStartDate = re.search("\w+:\w+ (\w+:\w+) .*", startdate)
                startdate = startdate.replace(matchStartDate.group(1), "") if matchStartDate else startdate
                item['start_date_local'] = convert_date(startdate)

                enddate = v2 + " " + v1[2]
                matchEndDate =  re.search("(\w+:\w+) \w+:\w+ .*", enddate)
                enddate = enddate.replace(matchEndDate.group(1), "") if matchEndDate else enddate
                item['end_date_local'] = convert_date(enddate)
                locationInfo = netcom.get_location_info(v1[3])
                item = append_dic(item, locationInfo)
                item['location_display'] = v1[3]

                price = get_price_info("$%s USD" % (v1[7].replace('\'', '')))
                #regular for location name location_name
                #value 1 : New York City, NY (or Attend Online)
                #value 2 : NJ - Ramapo College (or Attend Online)
                patterns = [".*-(.*)\(.*\)", "(.*),.*\(.*\)"]
                for i in patterns:
                    f = re.search(i, item['location_display'])
                    if f:
                        item['location_name'] = f.group(1).strip()
                        break
                #"6:00pm 10:00pm Dec 2, 2014"

                if price:
                    item = append_dic(item, price,False)
                finalResult.append(item)
        else:
            events = response.xpath("//tr[contains(.,'USD')]")
            objectclone = result[0]
            try:
                for event in events:
                    item = copy.deepcopy(objectclone)
                    price = normalize_space(event.xpath("./td[3]/text()").extract())
                    priceInfo = get_price_info(price)
                    item = append_dic(item, priceInfo,False)
                    locationInfo = netcom.get_location_info(event.xpath("./td[1]/nobr/text()").extract()[0])
                    item = append_dic(item, locationInfo)
                    finalResult.append(item)

            except:
                item = copy.deepcopy(objectclone)
                date_data = response.xpath("//div[contains(.,'Dates')]/following-sibling::div[1]/text()").extract()
                for data in date_data:
                    if convert_date(data):
                        date_data = convert_date(data)
                        break
                item['start_date_local'] = date_data
                price = normalize_space(Selector(response).re("\$\d*.*USD"))
                priceInfo = get_price_info(price)
                ##location
                jsparameter = source["1"].xpath("//a[contains(@title,'See prices')]/@onclick").extract()
                jsparameter = normalize_space(jsparameter)
                v1 = re.search(".*ShowHide\((.+?)\).*", normalize_unicode(jsparameter[0])).group(1).split('\',\'')
                item = append_dic(item, priceInfo,False)
                locationInfo = netcom.get_location_info(v1[5])
                item = append_dic(item, locationInfo)
                finalResult.append(item)
        return finalResult

    @classmethod
    def get_location_info(self, value):
        value = normalize_space(value)
        location_city = None
        location_state = None
        location_display = None
        try:
            if ',' in value:
                location_city = value.split(',')[0].strip()
                location_state = value.split(',')[1].strip()
                location_display = value
            elif '-' in value:
                location_state = value.split('-')[0].strip()
                location_display = value
        except:
            pass
        return {"location_city": location_city, "location_state": location_state, "location_display": location_display}














