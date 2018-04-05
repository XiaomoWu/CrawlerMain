
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from crawler.items import TestItem
from crawler.settings import *
from datetime import datetime, timedelta
import json
import time
import pymongo
import re   
import logging
import chardet
import copy

class TestSpider(Spider):
    name = "CrawlerTest"

    def start_requests(self):
       yield Request(url = "http://manmanbuy.com", callback = self.parse)

    def parse(self, response):
        top = {"a":1}
        
        docs = []
        for i in range(10):
            doc = top
            doc.update({"b":i})
            docs.append(doc)

        item = TestItem()
        item['content'] = docs
        yield item