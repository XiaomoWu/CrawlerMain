# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class CrawlerItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class GubaUserItem(Item):
    item_name = Field()
    user_id = Field()
    user_name = Field()
    web_field = Field()
    official = Field()
    date_first_post = Field()
    date_last_post = Field()
    sql_update = Field()

class GubaStockItem(Item):
    item_name = Field()
    stock_id = Field()
    stock_name = Field()
    stock_url = Field()
    web_field = Field()
    stock_click = Field()
    stock_post = Field()
    stock_tag = Field()
    stock_lastcrawl = Field()
    date_insert = Field()
    date_delete = Field()
    sql_update = Field()

class GubaPostListItem(Item):
    bbs_id = Field()
    bbs_url = Field()
    bbs_lastcrawl = Field()
    bbs_listnum = Field()
    bbs_valid = Field()

class GubaPostItem(Item):
    item_name = Field()
    post_id = Field()
    post_stock_id = Field()
    post_url = Field()
    post_view = Field()
    post_replynum = Field()
    post_title = Field()
    post_author = Field()
    post_authorid = Field()
    post_pubdate = Field()
    post_activedate = Field()
    post_content = Field()
    post_lastcrawl = Field()
    post_valid = Field()
    sql_update = Field()
    sticky = Field()
    official = Field()
    url_group = Field()
    
class GubaReplyItem(Item):
    item_name = Field()
    reply_id = Field()
    reply_li_id = Field()
    reply_post_id = Field()
    reply_date = Field()
    reply_floor = Field()
    replyer_id = Field()
    replyer_name = Field()
    reply_content = Field()
    reply_quote = Field()
    reply_lastcrawl = Field()
    sql_update = Field()
    web_field = Field()

class FundReplyListItem(Item):
    item_name = Field()
    item_list = Field()

class SinaNewsItem(Item):
    item_name = Field()
    news_id = Field()
    news_stock_id = Field()
    news_url = Field()
    news_sector_id = Field()
    news_hotness = Field()
    news_replynum = Field()
    news_title = Field()
    news_author = Field()
    news_pubdate = Field()
    news_content = Field()
    news_lastcrawl = Field()
    news_info_source = Field()
    news_valid = Field()
    news_table = Field()

class SinaNewsReplyItem(Item):
    item_name = Field()
    news_id = Field()
    reply_id = Field()
    content = Field()
    reply_lastcrawl = Field()
    reply_table = Field()
    
