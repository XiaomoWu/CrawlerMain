from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from scrapy.http import Request
from scrapy.item import Item
from crawler.items import GubaStockItem
from crawler.settings import *
import urllib2,urllib
import json
import time
import MySQLdb
import re

class GubaBBSStockSpider(BaseSpider):
    name = GUBABBS_STOCK_SPIDER_NAME
    allowed_domains = GUBABBS_ALLOWED_DONAIMS
    start_urls = GUBABBS_STOCK_START_URLS

    def __init__(self):
        self.conn = MySQLdb.connect(user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, host=SQL_HOST,
                                    charset=SQL_CHARSET, use_unicode=SQL_UNICODE)
        self.cursor = self.conn.cursor()
        
    def __get_id_from_stock_url(self, web_tag, url):
        m = re.search("^http://" + web_tag + ".eastmoney.com/(\w+),(\w+).html$", url)
        if m:
            d = {}
            d['stock_id'] = m.group(2)
            return d['stock_id']
        else:
            return 0
        
    def __get_id_from_stock_type(self, url):
        m = re.search("^http://guba.eastmoney.com/remenba.aspx\?type=(\d+)$", url)
        if m:
            d = {}
            d['stock_type'] = m.group(1)
            return d
        else:
            d = {}
            d['stock_type'] = GUBABBS_STOCK_TYPE_UNKNOWN
            return d
        
    def parse(self, response):
        hxs = Selector(response)
        stock_type_id = self.__get_id_from_stock_type(response.url)['stock_type']
        stock_type_l = hxs.xpath('//*[@id="zhutitab"]/ul/li[' + str(stock_type_id) + ']/a/text()').extract()
        stock_type = ""
        d = {}
        items = []
        self.log("Fetch Guba BBS Stock List: %s" % str(response.url), level=log.INFO)
        if PRINT_LOG:
            print ("%s:fetch %s") % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
                                     str(response.url))
        if stock_type_l:
            stock_type = stock_type_l[0]
        else:
            stock_type = GUBABBS_STOCK_TYPE_UNKNOWN
        if stock_type_id == '1':
            d = self.parse_1(stock_type, response, stock_type_id)
        elif stock_type_id == '2':
            d = self.parse_2(stock_type, response, stock_type_id)
        elif stock_type_id == '3':
            d = self.parse_3(stock_type, response, stock_type_id)
        elif stock_type_id == '4':
            d = self.parse_4(stock_type, response, stock_type_id)
        else:
            log.msg("Unknown stock type:%s" % response.url, level=log.ERROR)
            return
        items = self.parse_init(d['url'], d['name'], d['stock_type'])
        for item in items:
            yield Request(url = item['stock_url'], meta = {'item': item, 'web_field' : item['web_field']},
                          callback = self.parse_stock)
        
    def parse_1(self, stock_type, response, stock_type_id):
        hxs = Selector(response)
        url = hxs.xpath('//div[@class="ngbglistdiv"]/ul[@class="ngblistul2"]/li/a/@href').extract()
        max_url = len(url)
        for i in range(0, max_url):
            url[i] = urljoin_rfc('http://guba.eastmoney.com/', url[i])
        url += hxs.xpath('//ul[@class="ngblistul3"]/li/a/@href').extract()
        url += hxs.xpath('//div[@class="ngbglistjjt"]/a/@href').extract()
        name = hxs.xpath('//div[@class="ngbglistdiv"]/ul[@class="ngblistul2"]/li/a/text()').extract()
        name += hxs.xpath('//ul[@class="ngblistul3"]/li/a/text()').extract()
        name += hxs.xpath('//div[@class="ngbglistjjt"]/a/text()').extract()
        d = {}
        d['url'] = url
        d['name'] = name
        d['stock_type'] = stock_type
        return d

    def parse_2(self, stock_type, response, stock_type_id):
        hxs = Selector(response)
        url = hxs.xpath('//div[@class="allzhutilistb"]/ul/li/a/@href').extract()
        max_url = len(url)
        for i in range(0, max_url):
            url[i] = urljoin_rfc('http://guba.eastmoney.com/', url[i])
        name = hxs.xpath('//div[@class="allzhutilistb"]/ul/li/a/text()').extract()
        d = {}
        d['url'] = url
        d['name'] = name
        d['stock_type'] = stock_type
        return d

    def parse_3(self, stock_type, response, stock_type_id):
        hxs = Selector(response)
        url = hxs.xpath('//div[@class="ngblistitem"]/ul[@class="ngblistitemul"]/li/a/@href').extract()
        max_url = len(url)
        for i in range(0, max_url):
            url[i] = urljoin_rfc('http://guba.eastmoney.com/', url[i])
        name = hxs.xpath('//div[@class="ngblistitem"]/ul[@class="ngblistitemul"]/li/a/text()').extract()
        d = {}
        d['url'] = url
        d['name'] = name
        d['stock_type'] = stock_type
        return d

    def parse_4(self, stock_type, response, stock_type_id):
        hxs = Selector(response)
        url = hxs.xpath('//div[@class="ngblistitem"]/ul[@class="ngblistitemul"]/li/a/@href').extract()
        max_url = len(url)
        for i in range(0, max_url):
            url[i] = urljoin_rfc('http://guba.eastmoney.com/', url[i])
        name = hxs.xpath('//div[@class="ngblistitem"]/ul[@class="ngblistitemul"]/li/a/text()').extract()
        d = {}
        d['url'] = url
        d['name'] = name
        d['stock_type'] = stock_type
        return d

    
    def parse_init(self, url, name, stock_type):
        items = []
        max_url = len(url)
        for i in range(0, max_url):
            item = GubaStockItem()
            item['item_name'] = GUBABBS_STOCK_ITEM_NAME
            item['stock_name'] = name[i]
            item['stock_url'] = url[i]
            item['stock_tag'] = stock_type
            if re.search('guba.eastmoney.com/', url[i]):
                item['web_field'] = 'guba'
            elif re.search('fund2.eastmoney.com/', url[i]):
                item['web_field'] = 'fund2'
            else:
                item['web_field'] = 'unknown'
            stock_id = self.__get_id_from_stock_url(item['web_field'], item['stock_url'])
            item['stock_id'] = stock_id
            # print type(item['stock_name']), type(item['stock_id'])
            if item['web_field'] != 'unknown' and item['stock_id'] != 0:
                result = self.cursor.execute('''select url from stock where id=%s''',str(item['stock_id']))
                if result:
                    item['sql_update'] = ITEM_SQL_UPDATE
                else:
                    item['sql_update'] = ITEM_SQL_INSERT
                    item['date_insert'] = str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                items.append(item)
        self.cursor.execute('''select url from stock''')
        result = self.cursor.fetchall()
        '''
        for i in result:
            if i[0] not in url:
                stock_id = self.__get_id_from_stock_url(item['web_field'], item['stock_url'])
                del_time = str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                self.cursor.execute('update stock set date_delete values (%s) where stock_id = %s',
                                    del_time.encode('utf-8'), stock_id)
                self.conn.commit()
                log.msg("Stock delete:%s" % stock_id.encode('utf-8'), level=log.WARNING)
        '''
        return items
    
    def parse_stock(self, response):
        item = response.meta['item']
        web_field = response.meta['web_field']
        hxs = Selector(response)
        if web_field == 'guba':
            '''
            click = hxs.xpath('//div[@id="stockheader"]/span[@id="stockifm"]/em[@class="strongc1"]/text()').extract()
            if click:
                click_num = re.search('(\d+)', click[0])
                if click_num:
                    item['stock_click'] = int(click_num.group())
                else:
                    item['stock_click'] = 0
            else:
                item['stock_click'] = 0
            '''
            post = hxs.xpath('//div[@class="pager"]/text()').extract()
            if post:
                post_num = re.search('(\d+)', post[0])
                if post_num:
                    item['stock_post'] = int(post_num.group())
            else:
                item['stock_post'] = 0 
        elif web_field == 'fund2':
            item['stock_click'] = 0
            post = hxs.xpath('//div[@class="hang5"]/text()').extract()
            if post:
                post_num = re.search('(\d+)', post[0])
                if post_num:
                    item['stock_post'] = int(post_num.group())
            else:
                item['stock_post'] = 0
        item['date_delete'] = ""
        item['stock_url'] = response.url
        item['stock_lastcrawl'] = str(time.time())
        #return item
        r_url = "http://iguba.eastmoney.com/action.aspx?action=opopstock&code="+str(item['stock_id'])
        #return item
        yield Request(url=r_url, meta={'item':item}, callback = self.parse_click)
        
    def parse_click(self, response):
        item = response.meta['item']
        click_check = re.search('\"following\":\"(\d+)\"',response.body)
        if click_check:
            item['stock_click'] = click_check.group(1)
        else:
            item['stock_click'] = 0
        return item
            
            
        
                
            
            
        
        
        
        
