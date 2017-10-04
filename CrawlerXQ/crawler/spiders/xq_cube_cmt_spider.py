#coding=utf-8
from scrapy import log
from scrapy.spider import BaseSpider
# from scrapy import log
from scrapy.http import Request
from crawler.items import XQCubeItem
from datetime import datetime
from crawler.settings import *
import json, re, MySQLdb

class XQCubeCmtSpider(BaseSpider):
    name='XQCubeCmtSpider'
    handle_httpstatus_list = [404,403]
    def __init__(self):
        self.__set_default_item_to_none()
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db=SQL_DB, host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select cube_symbol from xq_cube_info''')
        rows=self.cursor.fetchall()
        self.start_url="http://xueqiu.com/statuses/search.json?count=50&comment=0&hl=0&source=all&sort=time&symbol="
        self.urls=[]
        for row in rows:
            symbol=str(row[0])
            url=self.start_url+"&page=1&symbol="+str(row[0])
            self.urls.append(url)
        self.urls=["http://xueqiu.com/statuses/search.json?count=50&comment=0&page=1&symbol=ZH000142"]
    def start_requests(self):
        for i in self.urls:
            yield Request(url=i,
                                   cookies={'xq_a_token':'jjAGXipL56Js1irdPjDDDf',
                                                   'xq_r_token':'87JSx9aEvKEPTy3qrj2Bvh'}, 
                                   callback=self.parse)

    def parse(self, response):
        item=XQCubeItem()
        if response.status!=404:
            body=response.body.strip()
            body = re.sub("[\t\v\f]", "", body)
            d_json=json.loads(body)
            if d_json['maxPage']:
                symbol=re.search('(ZH\d{6})', response.url).group(1)
                max_page=d_json['maxPage']
                if max_page>=1:
                    for i in range(1,2):
                        url=self.start_url+"&symbol="+symbol+"&page="+str(i)
                        yield Request(url=url,
                                               cookies={'xq_a_token':'jjAGXipL56Js1irdPjDDDf',
                                                              'xq_r_token':'87JSx9aEvKEPTy3qrj2Bvh'}, 
                                               callback=self.parse_cmt)
            else:
                return
        else:
            return
     
    def parse_cmt(self, response):
        body=response.body.strip()
        body=re.sub('[\v\f]','',body)
        d_json=json.loads(body)
        list=d_json['list']
        if list:
            item=self.__set_default_item_to_none()
            item['cube_symbol']=d_json['symbol'].strip()
            for s in list:
                log.msg(str(s))
                item['item_name']='xq_cube_cmt'
                item['table_name']='xq_cube_cmt'
                item['cmt_id']=s['id']
                item['cmt_creator_id']=s['user_id']
                item['cmt_title']=s['title']
                log.msg(str(item['cmt_title']))
                if s['created_at']:
                    item['cmt_created_at']=datetime.fromtimestamp(s['created_at']/1000)
                item['retweet_count']=s['retweet_count']
                item['reply_count']=s['reply_count']
                item['fav_count']=s['fav_count']
                item['truncated']=s['truncated']
                item['commentId']=s['commentId']
                item['retweet_status_id']=s['retweet_status_id']
                item['cmt_symbol_id']=s['symbol_id']
                item['cmt_type']=s['type']
                if s['edited_at']:
                    item['cmt_edited_at']=datetime.fromtimestamp(s['edited_at']/1000)
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
                item['comment']=s['comment']
                item['can_edit']=s['canEdit']
                item['expend']=s['expend']
                item['cmt_text']=s['text']
                item['cmt_source']=s['source']
                item['lastcrawl']=datetime.now()
                yield item
        else:
            return
