# Scrapy settings for crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'
ITEM_PIPELINES = {
    'crawler.pipelines.GubaBBSPipeline': 300,
    'crawler.pipelines.SinaNewsPipeline': 301,
}

#DOWNLOAD_DELAY = 0.25

COOKIES_ENABLED = False
DOWNLOADER_MIDDLEWARES = {
    'crawler.middleware.RandomUserAgent': 1,
    #'crawler.scrapy_redis.pipelines.RedisPipeline': 2,
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

LOG_FILE = 'log.log'
STOCK_LOG_FILE = 'stock.log'
OUSER_LOG_FILE = 'ouser.log'
GPOST_LOG_FILE = 'gpost.log'
FPOST_LOG_FILE = 'fpost.log'
SINAPOST_LOG_FILE = 'sinapost.log'
PRINT_LOG = True
LOG_LEVEL = 'DEBUG'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "crawler.scrapy_redis.scheduler.Scheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderQueue'

# Schedule requests using a stack (LIFO).
#SCHEDULER_QUEUE_CLASS = 'crawler.scrapy_redis.queue.SpiderStack'

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).
SCHEDULER_IDLE_BEFORE_CLOSE = 10


# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# mysql setting
SQL_USER = 'root'
SQL_PWD = 'zju410'
SQL_DB = 'gubabbs'
SQL_SINA_NEWS_DB = 'sinanews'
SQL_HOST = 'localhost'
#SQL_CHARSET = 'utf8mb4'
SQL_CHARSET = 'utf8'
SQL_UNICODE = True


# custom setting for spider
### GubaBBS
# {{{
# spider name
GUBABBS_STOCK_SPIDER_NAME = 'GubaBBSStock Spider'

GUBABBS_POST_SPIDER_NAME = 'GubaBBSPost Spider'

GUBABBS_OFFICIAL_USER_SPIDER_NAME = 'GubaBBSOfficialUser Spider'

# allowed_domains
GUBABBS_ALLOWED_DONAIMS = [
    "guba.eastmoney.com",
    "fund2.eastmoney.com",
    "iguba.eastmoney.com",
    ]

# start_urls(BaseSpider)
GUBABBS_STOCK_START_URLS = [
    'http://guba.eastmoney.com/remenba.aspx?type=1',
    'http://guba.eastmoney.com/remenba.aspx?type=2',
    'http://guba.eastmoney.com/remenba.aspx?type=3',
    'http://guba.eastmoney.com/remenba.aspx?type=4',
    ]

GUBABBS_POST_START_URLS = [
    "http://guba.eastmoney.com/list,cjpl_%d.html" %
    (n) for n in range(1, 2)
    #'http://guba.eastmoney.com/list,000897_1.html',
    #'http://guba.eastmoney.com/list,600228_1.html',
    #'http://guba.eastmoney.com/list,cjpl.html',
    #'http://guba.eastmoney.com/list,gssz.html',
    #'http://guba.eastmoney.com/type,420.html',
    #'http://guba.eastmoney.com/type,429.html',
    #'http://guba.eastmoney.com/type,593.html',
    #'http://guba.eastmoney.com/type,499.html',
    ]
# stock type unknown
GUBABBS_STOCK_TYPE_UNKNOWN = 'Unknown'

# 404 redirect url
GUBABBS_404_URL = 'http://guba.eastmoney.com/404.aspx'

# post per page
GUBABBS_POST_PER_PAGE = 80
# reply per page
GUBABBS_REPLY_PER_PAGE = 40

# Item name
GUBABBS_USER_ITEM_NAME = 'item_user'
GUBABBS_STOCK_ITEM_NAME = 'item_stock'
GUBABBS_POST_ITEM_NAME = 'item_post'
GUBABBS_REPLY_ITEM_NAME = 'item_reply'

# Item sql status
ITEM_SQL_UPDATE = 'update'
ITEM_SQL_INSERT = 'insert'
ITEM_SQL_DO_NOTHING = 'nothing'

# POST item
GUBABBS_POST_STICKY = '1'
GUBABBS_POST_NOT_STICKY = '0'
GUBABBS_POST_OFFICIAL = '1'
GUBABBS_POST_NOT_OFFICIAL = '0'

# Error POST item
GUBABBS_POST_ERROR_TITLE = 'None'
GUBABBS_POST_ERROR_AUTHOR = 'None'
GUBABBS_POST_ERROR_AUTHORID = 'None'
GUBABBS_POST_ERROR_CONTENT = 'Delete'
GUBABBS_POST_ERROR_LASTCRAWL = '0'
GUBABBS_POST_ERROR_VALID = 'None'
GUBABBS_POST_ERROR_REPLYNUM = '0'
GUBABBS_POST_ERROR_OFFICIAL = '0'
GUBABBS_POST_ERROR_PUB_DATE = '1900-01-01 00:00:00'

# USER item
GUBABBS_USER_ERROR_POST_FIRST_DATE = '1900-01-01 00:00:00'
GUBABBS_USER_ERROR_POST_LAST_DATE = '1900-01-01 00:00:00'

# REPLY item
GUBABBS_REPLY_NO_QUOTE = 'None'
GUBABBS_REPLY_ERROR_AUTHOR = 'None'
GUBABBS_REPLY_ERROR_AUTHORID = 'None'
GUBABBS_REPLY_ERROR_CONTENT = 'Delete'
GUBABBS_REPLY_ERROR_LASTCRAWL = '0'
GUBABBS_REPLY_ERROR_PUB_DATE = '1900-01-01 00:00:00'

# }}}

### FundBBS
# {{{
# spider name
FUNDBBS_POST_SPIDER_NAME = 'FundBBSPost Spider'


# allowed_domains
FUNDBBS_ALLOWED_DONAIMS = [
    "fund2.eastmoney.com",
    ]

# start_urls(BaseSpider)
FUNDBBS_POST_START_URLS = [
    "http://fund2.eastmoney.com/default_%d.html" %
    (n) for n in range(1, 2)
    #'http://guba.eastmoney.com/list,000897_1.html',
    #'http://guba.eastmoney.com/list,600228_1.html',
    #'http://guba.eastmoney.com/list,cjpl.html',
    #'http://guba.eastmoney.com/list,gssz.html',
    #'http://guba.eastmoney.com/type,420.html',
    #'http://guba.eastmoney.com/type,429.html',
    #'http://guba.eastmoney.com/type,593.html',
    #'http://guba.eastmoney.com/type,499.html',
    ]

# Item name
FUNDBBS_REPLY_LIST_ITEM_NAME = 'item_reply_fund_list'

# post per page
FUNDBBS_POST_PER_PAGE = 40
# reply per page
FUNDBBS_REPLY_PER_PAGE = 50
# }}}

### Sina News
# {{{
# spider name
SINA_NEWS_SPIDER_NAME = 'SinaNews Spider'

# allowed_domains
SINA_NEWS_ALLOWED_DONAIMS = [
    "www.sina.com.cn",
    ]

# start_urls(BaseSpider)
SINA_NEWS_START_URLS = [
    "",
    ]
SINA_NEWS_DATE = {
    'start':'2014-8-10',
    'end':'2014-10-10'
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
