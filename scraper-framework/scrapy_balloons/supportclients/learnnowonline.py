from scrapy import log
from scrapy_balloons.selenium_api import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class learnnowonline:
    is_click = False
    @classmethod
    def click_multi_and_follow(self, response):
        def build_xpath_cat(indice):
            return "//a[@href='#%s']" % (indice)
        def build_xpath_next(indice):
            return "//div[@id='%s']//a[not(contains(@class,'k-state-disabled')) and contains(./span,'arrow-e')]" % (indice)
        try:
            from scrapy_balloons.spiders.balloon import config
            from scrapy_balloons.selenium_api import slm_config, driver, balloon_spider
            slmStep = SlmStep(slm_config['click_multi'])
            slm_response = SeleniumResponse()
            if self.is_click is False:
                driver.get(response.url)
                indices = ["SearchTabs-1", "SearchTabs-2", "SearchTabs-3"]
                # add response when starting
                slm_response.add_html_res(response.url, driver.page_source.encode('utf-8'))
                for i, indice in enumerate(indices):
                    try:
                        if i>0:
                            # try to find and click
                            for j in range(0, 10):
                                try :
                                    time.sleep(slmStep.sleep)
                                    linkCat = driver.find_element_by_xpath(build_xpath_cat(indice))
                                    if linkCat is None:
                                        print "Retry to find the linkcat xpath %s %s times "%(build_xpath_cat(indice), j)
                                    else:
                                        linkCat.click()
                                        time.sleep(slmStep.sleep)
                                        break
                                except:
                                    traceback.print_exc()
                                    pass
                            # add response when starting new category
                            slm_response.add_html_res(response.url, driver.page_source.encode('utf-8'))
                        for i in range(0,5):
                            elm = WebDriverWait(driver, slmStep.sleep).until(
                                EC.presence_of_element_located((By.XPATH, build_xpath_next(indice)))
                            )
                            elm.click()
                            print "Click on the next link"
                            WebDriverWait(driver, slmStep.timeout).until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='k-loading-mask']")))
                            #add response when the click is successfully
                            slm_response.add_html_res(response.url, driver.page_source.encode('utf-8'))

                    except:
                        log.msg("learnnowonline.click_multi_and_follow has no more link to click ")
                        pass
                self.is_click = True
                return RequestService.requests_to_follow(slm_response.get_html_res())
            else:
                return None
        except:
            traceback.print_exc()
            pass




