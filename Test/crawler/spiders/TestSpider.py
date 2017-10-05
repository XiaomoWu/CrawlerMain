
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
        url = "http://news.sina.com.cn/c/2010-09-30/105521202249.shtml"

        yield Request(url = url, callback = self.parse)
    
    def parse(self, response):
        filter_body = response.body.decode('gbk')
        filter_body = re.sub('<[A-Z]+[0-9]*[^>]*>|</[A-Z]+[^>]*>', '', filter_body)
        response = response.replace(body = filter_body)
        hxs =Selector(response)

        m = re.search('channel:"(.+?)",newsid:"(.+?)"', filter_body)
        print(m.group(1))
        print(m.group(2))

        #cid = hxs.xpath("//head/script[@type='text/javascript']").extract()
        #print(cid)
        
    
