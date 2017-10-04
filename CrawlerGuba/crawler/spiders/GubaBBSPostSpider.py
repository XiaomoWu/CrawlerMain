# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from scrapy.http import Request
from scrapy.item import Item
from crawler.items import GubaPostListItem, GubaPostItem, GubaReplyItem
from crawler.settings import *
import json
import time
from datetime import datetime
import MySQLdb
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
    
class GubaBBSPostSpider(BaseSpider):
    name = GUBABBS_POST_SPIDER_NAME
    allowed_domains = GUBABBS_ALLOWED_DONAIMS
    #start_urls = GUBABBS_POST_START_URLS
    start_urls = []
    def __init__(self):
        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''select id from user where official=1''')
        tmp = self.cursor.fetchall()
        self.official_user_l = []
        for i in tmp:
            self.official_user_l.append(i[0])
        log.msg("%s official users." % len(self.official_user_l), level=log.INFO)
        #self.cursor.execute('''select url from stock where web_field = "guba" and tag = "个股吧"''')
        self.cursor.execute('''select url from stock where web_field = "guba" and tag = "个股吧" and id != 'szzs' and (id < 001000 or (id > 002000 and id < 003000))''')
        urls = self.cursor.fetchall()
        urls = []
        s_urls = []
        max_url = len(urls)
        print "len of urls:",max_url
        for i in range(0, max_url-1):
            s_urls.append(str(re.sub('.html', '_1.html', urls[i][0])))
            #s_urls.append(str(re.sub('.html', '_1.html', urls[i])))

        self.start_urls += s_urls
        
    def __get_id_from_postlist_url(self, url):
        m = re.search("^http://guba.eastmoney.com/(\w+),(\w+)_(\d+).html$", url)
        if m:
            d = {}
            d['url'] = str(m.group(2)) + '_' + str(m.group(3))
            d['id'] = str(m.group(2))
            return d
        else:
            d = {}
            d['url'] = "error"
            d['id'] = "error"
            return d

    def parse_reply(self, response):
        return
    
    def parse_post(self, response):
        item = response.meta['item']
        bbs_id = response.meta['bbs_id']
        url_s = re.search(GUBABBS_404_URL, response.url)
        if url_s or response.status == 404:
            item['post_replynum'] = GUBABBS_POST_ERROR_REPLYNUM
            item['post_title'] = GUBABBS_POST_ERROR_TITLE
            item['post_author'] = GUBABBS_POST_ERROR_AUTHOR
            item['post_authorid'] = GUBABBS_POST_ERROR_AUTHORID
            item['post_pubdate'] = GUBABBS_POST_ERROR_PUB_DATE
            item['post_content'] = GUBABBS_POST_ERROR_CONTENT
            item['post_lastcrawl'] = GUBABBS_POST_ERROR_LASTCRAWL
            item['post_valid'] = GUBABBS_POST_ERROR_VALID
            item['official'] = GUBABBS_POST_NOT_OFFICIAL
            log.msg("%s DELETE" % item['post_url'], level=log.WARNING)
            return item

        #filter_body = response.body
        #filter_body = re.sub('<[A-Z]+[0-9]*[^>]*>|</[A-Z]+[^>]*>', '', filter_body)
        #response = response.replace(body = filter_body)
        hxs =Selector(response)
        # parse author and author id
        author = hxs.xpath('//div[@id="zwconttbn"]/strong/a/text()').extract()
        if author:
            au_url = hxs.xpath('//div[@id="zwconttbn"]/strong/a/@href').extract()[0]
            au_id = re.search('http://iguba.eastmoney.com/(\w+)', au_url)
            if au_id:
                item['post_authorid'] = str(au_id.group(1))
            else:
                item['post_authorid'] = GUBABBS_POST_ERROR_AUTHORID
            item['post_author'] = author[0]
        else:
            author_t = hxs.xpath('//div[@id="zwconttbn"]/strong/span/text()').extract()
            if author_t:
                item['post_author'] = author_t[0]
                item['post_authorid'] = GUBABBS_POST_ERROR_AUTHORID
            else:
                item['post_author'] = GUBABBS_POST_ERROR_AUTHOR
                item['post_authorid'] = GUBABBS_POST_ERROR_AUTHORID
        # parse official
        if item['post_authorid'] in self.official_user_l:
            item['official'] = GUBABBS_POST_OFFICIAL
        else:
            item['official'] = GUBABBS_POST_NOT_OFFICIAL
        # parse title
        post_title = hxs.xpath('//div[@id="zwconttb"]/div[@id="zwconttbt"]/text()').extract()
        if post_title:
            if post_title[0].strip() == '':
                item['post_title'] = GUBABBS_POST_ERROR_TITLE
            else:
                item['post_title'] = post_title[0].strip()
        else:
            item['post_title'] = GUBABBS_POST_ERROR_TITLE
        # parse pub date
        pub_date = hxs.xpath('//div[@id="zwconbotl"]/text()').extract()
        if pub_date:
            item['post_pubdate'] = re.search('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', pub_date[0]).group()
        else:
            item['post_pubdate'] = GUBABBS_POST_ERROR_PUB_DATE
        # parse content
        # xpath sometimes doesn't work as pork in mouth.
        '''
        check_content = hxs.xpath('//div[@id="zwconbody"]/*/text()').extract()
        if not check_content:
            content = hxs.xpath('//div[@id="zwconbody"]/text()').extract()
            if content:
                tmp = ""
                for i in content:
                    tmp += i.strip()
                    tmp += "\n"
                item['post_content'] = tmp.strip()
            else:
                item['post_content'] = content.strip()
        else:
            tmp = ""
            for i in check_content:
                tmp += i.strip()
                tmp += "\n"
            item['post_content'] = tmp.strip()
        '''
        # if not item['post_content']:
        check_content = hxs.xpath('//div[@id="zwconbody"]').extract()
        if check_content:
            filter_content = re.sub('<br>|</br>', '\n', check_content[0])
            filter_content = re.sub('<[^>]*>|</[^>]*>', '', filter_content)
            item['post_content'] = filter_content.strip()
        else:
            item['post_content'] = GUBABBS_POST_ERROR_CONTENT
        
        # parse post valid
        if not item['post_content']:
            item['post_valid'] = 0
        else:
            item['post_valid'] = 1
        # parse relpynum
        reply_num = []
        reply_num = hxs.xpath('//*[@id="zwcontab"]/ul/li[1]/a/text()').extract()
        if reply_num:
            item['post_replynum'] = int(re.search('(\d+)', reply_num[0]).group())
        else:
            item['post_replynum'] = GUBABBS_POST_ERROR_REPLYNUM
        item['post_lastcrawl'] = str(time.time())

        # parse user
        self.cursor.execute("select date_first_post, date_last_post from user where id=%s and name=%s",
                            (str(item['post_authorid']), item['post_author'].encode('utf-8')))
        tmp = self.cursor.fetchall()
        if tmp:
            f_d = tmp[0][0]
            l_d = tmp[0][1]
            if f_d == GUBABBS_USER_ERROR_POST_FIRST_DATE:
                self.cursor.execute("UPDATE user SET date_first_post=%s, date_last_post=%s where id=%s and name=%s",
                            (item['post_pubdate'].encode('utf-8'), item['post_pubdate'].encode('utf-8'),
                             str(item['post_authorid']), item['post_author'].encode('utf-8')))
                self.conn.commit()
            else:
                #f_datetime = datetime.strptime(f_d, "%Y-%m-%d %H:%M:%S")
                #l_datetime = datetime.strptime(l_d, "%Y-%m-%d %H:%M:%S")
                cur_datetime = datetime.strptime(item['post_pubdate'], "%Y-%m-%d %H:%M:%S")
                flag = False
                f_dd = f_d.strftime("%Y-%m-%d %H:%M:%S")
                l_dd = l_d.strftime("%Y-%m-%d %H:%M:%S")
                if f_d > cur_datetime:
                    f_dd = item['post_pubdate']
                    flag = True
                if l_d < cur_datetime:
                    l_dd = item['post_pubdate']
                    flag = True
                if flag:
                    self.cursor.execute("UPDATE user SET date_first_post=%s,date_last_post=%s where id=%s and name=%s",
                            (f_dd.encode('utf-8'), l_dd.encode('utf-8'),
                             str(item['post_authorid']), item['post_author'].encode('utf-8')))
                    self.conn.commit()
        else:
            self.cursor.execute("replace into user (id, name, official,date_first_post,date_last_post) VALUES (%s, %s, %s, %s, %s)",
                                (item['post_authorid'].encode('utf-8'), item['post_author'].encode('utf-8'), str(0),
                                 item['post_pubdate'].encode('utf-8'), item['post_pubdate'].encode('utf-8')))
            self.conn.commit()
        return item
        # parse reply
        '''
        if item['post_valid'] == 1 and item['post_replynum'] >= 1:
            reply_page = int((int(item['post_replynum']) + GUBABBS_REPLY_PER_PAGE - 1)/GUBABBS_REPLY_PER_PAGE)
            yield Request(url = '', meta = {'post_id':item['post_id'], 'post_pubdate':item['post_pubdate'],
                                            'response':response, 'page':1},callback = self.parse_reply_page)
            for i in range(2, reply_page+1):
                reply_url = re.sub('.html','_'+str(i)+'.html', response.url)
                yield Request(url = reply_url, meta = {'post_id':item['post_id'], 'post_pubdate':item['post_pubdate'],
                                        'response':'None', 'page':i},callback = self.parse_reply_page) 
        '''

    def parse_reply_page(self, response):
        hxs =Selector(response)
        post_id = response.meta['post_id']
        page = response.meta['page']
        #self.log("Fetch Guba BBS Reply List: %s, page %s" % (str(post_id), str(page)), level=log.INFO)
        reply_id_check = hxs.xpath("//div[@id='zwlist']/div/@id").extract()
        reply_id = []
        if reply_id_check:
            reply_id = reply_id_check
        #else:
            #return
        
        items = []
        count = 1
        for i in reply_id:
            item = GubaReplyItem()
            item['item_name'] = GUBABBS_REPLY_ITEM_NAME
            item['reply_post_id'] = post_id
            item['reply_li_id'] = i
            item['web_field'] = 'guba'
            item['reply_floor'] =  (page-1)*GUBABBS_REPLY_PER_PAGE + count
            count += 1
            r_id = re.search('(\d+)', i)
            if r_id:
                item['reply_id'] = int(r_id.group(1))
            else:
                continue
            reply_date_check = hxs.xpath("""//div[@id='"""+i+"""']/div[@class='zwlitx']/div[@class='zwlitxt']/
                                         div[@class='zwlitxtbc']/div[@class='zwlitxb']/text()""").extract()
            if reply_date_check:
                item['reply_date'] = reply_date_check[0]
            else:
                item['reply_date'] = GUBABBS_REPLY_ERROR_PUB_DATE
            replyer_check = hxs.xpath("""//div[@id='"""+i+"""']/div[@class='zwlitx']/div[@class='zwlitxt']/
                                    div[@class='zwlianame']/strong/span/text()""").extract()
            if replyer_check:
                item['replyer_name'] = replyer_check[0]
                item['replyer_id'] = GUBABBS_REPLY_ERROR_AUTHORID
            else:
                replyer_check_a = hxs.xpath("""//div[@id='"""+i+"""']/div[@class='zwlitx']/div[@class='zwlitxt']/
                                    div[@class='zwlianame']/strong/a/text()""").extract()
                if replyer_check_a:
                    item['replyer_name'] = replyer_check_a[0].strip()
                    a_id = hxs.xpath("""//div[@id='"""+i+"""']/div[@class='zwlitx']/div[@class='zwlitxt']/
                                    div[@class='zwlianame']/strong/a/@href""").extract()[0]
                    a_id_b = re.search('http://iguba.eastmoney.com/(\w+)', a_id)
                    if a_id_b:
                        item['replyer_id'] = str(a_id_b.group(1))
                    else:
                        item['replyer_id'] = GUBABBS_REPLY_ERROR_AUTHORID
                else:
                    item['replyer_name'] = GUBABBS_REPLY_ERROR_AUTHOR
                    item['replyer_id'] = GUBABBS_REPLY_ERROR_AUTHORID
            reply_content_check = hxs.xpath("""//div[@id='"""+i+"""']/div[@class='zwlitx']/
                                        div[@class='zwlitxt']/div[@class='zwlitext']""").extract()
            if reply_content_check:
                filter_content = re.sub('<br>|</br>', '\n', reply_content_check[0])
                filter_content = re.sub('<[^>]*>|</[^>]*>', '', filter_content)
                item['reply_content'] = filter_content.strip()
                if item['reply_content'] == '':
                    item['reply_content'] = GUBABBS_REPLY_ERROR_CONTENT
            else:
                item['reply_content'] = GUBABBS_REPLY_ERROR_CONTENT
            self.cursor.execute('''select floor from reply where id=%s and post_id=%s''',
                                (item['reply_id'], item['reply_post_id']))
            tt = self.cursor.fetchall()
            if tt:
                continue
            else:
                item['sql_update'] = ITEM_SQL_INSERT
            items.append(item)
        json_request = 'http://guba.eastmoney.com/get_json.aspx?action=gethuifu&encode=utf8&id='
        json_request_tail = '&huifu_id='
        for item in items:
            #print str(bbs_parse['url']) + ":" + item['post_url']
            p_id_check = re.search("(\w+)_(\w+)", item['reply_post_id'])
            p_id = ''
            if p_id_check:
                p_id = p_id_check.group(2)
            else:
                p_id = 'None'
            r_url = json_request + str(p_id) + json_request_tail + str(item['reply_id'])
            yield Request(url = r_url, meta = {'item': item}, callback = self.parse_reply_quote)

    def parse_reply_quote(self, response):
        d_json = json.loads(response.body)
        item = response.meta['item']
        last_quote = {}
        if d_json['reply']:
            d_json['reply'][-1]["nicheng"] = d_json['reply'][-1]["nicheng"].strip()
            filter_content = re.sub('<br>|</br>', '\n', d_json['reply'][-1]["text"])
            filter_content = re.sub('<[^>]*>|</[^>]*>', '', filter_content)
            d_json['reply'][-1]["text"] = filter_content.strip()
            last_quote = json.dumps(d_json['reply'][-1])
        if last_quote:
            item['reply_quote'] = last_quote
        else:
            item['reply_quote'] = GUBABBS_REPLY_NO_QUOTE
        item['reply_lastcrawl'] = str(time.time())
        return item
        
    
    def parse(self, response):
        bbs_parse = self.__get_id_from_postlist_url(response.url)
        self.log("Fetch Guba BBS Post List: %s" % str(bbs_parse['url']), level=log.INFO)
        if PRINT_LOG:
            print ("%s:fetch %s") % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
                                     str(bbs_parse['url']))          
        hxs = Selector(response)

        items = []
        replys = []
        # get all the post url
        url = hxs.xpath('//div[@id="articlelistnew"]/*/span[@class="l3"]/a/@href').extract()
        # get all the view number of post
        view = hxs.xpath('//div[@id="articlelistnew"]/*/span[@class="l1"]/text()').extract()
        active_time = hxs.xpath('//div[@id="articlelistnew"]/*/span[@class="l5"]/text()').extract()
        sticky = hxs.xpath('//div[@id="articlelistnew"]//span[@class="l3"]/em/text()').extract()
        reply = hxs.xpath('//div[@id="articlelistnew"]/*/span[@class="l2"]/text()').extract()
        sticky_num = 0
        if sticky:
            sticky_num = len(sticky)
        else:
            sticky_num = 0
        post_num_v = hxs.xpath('//div[@class="pager"]/text()').extract()
        if post_num_v:
            post_num = re.search('(\d+)', post_num_v[0]).group()
        else:
            post_num = 1
        post_page = int((int(post_num) + GUBABBS_POST_PER_PAGE - 1)/GUBABBS_POST_PER_PAGE)
        max_url = len(url)
        for i in range(0, max_url):
            item = GubaPostItem()
            item['post_url'] = urljoin_rfc('http://guba.eastmoney.com/', url[i])
            m = re.search("^news,(\w+),(\w+).html", url[i])
            item['post_id'] = m.group(1) + "_" + m.group(2)
            item['post_view'] = int(view[i+1])
            item['post_activedate'] = str(active_time[i+1])
            item['post_stock_id'] = bbs_parse['id']
            item['item_name'] = GUBABBS_POST_ITEM_NAME
            if i <= (sticky_num - 1):
                item['sticky'] = GUBABBS_POST_STICKY
            else:
                item['sticky'] = GUBABBS_POST_NOT_STICKY
            self.cursor.execute('''select activedate from post where id = \"%s\"''' % item['post_id'])
            tt = self.cursor.fetchall()
            replys.append((reply[i+1], item['post_url'], item['post_id']))
            if tt:
                if str(tt[0][0]) == item['post_activedate']:
                    continue
                else:
                    item['sql_update'] = ITEM_SQL_UPDATE
            else:
                item['sql_update'] = ITEM_SQL_INSERT
            items.append(item)
        max_items = len(items)
        max_replys = len(replys)
        for i in range(0, max_items):
            yield Request(url = items[i]['post_url'], meta = {'item':items[i], 'bbs_id':bbs_parse['id']},
                          callback = self.parse_post)
        for i in range(0, max_replys):
            reply_page = int((int(replys[i][0]) + GUBABBS_REPLY_PER_PAGE - 1)/GUBABBS_REPLY_PER_PAGE)
            for r in range(1, reply_page+1):
                reply_url = re.sub('.html','_'+str(r)+'.html', replys[i][1])
                yield Request(url = reply_url, meta = {'post_id':replys[i][2],
                                                       'response':'None', 'page':r},
                              callback = self.parse_reply_page)
        if post_page >= 2 and not response.meta.has_key('parse_next'):
            for i in range(2, 3):
                u = re.sub('1.html', str(i)+'.html', response.url)
                yield Request(url = u, meta = {'parse_next': True, 'next_page': i},callback = self.parse)
        if response.meta.has_key('next_page'):
            next_page = response.meta['next_page']
            #print "NEXT PAGE:=========", post_page, next_page, max_items
            if post_page >= (int(next_page)+1) and response.meta.has_key('parse_next') and len(items) != 0:
                #print "NEXT PAGE:~~~~"
                u = re.sub( str(next_page) + '.html', str(int(next_page)+1)+'.html', response.url)
                yield Request(url = u, meta = {'parse_next': True, 'next_page': int(next_page)+1},callback = self.parse)
        #log.msg("%s DONE" % bbs_url, level=log.INFO)
        #self.cursor.close()
        #self.conn.close()

