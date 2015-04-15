from scrapy_balloons.utils.allfunctions import *

NO_LIMIT = -1


class BalloonCrawl(CrawlSpider):
    request_product_count = 0
    request_cat_count = 0
    resolved = {}
    name = "web_scraper"
    base_url = ""
    request_caches = {}
    products_caches = None
    limit = NO_LIMIT
    is_must_login = False
    is_compile_rules = False
    root_level = "0"
    debug = None
    resources_ext = SizedDict()
    pre_run_service = None
    config = None
    all_url_sent = set()
    suspect_requests = []
    collector = None
    summary = None
    compress = None
    s3 = None
    csv = None
    #object process_request_original :store process_request by rule, extracted from config file
    process_request_original = {}


    def __init__(self, config_file=None, debug=None, limit=NO_LIMIT, summary=summary, suspect_urls_log=None,
                 compress=None, s3=None, csv=None,
                 *args, **kwargs):
        """
        Keyword arguments:
        limit :
        config_file, Ex : treehouse_config.json -- file name of configuration file, base on this, spider will understand how to extract data
        debug, Ex : description,true -- the spider will set the pdb.set_trace() when have null on field description
        summary Ex : treehouse_summary.json -- file name that store the statistic of output json
        suspect_urls_log Ex : errors_url.txt -- file name that store urls that have the response code different 200
        compress: Ex : compress : --folder path where the compress file will be created
        csv : Ex csv : --folder path where the csv file will be created
        limit -- number of course to export.


        Example of full command : go to scraper-framework folder
        scrapy crawl web_scraper -a config_file=config/02geek_config.json -a limit=5 -o transcer.json -a compress=compress -a csv=csv -a summary=summary.json
        """
        json_data = open(config_file)
        # all information in config file will be stored in config object
        global config
        global balloon_spider
        balloon_spider = self
        config = ConfigFile(config=json.load(json_data), config_file_path=config_file)
        self.config = config
        json_data.close()
        self.base_url = config.base_url
        self.limit = int(limit)
        self.debug = DebugParameter(debug)
        self.products_caches = ProductCache()
        self.suspect_urls_log = suspect_urls_log
        self.compress = compress
        self.s3 = s3
        self.summary = summary
        self.csv = csv
        # SeleniumApi.init(self)
        # check and process pre run if exist pre run config
        if config.pre_run:
            self.pre_run_service = PreRunService(config.pre_run)
            self.start_urls = config.start_urls
        elif config.login:
            try:
                self.log("Processing to login %s page" % str(config.login['start_url']))
                url = config.login['start_url']
                self.start_urls = url if isinstance(url, list) else [url]
                self.is_must_login = True
            except:
                print("Error when reading the login config, url %s " % str(url))
        else:
            self.start_urls = config.start_urls
        self.collector = StatsCollector(spider=self)
        signal.signal(signal.SIGALRM, self.collector.item_scraped_must_growing)
        signal.alarm(CHECK_ITEM_SCRAPED_COUNT_PERIODIC_TIME)


    def parse(self, response):

        """
        Priority for handling a response
        1 -- pre run
        2 -- login
        3 -- apply rule extractor of scrapy framework
        4 -- apply custom extractor ( xpath + code python)
        """
        self.resources_ext[response.url] = response
        if self.pre_run_service and self.pre_run_service.started is False:
            return self.pre_run_service.start_process()
        elif self.is_must_login:
            self.is_must_login = False
            return self.process_login(response)
        elif contains(config.levels, "0") and get_attr(self.resolved, 'parse_levels_0', False) is False:
            self.resolved['parse_levels_0'] = True
            return self.parse_levels_0(response)
        elif 'extractor_rules' in config.output and (
                        get_attr(self.resolved, "extractor_rules", False) is False or response.url in self.start_urls):
            self.resolved['extractor_rules'] = True
            return self.parse_rules(response)
        elif contains(config.output, 'xpath') or contains(config.output, 'python'):
            return self.parse_xpath_python(response)
        else:

            self.request_product_count += 1
            response.meta['index'] = self.request_product_count
            response.meta['level'] = '1'
            return self.parse_product(response)


    def parse_xpath_python(self, response):
        products_html = None
        if 'xpath' in config.output:
            products_html = xpath(response, config.output['xpath'])
        if 'python' in config.output:
            products_html = eval(config.output['python'])
        for product_html in products_html:
            yield self.start_download(product_html, response)


    def parse_rules(self, response):
        # set rules for spider  and compile
        self.rules = self.eval_rules(config.output['extractor_rules']['rules'])
        # set process_request
        for (index, r) in enumerate(self.rules):
            if r.process_request:
                self.process_request_original[index] = r.process_request
            if r.callback is 'parse_product' or callable(r.callback):
                #ovveride  process_request
                r.process_request = self.process_request
            else:
                #ovveride  process_request
                r.process_request = self.process_request_cat
        super(BalloonCrawl, self).__init__()
        return self._parse_response(response, self.parse_start_url, cb_kwargs={})

    def parse_levels_0(self, response):
        config_level_0 = config.levels['0']
        data = self.process_extract_data(None, response, config_level_0)
        callback = get_attr(config_level_0, 'callback')
        if data == config_level_0 and callback:
            # data unchanged and has callback, use-case of evisors website
            return eval(callback)(response)
        elif data and isinstance(data, list):
            data = data[0]
        if isinstance(data, HtmlResponse):
            # case selenium, see hubspot config
            if callback:
                return eval(callback)(data)
            else:
                return self.parse(data)


    def start_download(self, html, source):
        """
        As a product need to crawl multiples pages corresponding multiple levels, first spider will crawl
        all levels needed for a product and stored them in a product cache  object. Each cached object identified by a id,
        increment by 1. This method will extract links of all levels to crawl
        Keyword arguments:
        html -- HtmlResponse or Selector
        source -- HtmlResponse
        """
        # get the config corresponding for the level
        if contains(config.levels, '1'):
            config_level = config.levels['1']
            href_info = None
            request = None
            if isinstance(config_level, dict):
                href_info = self.process_extract_data(None, html, config_level)
            elif isinstance(config_level, unicode) or isinstance(config_level, str):
                href_info = extract_data(xpath(html, config_level))
            if href_info:
                if isinstance(href_info, Request):
                    href_info.callback = self.parse_product
                    return self.process_request(href_info, html, source)
                else:
                    href_info = href_info[0] if isinstance(href_info, list) else href_info
                    request = Request(urljoin(self.base_url, href_info), callback=self.parse_product)
                    return self.process_request(request, html, source)
            else:
                log.msg("The course link must be not null", level=log.ERROR)
                return None
        elif html and ( isinstance(html, unicode) or isinstance(html, str)):
            request = Request(urljoin(self.base_url, html), callback=self.parse_product)
            return self.process_request(request, html, source)
        else:
            self.request_product_count += 1
            self.products_caches.add_data_index_level(self.request_product_count, "root", source)
            self.products_caches.add_data_index_level(self.request_product_count, "0", html)
            return self.process_filter_fill_data(self.request_product_count)

    def parse_product(self, response):
        """
        extracts all urls necessary for a product and process request
        """
        #print "parse_product %s "%(response.url)
        def make_request(index, level, urls, params=None):
            urls = unique(urls) if isinstance(urls, list) else [urls]
            headers = get_attr(params, 'headers', None)
            meta = {"level": level, "index": index, 'dont_redirect': True}
            method = get_attr(params, 'method', 'GET')
            body = get_attr(params, 'body', "")
            if get_attr(params, 'next_request'):
                meta['next_request'] = get_attr(params, 'next_request')
            requests = [Request(urljoin(self.base_url, url), callback=self.parse_product,
                                meta=meta, method=method, body=body,
                                dont_filter=True, headers=headers) for url in urls]
            if len(requests) == 0:
                # need set None for this, useful when check is finish download
                self.products_caches.get(index)[level] = None
            else:
                # set if len > 0, to check if a course has response for all levels
                self.products_caches.get(index)[level + '_remaining'] = len(requests)

            return requests

        index = response.meta['index']
        level = response.meta['level']
        product_cache = self.products_caches.add_data_index_level(index, level, response)
        next_request = False
        if 'next_request' in response.meta:
            data = eval(response.meta['next_request'])(response)
            if data:
                next_request = True
                requests = make_request(index, level, data['url'], data)
                for r in requests:
                    yield r
        else:
            sub_levels = self.get_levels_child(level)

            for (l1, c1) in sub_levels.iteritems():
                try:
                    if isinstance(c1, unicode) or isinstance(c1, str):
                        # if config is unicode, extract directly, not work with process_extract_data
                        data = extract_data(xpath(response, c1))
                    else:
                        data = self.process_extract_data(product_cache, response, c1)
                    if data is None:
                        product_cache[l1] = None
                        # here we will set all response for child level == None
                        sub_levels_ = self.get_levels_child(l1)
                        for (l2, c2) in sub_levels_.iteritems():
                            product_cache[l2] = None
                    else:

                        requests = []
                        if contains(c1, 'selenium_function') or isinstance(data, Selector) or isinstance(data,
                                                                                                         HtmlResponse):
                            # The type of data will be a HtmlResponse or a Selector
                            product_cache = self.products_caches.add_data_index_level(index, l1, data)
                            # This is the case that data got after a call selenium => need find the child config and extract
                            sub_levels_ = self.get_levels_child(l1)
                            for (l2, c2) in sub_levels_.iteritems():
                                data = self.process_extract_data(product_cache, data, c2)
                                requests += make_request(index, l2, data)
                        else:
                            if isinstance(data, list):
                                # only urls
                                requests += make_request(index, l1, data)
                            elif isinstance(data, dict):

                                # utype(data
                                requests += make_request(index, l1, data['url'], data)
                            else:
                                requests += make_request(index, l1, data)
                        if requests:
                            for r in requests:
                                # Attention, the callback function must return a Request, BaseItem
                                yield r
                except:
                    traceback.print_exc()
                    pass
        # self.print_debug("\nINFO %s : Index %s : %s " % (
        #     self.get_provider_id(), index, object_to_string(self.products_caches.get(index))))
        if self.is_finish_download(index, response) is True and next_request is False:
            self.print_debug("Index %s FINISHED DOWNLOAD" % (index))
            yield self.process_filter_fill_data(index)


    def process_filter_fill_data(self, index):
        if self.process_pre_filters(self.products_caches.get(index), config.pre_filters):
            item = eval(config.output['type'])()
            product_cache = self.products_caches.get(index)
            item['product_url'] = product_cache["1"].url if contains(product_cache, "1") else product_cache["root"].url
            item = self.fill_data_recursive(product_cache, item, config.output['fields'])
            ##finish
            self.products_caches.delete(index)
            return item
        else:
            return None


    def get_data_at_level(self, source, field_config=None, level=None):
        """
        function get html data from a level. The level is extracted from field in config json.
        if level is None => return the value '0' or '1'
        if level can be a key in pre_run
        """
        # level can be : "0", "1", "price" <- come from pre_run
        if source:
            level = self.get_level_value(field_config) if level is None else level
            data = []
            if level:
                if isinstance(level, unicode) or isinstance(level, str):
                    if contains(source, level):
                        data = source[level]
                    elif self.pre_run_service and contains(self.pre_run_service.responses_received_by_key, level):
                        data = self.pre_run_service.responses_received_by_key[level]
                        data = data[0] if isinstance(data, list) and len(data) == 1 else data
                elif isinstance(level, list):
                    data = []
                    for l in level:
                        sub_response = source[l] if isinstance(source[l], list) else [source[l]]
                        sub_response = [r for r in sub_response if r]
                        data.extend(sub_response)
                # level contains python key
                if isinstance(field_config, dict) and contains(field_config, 'level') and contains(
                        field_config['level'], 'python'):
                    data = eval(get_attr(field_config['level'], 'python'))
            return data if data else None
        else:
            return None


    def get_level_value(self, field):
        # return value None, "0" , "1", or  key in pre_run
        if contains(field, 'level'):
            return field['level']['value'] if isinstance(field['level'], dict) else field['level']
            return value
        else:
            return None


    def fill_data_recursive(self, source, product_cache, fields):
        level_fields = {}

        def add_field(field_name, level):
            level = level if isinstance(level, list) else [level]
            for l in level:
                if l in level_fields:
                    level_fields[l].append(field_name)
                else:
                    level_fields[l] = [field_name]

        for (k, v) in fields.iteritems():
            level = self.get_level_value(v)
            level = level if level else self.get_root_level(source)
            if get_process_type(v) in ['object', 'abstract', 'list']:
                add_field(k, level)
            response_level = self.get_data_at_level(source, field_config=v)
            response = response_level if response_level else source[level]
            product_cache[k] = self.process_extract_data(source, response, v, field_name=k)
        if 'raw_html' not in config.ignore_fields:
            raw_html = self.get_raw_html(product_cache)
            for (key, field_names) in level_fields.iteritems():
                html_source = self.get_data_at_level(source, level=key)
                if html_source:
                    sub_raw_html = self.create_raw_html(html_source, field_names)
                    raw_html.append(sub_raw_html)
        return product_cache


    def process_extract_data(self, source, response, field, **kw):
        if isinstance(field, list):
            for sub_config in field:
                response_level = self.get_data_at_level(source, field_config=sub_config)
                if response_level:
                    result = self.process_extract_data_(source, response_level, sub_config, **kw)
                else:
                    result = self.process_extract_data_(source, response, sub_config, **kw)
                if result:
                    return result
            return None
        else:
            response_level = self.get_data_at_level(source, field_config=field)
            response_level = response_level if response_level else response
            return self.process_extract_data_(source, response_level, field, **kw)


    def process_extract_data_(self, source, response, field, **kw):
        final_result = []
        if isinstance(response, list):
            for res in response:
                result = self.process_extract_data_1(source, res, field, **kw)
                if result:
                    if isinstance(result, list):
                        final_result.extend(result)
                    else:
                        final_result.append(result)
            return final_result
        else:
            return self.process_extract_data_1(source, response, field, **kw)


    def process_extract_data_1(self, source, response, field, **kw):
        # by pass field with postAction key
        process_type = get_process_type(field)
        if process_type == 'list':
            # can be a list object or list string
            data = []
            selector = get_selector(response, field)
            item = eval(field['type'])[0]
            selector = SelectorList([selector]) if isinstance(selector, Selector) else selector
            selector = [] if selector is None else selector
            if 'pre_run' in field:
                selector = self.python(None, field['pre_run'], selector, response, source, **kw)
                selector = selector if selector else []
            for sub_selector in selector:
                if item is str:
                    #object inside is string
                    sub_data = self.python(extract_data(sub_selector), field, sub_selector, response, source, **kw)
                    if sub_data:
                        data = append_to_list(data, sub_data)
                else:
                    #recreated object
                    sub_data = eval(field['type'])[0]()
                    for (k, v) in field['fields'].iteritems():
                        response_level = self.get_data_at_level(source, field_config=v)
                        response = response_level if response_level else sub_selector
                        sub_data[k] = self.process_extract_data(source, response, v, field_name=k)
                    data.append(sub_data)
            #check if rewrite all the result variable
            return self.python(data, field, selector, response, source, **kw)
        elif process_type == 'abstract':
            selector = None;
            data = None
            try:
                selector = get_selector(response, field)
                data = extract_data(selector, field)
                data = self.python(data, field, selector, response, source, **kw)
                if kw.get('set_strace') == True:
                    pdb.set_trace()
            except:
                traceback.print_exc()
            finally:
                if data is None and self.debug:
                    debug = self.debug
                    if (kw.get('field_name') == debug.field_name and debug.field_name is not None) or (
                                debug.field_name == '*'):
                        self.print_debug_kw(source=source, field_name=kw.get('field_name'),
                                            response=response, selector=selector, field=field, data=data)
                        if kw.get('set_strace'):
                            return
                        elif bool(debug.set_trace):
                            self.process_extract_data_1(source, response, field,
                                                        set_strace=bool(debug.set_trace))
            return data
        elif process_type == 'object':
            selector = get_selector(response, field)
            data = eval(field['type'])()
            for (k, v) in field['fields'].iteritems():
                response_level = self.get_data_at_level(source, field_config=v)
                response = response_level if response_level else selector
                data[k] = self.process_extract_data(source, response, v, field_name=k)
                data[k] = self.python(data[k], v, selector, response, source, **kw)
            data = self.python(data, field, selector, response, source, **kw)
            return data
        else:
            return field


    def print_debug(self, msg):
        if self.debug.field_name:
            print msg


    def print_debug_kw(self, **kw):
        print "\n-------------------BEGIN DEBUGGING %s ----------------------------" % kw.get('field_name')
        print "Available Scrapy objects: {0} | {1} | {2} | {3}".format('source', 'response', 'selector', 'field')
        print "{0:<15} : {1}".format('view(response)', "View response in browser or txt file, after ctrl+D to go back")
        print "{0:<15} : {1}".format('source', object_to_string(kw.get('source')))
        #print "{0:<15} : {1}".format('level', kw.get('level'))
        print "{0:<15} : {1}".format('field_name', kw.get('field_name'))
        print "{0:<15} : {1}".format('response', kw.get('response'))
        print "{0:<15} : {1}".format('xpath', get_attr(kw.get('field'), 'xpath'))
        print "{0:<15} : {1}".format('selector', kw.get('selector'))
        print "{0:<15} : {1}".format('python', get_attr(kw.get('field'), 'python'))
        print "{0:<15} : {1}".format('data ', kw.get('data'))
        print "-------------------END DEBUGGING %s ----------------------------" % kw.get('field_name')


    def python(self, data, field=None, selector=None, response=None, source=None, **kw):
        # two variables available for python , selector and data, Attention : dont remove data variable here
        try:
            if contains(field, "python"):
                response = head(response) if isinstance(response, list) else response
                data = eval(field['python'])
            try:
                data = eval(field['selenium_function']) if contains(field, 'selenium_function') else data
            except:
                return data if data else None
            return data
        except:
            #traceback.print_exc()
            return None


    def after_login(self, response):
        balloon_spider.start_urls = config.start_urls
        return balloon_spider.start_requests()


    def process_login(self, response):
        from_response = get_attr(config.login, 'from_response')
        formname = get_attr(config.login, 'formname')
        formnumber = get_attr(config.login, 'formnumber', 0)
        formdata = get_attr(config.login, 'formdata')
        clickdata = get_attr(config.login, 'clickdata')
        dont_click = get_attr(config.login, 'dont_click', False)
        formxpath = get_attr(config.login, 'formxpath')
        if from_response == True:
            return FormRequest.from_response(response, formname=formname, formnumber=formnumber, formdata=formdata,
                                             clickdata=clickdata, dont_click=dont_click, formxpath=formxpath,
                                             callback=self.after_login)
        else:
            #to do
            return FormRequest(url=config.login['start_url'], formdata=formdata, callback=self.after_login)


    def get_root_level(self, source):
        if "0" in source:
            self.root_level = "0"
            return self.root_level
        elif "1" in source:
            self.root_level = "1"
            return self.root_level
        else:
            print ("Error : Source don't have root level %s" % (str(source)))


    def create_raw_html(self, source, fields):
        raw_html = {}
        if isinstance(source, Selector):
            raw_html['link'] = self.start_urls[0]
            raw_html['source'] = clean_html(source.extract())
        elif isinstance(source, HtmlResponse):
            raw_html['link'] = source.url
            raw_html['source'] = clean_html(source.body)
        elif isinstance(source, list):
            links = []
            for item in source:
                if isinstance(item, HtmlResponse):
                    links.append(item.url)
            raw_html['link'] = links
            raw_html['source'] = "Please access by access the url, not include here because the reason of size"
        raw_html['fields'] = fields
        return raw_html


    def get_fields_to_fill(self, fields, currentLevel):
        results = {}
        #ROOT LEVEL
        for (k, v) in fields.iteritems():
            if not contains(v, 'level'):
                if currentLevel == self.root_level:
                    results[k] = v
            elif v['level'] == currentLevel:
                results[k] = v
        return results


    def is_finish_download(self, index, response):
        product_cache = self.products_caches.get(index)
        # all levels must be present, and _remaining = 0
        for level, value in config.levels.items():
            if level != '0' and not level in product_cache.keys():
                return False
            elif contains(product_cache, level + '_remaining') and product_cache[level + '_remaining'] != 0:
                return False
        return True


    def get_levels_child(self, parent):
        child = {}
        for (k, v) in config.levels.iteritems():
            if k[:-2] == parent:
                child[k] = v
        return child


    def get_html_parent(self, htmlRoot, index, level):
        if level == "1":
            return htmlRoot
        else:
            levelParent = level[:-2]
            return self.products_caches.get_data_index_level(index, levelParent)


    def process_pre_filters(self, levels, filters_config):
        """
        levels -- list of html response for all levels,
        filters -- list of filter config, write in python code, all levels must match all to be able continue
        filters_not -- list of filter config, write in python code, if one  level match one of these list, the product will be ignored
        """
        try:
            if 'filters' in filters_config:
                for filter in filters_config['filters']:
                    ## if found one false, ignore this item
                    response = levels[filter['level']]
                    if eval(filter['python']) == False:
                        return False
            if 'filters_not' in filters_config:
                for filter_not in filters_config['filters_not']:
                    ## if found one True, ignore this item
                    response = levels[filter_not['level']]
                    if eval(filter_not['python']) == True:
                        return False
            return True
        except:
            return True


    def get_raw_html(self, item):
        if contains(item, 'raw_html'):
            return item['raw_html']
        else:
            self.set_value(item, 'raw_html', [])
            return item['raw_html']


    def create_new_product(self):
        product = eval(config.output['type'])()
        for (k, v) in config.output['fields'].iteritems():
            product[k] = self.process_extract_data(None, None, v, field_name=k)
        return product


    def eval_rules(self, rules):
        if isinstance(rules, list):
            exp = ""
            for v in rules:
                exp = exp + v + ','
            return eval("[%s]" % (exp[:exp.rfind(',')]))
        else:
            return eval(rules)


    # def closed(self, reason):
    #     from scrapy_balloons.selenium_api import driver
    #
    #     try:
    #         driver.close()
    #         print "Selenium driver has closed"
    #     except:
    #         pass


    def process_request(self, request, html=None, source=None):
        # if there is not key index and level in meta, assign it to level 1
        if not contains(request.meta, 'index') and not contains(request.meta, 'level'):
            if (self.limit != NO_LIMIT and self.request_product_count >= self.limit) or (
                        request.url in self.all_url_sent):
                return None
            else:
                self.all_url_sent.add(request.url)
                self.request_product_count += 1
                # self.print_debug("INFO %s : Sending product request Index %s, URL %s " % (
                #     self.get_provider_id(), self.request_product_count, request.url))
                if source and html and isinstance(html, Selector):
                    self.products_caches.add_data_index_level(self.request_product_count, "root", source)
                    self.products_caches.add_data_index_level(self.request_product_count, "0", html)
                request.meta['index'] = self.request_product_count
                request.meta['level'] = '1'
                try:
                    # if process_request exist from config file, execute it
                    if request.meta['rule'] in self.process_request_original:
                        request = self.process_request_original[request.meta['rule']](request)
                except:
                    pass
                # selenium for level 1
                try:
                    selenium_function = config.levels['1']['selenium_function']
                    response = eval(selenium_function)
                    response = response[0] if isinstance(response, list) else response
                    result = list(self.parse_product(response))
                    return result[0]
                except:
                    pass
        return request


    def process_request_cat(self, request):
        self.print_debug("Spider process_request_cat %s " % (request))
        if (self.limit != NO_LIMIT and (
                        self.request_product_count >= self.limit or self.request_cat_count >= self.limit + 5)) or (
                    request.url in self.all_url_sent):
            return None
        else:
            self.all_url_sent.add(request.url)
            self.request_cat_count += 1
            # self.print_debug("INFO %s : Sending categories request Index %s, URL %s " % (
            #     self.get_provider_id(), self.request_cat_count, request.url))
            return request


    def set_value(self, product, field_name, field_value):
        try:
            product[field_name] = field_value
        except:
            log.msg("Problem when set value key %s % value " % (field_name, field_value), level=log.WARNING)
            pass


    # def get_provider_id(self):
    #     return sub_string(config.output['fields']['provider_id'], 10)

        #def passCat(self, response):
        #    print "passCat %s" % (response.url)


