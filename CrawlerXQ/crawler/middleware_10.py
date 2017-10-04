# -*- coding: utf-8 -*-
import chardet
import random
import redis
import time
import winsound
import json
import crawler.scrapy_redis.connection
from datetime import datetime
import logging
from scrapy.selector import Selector
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.request import request_fingerprint
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.project import get_project_settings
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.xlib.tx import ResponseFailed


class RandomRequestHeaders(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents, cookies):
        self.agents = agents
        self.cookies = cookies

    @classmethod
    def from_crawler(cls, crawler):
        ua = crawler.settings.getlist('USER_AGENTS')
        ck = crawler.settings.getlist('COOKIES')
        return cls(ua, ck)

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))
#         request.cookies = random.choice(self.cookies)
        request.cookies = self.cookies[1]

class CustomRetryMiddleware(object):
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError)
    
    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.start_at=datetime.now()
        self.last_stop=datetime.now()
        self.host = 'localhost'
        self.port = 6379
        self.server=redis.Redis(host=self.host, port=self.port)
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
#         self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        self.priority_adjust = 1
        self.beep_frequency = 900  #900Hz
        self.beep_duration = 1000  #1s
        self.http_retry_times = 5
        self.http_retry_interval = 2  
        self.ban_retry_times = 999999999
        self.ban_retry_interval = 5   
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_response(self, request, response, spider):
        if 'dont_retry' in request.meta:
            return response

        #retry error_description
        if (response.body).find('error_description') >= 1:
            # webpage is coded with utf8 WITH BOM
            d_json=json.loads(response.body.decode("utf-8-sig"))
            if d_json['error_description']:
                # in python, d_json is represented as UNICODE while windows command line is coded as GBK. to match them, i save the scripts as GBK and transform the UNICODE string in json to GBK
                reason=d_json['error_description'].encode('utf-8')
                if reason=='用户不存在':
                    logging.info('User Not Exists: '+str(request))
                    raise IgnoreRequest
                elif reason=='该组合不存在':
                    # so many cubes not exists anymore, avoid output
                    # logging.info('Cube Not Exists: '+str(request))
                    raise IgnoreRequest
                elif reason=='用户未登录':
                    logging.info('User Not Login: '+str(request))
                    raise IgnoreRequest
                elif reason=='用户id无效':
                    logging.info('Invalid User ID: '+str(request))
                    raise IgnoreRequest
                elif reason=="无效的组合id":  # 原来参加实盘的人不参加了
                    logging.info('Invalid GWS/CUBE ID: '+str(request))
                elif reason=="请求分页超过了最大限制":  # cube_rb的实际页数小于json中的maxPage
                    logging.info('Out of max page: '+str(request))
                    raise IgnoreRequest
                elif reason=="Runtime unknown internal error":
                    logging.info("Runtime unknown internal error"+str(request))
                    raise IgnoreRequest
                else:
                    reason=reason.decode('utf-8').encode('gbk')
                    return self._retry(request, reason, spider, self.ban_retry_times, self.http_retry_interval) or response
            else:
                reason='UNKNOW ERROR: '+'\n      --'+response.body
                return self._retry(request, reason, spider, self.ban_retry_times, self.http_retry_interval) or response
            
        #retry ban
        # chardet.detect(response.body))==utf-8
        #d_json=json.loads(response.body)
        #logging.info(chardet.detect(d_json))
        if (response.body).find('请输入验证码 - 雪球')>=1:
            reason = 'BAN'
            
            # download captcha
            #hxs=Selector(response)
            #captcha_url=hxs.xpath("//div[@id='container']//div[@class='image']//@src").extract()
            if spider.name != 'TestSpider':
                return self._retry(request, reason, spider, self.ban_retry_times, self.ban_retry_interval) or response

        #retry lost-connection
        if str(response.body).find('http://net.zju.edu.cn')>=1:
            reason = 'ZJUWLAN Sign Out'
            return self._retry(request, reason, spider, self.ban_retry_times, self.ban_retry_interval) or response
        
        #retry http status error
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider, self.http_retry_times, self.http_retry_interval) or response
        
        #log status : 404
        if response.status == 404 :
            if (spider.name != 'XQCubeInfoSearch' and
                spider.name != 'XQUserInfo'):
                logging.info('STATUS ERROR : '+str(response.status)+' '+response.url)
        elif response.status==400 or response.status==502:
            logging.info('STATUS ERROR: '+str(response.status)+' '+response.url)

        #add to downloaded list
        if True:
            fp=request_fingerprint(request)
            self.server.sadd('%s:downloaded' % (spider.name), fp)
            return response
    
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and 'dont_retry' not in request.meta:
            return self._retry(request, exception, spider, self.http_retry_times, self.http_retry_interval)    
    
    def _retry(self, request, reason, spider, custom_retry_times, retry_interval):
        retries = request.meta.get('retry_times', 0) + 1
        winsound.Beep(self.beep_frequency,self.beep_duration)
        time.sleep(retry_interval)
        if retries <= custom_retry_times:
            logging.info("Retrying %(request)s \n(failed %(retries)d / %(max_retry)s times): %(reason)s"  
                   % {'request' : request, 'retries' : retries, 'reason' : reason, 'max_retry' : custom_retry_times})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            logging.info("Gave up retrying %(request)s \n(failed %(retries)d / %(max_retry)s times): %(reason)s" 
                   % {'request' : request, 'retries' : retries, 'reason' : reason, 'max_retry' : custom_retry_times+2})