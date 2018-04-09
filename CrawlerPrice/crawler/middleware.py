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
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError, TCPTimedOutError
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
                reason = 'Retry: currentPrice == 0 %s' % response.url
                logger.warn(reason)
                return self._retry(request, reason, spider) or response

        return response

class CustomHttpProxyMiddleware(object):
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError, TCPTimedOutError)

    def __init__(self):
        # 每隔一定时间，强制提取代理
        self.fetch_proxy_interval = 10
        # 当有效的proxy小于阈值时，强制提取代理
        self.extend_proxy_threshold = 1
        # 建立 redis 链接
        self.conn = util.set_redis_server()
        # 初始化proxy队列
        self.init_valid_proxy_ids()

    # 把redis中所有的"proxy:"键都重置
    def flush(self):
        keys = self.conn.keys('proxy:*')
        for k in keys:
            self.conn.delete(k.decode())

    # 初始化 proxy 队列，把redis中valid_proxy_ids清空
    def init_valid_proxy_ids(self):
        # 清空代理数据库？
        if PROXY_FLUSH_ON_START:
            self.flush()
        # 自上次更新大于1分钟，则重新抓取代理
        if not self.conn.get('proxy:last_fetch_time'):
            self.fetch_proxy_api()
        elif datetime.now() > datetime.strptime(self.conn.get('proxy:last_fetch_time').decode(), '%Y-%m-%d %H:%M:%S.%f') + timedelta(minutes = 1):
            self.fetch_proxy_api()

    # 提取代理，并更新至redis
    def fetch_proxy_api(self):
        #api链接
        api_url = "http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD201849617424AALc/c71b2df37db611e7bcaf7cd30abda612?returnType=2"

        with urllib.request.urlopen(api_url) as url:
            response = json.loads(url.read())

        if response['ERRORCODE'] == '0':
            ip = response['RESULT']['wanIp']
            port = response['RESULT']['proxyport']
            proxy = 'http://' + ip + ':' + port

            # update proxy:last_fetch_time:
            self.last_fetch_time = datetime.now()
            self.conn.set('proxy:last_fetch_time', self.last_fetch_time)

            # 返回1说明添加元素成功，继续populate其它的key；返回0说明已经有该proxy，不进行任何操作

            # 'proxy:' 记录 id 的最大值，自动递增
            # 'proxy:id - ip' 代理的 ip
            # 'proxy:id - count' 代理被使用的次数
            # 'proxy:id - success_count' 代理成功请求的次数
            # 'proxy:id - valid' 代理是否有效
            # 'proxy:id - last_use_time' 代理上次使用的时间
            # 'proxy:id - fetch_time' 代理从 API 中提取的时间

            if self.conn.sadd('proxy:exist_proxies', proxy) == 1:
                id = str(self.conn.incr('proxy:')) 
                # 这里使用了redis的事务
                pip = self.conn.pipeline()
                # populate key 'proxy:id'
                pip.hmset('proxy:' + id, {'ip':proxy, 'count':0, 'success_count':0, 'valid':True, 'fetch_time':self.last_fetch_time})
                # populate key: valid_proxy_ids. The score is 'success_count'
                pip.zadd('proxy:valid_proxy_ids', 0, id)
                pip.execute()

                logger.info('Fetch http API succeeded, get %s' % (proxy))
            
            else:
                logger.info('Duplicated proxy, try again!')
                time.sleep(1/4)
                self.fetch_proxy_api()

        else:
            logger.info("Fetch http API failed! Try again!")
            time.sleep(1/4)
            self.fetch_proxy_api()

        """
        # 更新 proxy_list
        api_url = "http://svip.kuaidaili.com/api/getproxy/?orderid=992308084790381&num=10&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=1&an_an=1&an_ha=1&sp1=1&sort=1&quality=2&format=json&sep=1&dedup=1"

        # 提取 API
        with urllib.request.urlopen(api_url) as url:
            p_list = json.loads(url.read()).get('data').get('proxy_list')

        if len(p_list) > 0:

            valid_proxy_num_before = self.conn.zcard('proxy:valid_proxy_ids')

            # update proxy:last_fetch_time:
            self.last_fetch_time = datetime.now()
            self.conn.set('proxy:last_fetch_time', self.last_fetch_time)

            for proxy in p_list:
                proxy = 'http://' + str(proxy)
                # 返回1说明添加元素成功，继续populate其它的key；返回0说明已经有该proxy，不进行任何操作

                # 'proxy:' 记录 id 的最大值，自动递增
                # 'proxy:id - ip' 代理的 ip
                # 'proxy:id - count' 代理被使用的次数
                # 'proxy:id - success_count' 代理成功请求的次数
                # 'proxy:id - valid' 代理是否有效
                # 'proxy:id - last_use_time' 代理上次使用的时间
                # 'proxy:id - fetch_time' 代理从 API 中提取的时间

                if self.conn.sadd('proxy:exist_proxies', proxy) == 1:
                    id = str(self.conn.incr('proxy:')) 
                    # 这里使用了redis的事务
                    pip = self.conn.pipeline()
                    # populate key 'proxy:id'
                    pip.hmset('proxy:' + id, {'ip':proxy, 'count':0, 'success_count':0, 'valid':True, 'fetch_time':self.last_fetch_time})
                    # populate key: valid_proxy_ids. The score is 'success_count'
                    pip.zadd('proxy:valid_proxy_ids', 0, id)
                    pip.execute()

            valid_proxy_num_after = self.conn.zcard('proxy:valid_proxy_ids')

            if valid_proxy_num_after > valid_proxy_num_before:
                logger.info('Fetch http API succeeded! Extend from %s proxeis to %s' % (valid_proxy_num_before, valid_proxy_num_after))
            else:
                logger.info('No new proxy fetched, try again!')
                time.sleep(0.5)
                self.fetch_proxy_api()

        else:
            logger.info("Fetch http API failed! Try again!")
            self.fetch_proxy_api()
        """

    # need to extend proxy?
    def check_extend_proxy(self):
        # 有效代理小于阈值，或者一定时间没有抓新的代理，扩展代理列表
        current_valid_proxy_num = self.conn.zcard('proxy:valid_proxy_ids')
        timedelta_from_last_fetch = round((datetime.now() - datetime.strptime(self.conn.get('proxy:last_fetch_time').decode(), '%Y-%m-%d %H:%M:%S.%f')).seconds/60, 1)

        if current_valid_proxy_num < self.extend_proxy_threshold or timedelta_from_last_fetch > self.fetch_proxy_interval:
            logger.info("Extend proxy, current has %s valid proxies, last update %s minutes ago" % (current_valid_proxy_num, timedelta_from_last_fetch))
            self.fetch_proxy_api()

    # 选择一个新的代理加入原有的request，并返回新的request
    def add_proxy(self, request):
        # 首先检查是否有足够的有效代理，如果不足，先进行提取
        self.check_extend_proxy()

        # 获得新的 proxy。在所有valid proxies中选择success_count最小的（被用得最少）
        id = self.conn.zrange('proxy:valid_proxy_ids', 0, 0, desc = False)[0].decode()

        proxy_id = 'proxy:' + id
        proxy = self.conn.hget(proxy_id, 'ip').decode()

        pip = self.conn.pipeline()
        # count + 1
        self.conn.hincrby(proxy_id, 'count')
        # update proxy:id - last_use_time
        self.conn.hset(proxy_id, 'last_use_time', datetime.now())
        pip.execute()

        success_count = self.conn.hget(proxy_id, 'success_count').decode()

        # 生成新的 request
        req = request.copy()
        req.dont_filter = True
        req.meta['proxy'] = proxy
        req.meta['proxy_id'] = id
        logger.debug("Use proxy:%s, success_count is %s" % (id, success_count))
        return req
    
    # 把当前无效的proxy设置为invalid
    def invalid_proxy(self, id, proxy):
        proxy_id = 'proxy:' + id
        success_count = self.conn.hget(proxy_id, 'success_count').decode()
        # set proxy:id - valid to False
        self.conn.hset(proxy_id, 'valid', False)
        # remove from valid 
        self.conn.zrem('proxy:valid_proxy_ids', id)

        logger.info("Failed: Proxy:%s, success_count %s, disable it" % (id, success_count))
                

    # 代理成功，增加success_count
    def valid_proxy(self, id, proxy):
        proxy_id = 'proxy:' + id
        
        pip = self.conn.pipeline()
        self.conn.hincrby(proxy_id, 'success_count')
        self.conn.zincrby('proxy:valid_proxy_ids', id)
        pip.execute()

        success_count = self.conn.hget(proxy_id, 'success_count').decode()
        logger.debug('Succeeded! Proxy:%s  (success_count %s) ' % (id, success_count))

    # 用于检测proxy是否返回一些奇怪的页面
    def detect_proxy_fail(self, response):
        m = re.search("Please try again later", response.body.decode('ISO-8859-1'))
        httperror = response.status in [500, 403, 502]
        return m or httperror

    # 如果spider.name == MMBHist，callback == parse.mult，且没采用代理，默认启用代理
    def process_request(self, request, spider):
        if spider.name == 'MMBHist' and spider.parse_mult == request.callback:
            if not request.meta.get('proxy'):
                return self.add_proxy(request)

    # 根据 response，决定是否采用/更换代理
    def process_response(self, request, response, spider):

        # 获得所用代理的 ip 和 id（如果有的话）
        proxy = request.meta.get('proxy')
        id = request.meta.get('proxy_id')

        # Banned
        if response.url == "http://www.manmanbuy.com/404.html" or response.status == 302:
            logger.debug("Banned! %s" % request.url)
            # use proxy but was banned, change to new proxy
            if proxy and id:
                # 将无用的代理设置为invalid
                self.invalid_proxy(id, proxy)
                # 使用新的代理重新发送一遍请求
                return self.add_proxy(request)

            # Banned but didn't use proxy, start to use proxy
            else:
                return self.add_proxy(request)

        # Not banned
        else:
            if proxy and id:
            # 如果使用了代理，且返回一些奇怪的页面（例如“please try again later”），则切换代理
                if self.detect_proxy_fail(response):
                    logger.info("Proxy:%s abnormal response, changed to new one." % id)
                    self.invalid_proxy(id, proxy)
                    return self.add_proxy(request)
            # 如果使用了代理，且返回正常，调用validproxy
                else:
                    self.valid_proxy(id, proxy)

            return response

    def process_exception(self, request, exception, spider):
        # 获得所用代理的 ip 和 id（如果有的话）
        proxy = request.meta.get('proxy')
        id = request.meta.get('proxy_id')

        if isinstance(exception, self.DONT_RETRY_ERRORS):
            logger.info("Timeout: Proxy:%s %s" % (id, request.url))
            self.invalid_proxy(id, proxy) 
            return self.add_proxy(request)

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
        new_request.dont_filter = True
        logger.debug("Use proxy to request %s" % new_request.url)
        return new_request

    def process_request(self, request, spider):
        # 在抓取 MMBHist 时，默认开启代理
        if spider.name == 'MMBHist' and spider.parse_mult == request.callback:
            if not request.meta.get('proxy'):
                return self.add_proxy(request)

    def process_response(self, request, response, spider):
        # 如果被ban，启用代理
        if response.url == "http://www.manmanbuy.com/404.html":
            logger.debug("Banned when requesting %s" % request.url)        
            return add_proxy(request)
            
        # 如果代理API请求太频繁，重新请求
        if response.status in [429]:
            logger.info("%s Request too frequently! Please slow down!" % response.status)
            return add_proxy(reqeust)

        # response正常，进入后续处理
        return response


