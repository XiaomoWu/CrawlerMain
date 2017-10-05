from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from crawler.items import SinaNewsItem
from crawler.settings import *
from datetime import datetime, timedelta
import json
import time
import demjson
import pymongo
import re   
import logging

class SinaNewsSpider(Spider):
    name = "CrawlerSinaNews"

    def start_requests(self):
        start_url = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=97,98,99&type=2,1&num=5000&date="    
        start_date = datetime.strptime("2010-01-01", "%Y-%m-%d").date()
        end_date = datetime.strptime("2017-09-30", "%Y-%m-%d").date()
        url_date = []
        
        s_d = start_date
        c_d = s_d.strftime("%Y-%m-%d")
        url_date.append(c_d)
        while s_d < end_date:
            s_d = s_d + timedelta(days=1)
            c_d = s_d.strftime("%Y-%m-%d")
            url_date.append(c_d)
        
        for i in range(len(url_date)):
            url = start_url + url_date[i]
            # 每抓取15天print log
            if i%15 == 0:
                print("Now crawl at: " + url_date[i])
            yield Request(url = url, callback = self.parse)
    
    def parse(self, response):
        item = SinaNewsItem()
        #print(type(response.body.decode("gbk")))
        #hxs = Selector(response)
        body = re.sub("[\s]", "", response.body.decode("GBK"))
        m = re.search("varjsonData=({\S+?});", body)
        if m:
            js = demjson.decode(m.group(1).strip())
            for i in js['list']: 
                item['content'] = i
                url = i['url']
                yield Request(url = url, callback = self.parse_content, meta = {'item' : item})

    def parse_content(self, response):
        item = response.meta['item']
        try:
            filter_body = response.body.decode('utf8')
        except Exception as ex:
            filter_body = response.body.decode("gbk")
        filter_body = re.sub('<[A-Z]+[0-9]*[^>]*>|</[A-Z]+[^>]*>', '', filter_body)
        response = response.replace(body = filter_body)
        hxs =Selector(response)

        # parse id
        news_id_from_comment = hxs.xpath('//head/*[@name="comment"]/@content').extract()
        news_id_from_publishid = hxs.xpath('//head/*[@name="publishid"]/@content').extract()
        if news_id_from_comment:
            item['content']['news_id'] = news_id_from_comment[0]              
        elif news_id_from_publishid:
            item['content']['news_id'] = news_id_from_publishid[0]
        else:
            print("No news_id !!!")
            print(response.url)
            return

        # keywords / tag
        key_words = hxs.xpath('//head/*[@name = "keywords"]/@content').extract()      
        if key_words:
            item['content']['keywords'] = key_words[0]  

        tags = hxs.xpath('//head/*[@name = "tags"]/@content').extract()      
        if tags:
            item['content']['tags'] = tags[0]

        # article create / update / publish time  
        create = hxs.xpath('//head/*[@name = "weibo: article:create_at"]/@content').extract()      
        if create:
            item['content']['news_create_time'] = create[0]
        update = hxs.xpath('//head/*[@name = "weibo: article:update_at"]/@content').extract()      
        if update:
            item['content']['news_update_time'] = update[0]
        publish = hxs.xpath('//head/*[@property = "article:published_time"]/@content').extract()      
        if publish:
            item['content']['news_publish_time'] = publish[0]

        # parse content
        content = hxs.xpath('//*[@id="artibody"]/p/text()').extract()
        if content:
            item['content']['content'] = "\n".join(content)
            item['url'] = response.url
        
        # parse source / author
        source = hxs.xpath('//head/*[@name="mediaid"]/@content').extract()
        if source:
            item['content']['source'] = source[0]

        author = hxs.xpath('//head/*[@property="article:author"]/@content').extract()
        if author:
            item['content']['author'] = author[0]        

        # parse reply
        # com 包含了新闻的id和channel，用于生成reply_url
        k =  item['content']['news_id'].split(':')
        cmt_id = {}

        if len(k) == 2:
            cmt_id['channel'] = k[0]
            cmt_id['news_id'] = k[1]
        
            reply_url_stat = "http://comment5.news.sina.com.cn/page/info?version=1&format=json&compress=1&ie=utf-8&oe=utf-8&page=1&page_size=20&channel=" + cmt_id['channel'] + "&newsid=" + cmt_id['news_id']

            reply_url = "http://comment5.news.sina.com.cn/page/info?version=1&format=json&compress=1&ie=utf-8&oe=utf-8&page_size=100&channel=" + cmt_id['channel'] + "&newsid=" + cmt_id['news_id'] + "&page="
        
            yield Request(url = reply_url_stat, meta = {'item':item, 'cmt_url':reply_url}, callback = self.parse_reply)
        
        # 如果解析不出comment reply，那么就不抓reply
        else:
            yield item

    # parse_reply并不解析回复正文，只用来确定总回复数，总翻页数等summary。解析回复正文在parse_reply_json
    def parse_reply(self, response):
        d_json = json.loads(response.body.decode('utf8'))
        item = response.meta['item']
        cmt_url = response.meta['cmt_url']
        
        try:
            reply = {}
            if d_json['result']:
                # 存在回复的情况
                if 'count' in d_json['result']:
                    reply['replynum'] = int(d_json['result']['count']['show'])
                    reply['hotness'] = int(d_json['result']['count']['total'])
                    reply['qreply'] = int(d_json['result']['count']['qreply']) # 并不知道qreply是什么
                    item['content']['reply'] = reply
        
                    # 确定需要翻页数        
                    rptotal = 0
                    if reply['replynum']%100 == 0:
                        rptotal = reply['replynum']/100
                    else:
                        rptotal = int(reply['replynum']/100) + 1

                    if rptotal > 0:
                        yield Request(url = cmt_url + str(1), meta = {'item':item, 'rptotal':rptotal, 'page':1,
                                        'cmt_url':cmt_url},callback = self.parse_reply_json)
                    else:
                        yield item

        # 不存在回复，直接返回item
        except Exception as ex:
            yield item

    def parse_reply_json(self, response):
        item = response.meta['item']
        cmt_url = response.meta['cmt_url']
        page = response.meta['page']
        rptotal = response.meta['rptotal']        

        d_json = json.loads(response.body.decode('utf8'))
        if d_json['result']:
            if 'cmntlist' in d_json['result']:
                if len(d_json['result']['cmntlist']) > 0:
                    item = response.meta['item']
                    item['content']['reply']['reply_content'] = d_json['result']['cmntlist']

        if rptotal > page:
            yield Request(url = cmt_url + str(page+1), meta = {'item':item, 'rptotal':rptotal,
                        'cmt_url':response.meta['cmt_url'], 'page':page+1}, callback = self.parse_reply_json)
        yield item
        
    
