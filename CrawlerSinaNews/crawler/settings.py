# Scrapy settings for crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler_sinanews'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'
ITEM_PIPELINES = {
    'crawler.pipelines.SinaNewsPipeline': 100,
    'crawler.scrapy_redis.pipelines.RedisPipeline': 300,
}

#DOWNLOAD_DELAY = 0.25
DOWNLOADER_STATS = True
DUPEFILTER_DEBUG = False

COOKIES_ENABLED = False
DOWNLOADER_MIDDLEWARES = {
    'crawler.middleware.RandomUserAgent': 1,

}

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
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
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

#Cookies settings
DOWNLOADER_STATS = True
COOKIES_ENABLED = True
COOKIES_DEBUG = False
COOKIES = [{'xq_a_token': 'd63cbda98542f40f236036739b5f6cad61b56feb',
'xq_r_token': 'd63cbda98542f40f236036739b5f6cad61b56feb'}]

# Config Log
LOG_FILE_SINANEWS = 'C:/Crawler/CrawlerSinaNews/log-sinanews.log'
PRINT_LOG = True
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_ENABLED = True
LOG_STDOUT = False

# Enables scheduling storing requests queue in redis.
SCHEDULER = "crawler.scrapy_redis.scheduler.Scheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "crawler.scrapy_redis.dupefilter.RFPDupeFilter"

# Schedule requests using a priority queue. (default)
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderQueue'

# Schedule requests using a stack (LIFO).
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderStack'

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).
#SCHEDULER_IDLE_BEFORE_CLOSE = 10


# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

#MongoDB settings
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DBNAME = 'sinanews'
# mysql setting
#SQL_USER = 'root'
#SQL_PWD = 'Rosalie19900422'
#SQL_SINA_NEWS_DB = 'sinanews'
#SQL_HOST = 'localhost'
#SQL_CHARSET = 'utf8'
#SQL_UNICODE = True

# redis setting
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
DUPEFILTER_KEY = '%(spider)s:dupefilter'

# custom setting for spider
### Sina News
# {{{
# spider name
SINA_NEWS_SPIDER_NAME = 'SinaNewsSpider'

# allowed_domains
SINA_NEWS_ALLOWED_DONAIMS = [
    "www.sina.com.cn",
    ]

# start_urls(BaseSpider)
SINA_NEWS_START_URLS = [
    "",
    ]
SINA_NEWS_DATE = {
    'start':'2015-1-1',
    'end':'2015-2-1'
    }
SINA_NEWS_RSS_URLS = [
    "http://rss.sina.com.cn/rollnews/news_gn/",
    "http://rss.sina.com.cn/rollnews/news_sh/",
    "http://rss.sina.com.cn/rollnews/news_gj/",
    "http://rss.sina.com.cn/rollnews/sports/",
    "http://rss.sina.com.cn/rollnews/jczs/",
    "http://rss.sina.com.cn/rollnews/tech/",
    "http://rss.sina.com.cn/rollnews/ent/",
    "http://rss.sina.com.cn/rollnews/finance/",
    "http://rss.sina.com.cn/rollnews/stock/",
    ]
SINA_NEWS_REPLY_URL = "http://comment5.news.sina.com.cn/page/info?format=json&compress=1&ie=utf-8&oe=utf-8"
# stock type unknown
SINA_NEWS_STOCK_TYPE_UNKNOWN = 'Unknown'

# 404 redirect url
SINA_NEWS_404_URL = ''

# Item name
SINA_NEWS_ITEM_NAME = 'item_sina_news'
SINA_NEWSLIST_ITEM_NAME = 'item_sina_newslist'
SINA_NEWS_REPLY_ITEM_NAME = 'item_sina_news_reply'

# Item sql status
ITEM_SQL_UPDATE = 'update'
ITEM_SQL_INSERT = 'insert'
ITEM_SQL_DO_NOTHING = 'nothing'

# Error News item
SINA_NEWS_ERROR_ID = 'None'
SINA_NEWS_ERROR_TITLE = 'None'
SINA_NEWS_ERROR_AUTHOR = 'None'
SINA_NEWS_ERROR_AUTHORID = 'None'
SINA_NEWS_ERROR_CONTENT = 'Delete'
SINA_NEWS_ERROR_INFO_SOURCE = 'None'
SINA_NEWS_ERROR_STOCK_ID = 'None'
SINA_NEWS_ERROR_LASTCRAWL = '1900-01-01 00:00:00'
SINA_NEWS_ERROR_VALID = 'None'
SINA_NEWS_ERROR_REPLYNUM = 0
SINA_NEWS_ERROR_HOTNESS = 0
SINA_NEWS_ERROR_PUB_DATE = '1900-01-01 00:00:00'
SINA_NEWS_ERROR_INVALID = 0

SINA_NEWS_VALID = 1
SINA_NEWS_TABLE = 'news_'

# REPLY item
SINA_REPLY_NO_QUOTE = 'None'
SINA_REPLY_ERROR_AUTHOR = 'None'
SINA_REPLY_ERROR_AUTHORID = 'None'
SINA_REPLY_ERROR_CONTENT = 'Delete'
SINA_REPLY_ERROR_LASTCRAWL = '1900-01-01 00:00:00'
SINA_REPLY_ERROR_PUB_DATE = '1900-01-01 00:00:00'

SINA_NEWS_REPLY_TABLE = 'news_reply_'
# }}}
