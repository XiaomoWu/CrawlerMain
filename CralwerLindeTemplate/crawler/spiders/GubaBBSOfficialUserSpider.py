from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from scrapy.http import Request
from scrapy.item import Item
from crawler.items import GubaUserItem
from crawler.settings import *
import time
import MySQLdb
import re   
    
class GubaBBSOfficialUserSpider(BaseSpider):
    name = GUBABBS_OFFICIAL_USER_SPIDER_NAME
    allowed_domains = GUBABBS_ALLOWED_DONAIMS
    conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
    cursor = conn.cursor()
    cursor.execute('''select url from stock where web_field = "guba"''')
    urls = cursor.fetchall()
    s_urls = []
    max_url = len(urls)
    for i in range(0, max_url):
        s_urls.append(str(re.sub('.html', ',1,f_1.html', urls[i][0])))
    cursor.close()
    conn.close()
    
    start_urls = s_urls
    
    def __init__(self):
        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
        self.cursor = self.conn.cursor()

    def parse_next(self, response):
        #self.log("Fetch Guba BBS Official User List: %s" % str(response.url), level=log.INFO)
        hxs = Selector(response)

        items = []
        parse_next = True
        # get all the post url
        user_name = hxs.xpath('//div[@id="articlelistnew"]//span[@class="l4"]/a/text()').extract()
        user_url = hxs.xpath('//div[@id="articlelistnew"]//span[@class="l4"]/a/@href').extract()
        post_num_v = hxs.xpath('//div[@class="pager"]/text()').extract()
        if post_num_v:
            post_num = re.search('(\d+)', post_num_v[0]).group()
        else:
            post_num = 1
        post_page = int((int(post_num) + 80 - 1)/80)
        max_url = len(user_url)
        for i in range(0, max_url):
            item = GubaUserItem()
            m = re.search("http://iguba.eastmoney.com/(\w+)", user_url[i])
            if m:
                item['user_id'] = m.group(1)
                item['official'] = 1
                item['user_name'] = user_name[i]
                item['item_name'] = GUBABBS_USER_ITEM_NAME
            else:
                continue
            self.cursor.execute('''select official from user where id = \"%s\" and name = \"%s\"''' %
                                (str(item['user_id']), item['user_name']))
            tt = self.cursor.fetchall()
            if tt:
                e_f = GUBABBS_USER_ERROR_POST_FIRST_DATE
                log("%s+++++++++++++++++" % e_f, level.INFO)
                if int(tt[0][0]) == 1:
                    continue
                else:
                    self.cursor.execute('''UPDATE user SET official=%s where id = \"%s\" and name = \"%s\"''',
                                (str(1), item['user_id'], item['user_name']))
                    self.conn.commit()
            else:
                e_f = GUBABBS_USER_ERROR_POST_FIRST_DATE
                log("%s========================" % e_f, level.INFO)
                self.cursor.execute('''insert into user (id, name, official,date_first_post,date_last_post)
                                VALUES (%s, %s, %s, %s, %s)''',
                                (item['user_id'].encode('utf-8'), item['user_name'].encode('utf-8'), str(1),
                                 str(GUBABBS_USER_ERROR_POST_FIRST_DATE), str(GUBABBS_USER_ERROR_POST_LAST_DATE)))
                self.conn.commit()
            item['sql_update'] = ITEM_SQL_DO_NOTHING
            items.append(item)
        if items:
            return items[len(items)-1]
    
    def parse(self, response):
        if response.url == 'http://www.eastmoney.com' or response.status == 404:
            return
        self.log("Fetch Guba BBS Official User List: %s" % str(response.url), level=log.INFO)
        if PRINT_LOG:
            print ("%s:fetch %s") % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
                                     str(response.url))
        hxs = Selector(response)

        items = []
        parse_next = True
        # get all the post url
        user_name = hxs.xpath('//div[@id="articlelistnew"]//span[@class="l4"]/a/text()').extract()
        user_url = hxs.xpath('//div[@id="articlelistnew"]//span[@class="l4"]/a/@href').extract()
        post_num_v = hxs.xpath('//div[@class="pager"]/text()').extract()
        if post_num_v:
            post_num = re.search('(\d+)', post_num_v[0]).group()
        else:
            post_num = 1
        post_page = int((int(post_num) + 80 - 1)/80)
        max_url = len(user_url)
        for i in range(0, max_url):
            item = GubaUserItem()
            m = re.search("http://iguba.eastmoney.com/(\w+)", user_url[i])
            if m:
                item['user_id'] = m.group(1)
                item['official'] = 1
                item['user_name'] = user_name[i]
                item['item_name'] = GUBABBS_USER_ITEM_NAME
            else:
                continue
            self.cursor.execute('''select official from user where id = \"%s\" and name = \"%s\"''' %
                                (str(item['user_id']), item['user_name']))
            tt = self.cursor.fetchall()
            if tt:
                if int(tt[0][0]) == 1:
                    continue
                else:
                    self.cursor.execute('''UPDATE user SET official=%s where id = \"%s\" and name = \"%s\"''',
                                (str(1), item['user_id'], item['user_name']))
                    self.conn.commit()
            else:
                self.cursor.execute('''insert into user (id, name, official,date_first_post,date_last_post)
                                VALUES (%s, %s, %s, %s, %s)''',
                                (item['user_id'].encode('utf-8'), item['user_name'].encode('utf-8'), str(1),
                                 str(GUBABBS_USER_ERROR_POST_FIRST_DATE), str(GUBABBS_USER_ERROR_POST_LAST_DATE)))
                self.conn.commit()
            item['sql_update'] = ITEM_SQL_DO_NOTHING
            items.append(item)
        if post_page >= 2 and not response.meta.has_key('parse_next'):
            for i in range(2, post_page+1):
            #print str(bbs_parse['url']) + ":" + item['post_url']
                u = re.sub('1.html', str(i)+'.html', response.url)
                yield Request(url = u, meta = {'parse_next': True},callback = self.parse)
        else:
            return
        #log.msg("%s DONE" % bbs_url, level=log.INFO)
        #self.cursor.close()
        #self.conn.close()

