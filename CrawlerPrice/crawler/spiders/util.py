from datetime import datetime
from crawler.settings import *
from scrapy_redis.defaults import REDIS_CLS
import pymongo
import logging

def set_redis_server():
    redis_server = REDIS_CLS(host = REDIS_HOST, port = REDIS_PORT)
    return redis_server

def set_mongo_server():
    conn = pymongo.MongoClient(host = MONGODB_HOST, port = MONGODB_PORT)
    return conn[MONGODB_DBNAME]

def set_logger(log_name, log_path):
    logger = logging.getLogger(log_name)
    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def get_crawled_n(spider_name):
    redis_server = set_redis_server()
    dup_key = spider_name +':dupefilter'
    return redis_server.scard(dup_key)

def get_progress(all_page, logger, spider_name, start_at):
    now = datetime.now()
    progress =round(float(get_crawled_n(spider_name))/all_page*100, 1)
    logger.info('Progress:%s%% %s' % (progress, str(now - start_at)))

import collections

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)