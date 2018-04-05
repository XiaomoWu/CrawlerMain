# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from crawler.spiders import util
from crawler.settings import *
import json
import logging

class MongoPipeline(object):
    def __init__(self):

        # set logger
        self.logger = util.set_logger('pipeline', LOG_FILE_PIPELINE)

        # 建立MongoDB server
        self.db = util.set_mongo_server()

        # 建立redis server
        self.redis_server = util.set_redis_server()

    def process_item(self, item, spider):
        try:
            if "content" in item:
                content = item['content']
                # type(MMB) = dict ; type(MMBHist) = list
                if type(content) == list:
                    self.db[spider.name].insert_many(content)
                elif type(content) == dict:
                    self.db[spider.name].insert_one(content)
                else:
                    self.logger.warn('Pipeline Error, unkown item["content"] type: %s %s %s' % (spider.name, str(type(content)), item['url']))

        except Exception as ex:
            self.logger.warn('Pipeline Error (others): %s %s' % (str(ex),  str(item['content'])))

