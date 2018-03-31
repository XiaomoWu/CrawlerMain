
from scrapy.spiders import Spider
from crawler.spiders import util
from scrapy.selector import Selector
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import PriceItem
from crawler.settings import *
import json
import time
import pymongo
import re   
import logging
import copy
import datetime


class MMBHistSpider(Spider):
    name = 'MMBHist'
    logger = util.set_logger(name, LOG_FILE_MMB)
    db = util.set_mongo_server()
    #handle_httpstatus_list = [404]
    #website_possible_httpstatus_list = [404]

    def start_requests(self): 
        
        # 首先处理只有“一家在售”的商品

        ids = []
        for id in self.db["MMB"].find({'price_multiple': False}, {'bjid': 1, '_id': 0}):
            ids.append(id['bjid'])
        ids = list(set(ids))

        # iterate each bjid
        all_page_n = len(ids)
        for i in range(all_page_n):
            bjid = ids[i].strip()
            now_page_n = i

            url = "http://tool.manmanbuy.com/history.aspx?action=gethistory&bjid=" + bjid

            # 进度条
            if i%500==0:
                self.logger.info('一家在售：(%s / %s) %s%%' % (str(now_page_n), str(all_page_n), str(round(float(now_page_n) / all_page_n * 100, 1))))

            #yield Request(url = url, meta = {'bjid':bjid}, callback = self.parse)

        # 然后处理“多家在售”的商品
        urls = []
        for u in self.db["MMB"].find({'price_multiple': True}, {'url': 1, 'spid': 1, 'name': 1, '_id': 0}):
            urls.append(u)

        all_page_n_mult = len(urls)
        for i in range(all_page_n_mult):
            url = urls[i]['url']
            now_page_n = i

            # 进度条
            if i%500==0:
                self.logger.info('多家在售： (%s / %s) %s%%' % (str(now_page_n), str(all_page_n_mult), str(round(float(now_page_n) / all_page_n_mult * 100, 1))))

            #yield Request(url = url, meta = urls[i], callback = self.parse_mult)

        yield Request(url = "http://www.manmanbuy.com/pb_569170.aspx", callback = self.parse_mult)

    def parse_mult(self, response):
        
        nodes = response.xpath('//div[contains(@class, "pro-mall-list")]//ul//li')

        #pro = response.xpath('//div[contains(@class, "pro-mall-list")]//ul//li//div[contains(@class, "item")]').extract()
        #print(pro)
        
        for n in nodes:
            seller_name = n.xpath('div[contains(@class, "item ")]//div[contains(@class, "mall")]//text()').extract()
            sell_name = ' '.join(' '.join(seller_name).split())
            print(sell_name)


            #n.xpath('/div[contains(@class="subitem")]//div[contains(@class="item singlebj")]')


    def parse(self, response):
        try:
            if response.status == 200:
                body = re.sub('[\s]', '', response.body.decode('gbk'))
                body = json.loads(body)
                item = PriceItem()
                item['url'] = response.url
                item['lastcrawl'] = datetime.datetime.utcnow()

                # p_info 包含除价格/日期外的所有
                p_info = {k: body[k] for k in ('siteName', 'siteId', 'zouShi', 'bjid', 'spName', 'spUrl', 'spbh', 'zouShi_test')}
                #print(p_info)

                # p_hist 只包含价格/日期
                p_hist = body['datePrice']
                p_hist = re.findall("\[(.+?)\]", p_hist)
                
                for p in p_hist:
                    # date
                    m = re.search("Date.UTC\((.+?)\),([\d\.]+)", p)
                    date = m.group(1)
                    date = datetime.datetime.strptime(date, "%Y,%m,%d")
                    
                    # price
                    price = float(m.group(2).strip())

                    # add date and price to p_info, then write to item['content']
                    obs = p_info
                    obs.update({"date":date, "price":price})
                    item['content'] = obs

                    return item

            else:
                self.logger.error('HTTP status not 200: %s' % (response.meta['bjid']))

        except Exception as ex:
            self.logger.error('Parse Exception: %s %s' % (str(ex), response.url))
            self.logger.info(str(response.body))
