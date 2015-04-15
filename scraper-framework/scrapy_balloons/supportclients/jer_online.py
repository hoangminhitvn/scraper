from scrapy_balloons.selenium_api import SeleniumApi as slm
from scrapy_balloons.selenium_api import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class jer_online:



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
            slm_response = SeleniumResponse(kwargs.get('request'))
            slmStep = SlmStep(slm_config['click'])

            driver.get(url)
            time.sleep(slmStep.sleep)

            slm.find_element(xpath="//select[@id='ddlFOS']/option[@value='1']").click()
            time.sleep(slmStep.sleep)

            slm.find_element(xpath="//select[@id='ddlCategory']/option[@value='1']").click()
            time.sleep(slmStep.sleep)

            slm.find_element(id='btnSearch2').click()
            time.sleep(slmStep.sleep)

            WebDriverWait(driver, 120).until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='UpdateProgress1']")))

            time.sleep(slmStep.sleep)
            slm_response.add_html_res(url, driver.page_source.encode('utf-8'))
        except:
            pass
        return slm_response.get_html_res()
