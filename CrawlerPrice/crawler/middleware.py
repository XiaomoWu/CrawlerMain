# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os
import random
import redis
import time
import json, urllib
import re
import logging
import urllib.request
from datetime import datetime, timedelta
from crawler.settings import *
from crawler.spiders import util
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.utils.response import response_status_message
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from crawler.spiders import util


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
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        # Retry: currentPrice == 0
        if request.meta.get('retry'):
            reason = 'Retry: currentPrice == 0'
            print(reason)
            return self._retry(request, reason, spider) or response

        return response


class CustomHttpProxyMiddleware(HttpProxyMiddleware):
    logger = util.set_logger("http_proxy", LOG_FILE_PROXY)

    def __init__(self, settings):
        # 每隔一定时间，强制提取代理
        self.fetch_proxy_interval = 1
        # 初始化抓取时间
        self.last_fetch_time = datetime.now()
        # 当有效的proxy小于阈值时，强制提取代理
        self.extend_proxy_threshold = 10
        # 初始化代理列表
        self.proxy_list = [{'proxy': None, 'valid': True, 'count': 0}]

    def fetch_proxy_api(self):
        #api链接
        api_url = "http://svip.kuaidaili.com/api/getproxy/?orderid=942290935960629&num=9999&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=1&an_an=1&an_ha=1&sp1=1&sp2=1&quality=2&sort=1&format=json&sep=1"

        # 更新 last_fetch_time
        self.last_fetch_time = datetime.now()

        # 提取 API
        with urllib.request.urlopen(api_url) as url:
            p_list = json.loads(url.read()).get('data').get('proxy_list')

        # 更新 proxy_list
        if len(p_list) > 0:
            self.logger.info('Fetch http API succeeded!')
            proxy_list = []
            for proxy in p_list:
                proxy = 'http://' + proxy
                proxy_list.append({'proxy': proxy, 'valid': True, 'count': 0})
            return proxy_list
        else:
            self.logger.info("Fetch http API failed!")
            return self.fetch_http_api()

    # 返回现有proxy_list中有效代理的数量
    def len_valid_proxy(self):
        count = 0
        for p in self.proxy_list:
            if p['valid']:
                count += 1
        return count

    # 检查是否需要重新提取
    def check_fetch_new_proxy(self):
        # 如果超过了fetch_http_interval，或者现有的valid proxy太少，强制提取
        if datetime.now() > self.last_fetch_time + timedelta(minutes = self.fetch_proxy_interval) or self.len_valid_proxy() < self.extend_proxy_threshold:
            proxy_list = self.fetch_proxy_api()
            return proxy_list
        else:
            return self.proxy_list


    # 为 request 设置 proxy
    def set_proxy(self, request):
        proxy_list = self.proxy_list

        # 从现有代理列表中选出一个valid的proxy
        valid_proxy_list = []
        for p in proxy_list:
            if p['valid']:
                valid_proxy_list.append(p)
        valid_proxy = random.choice(valid_proxy_list)

        # 为request设置代理
        #self.logger.info("Set to proxy: %s" % valid_proxy)
        request.meta['proxy'] = valid_proxy['proxy']
        valid_proxy['count'] += 1 # 这里是shallow copy，valid_proxy更改，self.proxy_list也随之改变

    def process_request(self, request, spider):
        # 首先检查是否需要重新提取API
        self.proxy_list = self.check_fetch_new_proxy()

        # 如果 use_proxy = True, 设置代理
        if request.meta.get('use_proxy'):
            self.set_proxy(request)

        return

    # 检查 response.url，决定是更换proxy进行retry，还是正常进入下一流程
    def process_response(self, request, response, spider):
        if response.url == "http://www.manmanbuy.com/404.html" or response.status == 302:
            self.logger.info("Got 404/302: change proxy now")
            new_request = request.copy()
            new_request.dont_filter = True
            new_request.meta['user_proxy'] = True
            return new_request
        else:
            return response