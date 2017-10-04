# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# Scrapy settings for crawler_test project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler_xq'

SPIDER_MODULES = ['crawler.spiders']
ITEM_PIPELINES = {
    'crawler.pipelines.XQPipeline':300,
}

DOWNLOADER_MIDDLEWARES = {
    'crawler.middleware.RandomRequestHeaders': 1,
  #  'crawler.middleware.HttpProxyMiddleware': 2,
#     'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 2,
  #  'crawler.middleware.CustomRetryMiddleware': 3,    
    #'crawler.scrapy_redis.pipelines.RedisPipeline': 2,
}
COOKIES_ENABLED = False

RETRY_ENABLED = True
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408]

COOKIES = [{'xq_a_token' : '5340e0ba441f75e15c2e40e508c3c87aaeb2bf68', 'xq_r_token' : '73735f5035a900e44e30ef73e194c8bf6dfc5f6c'}, {'xq_a_token':'cdd8894fa19a2a2678d2096ebd839e7dddebdf84', 'xqat':'cdd8894fa19a2a2678d2096ebd839e7dddebdf84', 'xq_r_token':'3663041b0aced6c9b7682195e91c5c4831d58eef',  'xq_is_login':1}]


USER_AGENTS = ["Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",]

#DOWNLOAD_DELAY = 0.25
DOWNLOADER_STATS = True
COOKIES_DEBUG = False

PRINT_LOG = True

#LOG_LEVEL = "DEBUG"
LOG_STDOUT = True # If True, all standard output (and error) of your process will be redirected to the log.  For example if you print 'hello' it will appear in the scrapy log.
#LOG_FILE = "C:/Users/rossz_000/OneDrive/Academy/Crawler/CrawlerXQ/"
#LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_ENABLED = True

import logging
import sys
logger = logging.getLogger("")
formatter = logging.Formatter('%(name)-4s %(asctime)s %(levelname)-6s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

DUPEFILTER_DEBUG = False

SQL_USER = 'root'
SQL_PWD = 'zju410'
SQL_DB = 'xueqiu'
SQL_HOST = 'localhost'
SQL_CHARSET = 'utf8'
SQL_UNICODE = True
SQL_PORT = 3306


# Enables scheduling storing requests queue in redis.
#SCHEDULER = "crawler.scrapy_redis.scheduler.Scheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
#SCHEDULER_PERSIST = True

# Schedule requests using a priority queue.  (default)
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).
# SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderQueue'

# Schedule requests using a stack (LIFO).
# SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderStack'

# Max idle time to prevent the spider from being closed when distributed
# crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time
# (because the queue is empty).
#SCHEDULER_IDLE_BEFORE_CLOSE = 10

# Specify the host and port to use when connecting to Redis (optional).
#REDIS_HOST = 'localhost'
#REDIS_HOST = '10.180.85.116'
#REDIS_PORT = 6379
