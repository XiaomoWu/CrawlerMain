#coding=utf-8
from scrapy.spider import Spider
from scrapy import log
from twisted.internet.error import TimeoutError
from scrapy.http import Request
from crawler.items import XQCmtItem
from datetime import datetime
from crawler.settings import *
from random import randint
import json, re, time, winsound, MySQLdb, traceback


class XQUserStatusesSpider(Spider):
    start_at=datetime.now()
    name='XQUserStatuses'
    handle_httpstatus_list = [400,404,403,502]
    def start_requests(self):
        self.start_url="http://xueqiu.com/v4/statuses/user_timeline.json?user_id="
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db=SQL_DB, host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select distinct uid from xq_gws_info;''')
        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' USERS to crawl in total')

        for i in xrange(len(rows)):
            row=rows[i]
            url=self.start_url+str(row[0])
            now=datetime.now()
            if i%50==0:
                log.msg('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),3)*100)+'%   '+str(now-self.start_at))
            yield Request(url=url,
                                   meta={'uid':row[0]},
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
    #                     log.msg('parse: '+url)
                        yield Request(url=url,
                                               callback=self.parse_cmt)
        except Exception, ex:
            log.msg('Parse Errors: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)
     
    def parse_cmt(self, response):
        try:
            body=response.body
            d_json=json.loads(body)
            list=d_json['statuses']
            if list:
                item=XQCmtItem()
                for s in list:
                    item['item_name']='xq_user_cmt'
                    item['cmt_id']=s['id']
                    item['uid']=s['user_id']
                    item['cmt_title']=s['title']
                    item['cmt_created_at']=datetime.fromtimestamp(s['created_at']/1000)
                    item['retweet_count']=s['retweet_count']
                    item['reply_count']=s['reply_count']
                    item['fv_count']=s['fav_count']
                    item['truncated']=s['truncated']
                    item['commentId']=s['commentId']
                    item['retweet_status_id']=s['retweet_status_id']
                    item['cmt_symbol_id']=s['symbol_id']
                    item['cmt_type']=s['type']
                    if s['edited_at']:
                        item['cmt_edited_at']=datetime.fromtimestamp(s['edited_at']/1000)
                    else:
                        item['cmt_edited_at']=None
                    item['retweeted_status']=s['retweeted_status']
                    item['fragment']=s['fragment']
                    item['blocked']=s['blocked']
                    item['blocking']=s['blocking']
                    item['topic_symbol']=s['topic_symbol']
                    item['topic_title']=s['topic_title']
                    item['topic_desc']=s['topic_desc']
                    item['donate_count']=s['donate_count']
                    item['donate_snowcoin']=s['donate_snowcoin']
                    item['cmt_view_count']=s['view_count']
                    item['cmt_mark']=s['mark']
                    item['favorited']=s['favorited']
                    if s['favorited_created_at']:
                        item['favorited_created_at']=datetime.fromtimestamp(s['favorited_created_at']/1000)
                    else:
                        item['favorited_created_at']=None
                    item['can_edit']=s['canEdit']
                    item['expend']=s['expend']
                    item['cmt_text']=s['text']
                    item['cmt_source']=s['source']
                    item['lastcrawl']=datetime.now()
                    yield item
        except Exception, ex:
            log.msg('Parse Errors: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)