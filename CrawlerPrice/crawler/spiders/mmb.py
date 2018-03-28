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
    name = 'CrawlerMMB'
    logger = util.set_logger(name, LOG_FILE_MMB)
    #handle_httpstatus_list = [404]
    #website_possible_httpstatus_list = [404]

    def start_requests(self): 
        start_url = 'http://home.manmanbuy.com/bijia.aspx'
        yield Request(url = start_url, callback = self.parse)

    # parse 用来抓首页入口
    # sample url：http://home.manmanbuy.com/bijia.aspx
    def parse(self, response):
        sclass_block = response.xpath('//div[@class="sclassBlock"]')

        # 每个 ele 相当于一个 cat1
        for ele in sclass_block:
            item = PriceItem()
            item['content'] = {}
            # 例子：
            # cat1：大家电；cat2：冰箱
            # cat1 约113个；cat2 约 700 个；
            cat1_name = ele.xpath('div[@class="sclassLeft"]/text()').extract()
            # 有些类别有 cat1，极少数没有cat1，而是从 cat2 开始。对这类 cat2，为其 cat1 赋值为 ""
            if cat1_name:
                cat1_name = cat1_name[0]
            else:
                cat1_name = None
            item['content']['cat1_name'] = cat1_name

            # 每个 cat2 相当于一个 cat2
            for node in ele.xpath('div[@class="sclassRight"]/a'):
                cat2_name = node.xpath('text()').extract()
                if cat2_name:
                    cat2_name = cat2_name[0] 
                else:
                    cat2_name = node.xpath('font/text()').extract()[0] 
                item['content']['cat2_name'] = cat2_name
                
                cat2_url = node.xpath('@href').extract()[0]
                item['content']['cat2_url'] = cat2_url

                print(cat2_url)

                #yield Request(url = cat2_url, meta = {'item':item}, callback = self.parse_item)


    def parse_item(self, response):
        print(response.url)
        pass
