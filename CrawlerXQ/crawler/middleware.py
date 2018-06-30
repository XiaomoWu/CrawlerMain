# -*- coding: utf-8 -*-
import random
import redis
import time
import json
import base64
from crawler.settings import *
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from twisted.web._newclient import ResponseNeverReceived
from twisted.python.failure import Failure
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError, TCPTimedOutError, ConnectionDone
from datetime import datetime
from scrapy import signals
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
        #request.cookies = random.choice(self.cookies)
        request.cookies = self.cookies[0]

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
        request.meta["proxy"] = self.proxy_server
        request.headers["Proxy-Authorization"] = self.proxy_auth
        request.dont_filter = True
        logger.debug("Use proxy to request %s" % request.url)
        request.priority = request.priority + RETRY_PRIORITY_ADJUST
        #time.sleep(HTTPPROXY_DELAY)
        return request

    def process_request(self, request, spider):
        # 所有spider全都开启代理
        request.meta['proxy'] = self.proxy_server
        request.headers['Proxy-Authorization'] = self.proxy_auth            

    def process_response(self, request, response, spider):         
        # 如果代理API请求太频繁，重新请求
        if response.status in [429]:
            logger.info("%s Please slow down!" % response.status)
            return self.add_proxy(request)

        # response正常，进入后续处理
        return response

    def process_exception(self, request, exception, spider):
        print("process_exception_middleware")
        DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError, TCPTimedOutError, ConnectionDone)

        if isinstance(exception, (ConnectionDone)):
            logger.info("Error: ConnectionDone")
            return self.add_proxy(request)

        if isinstance(exception, DONT_RETRY_ERRORS):
            logger.info("Middleware Exception %s, %s" % (request.url, exception))
            return self.add_proxy(request)