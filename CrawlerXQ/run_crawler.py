import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
# running the different spiders seperately
#spider_name = 'xq_cube_info_updt' # 
#spider_name = 'xq_cube_rb_updt'# 
spider_name = 'xq_cube_ret_updt'#
#spider_name = 'xq_cube_ret_updt_proxy'#
#spider_name = 'xq_user_fans_updt'# 
#spider_name = 'xq_user_follow_updt' # 
#spider_name = 'xq_user_info_updt' # 
#spider_name = 'xq_user_info_weibo_updt' # 
#spider_name = 'xq_user_stock_updt' #
#spider_name = 'xq_user_cmt_updt'
process.crawl(spider_name)
process.start()
