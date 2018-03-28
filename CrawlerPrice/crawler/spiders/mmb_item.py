
from scrapy.spiders import Spider
from crawler.spiders import util
from scrapy.selector import Selector
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import PriceItem
from crawler.settings import *
from datetime import datetime, timedelta
import json
import time
import pymongo
import re   
import logging
import copy


class MMBSpider(Spider):
    name = 'CrawlerMMBItem'
    logger = util.set_logger(name, LOG_FILE_MMB)
    #handle_httpstatus_list = [404]
    #website_possible_httpstatus_list = [404]

    def start_requests(self): 
        start_url = 'http://www.manmanbuy.com/list_57.aspx'
        yield Request(url = start_url, callback = self.parse)

    def parse(self, response):
        print(response.url)