class ConfigFile:
    def __init__(self, config=None, config_file_path=None):
        self.ignore_fields = get_attr(config, 'ignore_fields', [])
        self.login = get_attr(config, 'login')
        self.base_url = config['base_url']
        self.output = config['output_config']
        self.levels = config['levels']
        self.pre_filters = get_attr(self.output, 'pre_filters')
        self.post_filters = get_attr(self.output, 'post_filters')
        self.post_interceptors = get_attr(self.output, 'post_intemerceptors')
        self.ssl = get_attr(config, 'ssl')
        self.pre_run = get_attr(config, 'pre_run')
        self.selenium_config = get_attr(config, 'selenium_config')
        self.start_urls = config['start_url'] if isinstance(config['start_url'], list) else [
            config['start_url']]
        self.config_file_path = config_file_path
        self.config_file_name = config_file_path.split("/")[len(config_file_path.split("/")) - 1]
        self.settings = config['settings'] if contains(config, 'settings') else {}


class ProductCache:
    """
    a caches that store all response of different levels for a course.
    Each course identified by a unique id
    """
    products_caches = {}

    def get(self, index):
        if index in self.products_caches:
            return self.products_caches[index]
        else:
            item = {}
            self.products_caches[index] = item
            return self.products_caches[index]

    def get_data_index_level(self, index, level):
        product_cache = self.get_produc_cache_by_index(index)
        if contains(product_cache, level):
            return product_cache[level]
        return None

    def update(self, index, product_cache):
        self.products_caches[index] = product_cache

    def delete(self, index):
        del self.products_caches[index]

    def add_data_index_level(self, index, level, data):
        #data = data if isinstance(data,list) else [data]
        product_cache = self.get(index)
        if contains(product_cache, level + '_remaining'):
            product_cache[level + '_remaining'] -= 1
        if contains(product_cache, level):
            product_cache[level] = product_cache[level] if isinstance(product_cache[level], list) else [
                product_cache[level]]
            data = data if isinstance(data, list) else [data]
            product_cache[level] = product_cache[level] + data
        else:
            product_cache[level] = data
        return product_cache


