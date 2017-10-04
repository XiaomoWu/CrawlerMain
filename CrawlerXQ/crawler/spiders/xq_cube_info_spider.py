#coding=utf-8
from scrapy.spider import Spider
from scrapy import log
from datetime import datetime
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import XQCubeItem
from datetime import datetime
from crawler.settings import *
import json, re
import sys
import winsound

class XQCubeInfoSpider(Spider):
    start_at=datetime.now()
    name='XQCubeInfoSearch'
    handle_httpstatus_list = [400,404,403,502]
    
    def start_requests(self):
        logger.debug("xq_cube_info_spider start_requests")
        start_url="http://xueqiu.com/p/"
        for i in xrange(10000, 50000):
            symbol="ZH"+str(i).zfill(6)
            url=start_url+symbol
            logger.info(symbol)
            if i%1000==0:
                now=datetime.now()
                logger.info('Processing: '+str(round(float(i)/1000000,3)*100)+'%  @'+str(now-self.start_at))
            yield Request(url=url,
                                   meta={'symbol':symbol},
                                   callback=self.parse)

    def parse(self, response):
        logger.debug("xq_cube_info_spider parse")
        try:
            if response.status == 200:
                item=XQCubeItem()
                item['item_name']='xq_cube_info'
                hxs=Selector(response)
                script=''.join(hxs.xpath('//script[contains(., "cubeInfo")]//text()').extract())
                script = re.sub("[\s]", "", script)
                m=re.search("SNB.cubeInfo=({\S+?})SNB.cube", script)
                if m:
                    cube_info=m.group(1).strip()
                    d_json=json.loads(cube_info)
                    if d_json['id']:
                        item['table_name']='xq_cube_info'
                        item['cube_id']=d_json['id']
                        item['cube_symbol']=d_json['symbol']
                        item['cube_name']=d_json['name']
                        item['cube_description']=d_json['description']
                        item['active_flag']=d_json['active_flag']
                        item['star']=int(d_json['star'])
                        item['market']=d_json['market']
                        item['owner_id']=d_json['owner_id']
                        item['created_at']=datetime.fromtimestamp(d_json['created_at']/1000)
                        item['updated_at']=datetime.fromtimestamp(d_json['updated_at']/1000)
                        item['last_rb_id']=d_json['last_rb_id']
                        item['daily_gain']=(d_json['daily_gain'])
                        item['monthly_gain']=(d_json['monthly_gain'])
                        item['total_gain']=(d_json['total_gain'])
                        item['net_value']=(d_json['net_value'])
                        item['rank_percent']=(d_json['rank_percent'])
                        item['annualized_gain_rate']=(d_json['annualized_gain_rate'])
                        item['bb_rate']=(d_json['bb_rate'])
                        item['following']=d_json['following']
                        item['follower_count']=int(d_json['follower_count'])
                        item['lastcrawl']=datetime.now()
                        item['tag']=None
                        item['style_name']=None
                        item['style_degree']=None
                        if d_json['style']:
                            item['style_name']=d_json['style']['name']
                            item['style_degree']=(d_json['style']['degree'])
                        if d_json['tag']:
                            tag=[]
                            for j in d_json['tag']:
                                tag.append(j.encode('utf8').strip())
                            item['tag']=' '.join(tag)
                        yield item
        except Exception, ex:
            logger.info('Parse Exception: '+str(ex)+' @ '+str(response.url)+'\n          --'+str(response.body))
           # winsound.Beep(900,999999999)