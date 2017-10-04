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

class XQGwsInfoSpider(BaseSpider):
    name='XQGwsInfo'
    handle_httpstatus_list = [400,404,403,502]

    def start_requests(self):
        self.start_url="http://xueqiu.com/broker/cc/prank.json?period=5d&size=200"
        yield Request(url=self.start_url,
                               callback=self.parse)
        
    def parse(self, response):
        body=response.body
        d_json=json.loads(body)
        total_gws=d_json['count']
        total_page=total_gws/200+1
        for i in xrange(1,total_page+1):
            url=self.start_url+'&page='+str(i)
            log.msg(url)
            yield Request(url=url,
                          callback=self.parse_info)

    def parse_info(self, response):
        try:
            if response.status==200:
                item=XQGwsItem()
                item['item_name']='xq_gws_info'
                body=response.body
                body = re.sub("[\s]", "", body)
                d_json=json.loads(body)
                has_list=d_json['list']
                if has_list:
                    for i in has_list:
                        item['gws_id']=i['id']
                        item['gws_type']=i['type']
                        item['gws_symbol']=i['symbol']
                        item['uid']=i['uid']
                        item['group_id']=i['groupId']
                        item['client_id']=i['clientId']
                        item['created_at']=datetime.fromtimestamp(i['createdAt']/1000)
                        item['screen_name']=i['screenName']
                        item['assets_desc']=i['assetsDesc']
                        item['monetary_unit']=i['monetaryUnit']
                        item['update_time']=datetime.fromtimestamp(i['updateTime']/1000)
                        item['lastcrawl']=datetime.now()
                        yield item
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url)+'\n          --'+str(response.body))
#             winsound.Beep(900,999999999)
        except Exception, ex:
            log.msg('Parse Error: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)
        