import time
import connection
import random
from scrapy import log

from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint


class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplication filter"""

    def __init__(self, server, requested_key, downloaded_key):
        """Initialize duplication filter

        Parameters
        ----------
        server : Redis instance
        requested_key : str
        downloaded_key : str
            Where to store fingerprints
        """
        self.server = server
        self.requested_key = requested_key
        self.downloaded_key = downloaded_key

    @classmethod
    def from_settings(cls, settings):
        server = connection.from_settings(settings)
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        key = "dupefilter:%s" % int(time.time())
        return cls(server, key)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        fp = request_fingerprint(request)
        add_request = self.server.sadd(self.requested_key, fp)
        if_downloaded = self.server.sismember(self.downloaded_key, fp)
        if if_downloaded == 1:
            return True
        elif if_downloaded == 0:
            return False

    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
        self.clear()

    def clear(self):
        """Clears fingerprints data"""
        self.server.delete(self.key)
