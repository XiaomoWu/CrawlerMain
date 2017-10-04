#import redis
import os
from scrapy import log, signals
from crawler.settings import *
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from crawler.spiders.xq_cube_info_spider import XQCubeInfoSpider
from crawler.spiders.xq_cube_ret_spider import XQCubeRetSpider
from crawler.spiders.xq_cube_cmt_spider import XQCubeCmtSpider
from crawler.spiders.xq_cube_rb_spider import XQCubeRBSpider
from crawler.spiders.xq_stk_info_spider import XQStkInfoSpider
from crawler.spiders.xq_stk_cmt_spider import XQStkCmtSpider
from crawler.spiders.xq_gws_info_spider import XQGwsInfoSpider
from crawler.spiders.xq_gws_ret_spider import XQGwsRetSpider
from crawler.spiders.xq_gws_ret_day_spider import XQGwsRetDaySpider
from crawler.spiders.xq_gws_rb_spider import XQGwsRbSpider
from crawler.spiders.xq_user_info_spider import XQUserInfoSpider
from crawler.spiders.xq_user_stocks_spider import XQUserStocksSpider
from crawler.spiders.xq_user_favorites_spider import XQUserFavorites
from crawler.spiders.xq_user_members_spider import XQUserMembers
from crawler.spiders.xq_user_followers_spider import XQUserFollowers
from crawler.spiders.xq_user_cmt_spider import XQUserCmtSpider

NOW_CRAWL = "cube_info"
OVERWRITE_POOL = True
OVERWRITE_LOG = True


def select_spider():
    if NOW_CRAWL == "test":
        return TestSpider()
    if NOW_CRAWL == "stk_info":
        return XQStkInfoSpider()
    elif NOW_CRAWL == "gws_info":
        return XQGwsInfoSpider()
    elif NOW_CRAWL == "gws_ret":
        return XQGwsRetSpider()
    elif NOW_CRAWL == "gws_ret_day":
        return XQGwsRetDaySpider()
    elif NOW_CRAWL == "gws_rb":
        return XQGwsRbSpider()
    elif NOW_CRAWL == "cube_info":
        return XQCubeInfoSpider()
    elif NOW_CRAWL == 'cube_rb':
        return XQCubeRBSpider()
    elif NOW_CRAWL == 'cube_ret':
        return XQCubeRetSpider()
    elif NOW_CRAWL == "user_info":
        return XQUserInfoSpider()
    elif NOW_CRAWL == "user_followers":
        return XQUserFollowers()
    elif NOW_CRAWL == "user_members":
        return XQUserMembers()
    elif NOW_CRAWL == "user_favorites":
        return XQUserFavorites()
    elif NOW_CRAWL == "user_stocks":
        return XQUserStocksSpider()
    elif NOW_CRAWL == "user_cmt":
        return XQUserCmtSpider()
    else:
        log.msg("NO SPIDER NAMED: " + NOW_CRAWL)

def run_spider(spider):
    settings = get_project_settings()
    crawler = CrawlerProcess(settings)
    #crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
   # crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    '''if log_file:
        log.start(log_file, logstdout=True)
    else:
        log.start(logstdout=True)
    logger.info("Running Crawler...")
    log.msg('Running Crawler...', level=log.INFO)
    reactor.run() # the script will block here until the spider_closed signal was sent
    log.msg('Crawler stopped.\n', level=log.INFO)'''
    return

def overwrite_pool(spider_name):
    server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    log.msg("DELETE REDIS POOL: %s" % spider_name)
    server.delete(spider_name + ":downloaded")
    server.delete(spider_name + ":requested")

if __name__ == '__main__':
    spider = select_spider()
    settings = get_project_settings()
    #log_file = settings['LOG_FILE'] + NOW_CRAWL + ".log"

    # overwrite pool / log
    #if OVERWRITE_POOL == True:
     #   overwrite_pool(spider.name)
    #if (OVERWRITE_LOG == True) and (os.path.exists(log_file) == True):
    #    log.msg("Cleaning Log...")
    #    os.remove(log_file)

    # run spider
    run_spider(spider)

