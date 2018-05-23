from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from crawler.spiders import util
from crawler.settings import *
from crawler.items import PriceItem
import json
import time
import pymongo
import re   
import logging
import copy
import datetime
import ast
import pytz
import copy


class MMBHistSpider(Spider):
    name = 'MMBHist'
    logger = util.set_logger(name, LOG_FILE_MMB)
    handle_httpstatus_list = [404, 460, 504]
    db = util.set_mongo_server()

    # 抓“一家在售”
    if_crawl_onestore = True
    # 抓“多家在售”
    if_crawl_multstore = False


    def start_requests(self): 

        #“一家在售”的商品
        if self.if_crawl_onestore:
            bjids = []
            for id in self.db["MMB"].find({'bjid': {'$exists': True}}, {'bjid': 1, '_id': 0}):
                bjids.append(id['bjid'])
            bjids = list(set(bjids))

            # iterate each bjid
            all_page_n = len(bjids)
            for i in range(all_page_n):

                bjid = bjids[i].strip()
                now_page_n = i

                url = "http://tool.manmanbuy.com/history.aspx?action=gethistory&bjid=" + str(bjid)

                # 进度条
                if i%500==0:
                    self.logger.info('一家在售：(%s / %s) %s%%' % (str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))

                yield Request(url = url, callback = self.parse)

        # “多家在售”的商品
        if self.if_crawl_multstore:
            p_infos = []
            # 挑出spid, name, url 不重复的记录
            pipeline = [
                {'$match':{'bjid':{'$exists':False}}},
                {'$group': {'_id': {'spid': '$spid', 'name': '$name', 'url': '$url'}}},
            ]
            cur = self.db.MMB.aggregate(pipeline)
            for i in cur:
                p_infos.append(i['_id'])

            all_page_n_mult = len(p_infos)
            for i in range(all_page_n_mult):
                p_info = p_infos[i]

                url = p_info['url']
                now_page_n = i

                # 进度条
                if i%500==0:
                    self.logger.info('多家在售： (%s / %s) %s%%' % (str(now_page_n), str(all_page_n_mult), str(round(float(now_page_n) / all_page_n_mult * 100, 1))))

                yield Request(url = url, meta = {"p_info":p_info}, callback = self.parse_mult)

            #yield Request(url = 'http://www.manmanbuy.com/pb_567731.aspx', meta = {"p_info":p_info}, callback = self.parse_mult)

    def parse_mult(self, response):
        try:
            if response.status == 200:
                # 把上一步的 item 传进来
                p_info = response.meta['p_info']

                # 解析同一个商品下的多家平台的链接
                nodes = response.xpath('//div[contains(@class, "pro-mall-list")]//ul//li//div[contains(@class, "item ")]')

                for n in nodes:
                    # 店铺名，不等于 siteName。例如同样siteName = 天猫。可以有sell_name = “vivo旗舰店”or “vivo天诚专卖店”
                    seller_name = n.xpath('div[contains(@class, "mall")]//text()').extract()
                    seller_name = ' '.join(' '.join(seller_name).split())
            
                    # get skuid
                    skuid = n.xpath('@skuid').extract()[0]

                    # get bjid
                    bjid = n.xpath('@v').extract()[0].strip()
                    bjid = ast.literal_eval(bjid)['bjid']

                    p_info.update({"seller_name":seller_name, "skuid":skuid, "bjid":bjid})

                    # 生成请求
                    url = "http://tool.manmanbuy.com/history.aspx?action=gethistory&bjid=" + str(bjid)

                    yield Request(url = url, meta = {"p_info":p_info}, callback = self.parse)

            else:
                self.logger.error('HTTP status not 200: %s \n %s' % (response.url, response.body))  
                
        except Exception as ex:
            self.logger.error('Parse Exception - "parse_mult": %s %s' % (str(ex), response.url))

    def parse(self, response):
        try:
            # 如果 200，按正常解析
            if response.status == 200:
                # 把上一步的 item 传进来(如果有)
                p_info = {}
                if "p_info" in response.meta:
                    p_info = response.meta['p_info']

                # 解析价格 json
                body = re.sub('[\s]', '', response.body.decode('gbk'))
                body = json.loads(body)

                # 在p_info中添加产品基本信息
                p_info.update({k: body[k] for k in ('siteName', 'siteId', 'zouShi', 'bjid', 'spName', 'spUrl', 'spbh', 'zouShi_test')})

                # p_hist 只包含价格/日期
                p_hist = body['datePrice']
                p_hist = re.findall("\[(.+?)\]", p_hist)

                # 把价格list“展开”
                docs = []
                lastcrawl = datetime.datetime.utcnow()
                for p in p_hist:
                    # date
                    m = re.search("Date.UTC\((.+?)\),([\d\.]+)", p)
                    if m:
                        date = m.group(1)
                        date = datetime.datetime.strptime(date, "%Y,%m,%d") - datetime.timedelta(hours = 8) # 把 strptime的结果转换成UTC
                    
                        # price
                        price = float(m.group(2).strip())
                        
                        # create doc and add to docs
                        doc = p_info
                        doc.update({"date":date, "price":price, "lastcrawl":lastcrawl})
                        docs.append(copy.deepcopy(doc))

                item = PriceItem()
                item['content'] = docs
                yield item
                    
            else:
                self.logger.error('Got %s: %s' % (response.status, response.url))

        except Exception as ex:
            self.logger.error('Parse Exception - "parse": %s %s' % (str(ex), response.url))
            self.logger.info(str(response.body))