class PreRunService:
    """
      Example for prerun_config described as bellow. With this config, when the prerun finish,the result will be
      stored in object responses_received_by_key.

     "pre_run": {
          "price_info": {
          "xpath": "concat(//div[@class='plan-meta-silver']/span/text(),//div[@class='plan-meta-silver']/span/small/text())",
          "start_url": "https://f5.com/price"
        },
        "all_events": {
            "start_url": "https://f5.com/education/training/schedule",
            "extractor_rules": {
                "rules": [
                    "Rule(lxml(allow=('.*'), restrict_xpaths=\"//span[@id='dnn_ContentPane']//ul//li/a\"), follow=True)",
                    "Rule(lxml(allow=('schedule-plain',), tags=('iframe'), attrs=('src'), ), callback=balloon_spider.pre_run_service.parse)"
                ]
            }
        }
    }
    """
    # Example  requests_url_by_key : {'product_events':['http://url1','http://url2']}
    # every request will be added into this object, the purpose is to check if the prerun step send requests  and
    # received responses completely
    requests_url_by_key = dict()

    # Example requests_by_key : {'product_events':[scrapy.Request,scrapy.Request]}
    requests_by_key = dict()

    # Example : {'price_info':[HtmlResponse],'all_events':[HtmlResponse,HtmlResponse,HtmlResponse]}
    responses_received_by_key = dict()
    current_key = None
    started = False
    config = None
    price_info = None

    def __init__(self, config):
        self.config = config

    def process_request(self, request):
        self.add_request_by_key(self.current_key, request)
        request.meta['key'] = self.current_key
        return request

    def parse(self, response):
        key = response.meta['key']
        self.add_response_by_key(response)
        if self.is_need_parse_rules(response):
            return balloon_spider._parse_response(response, balloon_spider.parse_start_url, cb_kwargs={})
        elif self.is_received_all_requests_for_a_key(key):
            if self.next_key_to_process():
                return self.start_process()
            else:
                # finish all things in prerun step, back to main spider
                self.process_all_response()
                balloon_spider.start_urls = config.start_urls
                return balloon_spider.start_requests()

    def add_response_by_key(self, response):
        key = response.meta['key']
        if contains(self.responses_received_by_key, key):
            self.responses_received_by_key[key].append(response)
        else:
            self.responses_received_by_key[key] = [response]

    def add_request_by_key(self, key, request):
        if contains(self.requests_url_by_key, key):
            if request.url not in self.requests_url_by_key[key]:
                self.requests_url_by_key[key].append(request.url)
                self.requests_by_key[key].append(request)
        else:
            self.requests_url_by_key[key] = [request.url]
            self.requests_by_key[key] = [request]


    def is_received_all_requests_for_a_key(self, key):
        # check if Prerun has all responses for requests
        return len(self.requests_by_key[key]) == len(self.responses_received_by_key[key])


    def is_need_parse_rules(self, response):
        key = response.meta['key']
        url = response.url
        for (k, v) in self.config.iteritems():
            if k == key and contains(v, 'extractor_rules') and url in v['start_url']:
                return True
        return False

    def start_process(self):
        self.started = True
        key = self.next_key_to_process()
        self.current_key = key
        sub_config = self.config[key]
        requests = []
        params = {'callback': balloon_spider.pre_run_service.parse, 'meta': {"key": key, 'dont_redirect': True},
                  'dont_filter': True}
        if contains(sub_config, 'start_url'):
            if contains(sub_config, 'extractor_rules'):
                balloon_spider.rules = balloon_spider.eval_rules(sub_config['extractor_rules']['rules'])
                for r in balloon_spider.rules:
                    if r.callback:
                        r.process_request = balloon_spider.pre_run_service.process_request
                balloon_spider._compile_rules()
            start_urls = self.to_list(sub_config['start_url'])
            final_data = []
            for url in start_urls:
                # don't use deepcopy here
                params_ = copy.copy(params)
                params_['url'] = url
                final_data.append(params_)
            requests = make_request(final_data)
        elif contains(sub_config, 'python'):
            # result eval must return a dict or list of dict
            final_data = []
            data = self.to_list(eval(sub_config['python']))
            for data_ in data:
                final_data.append(dict(params.items() + data_.items()))
            requests = make_request(final_data)
        for r in requests:
            self.add_request_by_key(key, r)
            yield r

    def next_key_to_process(self):
        for k in self.config.keys():
            if not contains(self.requests_by_key, k):
                return k
        return None

    def to_list(self, value):
        return value if isinstance(value, list) else [value]

    def process_all_response(self):
        for (k, v) in self.responses_received_by_key.iteritems():
            # handle  for the library has done config for price
            if k == 'price':
                try:
                    price = balloon_spider.process_extract_data(None, v[0], self.config[k])
                    self.price_info = get_price_info(price)
                except:
                    traceback.print_exc()


class DebugParameter:
    def __init__(self, value):
        value = value.split(',') if value else []
        self.field_name = value[0] if len(value) > 0 else None
        self.set_trace = value[1] if len(value) > 1 else False
