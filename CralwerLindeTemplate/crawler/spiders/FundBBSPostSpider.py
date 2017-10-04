from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from scrapy.http import Request
from scrapy.item import Item
from scrapy.utils.response import open_in_browser
from crawler.items import GubaPostItem, GubaReplyItem, FundReplyListItem
from crawler.settings import *
import json
import time
from datetime import datetime
import MySQLdb
import re   
    
class FundBBSPostSpider(BaseSpider):
    name = FUNDBBS_POST_SPIDER_NAME
    allowed_domains = FUNDBBS_ALLOWED_DONAIMS
    start_urls = FUNDBBS_POST_START_URLS
    def __init__(self):
        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
        self.cursor = self.conn.cursor()
        
    def __get_id_from_postlist_url(self, url):
        m = re.search("^http://fund2.eastmoney.com/(\w+),(\w+)_(\d+).html$", url)
        if m:
            d = {}
            d['url'] = str(m.group(2)) + '_' + str(m.group(3))
            d['id'] = str(m.group(2))
            d['group'] = str(m.group(1))
            return d
        else:
            d = {}
            d['url'] = "error"
            d['id'] = "error"
            d['group'] = "error"
            return d

    def parse_reply(self, response):
        return
    
    def parse_post(self, response):
        item = response.meta['item']
        bbs_id = response.meta['bbs_id']
        url_m = re.search("http://fund2.eastmoney.com/(\w+),(\w+),(\d+).html", response.url)
        if url_m:
            url_group = url_m.group(1)
        else:
            url_group = ""
        if response.status == 404:
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
        item['post_url'] = response.url
        # parse author, pub date and author id
        author_date = ""
        if url_group == "look":
            author_date = hxs.xpath("//div[@id='zhuti']/div[@class='neirong']/div[@class='zuozhe']/text()").extract()
        elif url_group == "news":
            author_date = hxs.xpath("//div[@id='zhuti']/div[@class='zuozhe1']/text()").extract()
        else:
            author_date = ""
        if author_date:
            if url_group == "look":
                au_re = re.search(u'[\uff1a](\S+)([\xa0]+)', author_date[0])
            elif url_group == "news":
                au_re = re.search(': (\S+) ', author_date[0])
            if au_re:
                item['post_author'] = au_re.group(1).strip()
            else:
                item['post_author'] = GUBABBS_POST_ERROR_AUTHOR
            item['post_authorid'] = GUBABBS_POST_ERROR_AUTHORID
            date_re = re.search('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', author_date[0])
            if date_re:
                item['post_pubdate'] = date_re.group()
            else:
                item['post_pubdate'] = GUBABBS_POST_ERROR_PUB_DATE
        else:
            item['post_author'] = GUBABBS_POST_ERROR_AUTHOR
            item['post_authorid'] = GUBABBS_POST_ERROR_AUTHORID
            item['post_pubdate'] = GUBABBS_POST_ERROR_PUB_DATE
        # parse official
        item['official'] = GUBABBS_POST_NOT_OFFICIAL
        # parse title
        post_title = ""
        if url_group == "look":
            post_title = hxs.xpath("//div[@id='zhuti']/div[@class='neirong']/div[@class='biaoti']/text()").extract()
        elif url_group == "news":
            post_title = hxs.xpath("//div[@id='zhuti']/div[1]/text()").extract()
        else:
            post_title = ""
        if post_title:
            if post_title[0].strip() == '':
                item['post_title'] = GUBABBS_POST_ERROR_TITLE
            else:
                item['post_title'] = post_title[0].strip()
        else:
            item['post_title'] = GUBABBS_POST_ERROR_TITLE
    
        # parse content
        check_content = ""
        if url_group == "look":
            check_content = hxs.xpath("//div[@id='zhuti']/div[@class='neirong']/div[@class='huifu']").extract()
        elif url_group == "news":
            check_content = hxs.xpath("//div[@id='zhuti']/div[@class='zw']").extract()
        else:
            check_content = ""
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
        '''
        # parse relpynum
        reply_num = []
        reply_num = hxs.xpath("//div[@id='pinglun_fenye']/span/span[2]/text()").extract()
        if reply_num:
            item['post_replynum'] = int(reply_num[0])
        else:
            item['post_replynum'] = GUBABBS_POST_ERROR_REPLYNUM
        '''
        item['post_lastcrawl'] = str(time.time())

        # parse user
        self.cursor.execute("select date_first_post, date_last_post from user where id=%s and name=%s",
                            (str(item['post_authorid']), item['post_author'].encode('utf-8')))
        tmp = self.cursor.fetchall()
        if tmp:
            f_d = tmp[0][0]
            l_d = tmp[0][1]
            if f_d == GUBABBS_USER_ERROR_POST_FIRST_DATE:
                self.cursor.execute("UPDATE fund_user SET date_first_post=%s, date_last_post=%s where id=%s and name=%s",
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
            self.cursor.execute("insert into user (id, name, official,date_first_post,date_last_post) VALUES (%s, %s, %s, %s, %s)",
                                (item['post_authorid'].encode('utf-8'), item['post_author'].encode('utf-8'), str(0),
                                 item['post_pubdate'].encode('utf-8'), item['post_pubdate'].encode('utf-8')))
            self.conn.commit()
        return item

    def parse_reply_page(self, response):
        hxs =Selector(response)
        post_id = response.meta['post_id']
        page = response.meta['page']
        url_m = re.search("http://fund2.eastmoney.com/(\w+),(\w+),(\d+)_(\d+).html", response.url)
        if url_m:
            url_group = url_m.group(1)
        else:
            url_group = ""
        self.log("Fetch Fund BBS Reply List: %s, page %s" % (str(post_id), str(page)), level=log.INFO)
        floor = []
        floor_check = []
        if url_group == "look":
            floor_check = hxs.xpath("//div[@class='zw_nei']/div[@class='louceng']/text()").extract()
            #return
        elif url_group == "news":
            floor_check = hxs.xpath("//div[@class='louceng']/text()").extract()
            #print "news!!!!!!!!!!", post_id, " in page ", page, ' floor', len(floor_check), response.url
            #p = raw_input('show page')
            #if p:
                #print url_m.group(4)
        else:
            floor_check = []
        if floor_check:
            floor = floor_check
        #else:
            #return
        
        items = []
        #count = 1
        list_item = FundReplyListItem()
        for i in range(1, len(floor)+1):
            item = GubaReplyItem()
            item['item_name'] = GUBABBS_REPLY_ITEM_NAME
            item['reply_post_id'] = post_id
            item['reply_floor'] =  floor[i-1]
            item['web_field'] = 'fund'
            #count += 1
            reply_id_check = []
            if url_group == "look":
                reply_id_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                            /div[@class='zuozhe']/span[1]/@id""").extract()
            elif url_group == "news":
                reply_id_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                            /div[@class='zuozhe']/span[1]/@id""").extract()
            else:
                reply_id_check = []

            reply_id = ""
            if reply_id_check:
                m = re.search('(\d+)', reply_id_check[0])
                if m:
                    reply_id = m.group(1)
                    item['reply_id'] = item['reply_post_id'] + "_" + reply_id
                else:
                    #print reply_id_check[0], 2, response.url, floor[i-1]
                    continue
            else:
                continue
            replyer_check = []
            if url_group == "look":
                replyer_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                            /div[@class='zuozhe']/a/span[1]/text()""").extract()
            elif url_group == "news":
                replyer_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                            /div[@class='zuozhe']/a/span[1]/text()""").extract()
            else:
                replyer_check = []
            reply_date_check = []
            reply_content_check = []
            reply_quote_check = []
            if url_group == "look":
                if replyer_check:
                    reply_date_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                                /div[@class='zuozhe']/span[1]/text()""").extract()
                else:
                    replyer_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                                /div[@class='zuozhe']/span[1]/text()""").extract()
                    reply_date_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                                /div[@class='zuozhe']/span[2]/text()""").extract()
                reply_content_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                                /div[2]/text()""").extract()
                if not reply_content_check:
                    reply_content_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                                /div[2]""").extract()
                reply_quote_check = hxs.xpath("""//div[@class='zw_nei']/div[@class='neirong']["""+str(i)+"""]
                                /div[2]/div[@class='reply_this']/text()""").extract()
            elif url_group == "news":
                if replyer_check:
                    reply_date_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                                /div[@class='zuozhe']/span[1]/text()""").extract()
                else:
                    replyer_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                                /div[@class='zuozhe']/span[1]/text()""").extract()
                    reply_date_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                                /div[@class='zuozhe']/span[2]/text()""").extract()
                reply_content_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                                /div[2]/text()""").extract()
                reply_quote_check = hxs.xpath("""//div[@class='neirong']["""+str(i)+"""]
                                /div[2]/div[@class='reply_this']/text()""").extract()

            if reply_date_check:
                item['reply_date'] = reply_date_check[0]
            else:
                item['reply_dif url_group == "news":ate'] = GUBABBS_REPLY_ERROR_PUB_DATE

            if replyer_check:
                item['replyer_name'] = replyer_check[0]
                item['replyer_id'] = GUBABBS_REPLY_ERROR_AUTHORID
            else:
                item['replyer_name'] = GUBABBS_REPLY_ERROR_AUTHOR
                item['replyer_id'] = GUBABBS_REPLY_ERROR_AUTHORID

            if reply_content_check:
                filter_content = re.sub('<br>|</br>', '\n', reply_content_check[0])
                filter_content = re.sub('<[^>]*>|</[^>]*>', '', filter_content)
                item['reply_content'] = filter_content.strip()
                if item['reply_content'] == '':
                    item['reply_content'] = GUBABBS_REPLY_ERROR_CONTENT
            else:
                item['reply_content'] = GUBABBS_REPLY_ERROR_CONTENT

            if reply_quote_check:
                quote_content = ""
                if len(reply_quote_check) >= 2:
                    quote_content = reply_quote_check[-2].strip()
                else:
                    reply_quote_content_check = hxs.xpath("""//div[@class='neirong']["""+str(i-1)+"""]
                                /div[2]/div[@class='reply_this']""").extract()
                    if reply_quote_content_check:
                        filter_content = re.sub('<br>|</br>', '\n', reply_quote_content_check[0])
                        filter_content = re.sub('<[^>]*>|</[^>]*>', '', filter_content)
                        quote_content = filter_content.strip()
                quote_au_date_check = reply_quote_check[-1]
                dd = {}
                dd['text'] = quote_content
                if quote_au_date_check:
                    au_re = re.search(u'[\uff1a](\S+)([\xa0]+)', quote_au_date_check[0])
                    if au_re:
                        dd['nicheng'] = au_re.group(1).strip()
                    else:
                        dd['nicheng'] = GUBABBS_POST_ERROR_AUTHOR
                    dd['id'] = GUBABBS_POST_ERROR_AUTHORID
                    date_re = re.search('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', quote_au_date_check[0])
                    if date_re:
                        dd['time'] = date_re.group()
                    else:
                        dd['time'] = GUBABBS_POST_ERROR_PUB_DATE
                else:
                    dd['nicheng'] = GUBABBS_POST_ERROR_AUTHOR
                    dd['id'] = GUBABBS_POST_ERROR_AUTHORID
                    dd['time'] = GUBABBS_POST_ERROR_PUB_DATE
                item['reply_quote'] = json.dumps(dd)
            else:
                item['reply_quote'] = GUBABBS_REPLY_NO_QUOTE
            self.cursor.execute('''select floor from reply where id=%s and post_id=%s''',
                                (item['reply_id'], item['reply_post_id']))
            tt = self.cursor.fetchall()
            if tt:
                #if url_group == "news":
                    #for jjj in tt:
                        #print tt
                        #print item['reply_id'], item['reply_post_id']
                continue
            else:
                item['sql_update'] = ITEM_SQL_INSERT
            item['reply_lastcrawl'] = str(time.time())
            items.append(item)
        list_item['item_name'] = FUNDBBS_REPLY_LIST_ITEM_NAME
        list_item['item_list'] = items
        #if url_group == "news":
            #print "list_item of relply:", len(list_item['item_list']), response.url, page
            #if len(list_item['item_list']) ==0:
                #print "FFFFFFFFFFFFFFFFFFFFFFFFFFFFUCK"
                #kkkk = raw_input()
                #if kkkk == "a":
                    #open_in_browser(response)
            #print items[1]
        return list_item
        '''
        for item in items:
            item['reply_lastcrawl'] = str(time.time())
            yield Request(url = 'http:\\127.0.0.1', meta = {'item': item},callback = self.return_reply)
            '''

    def parse_reply(self, response):
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
    
    def return_reply(self, response):
        item = response.meta['item']
        return item

    def parse_reply_homepage(self, response):
        reply_page = response.meta['reply_page']
        post_id = response.meta['post_id']
        base_url = response.url
        #print "++parse reply home page:", response.url
        for r in range(1, min(int(reply_page)+1, 4)):
            reply_url = re.sub('.html','_'+str(r)+'.html', base_url)
            yield Request(url = reply_url, meta = {'post_id':post_id,'page':r},
                            callback = self.parse_reply_page)
    
    def parse(self, response):
        bbs_parse = self.__get_id_from_postlist_url(response.url)
        self.log("Fetch Fund BBS Post List: %s" % str(bbs_parse['url']), level=log.INFO)
        hxs = Selector(response)

        items = []
        replys = []
        # get all the post url
        url = hxs.xpath("//div[@class='liebiao']/div/ul/li[@class='l3']/a[1]/@href").extract()
        # get all the view number of post
        view = hxs.xpath("//div[@class='liebiao']/div/ul/li[@class='l1']/text()").extract()
        active_time = hxs.xpath("//div[@class='liebiao']/div/ul/li[@class='l5']/text()").extract()
        sticky = hxs.xpath("//div[@class='liebiao']/div/ul/li[@class='l3']/font/text()").extract()
        reply = hxs.xpath("//div[@class='liebiao']/div/ul/li[@class='l2']/text()").extract()
        sticky_num = 0
        if sticky:
            sticky_num = len(sticky)
        else:
            sticky_num = 0
        post_page = 1
        post_page_re = re.search('page_num=(\d+)', response.body)
        if post_page_re:
            post_page = int(post_page_re.group(1))
        else:
            post_page = 1
        print post_page
        max_url = len(url)
        print "url:" + str(len(url))
        print "view:" + str(len(view))
        print "active_time:" + str(len(active_time))
        print "sticky:" + str(len(sticky))
        print "reply:" + str(len(reply))
        for i in range(0, max_url):
            item = GubaPostItem()
            item['post_url'] = urljoin_rfc('http://fund2.eastmoney.com/', url[i])
            m = re.search("^(\w+),(\w+),(\w+).html", url[i])
            item['post_id'] = m.group(2) + "_" + m.group(3)
            item['url_group'] = m.group(1)
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
            replys.append((reply[i+1], item['post_url'],
                           item['post_id'], item['url_group']))
            item['post_replynum'] = reply[i+1]
            if tt:
                if str(tt[0][0]) == item['post_activedate']:
                    continue
                else:
                    item['sql_update'] = ITEM_SQL_UPDATE
            else:
                item['sql_update'] = ITEM_SQL_INSERT
            items.append(item)
            #replys.append(reply[i+1])
        max_items = len(items)
        max_replys = len(replys)
        print max_items, max_replys
        for i in range(0, max_items):
            yield Request(url = items[i]['post_url'], meta = {'item':items[i], 'bbs_id':bbs_parse['id']},
                          callback = self.parse_post)
        for i in range(0, max_replys):
            reply_page = int((int(replys[i][0]) - 1 + FUNDBBS_REPLY_PER_PAGE - 1)/FUNDBBS_REPLY_PER_PAGE)
            yield Request(url = replys[i][1], meta = {'post_id':replys[i][2],
                                           'reply_page':reply_page,
                                           'reply_list':("reply_list")},
                          dont_filter = True,
                          callback = self.parse_reply_homepage)
        #print post_page
        if post_page >= 2 and not response.meta.has_key('parse_next'):
            #for i in range(2, post_page+1):
            for i in range(2, min(post_page+1, 5)):
                u = re.sub('1.html', str(i)+'.html', response.url)
                yield Request(url = u, meta = {'parse_next': True},callback = self.parse)

        #log.msg("%s DONE" % bbs_url, level=log.INFO)
        #self.cursor.close()
        #self.conn.close()

