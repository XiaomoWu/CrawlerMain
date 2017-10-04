# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# -*- coding: utf-8 -*-
from scrapy.http import Request  
from scrapy.exceptions import DropItem
from scrapy import signals
from scrapy import log
from scrapy.xlib.pydispatch import dispatcher
from crawler.settings import *
import MySQLdb
class GubaBBSPipeline(object):
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
        self.cursor = self.conn.cursor()
        
    def process_item(self, item, spider):
        if item['item_name'] == GUBABBS_POST_ITEM_NAME:
            self.process_post_item(item)
        elif item['item_name'] == GUBABBS_REPLY_ITEM_NAME:
            self.process_reply_item(item)
        elif item['item_name'] == GUBABBS_STOCK_ITEM_NAME:
            self.process_stock_item(item)
        elif item['item_name'] == FUNDBBS_REPLY_LIST_ITEM_NAME:
            for i in item['item_list']:
                self.process_reply_item(i)
        return item
    
    def process_post_item(self, item):
        try:
            if item['sql_update'] == ITEM_SQL_INSERT:
                self.cursor.execute("""INSERT INTO post (id, stock_id, url, view, replynum, title,
                    author, authorid, pubdate, content, lastcrawl, valid, activedate, sticky, official) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['post_id'].encode('utf-8'), item['post_stock_id'].encode('utf-8'),
                     item['post_url'].encode('utf-8'), str(item['post_view']),
                     str(item['post_replynum']), item['post_title'].encode('utf-8'),
                     item['post_author'].encode('utf-8'), item['post_authorid'].encode('utf-8'),
                     item['post_pubdate'].encode('utf-8'), item['post_content'].encode('utf-8'),
                     item['post_lastcrawl'], str(item['post_valid']),
                     item['post_activedate'].encode('utf-8'), str(item['sticky']), str(item['official'])))
            elif item['sql_update'] == ITEM_SQL_UPDATE:
                self.cursor.execute("""UPDATE post SET url=%s, stock_id=%s, view=%s, replynum=%s, title=%s,
                    author=%s, authorid=%s, pubdate=%s, content=%s, lastcrawl=%s,
                    valid=%s, activedate=%s, sticky=%s, official=%s WHERE id=%s""",
                    (item['post_url'].encode('utf-8'), item['post_stock_id'].encode('utf-8'),
                     str(item['post_view']),str(item['post_replynum']), item['post_title'].encode('utf-8'),
                     item['post_author'].encode('utf-8'), item['post_authorid'].encode('utf-8'),
                     item['post_pubdate'].encode('utf-8'), item['post_content'].encode('utf-8'),
                     item['post_lastcrawl'], str(item['post_valid']), item['post_activedate'].encode('utf-8'),
                     str(item['sticky']), str(item['official']), item['post_id'].encode('utf-8')))
            self.conn.commit()
        except MySQLdb.Error, e:
            log.msg("MySQL error:[POST]%s" % item['post_url'].encode('utf-8'), level=log.ERROR)
            log.msg("%s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s"
                    % (item['post_id'].encode('utf-8'), item['post_stock_id'].encode('utf-8'),
                     item['post_url'].encode('utf-8'), str(item['post_view']),
                     str(item['post_replynum']), item['post_title'].encode('utf-8'),
                     item['post_author'].encode('utf-8'), item['post_authorid'].encode('utf-8'),
                     item['post_pubdate'].encode('utf-8'), item['post_content'].encode('utf-8'),
                     item['post_lastcrawl'], str(item['post_valid']),
                     item['post_activedate'].encode('utf-8'), str(item['sticky']), str(item['official'])),
                    level=log.ERROR)
            print "Error %d: %s" % (e.args[0], e.args[1])
            
    def process_reply_item(self, item):
        try:
            if item['sql_update'] == ITEM_SQL_INSERT:
                self.cursor.execute("""INSERT IGNORE INTO reply (id, post_id, floor, replyer_id, replyer,
                    content, reply_date, quote, lastcrawl, web_field) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (str(item['reply_id']), item['reply_post_id'].encode('utf-8'),str(item['reply_floor']),
                     item['replyer_id'].encode('utf-8'), item['replyer_name'].encode('utf-8'),
                     item['reply_content'].encode('utf-8'), item['reply_date'].encode('utf-8'),
                     item['reply_quote'], str(item['reply_lastcrawl']), item['web_field'].encode('utf-8')))
                self.conn.commit()
        except MySQLdb.Error, e:
            log.msg("MySQL error:[REPLY] in post %s, floor %s"
                    % (item['reply_post_id'].encode('utf-8'), str(item['reply_floor'])), level=log.ERROR)
            log.msg("%s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s"
                    % (str(item['reply_id']), item['web_field'].encode('utf-8'),
                       item['reply_post_id'].encode('utf-8'),str(item['reply_floor']),
                     item['replyer_id'].encode('utf-8'), item['replyer_name'].encode('utf-8'),
                     item['reply_content'].encode('utf-8'), item['reply_date'].encode('utf-8'),
                     item['reply_quote'], str(item['reply_lastcrawl'])), level=log.ERROR)
            print "Error %d: %s" % (e.args[0], e.args[1])
            
    def process_stock_item(self, item):
        try:
            if item['sql_update'] == ITEM_SQL_INSERT:
                self.cursor.execute("""INSERT INTO stock (id, name, url, web_field, click,
                    post, tag, lastcrawl, date_insert) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (str(item['stock_id']).encode('utf-8'), item['stock_name'].encode('utf-8'),
                     (item['stock_url']).encode('utf-8'),
                     str(item['web_field']), str(item['stock_click']),
                     str(item['stock_post']), item['stock_tag'].encode('utf-8'),
                     item['stock_lastcrawl'], item['date_insert'].encode('utf-8')))
            elif item['sql_update'] == ITEM_SQL_UPDATE:
                self.cursor.execute("""UPDATE stock SET id=%s, name=%s, url=%s,
                    web_field=%s, click=%s, post=%s, tag=%s, lastcrawl=%s
                    WHERE id=%s""",
                    (str(item['stock_id']).encode('utf-8'), item['stock_name'].encode('utf-8'),
                     (item['stock_url']).encode('utf-8'),
                     str(item['web_field']), str(item['stock_click']),
                     str(item['stock_post']), item['stock_tag'].encode('utf-8'),
                     item['stock_lastcrawl'], str(item['stock_id']).encode('utf-8')))
            self.conn.commit()
        except MySQLdb.Error, e:
            log.msg("MySQL error:[STOCK]%s" % item['stock_url'].encode('utf-8'), level=log.ERROR)
            log.msg("%s \n %s \n %s \n %s \n %s \n %s \n %s \n %s \n %s"
                    % (str(item['stock_id']).encode('utf-8'), item['stock_name'].encode('utf-8'),
                     (item['stock_url']).encode('utf-8'),
                     str(item['web_field']), str(item['stock_click']),
                     str(item['stock_post']), item['stock_tag'].encode('utf-8'),
                     item['stock_lastcrawl'], item['date_insert'].encode('utf-8')), level=log.ERROR)
            print "Error %d: %s" % (e.args[0], e.args[1])
            
    def spider_opened(self, spider):
        log.msg("GubaBBSPipeline.spider_opened called", level=log.INFO)
        
    def spider_closed(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        log.msg("GubaBBSPipeline.spider_closed called", level=log.INFO)

class SinaNewsPipeline(object):
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_SINA_NEWS_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
        self.cursor = self.conn.cursor()
        
    def process_item(self, item, spider):
        if item['item_name'] == SINA_NEWS_ITEM_NAME:
            self.process_sina_news_item(item)
        elif item['item_name'] == SINA_NEWS_REPLY_ITEM_NAME:
            self.process_sina_news_reply_item(item)
        return item
    
    def process_sina_news_item(self, item):
        try:
            self.cursor.execute("""REPLACE INTO """+ item['news_table']
                                +""" (id, stock_id, url, sector_id, title,
                        pubdate, content, lastcrawl, info_source, reply_num, hotness, valid) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (str(item['news_id']), item['news_stock_id'].encode('utf-8'),(item['news_url']),
                         item['news_sector_id'].encode('utf-8'), (item['news_title']).encode('utf-8'),
                         item['news_pubdate'], item['news_content'].encode('utf-8'),
                         item['news_lastcrawl'], item['news_info_source'].encode('utf-8'),
                         str(item['news_replynum']), str(item['news_hotness']), str(item['news_valid'])))
            self.conn.commit()
        except MySQLdb.Error, e:
            log.msg("MySQL error:[SINA NEWS] %s" % item['news_url'].encode('utf-8'), level=log.ERROR)
            log.msg("%s \n %s \n %s \n %s \n %s \n %s \n"
                    % (str(item['news_id']).encode('utf-8'), item['news_sector_id'].encode('utf-8'),
                     (item['news_title']).encode('utf-8'),item['news_content'].encode('utf-8'),
                     item['news_pubdate'], item['news_info_source'].encode('utf-8')), level=log.ERROR)
            print "Error %d: %s" % (e.args[0], e.args[1])
        return
    
    def process_sina_news_reply_item(self, item):
        try:
            self.cursor.execute("""REPLACE INTO """+ item['reply_table']
                                +""" (id, news_id, content, lastcrawl) 
                        VALUES (%s, %s, %s, %s)""",
                        (str(item['reply_id']).encode('utf-8'), item['news_id'].encode('utf-8'),
                         (item['content']), item['reply_lastcrawl']))
            self.conn.commit()
        except MySQLdb.Error, e:
            log.msg("MySQL error:[SINA NEWS REPLY] %s" % item['reply_id'].encode('utf-8'), level=log.ERROR)
            print "Error %d: %s" % (e.args[0], e.args[1])
        return
    
    def spider_opened(self, spider):
        log.msg("SinaNewsPipeline.spider_opened called", level=log.INFO)
        
    def spider_closed(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        log.msg("SinaNewsPipeline.spider_closed called", level=log.INFO)
