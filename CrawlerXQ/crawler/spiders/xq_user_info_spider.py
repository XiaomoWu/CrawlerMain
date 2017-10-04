#coding=utf-8
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.http import Request
from twisted.internet.error import TimeoutError
from scrapy.selector import Selector
from crawler.items import XQUserItem
from datetime import datetime
from crawler.settings import *
import time
import json, re, MySQLdb, traceback, winsound
import sys
from random import *

class XQUserInfoSpider(BaseSpider):
    start_at=datetime.now()
    name='XQUserInfo'
    handle_httpstatus_list = [400,404,403,502]

    def start_requests(self):
        start_url="http://xueqiu.com/"

        # scheme I: select from cube_info
        """
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                                  db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''select distinct owner_id from xq_cube_info''')
        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' USERS to crawl')
        for i in xrange(len(rows)):
            row=rows[i]
            # if if_commit=True, require Mysql to commit
            if_commit=False
            if i%100==0:
                now=datetime.now()
                log.msg('Processing: '+str(round(float(i)/len(rows),3)*100)+'%   '+str(now-self.start_at))
                if_commit=True
            url=start_url+row[0]
            yield Request(url=url,
                                   meta={'uid':row[0], 'if_commit': if_commit},
                                   callback=self.parse)
        """

        # scheme II: search along the network
        self.conn=MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD,
                            db='xueqiu', host=SQL_HOST)
        self.cursor=self.conn.cursor()

        # select depth.
        distance=None
        # self.cursor.execute('''select distinct uid from xq_gws_info''')

        # select 'g_f_0' 'g_f_1', 'g_f_2' 'g_l_1', 'g_l_2', 'g_l_3' 'g_a_1', 'g_a_2', 'g_a_3'
        '''
        (select distinct uid from xq_user_info 
                                         where distance='g_f_0')
                                         union
                                        (select distinct uid from xq_user_followers                     where distance in ('g_f_1', 'g_f_2'))
                                         union
                                        (select distinct uid from xq_user_members                    where distance in ('g_l_1', 'g_l_2', 'g_l_3'))
                                         union 
                                        (select distinct uid from xq_user_favorites                     where distance in ('g_a_1', 'g_a_2', 'g_a_3'));
        '''
        self.cursor.execute('''
                                        (select distinct fl.uid from xq_user_followers as fl
                                        where fl.uid not in (select distinct uinfo.uid from xq_user_info as uinfo));
                                     ''')

        rows=self.cursor.fetchall()
        log.msg('There are '+str(len(rows))+' users to crawl')
        for i in xrange(len(rows)):
            row=rows[i]
            # if if_commit=True, require Mysql to commit
            if_commit=False
            now=datetime.now()
            if i%100==0:
                log.msg('Processing '+str(self.name)+': '+str(round(float(i)/len(rows),3)*100)+'%   '+str(now-self.start_at))
                if_commit=True
            url=start_url+row[0]
            yield Request(url=url,
                                   meta={'uid':row[0], 'if_commit': if_commit, 
                                         'distance':distance},
                                   callback=self.parse)



    def parse(self, response):
        try:
            if response.status==200:
                item=XQUserItem()
                item['item_name']='xq_user_info'
                hxs=Selector(response)
                info=''.join(hxs.xpath('//body//script[contains(., "SNB.profileUser = {")]//text()').extract())
                info=re.sub('[\s]','',info)
#                 group=' '.join(hxs.xpath('//body//div[@id="center"]//div[@class="group-list-bd"]//@href').extract())
                m=re.search('SNB.profileUser=({\S+?"})', info)
                if m:
                    user_info=m.group(1)
                    d_json=json.loads(user_info)
                    if d_json['id']:
                        item['distance']=response.meta['distance']
                        item['if_commit']=response.meta['if_commit']
                        item['subscribeable']=d_json['subscribeable']
                        item['status']=d_json['status']
                        item['common_count']=d_json['common_count']
                        item['remark']=d_json['remark']
                        item['name']=d_json['name']
                        item['location']=d_json['location']
                        item['uid']=d_json['id']
                        item['type']=d_json['type']
                        item['url']=d_json['url']
                        item['description']=d_json['description']
                        item['domain']=d_json['domain']
                        item['blocking']=d_json['blocking']
                        item['screen_name']=d_json['screen_name']
                        item['verified']=d_json['verified']
                        item['verified_type']=d_json['verified_type']
                        item['st_color']=d_json['st_color']
                        item['allow_all_stock']=d_json['allow_all_stock']
                        item['following']=d_json['following']
                        item['following']=d_json['following']
                        item['donate_count']=d_json['donate_count']
                        item['verified_description']=d_json['verified_description']
                        item['status_count']=d_json['status_count']
                        item['last_status_id']=d_json['last_status_id']
                        item['follow_me']=d_json['follow_me']
                        item['friends_count']=d_json['friends_count']
                        item['city']=d_json['city']
                        item['gender']=d_json['gender']
                        item['followers_count']=d_json['followers_count']
                        item['province']=d_json['province']
                        item['recommend']=d_json['recommend']
                        item['blog_description']=d_json['blog_description']
                        item['step']=d_json['step']
                        item['intro']=d_json['intro']
                        item['stock_status_count']=d_json['stock_status_count']
                        item['stocks_count']=d_json['stocks_count']
                        item['group_ids']=d_json['group_ids']
                        item['lastcrawl']=datetime.now()
                        yield item
                else:
                    log.msg('There is no SNB.profile @ '+response.url)
        except ValueError, v:
            log.msg('ValueError: '+str(v)+' @ '+str(response.url)+'\n          --'+str(response.body))
#             winsound.Beep(900,999999999)
        except TimeoutError, te:
            log.msg('TimeoutError: '+str(te)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)
        except Exception, ex:
            log.msg('Undetected Error: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
            winsound.Beep(900,999999999)
