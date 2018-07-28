import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
#spider_name = 'guba_stock_posts'
#spider_name = 'guba_user_info'
spider_name = 'guba_reply_user_info'
process.crawl(spider_name)
process.start()
