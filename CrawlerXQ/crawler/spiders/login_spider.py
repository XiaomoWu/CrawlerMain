# -*- coding: utf-8 -*-
from scrapy import signals
from scrapy.spider import BaseSpider
from scrapy.crawler import Crawler
from scrapy.exceptions import DontCloseSpider
from scrapy.utils.project import get_project_settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy.selector import Selector
from scrapy import log
from scrapy.utils.misc import load_object
import urlparse
import hashlib

class LoginSpider(BaseSpider):
    name = 'XQLoginSpider'
    
    start_urls = ['http://xueqiu.com']
        #super(LoginSpider, self).__init__(*args, **kwargs)

    def __init__(self, account):
        # 用户名与密码设置
        self.account = account
        self.count = len(account)
        log.msg("!!!!!!!THE NUMBER OF ACCOUNTS is " + str(self.count))
           

    def parse(self, response):
        if self.count == 0:
            return
        log.msg(response.status)
        login_url = 'http://xueqiu.com/S/SZ300104'
        r = Request(login_url, callback = self.parse_form, dont_filter = True)
        r.meta['dont_merge_cookies'] = True
        r.meta['handle_httpstatus_all'] = True
        log.msg("Raise request %s" % r)
        yield r

    def parse_login(self, response):
        if self.count == 0:
            return
        else:
            self.count -= 1
        # check login succeed before going on
        if response.status != 200:
            self.log("Login failed", level=log.ERROR)
        else:
            log.msg("*****************")
            log.msg(response.headers)
            h = response.headers.getlist('Set-Cookie', [])
            a = []
            f = open("cookie.info", "a")
            for i in h:
                log.msg("++++++++++++++++++++")
                log.msg(str(i))
                k = i.split(';')
                f.write(k[0].strip())
                f.write('\n')
            f.close()
        self.faction = 'http://xueqiu.com/user/login'
        user = self.account[self.count - 1].split(':')[0].strip()
        pwd = self.account[self.count - 1].split(':')[1].strip()
        slod = hashlib.md5(pwd).hexdigest().upper()
        r = FormRequest(
            url = self.faction,
            formdata = {
                'username' : user,
                'areacode' : '86',
                'password' : slod,
                'remember_me' : '1',
                'submit' : u'登 录',
                },
            callback = self.parse_login,
            )

        r.meta['dont_redirect'] = True
        r.meta['dont_merge_cookies'] = True
        r.meta['handle_httpstatus_all'] = True
        yield r


    def parse_form(self, response):
        try:
            hxs = Selector(response)
            #action = hxs.xpath(u'//*[@id="loginForm"]/@action').extract()[0]
            #log.msg(action)
            #self.faction = urlparse.urljoin(response.url, action)
            self.faction = 'http://xueqiu.com/user/login'
            user = self.account[self.count - 1].split(':')[0].strip()
            pwd = self.account[self.count - 1].split(':')[1].strip()
            slod = hashlib.md5(pwd).hexdigest().upper()
            r = FormRequest(
                url = self.faction,
                formdata = {
                    'username' : user,
                    'areacode' : '86',
                    'password' : slod,
                    'remember_me' : '1',
                    'submit' : u'登 录',
                    },
                callback = self.parse_login,
                )

            r.meta['dont_redirect'] = True
            r.meta['dont_merge_cookies'] = True
            r.meta['handle_httpstatus_all'] = True
            yield r

        except Exception, e:
            log.err()
