# -*- coding: utf-8 -*-
from crawler.spiders import util
from scrapy.spiders import Spider
from datetime import datetime
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import XQItem
from crawler.settings import *
import json
import re


class XQCubeRBSpider(Spider):
    start_at=datetime.now()
    name = 'xq_cube_rb'
    logger = util.set_logger(name, LOG_FILE_CUBE_RB)
    #handle_httpstatus_list = [400]

    cube_type = 'ZH'

    def start_requests(self):
        zh_url = 'https://xueqiu.com/cubes/rebalancing/history.json?count=50&cube_symbol='
        sp_url = 'https://xueqiu.com/service/tc/snowx/PAMID/cubes/rebalancing/history?count=20&cube_symbol='


        # get start url from MongoDB
        db = util.set_mongo_server()
        symbols = []

        for s in db.xq_cube_info.find({'cube_type':self.cube_type}, {'symbol': 1, '_id': 0}):
            symbols.append(s['symbol'])
        symbols = list(set(symbols))

        # iterate each symbol
        all_page_n = len(symbols)
        for i in range(all_page_n):
            symbol = symbols[i].strip()
            now_page_n = i

            if self.cube_type == 'SP':
                url = sp_url + symbol
            elif self.cube_type == 'ZH':
                url = zh_url + symbol

            # 进度条
            if i%500==0:
                self.logger.info('%s (%s / %s) %s%%' % (symbol, str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))
                #util.get_progress(now_page = i, all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)

            yield Request(url = url,
                      callback = self.parse, meta = {'cube_type':self.cube_type, 'symbol':symbol})

        #yield Request(url = "https://xueqiu.com/service/tc/snowx/PAMID/cubes/rebalancing/history?count=20&cube_symbol=SP1013930",
        #              callback = self.parse, meta = {'cube_type':self.cube_type, 'symbol':symbol})


    def parse(self, response):
        try:
            #print(response.url)
            if response.status == 200 and str(response.url) != "https://xueqiu.com/service/captcha":
                body = re.sub('[\s]', '', response.body.decode('utf-8'))
                body = json.loads(body)

                if body['maxPage']:
                    max_page = body['maxPage']
                    
                    # First page, use parse_rb
                    for item in self.parse_rb(response):
                        yield item

                    # Second + page, parse_rb
                    if max_page > 1:
                        for i in range(2, max_page + 1):
                            url = response.url + '&page=' + str(i)
                            yield Request(url = url,
                                          meta = response.meta,
                                          callback = self.parse_rb)
            elif str(response.url) == "https://xueqiu.com/service/captcha":
                self.logger.error('CAPTURE ERROR: %s' % (response.meta['symbol']))

        except Exception as ex:
            self.logger.error('Parse Exception: %s %s' % (str(ex), response.url))
            self.logger.info(str(response.body))

    def parse_rb(self, response):
        try:
            body = re.sub('[\s]', '', response.body.decode('utf-8'))
            body = json.loads(body)
            if body['list']:
                for i in body['list']:
                    item = XQItem()
                    # i is of type dict
                    i['cube_symbol'] = response.meta['symbol']
                    i['cube_type'] = response.meta['cube_type']
                    item['url'] = response.url
                    item['content'] = i
                    item['fp'] = request_fingerprint(response.request)
                    yield item
        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))
            self.logger.info(body)


