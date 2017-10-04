#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import XQStkItem
from datetime import datetime
from crawler.settings import *
import json
import re
import sys

class XQStkInfoSpider(BaseSpider):
    name = 'XQStkInfoSpider'
    def __set_default_item_to_none(self):
        item = XQStkItem()
        item['stk_symbol'] = None
        item['stk_id'] = None
        item['stk_name'] = None
        item['stk_price'] = None
        return item
    
    def start_requests(self):
        self.start_url = "http://xueqiu.com/stock/cata/stocklist.json?size=100&order=asc&orderby=code&type=11"
        url = self.start_url + "&page=1"
        yield Request(url=url,
                               callback=self.parse)
    def parse(self, response):
        body = response.body.strip()
        body = re.sub('[\v\f]','',body)
        d_json = json.loads(body)
        count = d_json['count']['count']
        max_page = int(count / 100) + 3
        #max_page = 4
        for i in range(1, max_page):
            url = self.start_url + "&page=" + str(i)
            yield Request(url=url,
                                   callback=self.parse_stk_info)
            
    def parse_stk_info(self, response):
        item = self.__set_default_item_to_none()
        if response.status != 404:
            item['item_name'] = 'xq_stk_info'
            body = response.body.strip()
            body = re.sub('[\v\f]','',body)
            d_json = json.loads(body)
            stocks = d_json['stocks']
            if stocks:
                for s in stocks:
                    item['stk_symbol'] = s['symbol']
                    item['stk_id'] = s['code']
                    item['stk_name'] = s['name']
                    item['stk_price'] = s['current']
                    item['lastcrawl'] = datetime.now()
                    yield item
            else:
                return