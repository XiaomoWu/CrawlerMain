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

class XQGwsRetSpider(BaseSpider):
    name='XQGwsRet'
    handle_httpstatus_list = [400,404,403,502]
    def start_requests(self):
        self.start_url="http://xueqiu.com/broker/cc/prank.json?period=5d&size=200"
        yield Request(url=self.start_url,
                               callback=self.parse)
        
    def parse(self, response):
        body=response.body
        body = re.sub("[\s]", " ", body)
        d_json=json.loads(body)
        total_gws=d_json['count']
        total_page=total_gws/200+1
        for i in xrange(1,total_page+1):
            url=self.start_url+'&page='+str(i)
            yield Request(url=url,
                          callback=self.parse_ret)

    def parse_ret(self, response):
        try:
            if response.status==200:
                item=XQGwsItem()
                item['item_name']='xq_gws_ret'
                body=response.body
                body = re.sub("[\s]", "", body)
                d_json=json.loads(body)
                has_list=d_json['list']
                if has_list:
                    for i in has_list:
                        item['gws_id']=i['id']
                        item['gws_time']=datetime.fromtimestamp(i['time']/1000)
                        item['gws_time_ms']=datetime.fromtimestamp(i['timeMs']/1000)
                        item['principal']=i['principal']
                        item['cash']=i['cash']
                        item['assets']=i['assets']
                        item['market_value']=i['marketValue']
                        item['shares']=i['shares']
                        item['hold_percent']=i['holdpercent']
                        item['diluted_cost']=i['dilutedcost']
                        item['hold_cost']=i['holdcost']
                        item['accum_amount']=i['accumAmount']
                        item['accum_rate']=i['accumRate']
                        item['float_amount']=i['floatAmount']
                        item['float_rate']=i['floatRate']
                        item['day_amount']=i['dayAmount']
                        item['day_rate']=i['dayRate']
                        item['week_amount']=i['weekAmount']
                        item['week_rate']=i['weekRate']
                        item['month_amount']=i['monthAmount']
                        item['month_rate']=i['monthRate']
                        item['quarter_amount']=i['quarterAmount']
                        item['quarter_rate']=i['quarterRate']
                        item['year_amount']=i['yearAmount']
                        item['year_rate']=i['yearRate']
                        item['uid']=i['uid']
                        item['comment']=i['comment']
                        item['update_time']=datetime.fromtimestamp(i['updateTime']/1000)
                        item['lastcrawl']=datetime.now()
                        yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url)+'\n          --'+str(response.body))
#             winsound.Beep(900,999999999)
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)