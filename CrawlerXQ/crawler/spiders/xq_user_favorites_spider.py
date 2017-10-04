#coding=utf-8
from scrapy import log
from scrapy import signals
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import XQCmtItem
from datetime import datetime
from crawler.settings import *
from twisted.internet.error import TimeoutError
import time
import json, re, MySQLdb, traceback, winsound
import sys
from random import *

class XQUserFavorites(BaseSpider):
    start_at=datetime.now()
    name='XQUserFavorites'
    handle_httpstatus_list = [400,404,403,502]
    def start_requests(self):
        self.start_url="http://xueqiu.com/favorites.json?&size=200&userid="
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()

        # crawl followers of distance
        distance='g_a_3'
        self.cursor.execute('''select distinct uid from xq_user_favorites
                                        where distance='g_a_2' ''')
        rows=self.cursor.fetchall()
        logger.info('There are '+str(len(rows))+' USERS to crawl')

        for i in xrange(len(rows)):
            row=rows[i]
            # if if_commit=True, require Mysql to commit
            if_commit=False
            if i%20==0:
                now=datetime.now()

                logger.info('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),3)*100)+'%  '+str(now-self.start_at))
                if_commit=True
            url=self.start_url+row[0]
            yield Request(url=url,
                                   meta={'uid':row[0], 'if_commit': if_commit,
                                              'distance': distance},
                                   callback=self.parse)
            
    def parse(self, response):
        try:
            if response.status==200:
                body=response.body
                body=re.sub('[\s]',' ',body)
                d_json=json.loads(body)
                if d_json['maxPage']:
                    max_page=d_json['maxPage']
                    for i in range(1,max_page+1):
                        url=self.start_url+response.meta['uid']+"&page="+str(i)
                        yield Request(url=url,
                                      meta={'uid':response.meta['uid'],
                                            'if_commit': response.meta['if_commit'],
                                            'distance':response.meta['distance']},
                                      callback=self.parse_fv)
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url))
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))
            winsound.Beep(900,5)

    def parse_fv(self, response):
        try:
            item=XQCmtItem()
            item['if_commit']=response.meta['if_commit']
            item['distance']=response.meta['distance']
            item['item_name']='xq_user_favorites'
            user_info=response.body
            user_info=re.sub('[\s]',' ',user_info)
            d_json=json.loads(user_info)
            if d_json['list']:
                for i in d_json['list']:
                    item['fv_uid']=response.meta['uid']
                    item['cmt_id']=i['id']
                    item['uid']=i['user_id']
                    item['cmt_title']=i['title']
                    item['lastcrawl']=datetime.now()
                    yield item
            else:
                log.msg('There is no FAVORITES @ '+response.url)
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))
            winsound.Beep(900,5)

