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



class GubaReplyUserInfo(Spider):
    start_at = datetime.now()
    name = 'guba_reply_user_info'
    logger = util.set_logger(name, LOG_FILE_GUBA_REPLY_USER_INFO)

    def start_requests(self):
        db = util.set_mongo_server()
        reply_author_urls = []    
        #replys = list(db.CrawlerGuba.aggregate([{'$project':{'_id': 0, 'reply': 1}} ,{'$unwind': '$reply'}]))
        for url in db.guba_stock_posts.find({}, {'reply.reply_author_url': 1, '_id': 0}):
            if 'reply' in url:
                for e in url['reply']:
                    if 'reply_author_url' in e: 
                        reply_author_urls.append(e['reply_author_url'])
        reply_author_urls = list(set(reply_author_urls))
        all_page_n = len(reply_author_urls)
        for i in range(all_page_n):
            reply_author_url = reply_author_urls[i]
            url = reply_author_url

            if i%1000==0:
                    self.logger.info('%s / %s' % (str(i), str(all_page_n)))
                    util.get_progress(all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)
            
            yield Request(url = url, meta = {'reply_author_url': reply_author_url}, callback = self.parse)

    def parse(self, response):
        try:
            if response.status==200:
                hxs = Selector(response)
                reply_author_url = response.meta['reply_author_url']
                item = GubaItem()
                item['content'] = {}
                reply_author_name = hxs.xpath('//div[@class="taname"]/text()').extract()[0]
                item['content']['reply_author_name'] = reply_author_name.strip()
                sign_up_time = hxs.xpath('//div[@id="influence"]').extract()[0]
                sign_up_time = re.search('999;">\((.+)\)<\/span', sign_up_time).group(1).strip()
                sign_up_time = datetime.strptime(sign_up_time, "%Y-%m-%d")
                item['content']['sign_up_time'] = sign_up_time
                item['content']['reply_author_url'] = reply_author_url
                yield item

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))