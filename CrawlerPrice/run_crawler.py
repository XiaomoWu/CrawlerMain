import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
#spider_name = 'MMB'
spider_name = 'MMBHist'

process.crawl(spider_name)
process.start()
