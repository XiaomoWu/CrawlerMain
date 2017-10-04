from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings

from crawler.spiders.GubaBBSPostSpider import GubaBBSPostSpider
from crawler.spiders.FundBBSPostSpider import FundBBSPostSpider
from crawler.spiders.GubaBBSStockSpider import GubaBBSStockSpider
from crawler.spiders.GubaBBSOfficialUserSpider import GubaBBSOfficialUserSpider
from crawler.spiders.SinaNewsSpider import SinaNewsSpider

import redis
import argparse

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
DUPEFILTER_KEY = '%(spider)s:dupefilter'

def run_spider(spider, log_file):
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    if log_file:
        log.start(log_file, logstdout=False)
    else:
        log.start(logstdout=False)
    log.msg('Running Crawler...', level=log.INFO)
    reactor.run() # the script will block here until the spider_closed signal was sent
    log.msg('Crawler stopped.\n', level=log.INFO)
    return

def overwrite_pool(spider_name):
    server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    print "DELETE %s" % spider_name
    server.delete(spider_name)

if __name__=='__main__':
    settings = get_project_settings()
    parser = argparse.ArgumentParser(description='Fin spider')
    parser.add_argument('-s', '--stock', action='store_true',
                        help='Crawl guba stock list.', default=False)
    parser.add_argument('-u', '--user', action='store_true',
                        help='Crawl guba official user list.', default=False)
    parser.add_argument('-gp', '--gpost', action='store_true',
                        help='Crawl guba post list.', default=False)
    parser.add_argument('-fp', '--fpost', action='store_true',
                        help='Crawl fund post list.', default=False)
    parser.add_argument('-sinanews', '--sinanews', action='store_true',
                        help='Crawl sina news.', default=False)
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Crawl post list.', default=False)
    args = parser.parse_args()
    if args.stock:
        spider = GubaBBSStockSpider()
        if args.overwrite:
            overwrite_pool(DUPEFILTER_KEY % {'spider':spider.name})
        log_file = settings['STOCK_LOG_FILE']
        run_spider(spider, log_file)
    elif args.user:
        spider = GubaBBSOfficialUserSpider()
        if args.overwrite:
            overwrite_pool(DUPEFILTER_KEY % {'spider':spider.name})
        log_file = settings['OUSER_LOG_FILE']
        run_spider(spider, log_file)
    elif args.gpost:
        spider = GubaBBSPostSpider()
        if args.overwrite:
            overwrite_pool(DUPEFILTER_KEY % {'spider':spider.name})
        log_file = settings['GPOST_LOG_FILE']
        run_spider(spider, log_file)
    elif args.fpost:
        spider = FundBBSPostSpider()
        if args.overwrite:
            overwrite_pool(DUPEFILTER_KEY % {'spider':spider.name})
        log_file = settings['FPOST_LOG_FILE']
        run_spider(spider, log_file)
    elif args.sinanews:
        spider = SinaNewsSpider()
        if args.overwrite:
            overwrite_pool(DUPEFILTER_KEY % {'spider':spider.name})
        log_file = settings['SINAPOST_LOG_FILE']
        run_spider(spider, log_file)
        #run_spider(spider, None)
    else:
        parser.print_usage()
