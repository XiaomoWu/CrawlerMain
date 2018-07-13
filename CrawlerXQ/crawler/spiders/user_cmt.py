
# -*- coding: utf-8 -*-
from crawler.spiders import util
from scrapy.spiders import Spider
from datetime import datetime
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import XQItem
from crawler.settings import *
import json
import time

import re

class XQUserStatus(Spider):
    start_at=datetime.now()
    name = 'xq_user_cmt'
    logger = util.set_logger(name, LOG_FILE_USER_STATUS)
    #handle_httpstatus_list = [404]

    def start_requests(self):
        start_url="https://xueqiu.com/v4/statuses/user_timeline.json?&count=20&user_id="

        ## get start url from MongoDB
        db = util.set_mongo_server()
        owner_ids = []
        for id in db.xq_cube_info.find({}, {'owner_id': 1, '_id': 0}):
            owner_ids.append(id['owner_id'])
        owner_ids = list(set(owner_ids))

        #owner_ids = ["1001223822"]

        # iterate each symbol
        all_page_n = len(owner_ids)
        for i in range(all_page_n):
            owner_id = owner_ids[i]
            now_page_n = i
            url = start_url+str(owner_id)

            # progress
            if i%1000==0:
                 self.logger.info('%s (%s / %s) %s%%' % (owner_id, str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))
                #util.get_progress(all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)

            yield Request(url = url,
                        meta = {'user_id': owner_id},
                        callback = self.parse)

    def parse(self, response):
        try:
            if response.status == 200 and str(response.url) != "https://xueqiu.com/service/captcha":
                body = json.loads(response.body.decode('utf-8'))
                if body['maxPage']:
                    max_page = body['maxPage']
                    page = body['page']

                    # First page
                    if page == 1:
                        content = {}
                        content['user_id'] = response.meta['user_id']
                        content['statuses'] = body['statuses']
                        content['total'] = body['total']
                        content['max_page'] = body['maxPage']
                        content['page'] = body['page']

                        item = XQItem()
                        item['content'] = content
                        yield item

                    # Second + page
                    if max_page > 1:
                        for i in range(2, max_page + 1):
                            url = response.url + '&page=' + str(i)
                            yield Request(url = url,
                                          meta = {'user_id': response.meta['user_id']},
                                          callback = self.parse_status)

            elif str(response.url) == "https://xueqiu.com/service/captcha":
                self.logger.error('CAPTURE ERROR: User ID %s' % (response.meta['user_id']))

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))

    def parse_status(self, response):
        try:
            body = json.loads(response.body.decode('utf-8'))
            content = {}
            content['user_id'] = response.meta['user_id']
            content['statuses'] = body['statuses']
            content['total'] = body['total']
            content['max_page'] = body['maxPage']
            content['page'] = body['page']

            item = XQItem()
            item['content'] = content
            item['fp'] = request_fingerprint(response.request)
            yield item

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))
