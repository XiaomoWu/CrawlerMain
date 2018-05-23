import scrapy
from crawler.spiders import util
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
spider_name = 'MMB_' + util.make_date_str()
#spider_name = 'MMBHist'

process.crawl(spider_name)
process.start()
