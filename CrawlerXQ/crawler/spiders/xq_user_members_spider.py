#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from twisted.internet.error import TimeoutError
from scrapy.selector import Selector
from crawler.items import XQUserItem
from datetime import datetime
from crawler.settings import *
import time
import json, re, MySQLdb, traceback, winsound
import sys
from random import *

class XQUserMembers(BaseSpider):
    start_at=datetime.now()
    name='XQUserMembers'
    handle_httpstatus_list = [400,404,403,502]
    def start_requests(self):
        self.start_url="http://xueqiu.com/friendships/groups/members.json?&gid=0&uid="
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()

        # crawl followers of g_f_0
        distance='cube_owner'
        self.cursor.execute('''select distinct owner_id from xq_cube_info''')
        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' USERS to crawl')
        for i in xrange(len(rows)):
            row=rows[i]
            # if if_commit=True, require Mysql to commit
            if_commit=False
            if i%20==0:
                now=datetime.now()
                log.msg('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),3)*100)+'%  '+str(now-self.start_at))
                if_commit=True
            url=self.start_url+row[0]
            yield Request(url=url,
                                   meta={'uid':row[0], 'if_commit': if_commit,
                                              'distance':distance},
                                   callback=self.parse)
            
    def parse(self, response):
        try:
            if response.status==200:
                body=response.body
                d_json=json.loads(body)
                if d_json['maxPage']:
                    max_page=d_json['maxPage']
                    for i in range(1,max_page+1):
                        url=self.start_url+response.meta['uid']+"&page="+str(i)
                        yield Request(url=url,
                                      meta={'uid':response.meta['uid'],
                                            'if_commit': response.meta['if_commit'],
                                            'distance': response.meta['distance']},
                                      callback=self.parse_mb)
                return
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url))
#             winsound.Beep(900,999999999)
        except TimeoutError, te:
            log.msg('TimeoutError: '+str(te)+' @ '+str(response.url))
            winsound.Beep(900,999999999)
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))
            winsound.Beep(900,999999999) 

    def parse_mb(self, response):
        try:
            item=XQUserItem()
            item['if_commit']=response.meta['if_commit']
            item['distance']=response.meta['distance']
            item['item_name']='xq_user_members'
            user_info=response.body
            d_json=json.loads(user_info)
            if d_json['users']:
                for i in d_json['users']:
                    item['distance']=response.meta['distance']
                    item['mb_uid']=response.meta['uid']
                    item['uid']=i['id']
                    item['screen_name']=i['screen_name']
                    item['lastcrawl']=datetime.now()
                    yield item
            else:
                log.msg('There is no MEMBERS @ '+response.url)
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))
            winsound.Beep(900,999999999)
