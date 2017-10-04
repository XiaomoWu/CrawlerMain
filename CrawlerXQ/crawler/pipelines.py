# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from crawler.settings import *
from datetime import datetime
import traceback
import MySQLdb
from scrapy import log

class CrawlerPipeline(object):
    pass

class XQPipeline(object):
    def __create_table_cube_info(self):
        self.cursor.execute('''create table if not exists xq_cube_info
                                        (cube_id varchar(20) not null,
                                        cube_symbol varchar(20) not null,
                                        cube_name varchar(40) default null,
                                        cube_description varchar(200) default null,
                                        active_flag int(5) default null,
                                        star int(10) default null,
                                        market varchar(20) default null,
                                        owner_id varchar(20) default null,
                                        created_at datetime not null,
                                        updated_at datetime not null,
                                        last_rb_id varchar(20) default null,
                                        daily_gain float(20) default null,
                                        monthly_gain float(20) default null,
                                        total_gain float(20) default null,
                                        net_value float(20) default null,
                                        rank_percent float(20) default null,
                                        annualized_gain_rate float(20) default null,
                                        bb_rate float(20) default null,
                                        following int(5) default null,
                                        follower_count int(10) default null,
                                        style_name varchar(20) default null,
                                        style_degree int(10) default null,
                                        tag varchar(40) default null,
                                        lastcrawl datetime not null,
                                        primary key (cube_symbol, cube_id)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg('Table "xq_cube_info" Created')
    def __create_table_cube_cmt(self):
        self.cursor.execute('''create table if not exists xq_cube_cmt
                                     (cube_symbol varchar(20) not null,
                                     cmt_id varchar(20) not null,
                                     cmt_creator_id varchar(20) default null,
                                     cmt_title varchar(350) default null,
                                     cmt_created_at datetime default null,
                                     retweet_count int(10) default null,
                                     reply_count int(10) default null,
                                     fav_count int(10) default null,
                                     truncated int(5) default null,
                                     commentId varchar(20) default null,
                                     retweet_status_id varchar(20) default null,
                                     cmt_symbol_id varchar(20) default null,
                                     cmt_type varchar(20) default null,
                                     cmt_edited_at datetime default null,
                                     fragment varchar(20) default null,
                                     blocked int(5) default null,
                                     blocking int(5) default null,
                                     topic_symbol varchar(20) default null,
                                     topic_title varchar(350) default null,
                                     topic_desc varchar(350) default null,
                                     donate_count int(10) default null,
                                     donate_snowcoin int(10) default null,
                                     cmt_view_count int(10) default null,
                                     cmt_mark int(10) default null,
                                     favorited int(5) default null,
                                     favorited_created_at datetime default null,
                                     comment varchar(20) default null,
                                     can_edit int(5) default null,
                                     expend int(5) default null,
                                     cmt_text text default null,
                                     cmt_source varchar(40) default null,
                                     lastcrawl datetime not null,
                                     primary key (cube_symbol, cmt_id)
                                     ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg('Table "xq_cube_cmt" Created')
    def __create_table_cube_rb(self):
        self.cursor.execute('''create table if not exists xq_cube_rb
                                        (cube_id varchar(10) not null,
                                        cube_symbol varchar(20) not null,
                                        rb_id varchar(20) not null,
                                        rb_status varchar(20) default null,
                                        prev_rb_id varchar(20) default null,
                                        rb_category varchar(40) default null,
                                        exe_strategy varchar(40) default null,
                                        rb_created_at datetime default null,
                                        rb_updated_at datetime default null,
                                        rb_cash float(10) default null,
                                        rb_error_code int(10) default null,
                                        rb_error_message varchar(100) default null,
                                        rb_error_status varchar(20) default null,
                                        rb_holdings varchar(40) default null,
                                        rb_id2 varchar(20) default null,
                                        rb_stock_id varchar(20) default null,
                                        rb_stock_name varchar(40) default null,
                                        rb_stock_symbol varchar(40) default null,
                                        rb_volume float(20) default null,
                                        rb_price float(20) default null,
                                        rb_net_value float(20) default null,
                                        rb_weight float(20) default null,
                                        rb_target_weight float(20) default null,
                                        rb_prev_weight float(20) default null,
                                        rb_prev_target_weight float(20) default null,
                                        rb_prev_weight_adjusted float(20) default null,
                                        rb_prev_volume float(20) default null,
                                        rb_prev_price float(20) default null,
                                        rb_prev_net_value float(20) default null,
                                        rb_proactive varchar(20) default null,
                                        lastcrawl datetime default null,
                                        primary key (cube_symbol, rb_id, rb_id2)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
    def __create_table_cube_ret(self):
        self.cursor.execute('''create table if not exists xq_cube_ret
                                        (cube_symbol varchar(20) not null,
                                        cube_name varchar(40) default null,
                                        date datetime not null,
                                        value float(20) default null,
                                        percent float(20) default null,
                                        lastcrawl datetime not null,
                                        primary key (cube_symbol, date)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_cube_ret' Created")
    def __create_table_stk_info(self):
        self.cursor.execute('''create table if not exists xq_stk_info
                                        (stk_id varchar(20) not null,
                                        stk_symbol varchar(20) not null,
                                        stk_name varchar(50) default null,
                                        stk_price float(20) default null,
                                        lastcrawl datetime not null,
                                        primary key (stk_id, stk_symbol)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_stk_info' Created")
    def __create_table_stk_cmt(self):
        self.cursor.execute('''create table if not exists xq_stk_cmt
                                     (stk_symbol varchar(20) not null,
                                     cmt_id varchar(20) not null,
                                     uid varchar(20) default null,
                                     cmt_title varchar(350) default null,
                                     cmt_created_at datetime default null,
                                     retweet_count int(10) default null,
                                     reply_count int(10) default null,
                                     fv_count int(10) default null,
                                     truncated boolean default null,
                                     commentId varchar(20) default null,
                                     retweet_status_id varchar(20) default null,
                                     cmt_symbol_id varchar(20) default null,
                                     cmt_type varchar(10) default null,
                                     cmt_edited_at datetime default null,
                                     fragment varchar(20) default null,
                                     blocked boolean default null,
                                     blocking boolean default null,
                                     topic_symbol varchar(20) default null,
                                     topic_title varchar(350) default null,
                                     topic_desc varchar(350) default null,
                                     donate_count int(10) default null,
                                     donate_snowcoin int(10) default null,
                                     cmt_view_count int(10) default null,
                                     cmt_mark int(10) default null,
                                     favorited boolean default null,
                                     favorited_created_at datetime default null,
                                     comment varchar(20) default null,
                                     can_edit boolean default null,
                                     expend boolean default null,
                                     cmt_text text default null,
                                     cmt_source varchar(40) default null,
                                     lastcrawl datetime not null,
                                     primary key (stk_symbol, uid, cmt_id)
                                     ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg('Table "xq_stk_cmt" Created')
    def __create_table_gws_info(self):
        self.cursor.execute('''create table if not exists xq_gws_info
                                        (gws_id varchar(20) not null,
                                        gws_type int(10) not null,
                                        gws_symbol varchar(20) default null,
                                        uid varchar(20) not null,
                                        group_id varchar(20) not null,
                                        client_id varchar(50) not null,
                                        created_at datetime not null,
                                        screen_name varchar(50) not null,
                                        assets_desc varchar(50) not null,
                                        monetary_unit varchar(20) default null,
                                        update_time datetime not null,
                                        lastcrawl datetime not null,
                                        distance varchar(10) default 'g_f_0',
                                        entry_at datetime default null,
                                        valid int(1) default null,
                                        primary key (uid,gws_id)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_gws_info' Created")
    def __create_table_gws_ret(self):
        self.cursor.execute('''create table if not exists xq_gws_ret
                                        (gws_id varchar(20) not null,
                                        gws_time datetime not null,
                                        gws_time_ms datetime not null,
                                        principal float(20) default null,
                                        cash float(20) default null,
                                        assets varchar(40) default null,
                                        market_value float(20) default null,
                                        shares varchar(40) default null,
                                        hold_percent float(20) default null,
                                        diluted_cost float(20) default null,
                                        hold_cost float(20) default null,
                                        accum_amount float(20) default null,
                                        accum_rate float(20) default null,
                                        float_amount float(20) default null,
                                        float_rate float(20) default null,
                                        day_amount float(20) default null,
                                        day_rate float(20) default null,
                                        week_amount float(20) default null,
                                        week_rate float(20) default null,
                                        month_amount float(20) default null,
                                        month_rate float(20) default null,
                                        quarter_amount float(20) default null,
                                        quarter_rate float(20) default null,
                                        year_amount float(20) default null,
                                        year_rate float(20) default null,
                                        uid varchar(20) not null,
                                        comment varchar(40) default null,
                                        update_time datetime not null,
                                        lastcrawl datetime default null,
                                        primary key (uid,update_time,gws_id)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_gws_ret' Created")
    def __create_table_gws_rb(self):
        self.cursor.execute('''create table if not exists xq_gws_rb
                                        (gws_id varchar(20) not null,
                                        uid varchar(20) not null,
                                        stk_symbol varchar(20) default null,
                                        stk_name varchar(40) default null,
                                        buy_sell int(1) not null,
                                        rb_price float(10) default null,
                                        rb_amount float(10) default null,
                                        rb_time datetime default null,
                                        lastcrawl datetime default null,
                                        primary key (uid,gws_id,stk_symbol,buy_sell,rb_price,rb_amount,rb_time)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_gws_rb' Created")
    def __create_table_gws_ret_day(self):
        self.cursor.execute('''create table if not exists xq_gws_ret_day
                                        (uid varchar(20) not null,
                                        group_id varchar(20) not null,
                                        value float(10) default null,
                                        update_time datetime default null,
                                        lastcrawl datetime default null,
                                        primary key (uid,group_id,update_time)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_gws_ret_day' Created")
    def __create_table_gws_ret_wk(self):
        self.cursor.execute('''create table if not exists xq_gws_ret_wk
                                        (uid varchar(20) not null,
                                        group_id varchar(20) not null,
                                        value float(10) default null,
                                        update_time datetime default null,
                                        wk_flg int(1) default null,
                                        lastcrawl datetime default null,
                                        primary key (uid,group_id,update_time)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_gws_ret_wk' Created")
    def __create_table_user_info(self):
        self.cursor.execute('''create table if not exists xq_user_info
                                        (subscribeable boolean default null,
                                        uid varchar(20) not null,
                                        status int(5) default null,
                                        common_count int(10) default null,
                                        remark varchar(40) default null,
                                        name varchar(40) default null,
                                        location varchar(40) default null,
                                        type varchar(5) default null,
                                        url varchar(200) default null,
                                        description varchar(1000) default null,
                                        domain varchar(40) default null,
                                        blocking boolean default null,
                                        screen_name varchar(40) default null,
                                        verified boolean default null,
                                        verified_type int(5) default null,
                                        st_color varchar(5) default null,
                                        allow_all_stock boolean default null,
                                        following boolean default null,
                                        donate_count int(10) default null,
                                        verified_description varchar(200) default null,
                                        status_count int(10) default null,
                                        last_status_id varchar(20) default null,
                                        follow_me boolean default null,
                                        friends_count int(10) default null,
                                        city varchar(40) default null,
                                        gender varchar(5) default null,
                                        followers_count int(10) default null,
                                        province varchar(40) default null,
                                        recommend varchar(200) default null,
                                        blog_description varchar(200) default null,
                                        step varchar(20) default null,
                                        intro varchar(200) default null,
                                        stock_status_count int(10) default null,
                                        stocks_count int(10) default null,
                                        group_ids varchar(20) default null,
                                        depth varchar(10) default null,
                                        lastcrawl datetime not null,
                                        primary key (uid, screen_name)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_user_info' Created")
    def __create_table_user_stocks(self):
        self.cursor.execute('''create table if not exists xq_user_stocks
                                        (uid varchar(20) not null,
                                        stk_symbol varchar(20) not null,
                                        comment varchar(200) default null,
                                        sell_price float(20) default null,
                                        buy_price float(20) default null,
                                        create_at datetime not null,
                                        target_percent float(10) default null,
                                        is_notice int(5) default null,
                                        stk_name varchar(50) default null,
                                        lastcrawl datetime not null,
                                        primary key (uid, stk_symbol, create_at)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_user_stocks' Created")
    def __create_table_user_favorites(self):
        self.cursor.execute('''create table if not exists xq_user_favorites
                                        (fv_uid varchar(20) not null,
                                        cmt_id varchar(20) not null,
                                        uid varchar(20) default null,
                                        cmt_title varchar(350) default null,
                                        first_add datetime default null,
                                        lastcrawl datetime not null,
                                        primary key (fv_uid, cmt_id, uid)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_user_favorites' Created")
    def __create_table_user_members(self):
        self.cursor.execute('''create table if not exists xq_user_members
                                        (mb_uid varchar(20) not null,
                                        uid varchar(20) not null,
                                        screen_name varchar(40) default null,
                                        first_add datetime default null,
                                        distance varchar(10) default null,
                                        lastcrawl datetime not null,
                                        primary key (mb_uid, uid)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_user_favorites' Created")
    def __create_table_user_followers(self):
        self.cursor.execute('''create table if not exists xq_user_followers
                                        (fl_uid varchar(20) not null,
                                        uid varchar(20) not null,
                                        screen_name varchar(40) default null,
                                        first_add datetime default null,
                                        lastcrawl datetime not null,
                                        primary key (fl_uid, uid)
                                        ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg("Table 'xq_user_favorites' Created")
    def __create_table_user_cmt(self):
        self.cursor.execute('''create table if not exists xq_user_cmt
                                     (cmt_id varchar(20) not null,
                                     uid varchar(20) default null,
                                     cmt_title varchar(350) default null,
                                     cmt_created_at datetime default null,
                                     retweet_count int(10) default null,
                                     reply_count int(10) default null,
                                     fv_count int(10) default null,
                                     truncated boolean default null,
                                     commentId varchar(20) default null,
                                     retweet_status_id varchar(20) default null,
                                     cmt_symbol_id varchar(20) default null,
                                     cmt_type varchar(10) default null,
                                     cmt_edited_at datetime default null,
                                     fragment varchar(20) default null,
                                     blocked boolean default null,
                                     blocking boolean default null,
                                     topic_symbol varchar(20) default null,
                                     topic_title varchar(350) default null,
                                     topic_desc varchar(350) default null,
                                     donate_count int(10) default null,
                                     donate_snowcoin int(10) default null,
                                     cmt_view_count int(10) default null,
                                     cmt_mark int(10) default null,
                                     favorited boolean default null,
                                     favorited_created_at datetime default null,
                                     comment varchar(20) default null,
                                     can_edit boolean default null,
                                     expend boolean default null,
                                     cmt_text text default null,
                                     cmt_source varchar(40) default null,
                                     lastcrawl datetime not null,
                                     primary key (uid, cmt_id)
                                     ) engine=innodb default charset=utf8mb4;''')
        self.conn.commit()
        log.msg('Table "xq_user_cmt" Created')
    
    
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.conn = MySQLdb.connect(host = SQL_HOST ,user=SQL_USER, passwd=SQL_PWD, db=SQL_DB, charset=SQL_CHARSET)
        self.cursor = self.conn.cursor()
        self.__create_table_cube_info()
        self.__create_table_cube_rb()
        self.__create_table_cube_ret()
        self.__create_table_stk_info()
        self.__create_table_stk_cmt()
        self.__create_table_gws_info()
        self.__create_table_gws_ret()
        self.__create_table_gws_ret_day()
        self.__create_table_gws_ret_wk()
        self.__create_table_gws_rb()
        self.__create_table_user_info()
        self.__create_table_user_stocks()
        self.__create_table_user_favorites()
        self.__create_table_user_members()
        self.__create_table_user_followers()
        self.__create_table_user_cmt()
        
    def process_item(self, item, spider):
        try:
            if item['item_name'] == 'xq_cube_info':
                self.process_cube_info_item(item)
            elif item['item_name'] == 'xq_cube_ret':
                self.process_cube_ret_item(item)
            elif item['item_name'] == 'xq_cube_rb':
                self.process_cube_rb_item(item)
            elif item['item_name'] == 'xq_cube_cmt':
                self.process_cube_cmt_item(item)
            elif item['item_name'] == 'xq_stk_info':
                self.process_stk_info_item(item)
            elif item['item_name'] == 'xq_stk_cmt':
                self.process_stk_cmt_item(item)
            elif item['item_name'] == 'xq_gws_info':
                self.process_gws_info_item(item)
            elif item['item_name'] == 'xq_gws_ret':
                self.process_gws_ret_item(item)
            elif item['item_name'] == 'xq_gws_ret_day':
                self.process_gws_ret_day_item(item)
            elif item['item_name'] == 'xq_gws_entry':
                self.process_gws_entry_item(item)
            elif item['item_name'] == 'xq_gws_rb':
                self.process_gws_rb_item(item)
            elif item['item_name'] == 'xq_user_info':
                self.process_user_info_item(item)
            elif item['item_name'] == 'xq_user_stocks':
                self.process_user_stocks_item(item)
            elif item['item_name'] == 'xq_user_favorites':
                self.process_user_favorites_item(item)
            elif item['item_name'] == 'xq_user_members':
                self.process_user_members_item(item)
            elif item['item_name'] == 'xq_user_followers':
                self.process_user_followers_item(item)
            elif item['item_name'] == 'xq_user_statuses':
                self.process_user_statuses_item(item)
            return item
        except :
            log.msg('MySQLdb Error: ')
            traceback.print_exc()
            
            
            
    def process_cube_info_item(self, item):
        self.cursor.execute("""replace into xq_cube_info 
                    (cube_id, cube_symbol, cube_name, cube_description, active_flag, 
                    star, market, owner_id, created_at, updated_at, 
                    last_rb_id, daily_gain, monthly_gain, total_gain, net_value,
                    rank_percent, annualized_gain_rate, bb_rate, following, follower_count,
                    style_name, style_degree, tag, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['cube_id'], item['cube_symbol'], item['cube_name'], 
                     item['cube_description'], item['active_flag'], item['star'],
                     item['market'], item['owner_id'], item['created_at'],
                     item['updated_at'], item['last_rb_id'], item['daily_gain'],
                     item['monthly_gain'], item['total_gain'], item['net_value'],
                     item['rank_percent'], item['annualized_gain_rate'], item['bb_rate'],
                     item['following'], item['follower_count'], item['style_name'],
                     item['style_degree'], item['tag'], item['lastcrawl']))
        
        self.conn.commit()
    def process_cube_ret_item(self, item):
        self.cursor.execute("""insert ignore xq_cube_ret 
                    (cube_symbol, cube_name, date, value, percent, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    ((item['cube_symbol']), (item['cube_name']), item['date'],
                     item['value'], item['percent'], item['lastcrawl']))
        self.conn.commit()
    def process_cube_rb_item(self, item):
        self.cursor.execute("""insert ignore into xq_cube_rb
                    (cube_id, cube_symbol, rb_id, rb_status, prev_rb_id,
                     rb_category, exe_strategy, rb_created_at, rb_updated_at, rb_cash,
                     rb_error_code, rb_error_message, rb_error_status, rb_holdings, rb_id2,
                     rb_stock_id, rb_stock_name, rb_stock_symbol, rb_volume, rb_price,
                     rb_net_value, rb_weight, rb_target_weight, rb_prev_weight, rb_prev_target_weight,
                     rb_prev_weight_adjusted, rb_prev_volume, rb_prev_price, rb_prev_net_value, rb_proactive,
                     lastcrawl
                     ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    ((item['cube_id']), (item['cube_symbol']), (item['rb_id']),
                     item['rb_status'], (item['prev_rb_id']), (item['rb_category']),
                     item['exe_strategy'], item['rb_created_at'], item['rb_updated_at'],
                     item['rb_cash'], item['rb_error_code'], item['rb_error_message'],
                     item['rb_error_status'], item['rb_holdings'], item['rb_id2'],
                     item['rb_stock_id'], item['rb_stock_name'], item['rb_stock_symbol'],
                     item['rb_volume'], item['rb_price'], item['rb_net_value'], 
                     item['rb_weight'], item['rb_target_weight'], item['rb_prev_weight'],
                     item['rb_prev_target_weight'], item['rb_prev_weight_adjusted'], item['rb_prev_volume'],
                     item['rb_prev_price'], item['rb_prev_net_value'], item['rb_proactive'],
                     item['lastcrawl']))
        self.conn.commit()
    def process_cube_cmt_item(self, item):
        self.cursor.execute("""replace into xq_cube_cmt
                    (cube_symbol, cmt_id, cmt_creator_id, cmt_title, cmt_created_at,
                     retweet_count, reply_count, fav_count, truncated, commentId,
                     retweet_status_id, cmt_symbol_id, cmt_type, cmt_edited_at, fragment,
                     blocked, blocking, topic_symbol, topic_title, topic_desc, donate_count,
                     donate_snowcoin, cmt_view_count, cmt_mark, favorited, favorited_created_at,
                     comment, can_edit, expend, cmt_text, cmt_source, 
                     lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['cube_symbol'], item['cmt_id'], item['cmt_creator_id'],
                     item['cmt_title'], item['cmt_created_at'], item['retweet_count'],
                     item['reply_count'], item['fav_count'], item['truncated'],
                     item['commentId'], item['retweet_status_id'], item['cmt_symbol_id'],
                     item['cmt_type'], item['cmt_edited_at'], item['fragment'], 
                     item['blocked'], item['blocking'], item['topic_symbol'],
                     item['topic_title'], item['topic_desc'], item['donate_count'],
                     item['donate_snowcoin'], item['cmt_view_count'], item['cmt_mark'],
                     item['favorited'], item['favorited_created_at'], item['comment'],
                     item['can_edit'], item['expend'],item['cmt_text'], 
                     item['cmt_source'], item['lastcrawl']))
        self.conn.commit()
    def process_stk_info_item(self, item):
        self.cursor.execute("""insert into xq_stk_info
                    (stk_id, stk_symbol, stk_name, stk_price, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['stk_id'], item['stk_symbol'], item['stk_name'],
                     item['stk_price'], item['lastcrawl']))
        #self.conn.commit()
    def process_stk_cmt_item(self, item):
        self.cursor.execute("""replace into xq_stk_cmt
                    (stk_symbol, cmt_id, uid, cmt_title, cmt_created_at,
                     retweet_count, reply_count, fv_count, truncated, commentId,
                     retweet_status_id, cmt_symbol_id, cmt_type, cmt_edited_at, fragment,
                     blocked, blocking, topic_symbol, topic_title, topic_desc, donate_count,
                     donate_snowcoin, cmt_view_count, cmt_mark, favorited, favorited_created_at,
                     comment, can_edit, expend, cmt_text, cmt_source, 
                     lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['stk_symbol'], item['cmt_id'], item['uid'],
                     item['cmt_title'], item['cmt_created_at'], item['retweet_count'],
                     item['reply_count'], item['fv_count'], item['truncated'],
                     item['commentId'], item['retweet_status_id'], item['cmt_symbol_id'],
                     item['cmt_type'], item['cmt_edited_at'], item['fragment'], 
                     item['blocked'], item['blocking'], item['topic_symbol'],
                     item['topic_title'], item['topic_desc'], item['donate_count'],
                     item['donate_snowcoin'], item['cmt_view_count'], item['cmt_mark'],
                     item['favorited'], item['favorited_created_at'], item['comment'],
                     item['can_edit'], item['expend'],item['cmt_text'], 
                     item['cmt_source'], item['lastcrawl']))
        self.conn.commit()
    def process_gws_info_item(self, item):
        self.cursor.execute("""insert into xq_gws_info
                    (gws_id, gws_type, gws_symbol, uid, group_id,
                     client_id, created_at, screen_name, assets_desc, monetary_unit,
                     update_time, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['gws_id'], item['gws_type'], item['gws_symbol'],
                     item['uid'], item['group_id'], item['client_id'],
                     item['created_at'], item['screen_name'], item['assets_desc'],
                     item['monetary_unit'], item['update_time'], item['lastcrawl']))
        self.conn.commit()
    def process_gws_ret_item(self, item):
        self.cursor.execute("""insert into xq_gws_ret
                    (gws_id, gws_time, gws_time_ms, principal, cash,
                     assets, market_value, shares, hold_percent, diluted_cost,
                     hold_cost, accum_amount, accum_rate, float_amount, float_rate,
                     day_amount, day_rate, week_amount, week_rate, month_amount,
                     month_rate, quarter_amount, quarter_rate, year_amount, year_rate,
                     uid, comment, update_time, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['gws_id'],item['gws_time'],item['gws_time_ms'],
                    item['principal'],item['cash'],item['assets'],
                    item['market_value'],item['shares'],item['hold_percent'],
                    item['diluted_cost'],item['hold_cost'],item['accum_amount'],
                    item['accum_rate'],item['float_amount'],item['float_rate'],
                    item['day_amount'],item['day_rate'],item['week_amount'],
                    item['week_rate'],item['month_amount'],item['month_rate'],
                    item['quarter_amount'],item['quarter_rate'],item['year_amount'],
                    item['year_rate'],item['uid'],item['comment'],
                    item['update_time'], item['lastcrawl']))
        self.conn.commit()
    def process_gws_ret_day_item(self, item):
        self.cursor.execute("""insert into xq_gws_ret_day
                    (uid, group_id, value, update_time, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['uid'],item['group_id'],item['day_rate'],
                    item['update_time'], item['lastcrawl']))
        self.conn.commit()
    def process_gws_entry_item(self, item):
        self.cursor.execute('''update xq_gws_info
                    set entry_date=%s
                    where uid=%s and group_id=%s''',
                    (item['entry_date'],item['uid'],item['group_id']))
        self.conn.commit()
    def process_gws_rb_item(self, item):
        self.cursor.execute("""insert into xq_gws_rb
                    (uid, gws_id, stk_symbol, stk_name, buy_sell,
                     rb_price, rb_amount, rb_time, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['uid'],item['gws_id'],item['stk_symbol'],
                    item['stk_name'],item['buy_sell'],item['rb_price'],
                    item['rb_amount'],item['rb_time'], item['lastcrawl']))
        self.conn.commit()
    def process_user_info_item(self, item):
        self.cursor.execute("""replace into xq_user_info
                    (subscribeable, status, common_count, remark, name, 
                    location, uid, type, url, description, 
                    domain, blocking, screen_name, verified, verified_type, 
                    st_color, allow_all_stock, following, donate_count, verified_description, 
                    status_count, last_status_id, follow_me, friends_count, city, 
                    gender, followers_count, province, recommend, blog_description, 
                    step, intro, stock_status_count, stocks_count, group_ids,
                    distance, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)""",
                    (item['subscribeable'], item['status'], item['common_count'], 
                     item['remark'], item['name'], item['location'], 
                     item['uid'], item['type'], item['url'], 
                     item['description'], item['domain'], item['blocking'], 
                     item['screen_name'], item['verified'], item['verified_type'], 
                     item['st_color'], item['allow_all_stock'], item['following'], 
                     item['donate_count'], item['verified_description'], item['status_count'], 
                     item['last_status_id'], item['follow_me'], item['friends_count'], 
                     item['city'], item['gender'], item['followers_count'], 
                     item['province'], item['recommend'], item['blog_description'], 
                     item['step'], item['intro'], item['stock_status_count'], 
                     item['stocks_count'], item['group_ids'], item['distance'],
                     item['lastcrawl']))
        self.conn.commit()
    def process_user_stocks_item(self, item):
        self.cursor.execute("""insert into xq_user_stocks
                    (uid, stk_symbol, comment, sell_price, buy_price,
                    create_at, target_percent, is_notice, stk_name, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['uid'], item['stk_symbol'], item['comment'], 
                     item['sell_price'], item['buy_price'], item['create_at'], 
                     item['target_percent'], item['is_notice'], item['stk_name'],
                     item['lastcrawl']))
        self.conn.commit()
    def process_user_favorites_item(self, item):
        self.cursor.execute("""insert into xq_user_favorites
                    (fv_uid, cmt_id, uid, cmt_title, distance, 
                    lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl), distance=values(distance)""",
                    (item['fv_uid'], item['cmt_id'], item['uid'], 
                     item['cmt_title'], item['distance'], item['lastcrawl']))
        #if item['if_commit']==True:
        #    self.conn.commit()
        self.conn.commit()

    def process_user_members_item(self, item):
        self.cursor.execute("""insert into xq_user_members
                    (mb_uid, uid, screen_name, distance,
                    lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl), distance=values(distance)""",
                    (item['mb_uid'], item['uid'], item['screen_name'], 
                     item['distance'], item['lastcrawl']))
        #if item['if_commit']==True:
        #    self.conn.commit()
        self.conn.commit()
    def process_user_followers_item(self, item):
        self.cursor.execute("""insert into xq_user_followers
                    (fl_uid, uid, screen_name, distance, lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s) on duplicate key update lastcrawl=values(lastcrawl), distance=values(distance)""",
                    (item['fl_uid'], item['uid'], item['screen_name'], 
                     item['distance'], item['lastcrawl']))
        #if item['if_commit']==True:
        #    self.conn.commit()
        self.conn.commit()
    def process_user_statuses_item(self, item):
        self.cursor.execute("""insert into xq_user_cmt
                    (cmt_id, uid, cmt_title, cmt_created_at,
                     retweet_count, reply_count, fv_count, truncated, commentId,
                     retweet_status_id, cmt_symbol_id, cmt_type, cmt_edited_at, fragment,
                     blocked, blocking, topic_symbol, topic_title, topic_desc, donate_count,
                     donate_snowcoin, cmt_view_count, cmt_mark, favorited, favorited_created_at,
                     can_edit, expend, cmt_text, cmt_source, 
                     lastcrawl) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    on duplicate key update lastcrawl=values(lastcrawl)""",
                    (item['cmt_id'], item['uid'],
                     item['cmt_title'], item['cmt_created_at'], item['retweet_count'],
                     item['reply_count'], item['fv_count'], item['truncated'],
                     item['commentId'], item['retweet_status_id'], item['cmt_symbol_id'],
                     item['cmt_type'], item['cmt_edited_at'], item['fragment'], 
                     item['blocked'], item['blocking'], item['topic_symbol'],
                     item['topic_title'], item['topic_desc'], item['donate_count'],
                     item['donate_snowcoin'], item['cmt_view_count'], item['cmt_mark'],
                     item['favorited'], item['favorited_created_at'],
                     item['can_edit'], item['expend'],item['cmt_text'], 
                     item['cmt_source'], item['lastcrawl']))
        self.conn.commit()

            
    def spider_opened(self, spider):
        log.msg("XQCubePipeline.spider_opened called")
    def spider_closed(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        log.msg("XQPipeline.spider_closed called")
