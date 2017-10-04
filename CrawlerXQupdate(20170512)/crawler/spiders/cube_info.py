# -*- coding: utf-8 -*-
from crawler.spiders import util
from scrapy.spiders import Spider
from datetime import datetime
from scrapy import Request
from scrapy.selector import Selector
from crawler.items import XQItem
from crawler.settings import *
from scrapy.utils.request import request_fingerprint
import re
import json
import time




class XQCubeInfoSpider(Spider):
    start_at=datetime.now()
    name='xq_cube_info_updt'
    logger = util.set_logger(name, LOG_FILE_CUBE_INFO)
    handle_httpstatus_list = [404]
    website_possible_httpstatus_list = [404]

    cube_type = 'ZH'


    def start_requests(self):
        start_url="https://xueqiu.com/p/"
        start_page = 1500000

        end_page = 2000000

        # iterate each page
        all_page_n = end_page - start_page + 1
        for i in range(start_page, end_page):
            now_page_n = i - start_page

            if self.cube_type == 'ZH':
                if i <= 999999:
                    symbol="ZH"+str(i).zfill(6)
                    url=start_url+symbol
                elif i >= 1000000:
                    symbol="ZH"+str(i).zfill(7)
                    url=start_url+symbol
            elif self.cube_type == 'SP':
                symbol = "SP"+str(i).zfill(7)
                url=start_url+symbol

            #自定义进度条
            if i%500==0:
                self.logger.info('%s (%s / %s)' % (symbol, str(now_page_n), str(all_page_n)))
                util.get_progress(now_page = now_page_n, all_page = all_page_n, logger = self.logger, spider_name = self.name, start_at = self.start_at)

            yield Request(url=url,
                                callback=self.parse, meta = {'cube_type':self.cube_type})


    def parse(self, response):
        try:
            #print(response.url)
            #print(response.status)
            if response.status == 200 and str(response.url) != "https://xueqiu.com/service/captcha":
                item=XQItem()
                hxs=Selector(response)
                info_script=''.join(hxs.xpath('//script[contains(., "cubeInfo")]//text()').extract())
                info_script = re.sub("[\s]", "", info_script)
                m=re.search("SNB.cubeInfo=({\S+?});SNB.cube", info_script)
                if m:
                    content = json.loads(m.group(1).strip())
                    content['lastcrawl'] = int(time.time())
                    content['cube_type'] = response.meta['cube_type']
                    item['content'] = content
                    item['fp'] = request_fingerprint(response.request)
                    item['url'] = response.url
                    yield item
            # 返回404，但是非验证码情况，说明对应的cube symbol不存在，这些url也要写入redis，避免下次再进行抓取
            elif response.status == 404 and str(response.url) != "https://xueqiu.com/service/captcha":
                item=XQItem()
                item['fp'] = request_fingerprint(response.request)
                item['url'] = response.url
                yield item
                #self.logger.warn('404: %s' % (str(response.url)))

            elif str(response.url) == "https://xueqiu.com/service/captcha":
                self.logger.error('CAPTURE ERROR: %s' % (response.url))

        except Exception as ex:
            self.logger.warn('Parse Exception: %s %s' % (str(ex), response.url))
