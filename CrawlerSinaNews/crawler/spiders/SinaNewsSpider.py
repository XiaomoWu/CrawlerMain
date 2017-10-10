from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from crawler.items import SinaNewsItem
from crawler.settings import *
from crawler.spiders import util
from datetime import datetime, timedelta
import json
import time
import demjson
import pymongo
import re   
import logging

class SinaNewsSpider(Spider):
    name = "CrawlerSinaNews"
    logger = util.set_logger(name, LOG_FILE_SINANEWS)
    handle_httpstatus_list = [404]

    def start_requests(self):
        start_url = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=98&num=5010&date="    
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
                self.logger.info("Now crawl: " + url_date[i])
            yield Request(url = url, callback = self.parse)
    
    def parse(self, response):
        item = SinaNewsItem()
        body = re.sub("[\s]", "", response.body.decode("gbk"))
        m = re.search("varjsonData=({\S+?});", body)
        if m:
            js = demjson.decode(m.group(1).strip())
            for i in js['list']: 
                item['content'] = i
                if item['content']['time']:
                    item['content']['time'] = datetime.fromtimestamp(int(item['content']['time']))
                url = i['url']
                yield Request(url = url, callback = self.parse_content, meta = {'item' : item})
    
    # 抓取正文
    def parse_content(self, response):
        if response.status == 200:
            # 不抓取video、blog 、guba 以及 weibo 子域名
            if re.search("://.*video|://blog|://passport.weibo|://guba|://slide|://survey", response.url):
                return
            item = response.meta['item']
            # 老的页面可能用gbk/gb2312编码，新的页面一般用utf8编码，因此两种编码都要试一下
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

            # parse news_id 
            # news_id只可能来源于name="publishid"，如果不存在，则放弃该条新闻
            news_id = hxs.xpath('//head/*[@name="publishid"]/@content').extract()
            if news_id:
                item['content']['news_id'] = news_id[0]
            else:
                self.logger.info("No 'news_id'! Skip: %s" % (response.url))
                return

            # parse cmt_id
            # cmt_id可能来源于name="comment"（较新的网页），也可能来源于对html的正则解析（较旧的网页）
            cid = hxs.xpath('//head/*[@name="comment"]/@content').extract()
            if cid:
                # 新网页主要是这种格式
                d = cid[0].split(":")
                cmt_id = {"channel":d[0], "comment_id":d[1]}
                item['content']['cmt_id'] = cmt_id
                #print("cmt_id 1")
            else:
                # 旧网页主要是这种格式
                filter_body = re.sub("[\s]", "", filter_body)
                m = re.search('''channel:["'](.+?)["'],.*newsid:["'](.+?)['"]''', filter_body)
                if m:
                    cmt_id = {"channel":m.group(1), "comment_id":m.group(2)}
                    item['content']['cmt_id'] = cmt_id
                    #print("cmt_id 2")
                else:
                    # 个别特例
                    m = re.search('channel=(.+?)&newsid', filter_body)
                    if m:
                        cmt_id = {"channel":m.group(1), "comment_id":item['content']['news_id']}
                        item['content']['cmt_id'] = cmt_id
                        #print("cmt_id 3")
                    else:
                        self.logger.info("No 'cmt_id' found: %s" % (response.url))

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
            # cmt_id 包含了新闻的id和channel，用于生成reply_url
            if "cmt_id" in item['content']:
                reply_url_stat = "http://comment5.news.sina.com.cn/page/info?version=1&format=json&compress=1&ie=utf-8&oe=utf-8&page=1&page_size=20&channel=" + item['content']['cmt_id']['channel'] + "&newsid=" + item['content']['cmt_id']['comment_id']

                reply_url = "http://comment5.news.sina.com.cn/page/info?version=1&format=json&compress=1&ie=utf-8&oe=utf-8&page_size=100&channel=" +  item['content']['cmt_id']['channel'] + "&newsid=" +  item['content']['cmt_id']['comment_id'] + "&page="
        
                yield Request(url = reply_url_stat, meta = {'item':item, 'cmt_url':reply_url}, callback = self.parse_reply)
        
            # 如果解析不出comment reply，那么就不抓reply
            else:
                yield item

        elif response.status == 404:
            self.logger.error("Page 404: %s" % (response.url))
            return

    # parse_reply并不解析回复正文，只用来确定总回复数replynum，总翻页数rptotal等。解析回复正文在parse_reply_json
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

    # parse_reply_json才真正用来解析回复正文
    def parse_reply_json(self, response):
        item =  response.meta['item']
        cmt_url = response.meta['cmt_url']
        page = response.meta['page']
        rptotal = response.meta['rptotal']        

        d_json = json.loads(response.body.decode('utf8'))
        if d_json['result']:
            if 'cmntlist' in d_json['result']:
                # 如果reply_content是空的，说明page=1，直接赋值；否则说明page>1，使用extend方法
                if "reply_content" in item['content']['reply']:
                    item['content']['reply']['reply_content'].extend(d_json['result']['cmntlist'])
                else:
                    item['content']['reply']['reply_content'] = d_json['result']['cmntlist']

        # page为当前所处页面，直到page和总页数相等才停止抓取
        if page == rptotal:
            yield item
        elif page < rptotal:
            yield Request(url = cmt_url + str(page+1), meta = {'item':item, 'rptotal':rptotal, 'cmt_url':response.meta['cmt_url'], 'page':page+1}, callback = self.parse_reply_json)
        
    
