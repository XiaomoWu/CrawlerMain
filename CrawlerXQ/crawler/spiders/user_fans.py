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

class XQUserFensi(Spider):
    start_at=datetime.now()
    name = 'xq_user_fans'
    logger = util.set_logger(name, LOG_FILE_USER_FENSI)
    #handle_httpstatus_list = [404]
    cube_type = 'SP'


    def start_requests(self):
        start_url="http://xueqiu.com/friendships/followers.json?size=1000&uid="

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
                self.logger.info('%s (%s / %s) %s%%' % (owner_id, str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))                #util.get_progress(now_page = i, all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)

            yield Request(url = url,
                        meta = {'user_id': owner_id},
                        callback = self.parse)

    def parse(self, response):
        try:
            if response.status == 200 and str(response.url) != "https://xueqiu.com/service/captcha":
                content = json.loads(response.body.decode('utf-8'))
                if content['maxPage']:
                    max_page = content['maxPage']

                    # First page, use parse_gz
                    for item in self.parse_gz(response = response):
                        yield item

                    # Second + page, use parse_gz
                    if max_page > 1:
                        for i in range(2, max_page + 1):
                            url = response.url + '&pageNo=' + str(i)
                            yield Request(url = url,
                                          meta = {'user_id': response.meta['user_id']},
                                          callback = self.parse_gz)

            if str(response.url) == "https://xueqiu.com/service/captcha":
                self.logger.error('CAPTURE ERROR: User ID %s' % (response.meta['user_id']))

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))

    def parse_gz(self, response):
        try:
            body = json.loads(response.body.decode('utf-8'))
            content = {}
            content['user_id'] = response.meta['user_id']
            content['count'] = body['count']
            content['anonymous_count'] = body['anonymous_count']

            users = []
            for user in body['followers']:
                users.append(user['id'])
            content['fans'] = users
            content['lastcrawl'] = int(time.time())

            item = XQItem()
            item['url'] = response.url
            item['content'] = content
            item['fp'] = request_fingerprint(response.request)
            yield item

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))
