from scrapy.spiders import Spider
from crawler.spiders import util
from scrapy.selector import Selector
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import GubaItem
from crawler.settings import *
from datetime import datetime, timedelta
import json
#import demjson
import time
import pymongo
import re   
import logging
import copy

class GubaSpider(Spider):
    name = 'CrawlerGuba'
    logger = util.set_logger(name, LOG_FILE_GUBA)

    def start_requests(self): 
        start_url = 'http://guba.eastmoney.com/remenba.aspx?type='
        for type in range(1,5):
            start_urls = start_url + str(type)
            yield Request(url = start_urls, meta = {'type' : type}, callback = self.parse)
    
     #解析一开始的网址
    def parse(self, response):
        type =  response.meta['type']
        hxs = Selector(response)
        
        #个股吧
        if type ==1:
            stocks = hxs.xpath('//div[@class="ngbglistdiv"]/ul[@class="ngblistul2"]/li/a').extract()
            fund_orgs = hxs.xpath('//div[@class="ngbglistdiv"]/ul[@class="ngblistul2"]/div[@class="ngbglistjjt"]/a').extract()
            funds = hxs.xpath('//div[@class="ngbglistdiv"]/ul[@class="ngblistul2"]/ul[@class="ngblistul3"]/li/a').extract()
        
            #爬取股票论坛的地址和名字          
            for stock in stocks:
                m_stocks = re.search('href="(.+)">(.+)<\/a', stock)
                if m_stocks:
                    item = GubaItem()
                    item['content'] = {}
                    url_stock = "http://guba.eastmoney.com/" + m_stocks.group(1)
                    item['content']['guba_url'] = url_stock
                    item['content']['guba_name'] = m_stocks.group(2)
                   
                    yield Request(url = url_stock, meta = {'item':item}, callback = self.parse_page_num)

            #爬取基金论坛母吧的地址和名字
            for fund_org in fund_orgs:
                m_fund_orgs = re.search('href="(.+)">(.+)<\/a', fund_org)
                if m_fund_orgs:
                    item = GubaItem()
                    item['content'] = {}
                    url_fund_org = m_fund_orgs.group(2)
                    item['content']['guba_url'] = url_fund_org
                    item['content']['guba_name'] = m_fund_orgs.group(2)
                    print(item)

                    yield Request(url = url_fund, meta = {'item':item}, callback = self.parse_page_num)

            #爬取基金论坛子吧的地址和名字
            for fund in funds:
                m_funds = re.search('href="(.+)">(.+)<\/a', fund)
                if m_funds:
                    item = GubaItem()
                    item['content'] = {}
                    url_fund = m_funds.group(2)
                    item['content']['guba_url'] = url_fund
                    item['content']['guba_name'] = m_funds.group(2)
        
                    yield Request(url = url_fund, meta = {'item':item}, callback = self.parse_page_num)
        
        #主题吧
        elif type ==2:
            stocks = hxs.xpath('//div[@class="allzhutilistb"]/ul/li/a').extract()
            for stock in stocks:
                m_stocks = re.search('href="(.+)">(.+)<\/a', stock)
                item = GubaItem()
                item['content'] = {}
                url_stock = "http://guba.eastmoney.com/" + m_stocks.group(1)
                item['content']['guba_url'] = url_stock
                item['content']['guba_name'] = m_stocks.group(2)

                yield Request(url = url_stock, meta = {'item':item}, callback = self.parse_page_num)
        
        #行业吧
        elif type ==3:
            stocks = hxs.xpath('//ul[@class="ngblistitemul"]/li/a').extract()
            for stock in stocks:
                m_stocks = re.search('href="(.+)">(.+)<\/a', stock)
                item = GubaItem()
                item['content'] = {}
                url_stock = "http://guba.eastmoney.com/" + m_stocks.group(1)
                item['content']['guba_url'] = url_stock
                item['content']['guba_name'] = m_stocks.group(2)

                yield Request(url = url_stock, meta = {'item':item}, callback = self.parse_page_num)

        #概念吧
        elif type ==4:
            stocks = hxs.xpath('//ul[@class="ngblistitemul"]/li/a').extract()
            for stock in stocks:
                m_stocks = re.search('href="(.+)">(.+)<\/a', stock)
                item = GubaItem()
                item['content'] = {}
                url_stock = "http://guba.eastmoney.com/" + m_stocks.group(1)
                item['content']['guba_url'] = url_stock
                item['content']['guba_name'] = m_stocks.group(2)

                yield Request(url = url_stock, meta = {'item':item}, callback = self.parse_page_num)
        

    #解析每个论坛的页数
    def parse_page_num(self, response):
        item = response.meta['item']
        #forum_url = response.meta['forum_url']
        hxs = Selector(response)
        
        p = hxs.xpath('//div[@class="pager"]/span/@data-pager').extract()[0]
        m = re.search('(l.*_)\|(.+)\|(.+)\|(.*)', p)
        postnums = m.group(2)
        heads = m.group(1)
        #sfnums = headnums.group(1)

        for postnum in postnums:
            item['content']['postnums'] = int(postnum)
            #item['content']['s&f_nums'] = sfnums
           
        if item['content']['postnums']%80 == 0:
            ptotal = item['content']['postnums']/80
        else:
            ptotal = int(item['content']['postnums']/80) + 1

        for i in range(int(ptotal)):
            p_url = "http://guba.eastmoney.com/"+heads +str(i)+".html"
            yield Request(p_url, meta = {'item':item}, callback = self.parse_post_list)
        

    #抓取每个子吧的帖子条数并翻页
    def parse_post_list(self, response):
        hxs = Selector(response)
        posts = hxs.xpath('//div[@class="articleh"]').extract()
        for post in posts:
            item = response.meta['item']
            readnum = Selector(text = post).xpath('//span[@class="l1"]/text()').extract()[0]
            replynum = Selector(text = post).xpath('//span[@class="l2"]/text()').extract()[0]
            url = Selector(text = post).xpath('//span[@class="l3"]/a/@href').extract()[0]
            guba_id = re.search(',(.+)_\d+\.html',response.url).group(1)
            
            if re.search(guba_id, url):
                #stock
                m_stock = re.search("(^\/.+)", url)
                if m_stock:
                    post_url = "http://guba.eastmoney.com" + m_stock.group(1)
                    post_id = re.search('\/(n.+)\.html', url).group(1)
                    item['content']['readnum'] = readnum
                    item['content']['replynum'] = replynum  
                    item['content']['post_id'] = post_id
                    yield Request(url = post_url, meta={'item': copy.deepcopy(item), 'replynum': replynum}, callback = self.parse_post)
          
                #fund
                m_fund= re.search("(^n.+)",url)
                if m_fund:
                    post_url = "http://guba.eastmoney.com/" + m_fund.group(1)
                    post_id = re.search('(n.+)\.html', url).group(1)
                    item['content']['readnum'] = readnum
                    item['content']['replynum'] = replynum  
                    item['content']['post_id'] = post_id
                    yield Request(url = post_url, meta = {'item':copy.deepcopy(item), 'replynum': replynum}, callback = self.parse_post)
                    #print(item)


    
    def parse_post(self, response):
        item = response.meta['item']
        hxs = Selector(response)

        dt = hxs.xpath('//div[@class="zwfbtime"]/text()').extract()[0]
        dt = re.search('\D+(\d{4}-\d{2}-.+:\d{2}).+',dt).group(1)
        creat_time = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        item['content']['create_time'] = creat_time
        
        postitle = hxs.xpath('//div[@class="zwcontentmain"]/div[@id="zwconttbt"]/text()').extract()[0].strip()
        item['content']['title'] = postitle
       
        author_url = hxs.xpath('//div[@id="zwconttbn"]/strong/a/@href').extract()[0]
        item['content']['author_url'] = author_url

        postcontent = hxs.xpath('//div[@id="zwconbody"]/div[@class="stockcodec"]/text()').extract()[0].strip()
        item['content']['content'] = postcontent

        replynum= response.meta['replynum']
        item['content']['reply'] = []
        if int(replynum)%30 == 0:
            rptotal = int(int(replynum)/30)
        
        else:
            rptotal = int(int(replynum)/30)+1   

        if rptotal>0:
            head = re.search('(.+)\.html', response.url).group(1)
            reply_url = head+"_"+str(1)+".html"
            yield Request(url = reply_url, meta = {'item': item, 'page':1, 'rptotal': rptotal, 'head': head}, callback = self.parse_reply)
        else:
            yield item
            #print(item)

    def parse_reply(self, response):
        page = response.meta['page']
        rptotal = response.meta['rptotal']
        item = response.meta['item']
        head = response.meta['head']
        hxs = Selector(response)

       
        replists =hxs.xpath('//div[@id="zwlist"]/div[@class="zwli clearfix"]').extract()
        for replist in replists:
            reply = {}
            try:
                reply_author = Selector(text = replist).xpath('//div[@class="zwlianame"]//a/text()').extract()[0]
                reply['reply_author'] = reply_author
            except:
                try:
                    reply_author = Selector(text = replist).xpath('//span[@class="gray"]/text()').extract()[0]
                    reply['reply_author'] = reply_author
                except Exception as ex:
                        print("Decode webpage failed: " + response.url)
                        return

            reply_time = Selector(text = replist).xpath('//div[@class="zwlitime"]/text()').extract()[0]
            reply_time = re.search('\D+(\d{4}-\d{2}-.+:\d{2})',reply_time).group(1)
            reply_time = datetime.strptime(reply_time, "%Y-%m-%d %H:%M:%S")
            reply['reply_time'] = reply_time
            
            reply_content = Selector(text = replist).xpath('//div[contains(@class, "stockcodec")]').extract()[0]
            reply_content = re.search('stockcodec">(.+)<\/div>', reply_content).group(1).strip()
            reply['reply_content'] = reply_content
        
            reply_quote_author = Selector(text = replist).xpath('//div[@class="zwlitalkboxuinfo"]//a/text()').extract()
            if reply_quote_author:
                reply_quote_author = reply_quote_author[0]
                reply['reply_quote_author'] = reply_quote_author

            reply_quote_author_url = Selector(text = replist).xpath('//div[@class="zwlitalkboxuinfo"]//a/@href').extract()
            if reply_quote_author_url:
                reply_quote_author_url = reply_quote_author_url[0]
                reply['reply_quote_author_url'] = reply_quote_author_url

            reply_quote_text = Selector(text = replist).xpath('//div[@class= "zwlitalkboxtext"]').extract()
            if reply_quote_text:
                reply_quote_text = reply_quote_text[0]
                reply_quote_content = re.search('"zwlitalkboxtext">(.+)<\/div>', str(reply_quote_text)).group(1)
                reply['reply_quote_content'] =  reply_quote_content

            reply_quote_timestamp = Selector(text = replist).xpath('//div[@class="zwlitalkboxtime"]/text()').extract()
            if reply_quote_timestamp:
                reply_quote_timestamp = re.search('\D+(\d{4}.+:\d{2})',reply_quote_timestamp[0]).group(1)
                reply_quote_timestamp = re.sub("/","-",  reply_quote_timestamp)
                reply_quote_time = datetime.strptime(str(reply_quote_timestamp), "%Y-%m-%d %H:%M:%S")
                reply['reply_quote_time'] = reply_quote_time
           
            item['content']['reply'].append(reply)
            
        if page == rptotal:
           yield item
        
        elif page < rptotal:
            reply_url = head+ "_" +str(page+1) +".html"
            yield Request(url = reply_url, meta = {'item':item, 'rptotal':rptotal, 'page': page+1, 'head': head}, callback = self.parse_reply)
    
