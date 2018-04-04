from scrapy.spiders import Spider
from crawler.spiders import util
from scrapy.selector import Selector
from scrapy import Request
from scrapy.utils.request import request_fingerprint
from crawler.items import ChinaVitaeItem
from crawler.settings import *
import pymongo
import re   
import logging
import copy

class VippearSpider(Spider):
    name = 'CrawlerVippear'
    logger = util.set_logger(name, LOG_FILE_VIPPEAR)

    def start_requests(self):
        start_url = 'http://www.chinavitae.com/vip/index.php?mode=officials&map=show&type=cv'
        yield Request(url = start_url, callback = self.parse)
        
    def parse(self, response):
         names = response.xpath('//td[@align="left"]//a[@class="link12"]').extract()
         for name in names:
            item = ChinaVitaeItem()
            item['content'] = {}
            name_pinyin = Selector(text = name).xpath('//a[@class="link12"]/text()').extract()[0]
            item['content']['name_pinyin'] = name_pinyin
            name_url = Selector(text = name).xpath('//a/@href').extract()[0]
            res_url = 'http://www.chinavitae.com/vip/'+name_url
            yield Request(url = res_url, meta = {'url': res_url, 'item': item}, callback = self.parse_year)

    def parse_year(self, response):
        year = response.xpath('//p/a/text()').extract()
        year = ' '.join(year).strip()
        years = re.findall('\d{4}', year)
        item = response.meta['item']

        for y in years:
            res_url = response.meta['url']
            yield Request(url = res_url+ '&filter_year='+y, meta ={'item': item}, callback = self.parse_list)

    def parse_list(self, response):
        urls = response.xpath('//div[@class="link12b"]/a/@href').extract()
        item = response.meta['item']
        for url in urls:
            vippurl = 'http://www.chinavitae.com'+url
            yield Request(url = vippurl, meta ={'item': item}, callback = self.parse_vipp)

    def parse_vipp(self, response):
        item = response.meta['item']

        acti = response.xpath('//html//tr[2]/td[2]').extract()[0]
        acti = re.sub('\r\n', '', acti)
        acti = re.search('td>(.+)<\/td', acti).group(1)
        item['content']['activity'] = acti

        infos = response.xpath('//*[contains(@class, "link12")]//text()').extract()
        infos = ','.join(infos).strip()
        infos = re.sub('\n', '', infos)
        infos = re.sub('\t', '', infos)

        date = re.search('Date: ,(.+),Activity', infos).group(1).strip()
        item['content']['date'] = date

        try:
            location = re.search('Location: ,(.+),Attendees', infos).group(1).strip()
            item['content']['location'] = location
        except Exception as ex:
            print("With no Location: " + response.url)

        try:
            attendees = re.search('Attendees: ,(.+),Source', infos).group(1).strip()
            item['content']['attendees'] = attendees
        except:
            try:
                attendees = re.search('Attendees: ,(.+),Topics', infos).group(1).strip()
                item['content']['attendees'] = attendees
            except:
                try:
                    attendees = re.search('Attendees: ,(.+)', infos).group(1).strip()
                    item['content']['attendees'] = attendees
                except Exception as ex:
                    print("With no Attendees: " + response.url)
                    
        try:
            source = re.search('Source: ,(.+),Topics', infos).group(1).strip()
            item['content']['source'] = source
        except Exception as ex:
            print("With no Source: " + response.url)

        try:
            topics = re.search('Topics: ,(.+)', infos).group(1).strip()
            item['content']['topics'] = topics
        except Exception as ex:
            print("With no Topics: " + response.url)

        yield item
         
        
