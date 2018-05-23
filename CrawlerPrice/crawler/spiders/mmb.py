from scrapy.spiders import Spider
from crawler.spiders import util
from scrapy.selector import Selector
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import PriceItem
from crawler.settings import *
from datetime import datetime, timedelta
import time
import pymongo
import re, os   
import logging
import copy


class MMBSpider(Spider):

    name = 'MMB_' + util.make_date_str()
    logger = util.set_logger(name, LOG_FILE_MMB)
    #handle_httpstatus_list = [404]
    #website_possible_httpstatus_list = [404]

    def start_requests(self): 
        start_url = 'http://home.manmanbuy.com/bijia.aspx'
        yield Request(url = start_url, callback = self.parse)

    # parse 用来抓首页入口
    def parse(self, response):
        sclass_block = response.xpath('//div[@class="sclassBlock"]')

        # 每个 ele 相当于一个 cat1
        for ele in sclass_block:
            item = PriceItem()
            item['content'] = {}
            # 例子：
            # cat1：大家电；cat2：冰箱
            # cat1 约113个；cat2 约 700 个；
            cat1_name = ele.xpath('div[@class="sclassLeft"]/text()').extract()
            # 有些类别有 cat1，极少数没有cat1，而是从 cat2 开始。对这类 cat2，为其 cat1 赋值为 ""
            if cat1_name:
                cat1_name = cat1_name[0]
            else:
                cat1_name = None
            item['content']['cat1_name'] = cat1_name

            # 每个 cat2 相当于一个 cat2
            for node in ele.xpath('div[@class="sclassRight"]/a'):
                cat2_name = node.xpath('text()').extract()
                if cat2_name:
                    cat2_name = cat2_name[0] 
                else:
                    cat2_name = node.xpath('font/text()').extract()[0] 
                item['content']['cat2_name'] = cat2_name
                
                cat2_url = node.xpath('@href').extract()[0]
                item['content']['cat2_url'] = cat2_url

                # 带有 book 的 url 是图书比价，排除
                if "book" not in cat2_url:
                    yield Request(url = cat2_url, meta = {'item':item}, callback = self.parse_item_list)

        #yield Request(url = "http://www.manmanbuy.com/list_1758.aspx", meta = {'item':item}, callback = self.parse_item_list)

    # parse_item_list 用来抓价格
    def parse_item_list(self, response):
        item_list = response.xpath('//div[contains(@class, "item")]')

        for item_node in item_list:
            # 如果有 price 这个节点才抓
            if len(item_node.xpath('div[contains(@class, "price")]')) != 0:
                # 建立 Item
                item = PriceItem()
                item['content'] = {}

                # lastcrawl
                item['content']['lastcrawl'] = datetime.utcnow()
                item['url'] = response.url

                # url
                item_url = item_node.xpath('div[contains(@class, "name")]/a/@href').extract()[0]
                # 如果url包含了http://www.manmanbuy.com，说明只有一个报价；如果类似p_32342.aspx，说明有多个报价
                m = re.search("http://www.manmanbuy.com", item_url)
                if not m:
                    item_url = "http://www.manmanbuy.com/"+item_url

                item['content']['url'] = item_url

                # name
                item_name = item_node.xpath('div[contains(@class, "name")]/a/text()').extract()[0]
                item['content']['name'] = item_name

                # price_status。有些火爆产品会具有一个@class="status" 的节点，内容多为“热卖”，有的则没有
                item_status_tmp = item_node.xpath('div[contains(@class, "status")]//text()').extract()
                if len(item_status_tmp) > 0:
                    item_status = item_status_tmp[0].strip()
                    item['content']['status'] = item_status

                # 价格。如果只有一家电商，网页直接显示当前价格；如果多家电商，网页显示最低价，并且旁边会标注“起”
                # item_price 记录的是“最低价”（多家电商）或“当前价格”（一家电商）；
                item_price = item_node.xpath('div[contains(@class, "price")]/text()').extract()
                item_price = float(''.join(item_price).strip())
                item['content']['price'] = item_price

                # price_source。如果是抓的，为“crawl”，如果是来自MMB的历史数据，则为“history”
                item['content']['price_source'] = "crawl"

                # item_price_multiple 是一个 flag，“0”表示“单一价格”（此时html具有节点 span[@class="pricedanjia"]），“1”表示“多个价格”（此时 html 具有 font[@class="pricestart"]）节点。
                # 如果不在上述情况中，打印错误：Unkown price status
                try:
                    if len(item_node.xpath('div[contains(@class, "price")]//span[contains(@class, "pricestart")]')) == 1: # 多家在售
                        item_price_multiple = True
                        # spid：只有“多家在售”的商品才有 spid，一个 spid 可能对应多个 bjid；“一家在售”的商品只有 bjid，无 spid。
                        item_spid = re.search("p_(.+?)\.asp", item_url).group(1).strip()
                        item['content']['spid'] = item_spid

                    elif len(item_node.xpath('div[contains(@class, "price")]//font[contains(@class, "pricedanjia")]')) == 1: # 一家在售
                            item_price_multiple = False

                            # 对于只有一家在售的商店，直接从 item_list 中提取 bjid
                            item_price_bjid = item_node.xpath('div[contains(@class, "price")]//a/@href').extract()[0]
                            m = re.search("bjid=(.+)&", item_price_bjid)
                            if m:
                                item_price_bjid = m.group(1).strip()
                                item['content']['bjid'] = item_price_bjid
                            #else:
                            #    self.logger.warn("bjid NOT found\n%s\n%s" % (item_price_bjid, response.url))
                    else:
                        item_price_multiple = None
                        self.logger.info("Unknown Price Status")

                    item['content']["price_multiple"] = item_price_multiple

                except Exception as ex:
                    self.logger.error('Parse Exception - MMB.parse.[@class=pricedanjia]: %s %s' % (str(ex), response.url))

                # 历史价格
                # item_price_multiple == False，那么直接在列表页就抓取历史价格


                # 在售电商名称。如果只有一个，直接给出名字（例如：京东商城）；如果有多个，给出数字（例如：7家电商比价）
                item_mall = item_node.xpath('div[contains(@class, "mall")]//text()').extract()
                item_mall = ' '.join(item_mall).strip()
                item['content']['mall'] = item_mall

                # 销售/评论数。如果多家电商在售，显示的是评论数（例如：全网有xxx人评论）；如果只有一家，显示的是销量（例如：月销量xxx件）
                item_sales = item_node.xpath('div[contains(@class, "sales")]//text()').extract()
                item_sales = ' '.join(item_sales).strip()
                item['content']['sales'] = item_sales

                # 返回 item
                yield item

        # 翻页
        next_page = response.xpath('//div[@class="pagination"]//a[text()="下一页"]/@href').extract()

        if len(next_page) > 0:
            next_page = "http://manmanbuy.com/" + next_page[0]
            yield Request(url = next_page, callback = self.parse_item_list)
