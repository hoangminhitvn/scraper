from PyPDF2 import PdfFileReader
from scrapy.http.response import Response
from scrapy_balloons.utils.html_string import html_to_text
import StringIO
import pdb

import re


class compuworks:
    pdf_to_text = {}
    text = None
    @classmethod
    def get_description(cls, response):
        text = compuworks.get_text_from_cache(response)
        patterns = ["Description:(.*)Days",
                    "Description:(.*)Length:",
                    "Course Overview(.*)Course Objectives"
        ]
        for p in patterns:
            result = re.search(p, text, re.S)
            if result:
                return result.group(1).strip()


    @classmethod
    def get_text_from_cache(cls, response):
        if response.url not in compuworks.pdf_to_text:
            reader = PdfFileReader(StringIO.StringIO(response.body))
            text = ""
            for page in reader.pages:
                text += page.extractText()
            compuworks.pdf_to_text[response.url] = text
        return compuworks.pdf_to_text[response.url]


    @classmethod
    def get_prerequisites(cls, response):
        if isinstance(response, Response):
            text = compuworks.get_text_from_cache(response)
        else:
            text = html_to_text(response)
        patterns = ["Prerequisites:(.*)Course Outline",
                    "Prerequisites:(.*)(Unit 1:|Module 1:|Course Length)",
                    "Prerequisites:(.*)Designing and Deploy"
        ]
        for p in patterns:
            result = re.search(p, text, re.I)
            if result:
                if '**' in result.group(1):
                    result = result.group(1).replace('*', '')
                    result = re.sub("To ensure your success.*:", '', result).strip().split('.')
                    return [v for v in result if v.strip()]
                else:
                    result = re.sub("Before attending[^:]*:", '', result.group(1)).strip().split('  ')
                    return [v for v in result if v.strip()]

    @classmethod
    def get_toc(cls, response):
        text = compuworks.get_text_from_cache(response)
        patterns = ["Course Outline(.*)",
                    "(Module 1.*)",
                    "Course Modules(.*)"
        ]
        for p in patterns:
            result = re.search(p, text, re.I)
            if result:
                return result.group(1)


#http://www.compuworks.com/search/coursedet/858?cd=9087





