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

class ChinaVitaeSpider(Spider):
    name = 'CrawlerChinaVitae'
    logger = util.set_logger(name, LOG_FILE_CHINAVITAE)

    def start_requests(self):
        start_url = 'http://www.chinavitae.com/biography_browse.php?l='
        for i in range(97, 123):
            start_urls = start_url + chr(i)
            yield Request(url = start_urls, callback = self.parse)

    #crawl every name and of vitae
    def parse(self, response):
        hxs = Selector(response)
        names = hxs.xpath('//a[@class="link11"]').extract()
        if names:
            item = ChinaVitaeItem()
            item['content'] = {}
            item['content']['careers'] = []
            for name in names:
                name_pinyin = Selector(text = name).xpath('//a[@class="link11"]/text()').extract()[0]
                item['content']['name_pinyin'] = name_pinyin
                name_url = Selector(text = name).xpath('//a/@href').extract()[0]
                name_url = "http://www.chinavitae.com" + name_url + "/full"
                yield Request(url = name_url, meta = {'item': item}, callback = self.parse_biog)

    def parse_biog(self, response):
        item = response.meta['item']
     
        try: # Some of biography have no item with Chinese name
            name = response.xpath('//span[@style="font-family:Courier New, Courier, mono;"]/text()').extract()[0]
            item['content']['name'] = name
        except Exception as ex:
            print("With no Chinese name: " + response.url) 
        
        try: # title of the biography
            biotitle = response.xpath('//div[@class="bioTitle"]/text()').extract()[0]
            item['content']['biotitle'] = biotitle
        except Exception as ex:
            print("With no biotitle: " + response.url)
        
        try: # whole of biography
            bigph = response.xpath('//div[@id="dataPanel"]/p').extract()[0].strip()
            bigph = re.sub('\r\n', ' ', bigph)
            bigph = re.sub('<br>', '', bigph)
            bigph = re.search('<p>(.+)<\/p>', bigph).group(1)
            item['content']['biography'] = bigph
        except Exception as ex:
            print("With no bigph:" + response.url)

        try: #  borndate
            birth = response.xpath('//div[@class="bioDetails"]//text()').extract()
            if birth:
                birth = ' '.join(birth).strip()
                borndate = re.findall('\d+', birth)[0]
                item['content']['borndate'] = borndate
        except Exception as ex:
            print("With no borndate:" + response.url) 

        try: # birthplace
            birth = response.xpath('//div[@class="bioDetails"]//text()').extract()
            if birth:
                birth = ' '.join(birth).strip()
                birthplace = re.search('Birthplace:(.+)', birth).group(1)
                birthplace = re.sub(' ', '', birthplace)
                item['content']['birthplace'] = birthplace
        except Exception as ex:
            print("With no birthplace:" + response.url) 

        try: # Careers
            careers = response.xpath('//tr[@valign="top"]').extract()
            career = {}
            for c in careers:
                duration  = re.search('<td width="90" class="cdCell">(.+)<\/td>', c)
                if duration:
                    duration = re.sub("—", "-", duration.group(1))
                    career['duration'] = duration
                occupation = re.search('<strong>(.+)<\/strong>', c)
                if occupation:
                    career['occupation'] = occupation.group(1)
                branch = Selector(text = c).xpath('//a[contains(@class,"link11")]/text()').extract()           
                if branch:
                    career['branch'] = branch

                item['content']['careers'].append(copy.deepcopy(career))
        except Exception as ex:
            print("With no careers:" + response.url)
        
        yield item

        