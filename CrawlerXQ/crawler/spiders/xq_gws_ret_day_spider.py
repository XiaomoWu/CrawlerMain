#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from twisted.internet.error import TimeoutError
from crawler.items import XQGwsItem
from datetime import datetime
from crawler.settings import *
import json, re, time, winsound, MySQLdb, traceback
import sys

class XQGwsRetDaySpider(BaseSpider):
    start_at=datetime.now()
    name='XQGwsRetDay'
    handle_httpstatus_list = [400,404,403,502]
    def start_requests(self):
        self.start_url_day="http://xueqiu.com/broker/forchart/earnings.json?period=6m&exchange=all&isCapital=true"
        self.start_url_wk="http://xueqiu.com/broker/forchart/earnings.json?period=5y&exchange=all&isCapital=true"
        self.start_url_entry="http://xueqiu.com/broker/performance.json?"

        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db=SQL_DB, host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select distinct group_id, uid from xq_gws_info;''')
        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' USERS to crawl in total')

        for i in xrange(len(rows)):
            row=rows[i]
            url_day=self.start_url_day+'&group_id='+str(row[0])+'&uid='+str(row[1])
            url_wk=self.start_url_wk+'&group_id='+str(row[0])+'&uid='+str(row[1])
            url_entry=self.start_url_entry+'&group_id='+str(row[0])+'&uid='+str(row[1])

            now=datetime.now()
            if i%50==0:
                log.msg('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),4)*100)+'%   '+str(now-self.start_at))
            yield Request(url=url_day,
                                   meta={'uid':row[1], 'group_id':row[0]},
                                   callback=self.parse_day)
            yield Request(url=url_wk,
                                   meta={'uid':row[1], 'group_id':row[0]},
                                   callback=self.parse_wk)
            yield Request(url=url_entry,
                                   meta={'uid':row[1], 'group_id':row[0]},
                                   callback=self.parse_entry)

    def parse_day(self, response):
        try:
            if response.status==200:
                item=XQGwsItem()
                item['item_name']='xq_gws_ret_day'
                body=response.body
                body = re.sub("[\s]", "", body)
                d_json=json.loads(body)
                has_list=d_json[0]['list']
                if has_list:
                    for i in has_list:
                        item['uid']=response.meta['uid']
                        item['group_id']=response.meta['group_id']
                        item['day_rate']=i['value']
                        item['update_time']=datetime.fromtimestamp(i['time']/1000)
                        item['lastcrawl']=datetime.now()
                        yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url))
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))

    def parse_wk(self, response):
        try:
            if response.status==200:
                item=XQGwsItem()
                item['item_name']='xq_gws_ret_wk'
                body=response.body
                body = re.sub("[\s]", "", body)
                d_json=json.loads(body)
                has_list=d_json[0]['list']
                if has_list:
                    for i in has_list:
                        item['uid']=response.meta['uid']
                        item['group_id']=response.meta['group_id']
                        item['day_rate']=i['value']
                        item['update_time']=datetime.fromtimestamp(i['time']/1000)
                        item['lastcrawl']=datetime.now()
                        item['wk_flg']=1
                        yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url))
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))


    def parse_entry(self, response):
        try:
            if response.status==200:
                item=XQGwsItem()
                item['item_name']='xq_gws_entry'
                item['uid']=response.meta['uid']
                item['group_id']=response.meta['group_id']
                body=response.body
                body = re.sub("[\s]", "", body)
                d_json=json.loads(body)
                item['entry_date']=d_json['entry_date']
                yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url))
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url))