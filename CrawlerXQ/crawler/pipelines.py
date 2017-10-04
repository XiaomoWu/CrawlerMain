# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from crawler.spiders import util
from crawler.settings import *
import json
import logging



class CrawlerPipeline(object):
    pass

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
            # 如果item又有content又有fp，正常处理
            if "content" in item and "fp" in item:
                #判断 item['content'] 是否是 dict 
                content = item['content']
                if type(content) == dict:
                    self.db[spider.name].insert(content)
                elif type(content) == unicode:
                    content = json.loads(content)
                    self.db[spider.name].insert(content)
                else:
                    self.logger.warn('Pipeline Error (unknown content type): %s %s' % (spider.name, str(type(content)), item['url']))
                
                #return item
            
                # 只有成功写入数据库的request才会被加入dupefilter
                redis_key = '%s:dupefilter' % (spider.name)
                self.redis_server.sadd(redis_key, item['fp'])
                #print("write sp: normal")

            # 如果item没有content但是有fp，说明是cube_info中的404页面，这些也要写入redis，避免下次再进行抓取
            elif "content" not in item and "fp" in item:
                redis_key = '%s:dupefilter' % (spider.name)
                self.redis_server.sadd(redis_key, item['fp'])                

        except Exception as ex:
            self.logger.warn('Pipeline Error (others): %s %s' % (str(ex),  str(item['url'])))

        




