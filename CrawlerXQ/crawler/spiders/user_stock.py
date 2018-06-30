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

class XQUserInfo(Spider):
    start_at=datetime.now()
    name = 'xq_user_stock'
    logger = util.set_logger(name, LOG_FILE_USER_STOCK)
    #handle_httpstatus_list = [404]
    cube_type = 'ZH'

    def start_requests(self):
        start_url="https://xueqiu.com/stock/portfolio/stocks.json?size=5000&tuid="

        # get start url from MongoDB
        db = util.set_mongo_server()
        owner_ids = []
        for id in db.xq_cube_info.find({'cube_type':self.cube_type}, {'owner_id': 1, '_id': 0}):
            owner_ids.append(id['owner_id'])
        owner_ids = list(set(owner_ids))

        # iterate each symbol
        all_page_n = len(owner_ids)
        for i in range(all_page_n):
            now_page_n = i
            owner_id = owner_ids[i]
            url = start_url+str(owner_id)

            # progress
            if i%1000==0:
                self.logger.info('%s (%s / %s) %s%%' % (owner_id, str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))                   #util.get_progress(now_page = i, all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)

            yield Request(url = url,
                        meta = {'user_id': owner_id},
                        callback = self.parse)

    def parse(self, response):
        try:
            if response.status == 200 and str(response.url) != "https://xueqiu.com/service/captcha":
                content = json.loads(response.body.decode('utf-8'))
                item = XQItem()
                content['user_id'] = response.meta['user_id']
                item['url'] = response.url
                item['content'] = content
                item['fp'] = request_fingerprint(response.request)
                yield item

            if str(response.url) == "https://xueqiu.com/service/captcha":
                self.logger.error('CAPTURE ERROR: User ID %s' % (response.meta['owner_id']))

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))
