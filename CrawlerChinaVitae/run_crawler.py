import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
#spider_name = 'CrawlerChinaVitae'
spider_name = 'CrawlerVippear'
process.crawl(spider_name)
process.start()
