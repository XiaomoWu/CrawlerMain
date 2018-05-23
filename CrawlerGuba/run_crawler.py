import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
#spider_name = 'CrawlerGuba'
spider_name = 'CrawlerGubaExFund'
#spider_name = 'CrawlerGubaUserInfo'
#spider_name = 'CrawlerGubaReplyUserInfo'
process.crawl(spider_name)
process.start()
