#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from scrapy.selector import Selector
from twisted.internet.error import TimeoutError
from crawler.items import XQUserItem
from datetime import datetime
from crawler.settings import *
import json, re, MySQLdb, traceback, winsound
import sys

class XQUserStocksSpider(BaseSpider):
    start_at=datetime.now()
    name='XQUserStocks'
    handle_httpstatus_list = [400,404,403,502]

    def start_requests(self):
        start_url="http://xueqiu.com/stock/portfolio/stocks.json?size=5000&tuid="
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select distinct mb.uid from xq_user_followers as mb
                                        where mb.distance in ('g_f_2') 
                                        and mb.uid not in (select stk.uid from xq_user_stocks as stk)''')
        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' USERS to crawl')
        for i in xrange(len(rows)):
            row=rows[i]
            if i%50==0:
                now=datetime.now()
                log.msg('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),3)*100)+'%   '+str(now-self.start_at))
            url=start_url+row[0]
            yield Request(url=url,
                                   meta={'uid':row[0]},
                                   callback=self.parse)

    def parse(self, response):
        try:
            if response.status==200:
                item=XQUserItem()
                item['item_name']='xq_user_stocks'
                d_json=json.loads(response.body)
                stocks=d_json['stocks']
                if stocks:
                    for stock in stocks:
                        item['uid']=response.meta['uid']
                        item['stk_symbol']=stock['code']
                        item['comment']=stock['comment']
                        item['sell_price']=stock['sellPrice']
                        item['buy_price']=stock['buyPrice']
                        item['create_at']=datetime.fromtimestamp(stock['createAt']/1000)
                        item['target_percent']=stock['targetPercent']
                        item['is_notice']=stock['isNotice']
                        item['stk_name']=stock['stockName']
                        item['exchange']=stock['exchange']
                        item['lastcrawl']=datetime.now()
                        yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url))
        except TimeoutError, te:
            log.msg('TimeoutError: '+str(te)+' @ '+str(response.url))
        except Exception, ex:
            log.msg('Parse Errors: '+str(ex)+' @ '+str(response.url))
            winsound.Beep(900,999999999)

