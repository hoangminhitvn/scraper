from scrapy.spider import Spider
from scrapy.http import FormRequest
from oshcallianzassistance.items import OshcallianzassistanceItem

class TestRuleSpider(Spider):
    name = "osh"
    start_urls = ["https://www.oshcallianzassistance.com.au/default.aspx"]

    '''
    alpha = No of adults [1,2]
    beta = Dependant children [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    eta = Cover period [3, 4, ... 71, 72]

    Step 1: Create request from fromdata
    Step 2: Get info
    '''

    # Step 1
    def parse(self, response):
        alpha = range(1,3)
        beta = range(11)
        eta = range(3,73)
        # import pdb
        # pdb.set_trace()
        for b in beta:
            for e in eta:
                for a in alpha:
                    item = OshcallianzassistanceItem()
                    item['no_of_adults'] = str(a)
                    item['dependant_children'] = str(b)
                    item['cover_period'] = str(e) + ' Months'

                    request = FormRequest.from_response(response, formdata={
                        '__VIEWSTATE': '/wEPDwULLTE1NDAyNjk5MzkPZBYIAgQPZBYOAgEPEGQQFQIBMQEyFQIBMQEyFCsDAmdnZGQCAg8QZBAVCwEwATEBMgEzATQBNQE2ATcBOAE5AjEwFQsBMAExATIBMwE0ATUBNgE3ATgBOQIxMBQrAwtnZ2dnZ2dnZ2dnZ2RkAgMPEGQQFUYIMyBNb250aHMINCBNb250aHMINSBNb250aHMINiBNb250aHMINyBNb250aHMIOCBNb250aHMIOSBNb250aHMJMTAgTW9udGhzCTExIE1vbnRocwkxMiBNb250aHMJMTMgTW9udGhzCTE0IE1vbnRocwkxNSBNb250aHMJMTYgTW9udGhzCTE3IE1vbnRocwkxOCBNb250aHMJMTkgTW9udGhzCTIwIE1vbnRocwkyMSBNb250aHMJMjIgTW9udGhzCTIzIE1vbnRocwkyNCBNb250aHMJMjUgTW9udGhzCTI2IE1vbnRocwkyNyBNb250aHMJMjggTW9udGhzCTI5IE1vbnRocwkzMCBNb250aHMJMzEgTW9udGhzCTMyIE1vbnRocwkzMyBNb250aHMJMzQgTW9udGhzCTM1IE1vbnRocwkzNiBNb250aHMJMzcgTW9udGhzCTM4IE1vbnRocwkzOSBNb250aHMJNDAgTW9udGhzCTQxIE1vbnRocwk0MiBNb250aHMJNDMgTW9udGhzCTQ0IE1vbnRocwk0NSBNb250aHMJNDYgTW9udGhzCTQ3IE1vbnRocwk0OCBNb250aHMJNDkgTW9udGhzCTUwIE1vbnRocwk1MSBNb250aHMJNTIgTW9udGhzCTUzIE1vbnRocwk1NCBNb250aHMJNTUgTW9udGhzCTU2IE1vbnRocwk1NyBNb250aHMJNTggTW9udGhzCTU5IE1vbnRocwk2MCBNb250aHMJNjEgTW9udGhzCTYyIE1vbnRocwk2MyBNb250aHMJNjQgTW9udGhzCTY1IE1vbnRocwk2NiBNb250aHMJNjcgTW9udGhzCTY4IE1vbnRocwk2OSBNb250aHMJNzAgTW9udGhzCTcxIE1vbnRocwk3MiBNb250aHMVRgEzATQBNQE2ATcBOAE5AjEwAjExAjEyAjEzAjE0AjE1AjE2AjE3AjE4AjE5AjIwAjIxAjIyAjIzAjI0AjI1AjI2AjI3AjI4AjI5AjMwAjMxAjMyAjMzAjM0AjM1AjM2AjM3AjM4AjM5AjQwAjQxAjQyAjQzAjQ0AjQ1AjQ2AjQ3AjQ4AjQ5AjUwAjUxAjUyAjUzAjU0AjU1AjU2AjU3AjU4AjU5AjYwAjYxAjYyAjYzAjY0AjY1AjY2AjY3AjY4AjY5AjcwAjcxAjcyFCsDRmdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dkZAIEDw8WAh4HVmlzaWJsZWdkZAIFDw8WAh8AZ2RkAgYPDxYCHghJbWFnZVVybAUkL3NraW5zL29zaGMyL2ltYWdlcy9idG5DYWxjdWxhdGUuZ2lmFgYeC29uTW91c2VPdmVyBUlNTV9zd2FwSW1hZ2UoJ2J0bkNhbGN1bGF0ZScsJycsJy9za2lucy9vc2hjMi9pbWFnZXMvYnRuQ2FsY3VsYXRlXy5naWYnLDEpHgpvbk1vdXNlT3V0BRNNTV9zd2FwSW1nUmVzdG9yZSgpHgdvbkNsaWNrBRZyZXR1cm4gdmFsaWRhdGVGb3JtKCk7ZAIHDw8WAh8BBSMvc2tpbnMvb3NoYzIvaW1hZ2VzL2J0bkNvbnRpbnVlLmdpZhYGHwIFR01NX3N3YXBJbWFnZSgnYnRuQ29udGludWUnLCcnLCcvc2tpbnMvb3NoYzIvaW1hZ2VzL2J0bkNvbnRpbnVlXy5naWYnLDEpHwMFE01NX3N3YXBJbWdSZXN0b3JlKCkfBAUWcmV0dXJuIHZhbGlkYXRlRm9ybSgpO2QCBQ8PFgIeBFRleHQFCUFVJDE0Ny4wMGRkAgYPDxYCHwVlZGQCBw8PFgIfAGdkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAgUMYnRuQ2FsY3VsYXRlBQtidG5Db250aW51ZfZHUS9WFembeqSllD5dO8AKdZ7a',
                        '__EVENTVALIDATION': '/wEWVwKo6KrKCALBitaSDwL7mPi9BQL6mPi9BQL3sNG8CwLosNG8CwLpsNG8CwLqsNG8CwLrsNG8CwLssNG8CwLtsNG8CwLusNG8CwL/sNG8CwLwsNG8CwLosJG/CwLP+c+vCQLO+c+vCQLJ+c+vCQLI+c+vCQLL+c+vCQLa+c+vCQLV+c+vCQLN+Y+sCQLN+YOsCQLN+YesCQLN+busCQLN+b+sCQLN+bOsCQLN+besCQLN+ausCQLN+e+vCQLN+eOvCQLM+Y+sCQLM+YOsCQLM+YesCQLM+busCQLM+b+sCQLM+bOsCQLM+besCQLM+ausCQLM+e+vCQLM+eOvCQLP+Y+sCQLP+YOsCQLP+YesCQLP+busCQLP+b+sCQLP+bOsCQLP+besCQLP+ausCQLP+e+vCQLP+eOvCQLO+Y+sCQLO+YOsCQLO+YesCQLO+busCQLO+b+sCQLO+bOsCQLO+besCQLO+ausCQLO+e+vCQLO+eOvCQLJ+Y+sCQLJ+YOsCQLJ+YesCQLJ+busCQLJ+b+sCQLJ+bOsCQLJ+besCQLJ+ausCQLJ+e+vCQLJ+eOvCQLI+Y+sCQLI+YOsCQLI+YesCQLI+busCQLI+b+sCQLI+bOsCQLI+besCQLI+ausCQLI+e+vCQLI+eOvCQLL+Y+sCQLL+YOsCQLL+YesCQLarIaJCgKYm8bUBzEbTu/rBw2MOC88aj37GrnEigIk',
                        'tbStartDate': '26/05/2015',
                        'ddAdults': str(a),
                        'ddDependants': str(b),
                        'ddOshcCoverPeriod': str(e),
                        'btnCalculate.x': '0',
                        'btnCalculate.y': '0'
                    }, callback=self.get_price)

                    request.meta['keys'] = item
                    yield request

    # Step 2
    def get_price(self, response):
        item = response.meta['keys']
        item['price'] = response.xpath("//span[@id='lblPremium']//text()").extract()[0]
        yield item
