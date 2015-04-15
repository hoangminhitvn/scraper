import time, traceback
from selenium import webdriver
import selenium.webdriver.support.ui as ui

from scrapy import Request
from scrapy.http.response.html import HtmlResponse
from urlparse import urljoin

from scrapy_balloons.utils.basefunctions import get_attr

chrome64_path = "lib/chrome/64/chromedriver"
chrome32_path = "lib/chrome/32/chromedriver"
phantom_js_path_linux = "lib/phantomjs-1.9.8-linux-x86_64/bin/phantomjs"
phantom_js_path_macos = "lib/phantomjs-1.9.8-macosx/bin/phantomjs"


class SeleniumApi(object):
    @classmethod
    def init(self, spider):
        try:
            from scrapy_balloons.spiders.balloon import config

            global slm_config
            global driver
            global balloon_spider
            driver = None
            balloon_spider = spider
            if config.selenium_config:
                slm_config = config.selenium_config
                if slm_config['driver'] == 'phantomjs':
                    try:
                        driver = webdriver.PhantomJS(phantom_js_path_linux)
                        print "Info : Selenium starting with PhantomJS on Linux OS : Successful"
                    except:
                        driver = webdriver.PhantomJS(phantom_js_path_macos)
                        print "Info : Selenium starting with PhantomJS on Mac OSX : Successful"
                elif slm_config['driver'] == 'firefox':
                    driver = webdriver.Firefox()
                    print "Info : Selenium starting with Firefox : Successful"
                elif slm_config['driver'] == 'chrome':
                    try:
                        driver = webdriver.Chrome(chrome64_path)
                        print "Info : Selenium starting with Chrome 64 bits : Successful"
                    except:
                        driver = webdriver.Chrome(chrome32_path)
                        print "Info : Selenium starting with Chrome 32 bits  : Successful"
        except:
            traceback.print_exc()
            pass

    @classmethod
    def action(self, response):
        res = None
        try:
            driver.get(response.url)
            slm_step = SlmStep(slm_config['action'])
            for i in range(0, slm_step.repeat):
                for code in slm_step.python:
                    eval(code)
                time.sleep(slm_step.sleep)
        except:
            traceback.print_exc()
            pass
        html_res = HtmlResponse(response.url, encoding='utf-8', body=driver.page_source.encode('utf-8'))

        return balloon_spider._requests_to_follow(html_res)

    @classmethod
    def click_and_follow(self, response, **kwargs):
        """
        response -- HtmlResponse
        Click and apply RulesExtractor to make request
        """
        result = self.click_and_get_response(response.url, **kwargs)
        return balloon_spider._requests_to_follow(result[0])


    @classmethod
    def click_and_get_response(cls, url, **kwargs):
        """
        url -- type is str
        return list of SeleniumResponse
        """
        try:
            slm_response = SeleniumResponse(kwargs.get('request'))
            driver.get(url)
            slmStep = SlmStep(slm_config['click'])
            driver.find_element_by_xpath("//body").click()
            for i in range(0, slmStep.repeat):
                target = driver.find_element_by_xpath(slmStep.xpath).click()
                time.sleep(slmStep.sleep)
                print " click %s" % (i)
        except:
            traceback.print_exc()
            pass
        slm_response.add_html_res(url, driver.page_source.encode('utf-8'))
        return slm_response.get_html_res()

    @classmethod
    def click_multi_and_follow(self, response, **kwargs):
        html_res = self.click_multi_and_get_response(response.url, **kwargs)
        return RequestService.requests_to_follow(html_res)

    @classmethod
    def click_multi_and_get_response(self, url, **kwargs):
        try:
            slm_response = SeleniumResponse(kwargs.get('request'))
            driver.get(url)
            slmStep = SlmStep(slm_config['click_multi'])
            try:
                #pass condition wait
                wait = ui.WebDriverWait(driver, slmStep.timeout)
                for i in slmStep.wait_until_present:
                    wait.until(lambda driver: driver.find_elements_by_xpath(i))
            except:
                pass
            elms_click = []
            for x in slmStep.elements_click:
                elms_click = elms_click + driver.find_elements_by_xpath(x)
            for elm in elms_click:
                elm.click()
                time.sleep(slmStep.sleep)
                slm_response.add_html_res(url, driver.page_source.encode('utf-8'))

            return slm_response.get_html_res()
        except:
            traceback.print_exc()
            pass

    @classmethod
    def wait_until_available_and_follow(self, response, **kwargs):
        html_res = self.wait_until_available_and_get_response(response.url, **kwargs)
        return balloon_spider._requests_to_follow(html_res)


    @classmethod
    def wait_until_available_and_get_response(cls, url, **kwargs):
        url = urljoin(balloon_spider.config.base_url, url)
        slmStep = SlmStep(slm_config['wait_until_available'])
        cpt = 0
        driver.get(url)
        while (cpt <= slmStep.repeat):
            print "sleep %s second" % (slmStep.sleep)
            if driver.find_elements_by_xpath(slmStep.xpath):
                #time.sleep(config.wait_after_available)
                break
            cpt += 1
            time.sleep(slmStep.sleep)
        html_res = HtmlResponse(url, encoding='utf-8', body=driver.page_source.encode('utf-8'),
                                request=kwargs.get('request'))
        return html_res


    @classmethod
    def safe_click(cls, driver, xpath, repeat=60, sleep=1):
        for i in range(repeat):
            try:
                target = driver.find_element_by_xpath(xpath)
                target.click()
            except:
                time.sleep(sleep)
                print "%s times : Try to find and click element xpath %s " % (i, xpath)
                pass
        raise Exception("Impossible click on element %s" % (xpath))

    @classmethod
    def get(cls, url, **kwargs):
        driver.get(url)
        time.sleep(kwargs.get('sleep', 10))
        return HtmlResponse(url, encoding='utf-8', body=driver.page_source.encode('utf-8'),
                            request=kwargs.get('request'))


    @classmethod
    def schroll_down_and_follow(self, response, **kwargs):

        res = SeleniumApi.schroll_down_and_get_response(response.url, **kwargs)
        return RequestService.requests_to_follow(res)

    @classmethod
    def find_element(self, id=None, name=None, xpath=None, retries=10, is_display=True, sleep=1):
        while retries:
            try:
                element = None
                if id:
                    element = driver.find_element_by_id(id)
                elif name:
                    element = driver.find_element_by_name(name)
                elif xpath:
                    element = driver.find_element_by_xpath(xpath)
                if is_display and element.is_displayed():
                    return element
                else:
                    return element
            except:
                retries = retries - 1
                time.sleep(sleep)
                pass
        return None


    @classmethod
    def parse_product(self, response):
        driver.get(response.url)
        time.sleep(2)
        response = HtmlResponse(url=response.url, body=driver.page_source.encode('utf-8'), request=response.request,
                                status=response.status, headers=response.headers)
        return balloon_spider.parse_product(response)


    @classmethod
    def schroll_down_and_get_response(self, url, **kwargs):
        slmStep = SlmStep(slm_config['schroll_down'])
        retry = slmStep.retry_after_failed

        def trigger_schroll():
            value = slmStep.schroll_down_start_coefficient
            while value < 1:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight*%s);" % value)
                value += .01

        try:
            driver.get(url)
            print "GET URL %s " % (url)
            current_size = len(SeleniumResponse.get_html_res_from_driver(driver).xpath(slmStep.xpath))
            print "Current courses numbers : %s" % (current_size)
            for i in range(0, slmStep.repeat):
                trigger_schroll()
                time.sleep(slmStep.sleep)
                new_size = len(SeleniumResponse.get_html_res_from_driver(driver).xpath(slmStep.xpath))
                print "Current courses numbers : %s" % (new_size)
                if new_size > current_size:
                    current_size = new_size
                else:
                    retry -= 1
                    if retry == 0:
                        break
        except:
            traceback.print_exc()
        return SeleniumResponse.get_html_res_from_driver(driver, **kwargs)


