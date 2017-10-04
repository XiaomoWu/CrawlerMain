# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# -*- coding: utf-8 -*-
#from scrapy.http import Request  
#from scrapy.exceptions import DropItem
#from scrapy import signals
#from scrapy.xlib.pydispatch import dispatcher
from crawler.settings import *
from crawler.spiders import util
import json
import logging

class SinaNewsPipeline(object):
    def __init__(self):
        self.logger = util.set_logger('pipeline', LOG_FILE_PIPELINE)

        #building the MongoDB server
        self.db = util.set_mongo_server()
        
        #building the redis server
        self.redis_server = util.set_redis_server()

    def process_item(self, item, spider):
        try:
            #Justified item[spider.name] is a dict or not
            content = item['content']
            if type(content) == dict:
                self.db[spider.name].insert(content)
            elif type(content) == unicode:
                content = json.loads(content)
            else:
                self.logger.warn('Pipeline Error(unknown content type): %s %s' % (spider.name, str(type(content)),item['url']))
            
            #Only the request written into database will be queued dupefilter
            redis_key = '%s:dupefilter' % (spider.name)
            self.redis_server.sadd(redis_key, item['fp'])

        except Exception as ex:
            self.logger.warn('Pipeline Error (others): %s %s' % (str(ex), str(item['url'])))        
        



#class SinaNewsPipeline(object):
#    def __init__(self):
#        dispatcher.connect(self.spider_opened, signals.spider_opened)
#        dispatcher.connect(self.spider_closed, signals.spider_closed)
#        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_SINA_NEWS_DB, host=SQL_HOST,
#                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
#        self.cursor = self.conn.cursor()
        
#    def process_item(self, item, spider):
#        if item['item_name'] == SINA_NEWS_ITEM_NAME:
#            self.process_sina_news_item(item)
#        elif item['item_name'] == SINA_NEWS_REPLY_ITEM_NAME:
#            self.process_sina_news_reply_item(item)
#        return item
    
#    def process_sina_news_item(self, item):
#        try:
#            self.cursor.execute("""REPLACE INTO """+ item['news_table']
#                                +""" (id, stock_id, url, sector_id, title,
#                        pubdate, content, lastcrawl, info_source, reply_num, hotness, valid) 
#                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
#                        (str(item['news_id']), item['news_stock_id'].encode('utf-8'),(item['news_url']),
#                         item['news_sector_id'].encode('utf-8'), (item['news_title']).encode('utf-8'),
#                         item['news_pubdate'], item['news_content'].encode('utf-8'),
#                         item['news_lastcrawl'], item['news_info_source'].encode('utf-8'),
#                         str(item['news_replynum']), str(item['news_hotness']), str(item['news_valid'])))
#            self.conn.commit()
#        except MySQLdb.Error, e:
#            logging.ERROR("MySQL error:[SINA NEWS] %s" % item['news_url'].encode('utf-8'))
#            logging.ERROR("%s \n %s \n %s \n %s \n %s \n %s \n"
#                    % (str(item['news_id']).encode('utf-8'), item['news_sector_id'].encode('utf-8'),
#                     (item['news_title']).encode('utf-8'),item['news_content'].encode('utf-8'),
#                     item['news_pubdate'], item['news_info_source'].encode('utf-8')))
#            print "Error %d: %s" % (e.args[0], e.args[1])
#        return
    
#    def process_sina_news_reply_item(self, item):
#        try:
#            self.cursor.execute("""REPLACE INTO """+ item['reply_table']
#                                +""" (id, news_id, content, lastcrawl) 
#                        VALUES (%s, %s, %s, %s)""",
#                        (str(item['reply_id']).encode('utf-8'), item['news_id'].encode('utf-8'),
#                         (item['content']), item['reply_lastcrawl']))
#            self.conn.commit()
#        except MySQLdb.Error, e:
#            logging.ERROR("MySQL error:[SINA NEWS REPLY] %s" % item['reply_id'].encode('utf-8'))
#            print "Error %d: %s" % (e.args[0], e.args[1])
#        return
    
#    def spider_opened(self, spider):
#        logging.info("SinaNewsPipeline.spider_opened called")
        
#    def spider_closed(self, spider):
#        self.conn.commit()
#        self.cursor.close()
#        self.conn.close()
#        logging.info("SinaNewsPipeline.spider_closed called")
