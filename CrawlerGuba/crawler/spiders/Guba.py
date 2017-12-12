from scrapy.spiders import Spider
from crawler.spiders import util
from scrapy.selector import Selector
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import GubaItem
from crawler.settings import *
from datetime import datetime, timedelta
import json
import time
import pymongo
import re   
import logging
import copy

class GubaSpider(Spider):
    name = 'CrawlerGuba'
    logger = util.set_logger(name, LOG_FILE_GUBA)
    #handle_httpstatus_list = [404]
    #website_possible_httpstatus_list = [404]

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
                    url_fund_org = m_fund_orgs.group(1)
                    item['content']['guba_url'] = url_fund_org
                    item['content']['guba_name'] = m_fund_orgs.group(2)
                    yield Request(url = url_fund_org, meta = {'item':item}, callback = self.parse_page_num)

            #爬取基金论坛子吧的地址和名字
            for fund in funds:
                m_funds = re.search('href="(.+)">(.+)<\/a', fund)
                if m_funds:
                    item = GubaItem()
                    item['content'] = {}
                    url_fund = m_funds.group(1)
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
        #print(item)
        #forum_url = response.meta['forum_url']
        hxs = Selector(response)
        p = hxs.xpath('//div[@id="mainbody"]//div[@class="pager"]//@data-pager').extract()[0]
        m = re.search('(.*_)\|(.*)\|(.+)\|(.*)', p)
        postnums = m.group(2)
        heads = m.group(1)
        #sfnums = headnums.group(1)

        item['content']['postnums'] = int(postnums)
            #item['content']['s&f_nums'] = sfnums
           
        if item['content']['postnums']%80 == 0:
            ptotal = item['content']['postnums']/80
        else:
            ptotal = int(item['content']['postnums']/80) + 1

        if int(ptotal) ==0:
            yield item
        else:
            for i in range(int(ptotal)):
                p_url = "http://guba.eastmoney.com/"+heads +str(i)+".html"
                yield Request(p_url, meta = {'item':item}, callback = self.parse_post_list)

        

    #抓取每个子吧的帖子条数并翻页
    def parse_post_list(self, response):
        hxs = Selector(response)
        posts = hxs.xpath('//div[@class="articleh"]').extract()
        item = response.meta['item']
        for post in posts:
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
        try:
            if response.status == 200:
                try:
                    filter_body = response.body.decode('utf8')
                except:
                    try:
                        filter_body = response.body.decode("gbk")
                    except:
                        try:
                            filter_body = response.body.decode("gb2312")
                        except Exception as ex:
                            print("Decode webpage failed: " + response.url)
                            return
                filter_body = re.sub('<[A-Z]+[0-9]*[^>]*>|</[A-Z]+[^>]*>', '', filter_body)
                response = response.replace(body = filter_body)
                hxs =Selector(response)

                item = response.meta['item']
                dt = hxs.xpath('//div[@class="zwfbtime"]/text()').extract()[0]
                dt = re.search('\D+(\d{4}-\d{2}-.+:\d{2})',dt).group(1)
                creat_time = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                item['content']['create_time'] = creat_time
               
                author_url = hxs.xpath('//div[@id="zwconttbn"]/strong/a/@href').extract()[0]
                item['content']['author_url'] = author_url
                try: #针对普通帖子
                    postcontent = hxs.xpath('//div[@id="zwconbody"]/div[@class="stockcodec"]/text()').extract()[0].strip()
                    if postcontent:
                        item['content']['content'] = postcontent

                    postitle = hxs.xpath('//div[@class="zwcontentmain"]/div[@id="zwconttbt"]/text()').extract()[0].strip()
                    item['content']['title'] = postitle
                except: #针对问答帖子
                    try:
                        postcontent = hxs.xpath('//div[@class="qa"]//div[contains(@class,"content")]/text()').extract()
                        postquestion = postcontent[0]
                        postanswer = postcontent[2].strip()+postcontent[3].strip()
                        item['content']['content'] = postquestion
                        item['content']['answer'] = postanswer

                        postanswer_time = hxs.xpath('//div[@class="sign"]/text()').extract()
                        try:
                            postanswer_time = hxs.xpath('//div[@class="sign"]/text()').extract()
                            postanswer_time = re.search('\D+(\d{4}-\d{2}-.+:\d{2})', postanswer_time[1].strip()).group(1)
                            answer_time = datetime.strptime(postanswer_time, "%Y-%m-%d %H:%M:%S")
                            item['content']['answer_time'] = answer_time
                        except Exception as ex:
                            item['content']['answer_time'] = None

                        postitle = "Q&A"
                        item['content']['title'] = postitle
                    except Exception as ex:
                        print("Parse Exception: " + response.url)
                        return

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

        except Exception as ex:
            self.logger.warn('Parse Exception all: %s %s' % (str(ex), response.url))

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
                reply_author_url = Selector(text = replist).xpath('//div[@class="zwlianame"]//a/@href').extract()[0]
                reply['reply_author_url'] = reply_author_url
            except:
                try:
                    reply_author = Selector(text = replist).xpath('//span[@class="zwnick"]/span').extract()[0]
                    reply_author = re.search('"gray">(.+)<\/span>', reply_author).group(1)
                    reply['reply_author'] = reply_author
                except Exception as ex:
                        print("Decode webpage failed: " + response.url)
                        return

            reply_time = Selector(text = replist).xpath('//div[@class="zwlitime"]/text()').extract()[0]
            reply_time = re.search('\D+(\d{4}-\d{2}-.+:\d{2})',reply_time).group(1)
            reply_time = datetime.strptime(reply_time, "%Y-%m-%d %H:%M:%S")
            reply['reply_time'] = reply_time
            
            reply_content = Selector(text = replist).xpath('//div[contains(@class, "stockcodec")]').extract()[0]
            try:
                reply_content = re.search('stockcodec">(.+)<', reply_content).group(1).strip()
                reply['reply_content'] = reply_content
            except Exception as ex:
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
    
