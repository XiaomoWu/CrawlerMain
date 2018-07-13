# -*- coding: utf-8 -*-
from crawler.spiders import util
from scrapy.spiders import Spider
from scrapy.selector import Selector
from datetime import datetime
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import GubaItem
from crawler.settings import *
import pymongo
import logging
import json
import re

class GubaUserInfo(Spider):
    start_at = datetime.now()
    name = 'guba_user_info'
    logger = util.set_logger(name, LOG_FILE_GUBA_USER_INFO)

    def start_requests(self):
        db = util.set_mongo_server()
        author_urls = []
        for url in db.guba_stock_posts.find({},{'author_url': 1, '_id': 0}):
            if 'author_url' in url:
                author_urls.append(url['author_url'])
        author_urls = list(set(author_urls))
        all_page_n = len(author_urls)
        for i in range(all_page_n):
            author_url = author_urls[i]
            url = author_url

            if i%1000==0:
                self.logger.info('%s / %s' % (str(i), str(all_page_n)))
                util.get_progress(all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)
    
            yield Request(url = url, meta = {'author_url': author_url}, callback = self.parse)
            
    def parse(self, response):
        try:
            if response.status==200:
                hxs = Selector(response)
                author_url = response.meta['author_url']
                item = GubaItem()
                item['content'] = {}
                author_name = hxs.xpath('//div[@class="taname"]/text()').extract()[0]
                item['content']['author_name'] = author_name.strip()
                sign_up_time = hxs.xpath('//div[@id="influence"]').extract()[0]
                sign_up_time = re.search('999;">\((.+)\)<\/span', sign_up_time).group(1).strip()
                sign_up_time = datetime.strptime(sign_up_time, "%Y-%m-%d")
                item['content']['sign_up_time'] = sign_up_time
                item['content']['author_url'] = author_url
                yield item

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))