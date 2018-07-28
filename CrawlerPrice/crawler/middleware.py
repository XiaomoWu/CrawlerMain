# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import base64
import os
import random
import time
import json, urllib
import re
import redis
import logging
import urllib.request
from datetime import datetime, timedelta
from crawler.settings import *
from crawler.spiders import util
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from twisted.web._newclient import ResponseNeverReceived
from twisted.python.failure import Failure
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError, TCPTimedOutError, ConnectionDone
from crawler.spiders import util

logger = util.set_logger("http_proxy_middleware", LOG_FILE_MIDDLEWARE)

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
        
class CustomRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        # from Base RetryMiddleware
        if request.meta.get('dont_retry', False):
            return response

        # 对 MMBHist 的某些情况进行 retry
        # currentPrice == 0 时：
        if spider.name == "MMBHist" and request.callback == spider.parse:
            body = re.sub('[\s]', '', response.body.decode('gbk'))
            body = json.loads(body)
            if body['currentPrice'] == 0:
                reason = 'Retry: currentPrice is 0 %s' % response.url
                logger.warn(reason)
                return self._retry(request, reason, spider) or response

        return response

class CustomHttpTunnelMiddleware(object):
    def __init__(self):
        # 代理服务器
        self.proxy_server = "http://http-dyn.abuyun.com:9020"

        # 代理隧道验证信息
        # 别随便用老子花钱买的 API！
        proxy_user = "H28UQFV5946J854D"
        proxy_pass = "EAC3146D9528C257"
        auth = (proxy_user + ":" + proxy_pass).encode()
        self.proxy_auth = "Basic " + (base64.urlsafe_b64encode(auth)).decode()

    # 改造输入 request，增加代理
    def add_proxy(self, request):
        new_request = request.copy()
        new_request.meta["proxy"] = self.proxy_server
        new_request.headers["Proxy-Authorization"] = self.proxy_auth
        new_request.dont_filter = False
        logger.debug("Use proxy to request %s" % new_request.url)
        new_request.priority = new_request.priority + RETRY_PRIORITY_ADJUST
        time.sleep(HTTPPROXY_DELAY)
        return new_request

    def process_request(self, request, spider):
        # 在抓取 MMBHist 时，默认开启代理
        if spider.name == 'MMBHist' and spider.parse_mult == request.callback:
            if not request.meta.get('proxy'):
                return self.add_proxy(request)

    def process_response(self, request, response, spider):
        # 如果被ban，启用代理
        if response.url == "http://www.manmanbuy.com/404.html":
            logger.debug("Banned when requesting %s, use proxy now" % request.url)        
            return self.add_proxy(request)
            
        # 如果代理API请求太频繁，重新请求
        if response.status in [429]:
            logger.info("%s Please slow down!" % response.status)
            return self.add_proxy(request)

        # response正常，进入后续处理
        return response


    def process_exception(self, request, exception, spider):
        DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError, TCPTimedOutError, ConnectionDone)

        if isinstance(exception, (ConnectionDone)):
            logger.info("Error: ConnectionDone")
            return self.add_proxy(request)

        if isinstance(exception, DONT_RETRY_ERRORS):
            logger.info("Middleware Exception %s, %s" % (request.url, exception))
            return self.add_proxy(request)

