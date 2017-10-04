
#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from crawler.items import XQCubeItem
from crawler.settings import *
from datetime import datetime
from twisted.internet.error import TimeoutError
import time
import json, re, MySQLdb, traceback, winsound
import sys
from random import *

class XQCubeRBSpider(BaseSpider):
    name='XQCubeRb'
    handle_httpstatus_list = [400,404,403,502]
    def start_requests(self):
        start_url="http://xueqiu.com/cubes/rebalancing/history.json?count=50&cube_symbol="
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select distinct cube_symbol from xq_cube_info''')
        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' CUBES to crawl')
        for i in xrange(len(rows)):
            row=rows[i]
            url=start_url+str(row[0])
            if i%200==0:
                log.msg('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),3)*100)+'%  @'+str(datetime.now()))
            yield Request(url=url,
                                   callback=self.parse)
        
    def parse(self, response):
        try:
            if response.status==200:
                m=re.search('(ZH\d{6})',response.url)
                if m:
                    symbol=m.group(1)
                body=response.body
                body = re.sub("[\s]", "", body)
                d_json=json.loads(body)
                if d_json['maxPage']:
                    max_page=d_json['maxPage']
                    for i in range(1,max_page+1):
                        url=response.url+"&page="+str(i)
                        yield Request(url=url,
                                      meta={'symbol':symbol},
                                      callback=self.parse_rb)
        except Exception, ex:
            log.msg('Exception：'+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)
            
    def parse_rb(self, response):
        try:
            body=response.body
            body = re.sub("[\s]", "", body)
            symbol=response.meta['symbol']
            d_json=json.loads(body)
            if d_json['list']:
                for i in d_json['list']:
                    item=XQCubeItem()
                    item['item_name']='xq_cube_rb'
                    item['rb_id']=i['id']
                    item['cube_id']=i['cube_id']
                    item['rb_status']=i['status']
                    item['cube_symbol']=symbol
                    item['prev_rb_id']=i['prev_bebalancing_id']
                    item['rb_category']=i['category']
                    item['exe_strategy']=i['exe_strategy']
                    item['rb_created_at']=datetime.fromtimestamp(i['created_at']/1000)
                    item['rb_updated_at']=datetime.fromtimestamp(i['updated_at']/1000)
                    item['rb_cash']=i['cash']
                    item['rb_error_code']=i['error_code']
                    item['rb_error_message']=i['error_message']
                    item['rb_error_status']=i['error_status']
                    item['rb_holdings']=i['holdings']
                    if i['rebalancing_histories']:
                        for j in i['rebalancing_histories']:
                            item['rb_id2']=j['id']
                            item['rb_stock_id']=j['stock_id']
                            item['rb_stock_name']=j['stock_name']
                            item['rb_stock_symbol']=j['stock_symbol']
                            item['rb_volume']=j['volume']
                            item['rb_price']=j['price']
                            item['rb_net_value']=j['net_value']
                            item['rb_weight']=j['weight']
                            item['rb_target_weight']=j['target_weight']
                            item['rb_prev_weight']=j['prev_weight']
                            item['rb_prev_target_weight']=j['prev_target_weight']
                            item['rb_prev_weight_adjusted']=j['prev_weight_adjusted']
                            item['rb_prev_volume']=j['prev_volume']
                            item['rb_prev_price']=j['prev_price']
                            item['rb_prev_net_value']=j['prev_net_value']
                            item['rb_proactive']=j['proactive']
                            item['lastcrawl']=datetime.now()
                            yield item
            else:
                log.msg('There is no CUBE_REBALANCE @ '+response.url+'\n          --'+str(response.body))
        except Exception, ex:
            log.msg('Exception：'+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)