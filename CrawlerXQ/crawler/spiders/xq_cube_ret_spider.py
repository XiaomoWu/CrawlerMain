#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from crawler.items import XQCubeItem
from crawler.settings import *
from datetime import datetime
import time
import json, re, MySQLdb, traceback, winsound
import sys
from random import *

class XQCubeRetSpider(BaseSpider):
    name='XQCubeRet'
    handle_httpstatus_list = [400,404,403,502]
    
    def start_requests(self):
        start_url="http://xueqiu.com/cubes/nav_daily/all.json?cube_symbol="
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
#         注意：ret没有翻页！以后可能有翻页！
                item=XQCubeItem()
                body=response.body
                body=re.sub('[\s]','',body)
                d_json=json.loads(body)
                if d_json[0]:
                    cube=d_json[0]
                    item['item_name']='xq_cube_ret'
                    item['cube_symbol']=cube['symbol']
                    item['cube_name']=cube['name']
                    list=cube['list']
                    for i in list:
                        item['date']=datetime.fromtimestamp(i['time']/1000)
                        item['value']=i['value']
                        item['percent']=i['percent']
                        item['lastcrawl']=datetime.now()
                        yield item
                else:
                    log.msg('There is no CUBE_RET @ '+response.url+'\n          --'+str(response.body))
        except Exception, ex:
            log.msg('Exception：'+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)
