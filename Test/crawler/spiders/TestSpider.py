
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
        url = "http://news.sina.com.cn/c/2010-05-11/031117489938s.shtml"

        yield Request(url = url, callback = self.parse)
    
    def parse(self, response):
        filter_body = response.body.decode('gbk')
        filter_body = re.sub('<[A-Z]+[0-9]*[^>]*>|</[A-Z]+[^>]*>', '', filter_body)         
        filter_body = re.sub("[\s]", "", filter_body)

        response = response.replace(body = filter_body)
        hxs =Selector(response)

        cid = hxs.xpath('//head/*[@name="comment"]/@content').extract()
        if cid:
            # 新网页主要是这种格式
            d = cid[0].split(":")
            cmt_id = {"channel":d[0], "comment_id":d[1]}
            print("cmt_id 1")
        else:
            # 旧网页主要是这种格式
            filter_body = re.sub("[\s]", "", filter_body)
            m = re.search('''channel:["'](.+?)["'],.*newsid:["'](.+?)['"]''', filter_body)
            if m:
                cmt_id = {"channel":m.group(1), "comment_id":m.group(2)}
                print("cmt_id 2")
            else:
                # 个别特例
                m = re.search('channel=(.+?)&newsid', filter_body)
                if m:
                    cmt_id = {"channel":m.group(1), "comment_id":item['content']['news_id']}
                    print("cmt_id 3")
                else:
                    print("no cmt_id")
        print(m)

        #cid = hxs.xpath("//head/script[@type='text/javascript']").extract()
        #print(cid)
        
    