class SlmStep:
    def __init__(self, config):
        self.sleep = get_attr(config, 'sleep', 1)
        self.timeout = get_attr(config, 'timeout', 100)
        self.xpath = get_attr(config, 'xpath', None)
        self.python = get_attr(config, 'python', [])
        self.python = self.python if not isinstance(self.python, list) else self.python
        self.repeat = get_attr(config, 'repeat', None)
        self.wait_after_available = get_attr(config, 'wait_after_available', 0)
        self.retry_after_failed = get_attr(config, 'retry_after_failed', 3)
        self.elements_click = get_attr(config, 'elements_click', [])
        self.wait_until_present = get_attr(config, 'wait_until_present', [])
        self.schroll_down_start_coefficient = get_attr(config, 'schroll_down_start_coefficient', 0.7)
        if self.repeat == -1:
            self.repeat = 100
        else:
            self.repeat = 1 if self.repeat is None else self.repeat


class SeleniumResponse:
    def __init__(self, request=None):
        self.res = []
        self.request = request


    def add_html_res(self, url, content):
        self.res.append(HtmlResponse(url, encoding='utf-8', body=content, request=self.request))

    @classmethod
    def get_html_res_from_driver(self, driver, **kwargs):
        return HtmlResponse(driver.current_url, encoding='utf-8', body=driver.page_source.encode('utf-8'),
                            request=kwargs.get('request'))

    def get_html_res(self):
        return self.res


class RequestService:
    @classmethod
    def requests_to_follow(self, html_res):
        html_res = html_res if isinstance(html_res, list) else [html_res]
        seen = set()
        links_rules = []
        for r in html_res:
            for n, rule in enumerate(balloon_spider.rules):
                links = [l for l in rule.link_extractor.extract_links(r) if l not in seen]
                for link in links:
                    seen.add(link)
                    links_rules.append((link, rule))
        for link, rule in links_rules:
            r = Request(url=link.url, callback=balloon_spider._response_downloaded)
            r.meta.update(rule=n, link_text=link.text)
            yield rule.process_request(r)

    @classmethod
    def print_info_link(self, links):
        print "Selenium total links is  : %s" % (len(links))
        for link in links:
            print link.url


