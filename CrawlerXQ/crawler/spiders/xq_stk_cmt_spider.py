#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from crawler.items import XQCmtItem
from datetime import datetime
from crawler.settings import *
from random import randint
import json, re, time, MySQLdb, traceback


class XQStkCmtSpider(BaseSpider):
    name='XQStkCmtSpider'
    handle_httpstatus_list = [400,404,403]
    def start_requests(self):
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db=SQL_DB, host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select stk_symbol from xq_stk_info;''')
        rows=self.cursor.fetchall()
        self.start_url="http://xueqiu.com/statuses/search.json?count=50&comment=0&source=all&sort=time&symbol="
        for i in xrange(len(rows)):
            row=rows[i]
            url=self.start_url+str(row[0])
            time.sleep(1)
            if i%100==0:
                log.msg('Processing: '+str(round(float(i)/len(rows),3)*100)+'%')
                time.sleep(randint(1,3))
            url='http://xueqiu.com/statuses/search.json?count=15&comment=0&symbol=SH600030&source=all&sort=time&page=1'
            yield Request(url=url,
                                   meta={'stk_symbol':row[0]},
                                   cookies={'xq_a_token':'JxDkzB0RJmf8aSDaHul92x',
                                                   'xq_r_token':'69oXi8d7F1GWLWqFPFyBKP'}, 
                                   callback=self.parse)

    def parse(self, response):
        if response.status==200:
            body=response.body.strip()
            d_json=json.loads(body)
            if d_json['maxPage']:
                max_page=d_json['maxPage']
                for i in range(1,max_page+1):
                    url=self.start_url+response.meta['stk_symbol']+"&page="+str(i)
#                     log.msg('parse: '+url)
                    yield Request(url=url,
                                           cookies={'xq_a_token':'JxDkzB0RJmf8aSDaHul92x',
                                                          'xq_r_token':'69oXi8d7F1GWLWqFPFyBKP'}, 
                                           callback=self.parse_cmt)
        else:
            log.msg('STATUS ERROR: '+' '+str(response.status)+' '+response.url)
            return
     
    def parse_cmt(self, response):
        try:
            body=response.body
            d_json=json.loads(body)
            list=d_json['list']
            if list:
                item=XQCmtItem()
                item['stk_symbol']=d_json['symbol'].strip()
                for s in list:
                    item['item_name']='xq_stk_cmt'
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
                    item['comment']=s['comment']
                    item['can_edit']=s['canEdit']
                    item['expend']=s['expend']
                    item['cmt_text']=s['text']
                    item['cmt_source']=s['source']
                    item['lastcrawl']=datetime.now()
                    yield item
            else:
                return
        except:
                log.msg('ERROR: '+str(response.url)+':\n'+str(traceback.print_exc()))

