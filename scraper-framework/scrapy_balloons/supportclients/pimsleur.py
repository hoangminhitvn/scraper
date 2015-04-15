from scrapy import log
from scrapy_balloons.selenium_api import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pdb
import traceback


class pimsleur:
    @classmethod
    def click_and_get_response(cls, url, **kwargs):
        # Note the website need to run in USA to be able to have a good result
        """
        url -- type is str
        return list of SeleniumResponse
        """
        try:
            from scrapy_balloons.spiders.balloon import config
            from scrapy_balloons.selenium_api import slm_config, driver, balloon_spider
            slmStep = SlmStep(slm_config['click'])
            slm_response = SeleniumResponse(kwargs.get('request'))
            driver.get(url)
            wait = ui.WebDriverWait(driver, 3)
            slmStep = SlmStep(slm_config['click'])
            print "url %s add response 0 " % (url)
            slm_response.add_html_res(url, driver.page_source.encode('utf-8'))
            if driver.find_element_by_xpath(slmStep.xpath):
                for i in range(1, slmStep.repeat):
                    target = wait.until(lambda driver: driver.find_element_by_xpath(slmStep.xpath))
                    target.click()
                    time.sleep(slmStep.sleep)
                    print "url %s add response %s " % (url, i)
                    slm_response.add_html_res(url, driver.page_source.encode('utf-8'))
        except:
            print "Paging review end"
            pass
        return slm_response.get_html_res()