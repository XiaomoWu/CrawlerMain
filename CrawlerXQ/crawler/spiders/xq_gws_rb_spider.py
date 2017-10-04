#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from twisted.internet.error import TimeoutError
from crawler.items import XQGwsItem
from datetime import datetime
from crawler.settings import *
import json, re, MySQLdb, traceback, winsound
import sys

class XQGwsRbSpider(BaseSpider):
    name='XQGwsRb'
    handle_httpstatus_list = [400,404,403,502]
    
    def __init__(self):
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                          db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select uid, group_id, gws_id from xq_gws_info''')
        rows=self.cursor.fetchall()
        start_url="http://xueqiu.com/broker/transaction/list.json?size=500"
        self.urls=[]
        self.uids=[]
        self.gws_ids=[]
        for row in rows:
            uid=str(row[0])
            gws_id=str(row[1])
            url=start_url+'&uid='+uid+'&group_id='+gws_id
            self.uids.append(uid)
            self.gws_ids.append(gws_id)
            self.urls.append(url)
    
    def start_requests(self):
        for i in xrange(len(self.urls)):
            yield Request(url=self.urls[i],
                                   meta={'uid':self.uids[i],
                                               'gws_id':self.gws_ids[i]},
                                   callback=self.parse)
        
    def parse(self, response):
        try:
            if response.status==200:
                item=XQGwsItem()
                item['item_name']='xq_gws_rb'
                body=response.body
                d_json=json.loads(body)
                if d_json:
                    for i in d_json:
                        item['uid']=response.meta['uid']
                        item['gws_id']=response.meta['gws_id']
                        item['stk_symbol']=i['symbol']
                        item['stk_name']=i['name']
                        for j in i['list']:
                            item['rb_time']=datetime.strptime(j['time'],'%Y-%m-%d %H:%M:%S')
                            desc=j['desc'].encode('utf8')
                            m=re.search('([\d\.]+)([^\d\.]+)([\d\.]+)股',desc)
                            if m:
                                if m.group(2)=='买入': 
                                    item['buy_sell']=1
                                elif m.group(2)=='卖出': 
                                    item['buy_sell']=-1
                                item['rb_price']=m.group(1)
                                item['rb_amount']=m.group(3)
                                item['lastcrawl']=datetime.now()
                                yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url)+'\n          --'+str(response.body))
#             winsound.Beep(900,999999999)
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)