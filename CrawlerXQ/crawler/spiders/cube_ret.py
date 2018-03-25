# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from crawler.spiders import util
from scrapy.spiders import Spider
from datetime import datetime
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import XQItem
from crawler.settings import *
import pymongo
import logging
import json
import re



class XQCubeRetSpider(RedisSpider):

    name = 'xq_cube_ret_updt'
    start_at=datetime.now()
    logger = util.set_logger(name, LOG_FILE_CUBE_RET)
    #handle_httpstatus_list = []
    website_possible_httpstatus_list = [301,302,404]
    handle_httpstatus_list = [301, 302]
    cube_type = 'ZH'

    def start_requests(self):
        zh_url = 'https://xueqiu.com/cubes/nav_daily/all.json?cube_symbol='
        sp_url = 'https://xueqiu.com/service/tc/snowx/PAMID/cubes/nav_daily/all?cube_symbol='

        # get start url from MongoDB
        db = util.set_mongo_server()
        
        symbols = []
        for s in db.xq_cube_info_updt.find({'cube_type':self.cube_type}, {'symbol': 1, '_id': 0}):
            symbols.append(s['symbol'])
        symbols = list(set(symbols))

        #for s in db.fail.find({}, {'cube_symbol': 1, '_id': 0}):
        #    symbols.append(s['cube_symbol'])
        #symbols = list(set(symbols))
        #print(len(symbols))

        # iterate each symbol
        all_page_n = len(symbols)
        for i in range(all_page_n):
            now_page_n = i
            symbol = symbols[i].strip()
            if self.cube_type == 'SP':
                url = sp_url + symbol
            elif self.cube_type == 'ZH':
                url = zh_url + symbol

            # 进度条
            if i%1000==0:
                 self.logger.info('%s (%s / %s) %s%%' % (symbol, str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))
                #util.get_progress(now_page = i, all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)

            yield Request(url = url,
                    meta = {'symbol': symbol, 
                    'cube_type':self.cube_type},
                        callback = self.parse)

    def parse(self, response):
        try:
            if response.status == 200 and str(response.url) != "https://xueqiu.com/service/captcha":
                item = XQItem()
                body = re.sub('[\s]', '', response.body.decode('utf-8'))
                body = json.loads(body)
                
                if body[0]:
                    for content in body[0]['list']:
                        content['cube_symbol'] = response.meta['symbol']
                        content['cube_type'] = response.meta['cube_type']
                        item['url'] = response.url
                        item['content'] = content
                        item['fp'] = request_fingerprint(response.request)
                        yield item

            if response.status == 302 or str(response.url) == "https://xueqiu.com/service/captcha":
                self.logger.error('CAPTURE ERROR: %s' % (response.meta['symbol']))
                oldmeta = response.request.meta
                oldmeta["change_proxy"] = True
                yield Request(url=response.request.url,
                              meta=oldmeta,
                              callback = self.parse)
        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))

