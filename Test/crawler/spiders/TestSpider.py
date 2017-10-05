
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from crawler.items import TestItem
from crawler.settings import *
from datetime import datetime, timedelta
import json
import time
import demjson
import pymongo
import re   
import logging
import chardet

class SinaNewsSpider(Spider):
    name = "CrawlerTest"

    def start_requests(self):
        url = "http://finance.sina.com.cn/money/forex/20140711/134819678307.shtml"

        yield Request(url = url, callback = self.parse)
    
    def parse(self, response):
        filter_body = response.body.decode("iso-8859-1")
        body = response.body
        print(filter_body)
        pass
        
    
