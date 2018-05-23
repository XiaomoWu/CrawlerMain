import base64
import os
import random
import time
import json, urllib
import re
import pymongo
import redis
import logging
import urllib.request
from datetime import datetime, timedelta
from crawler.settings import *
from crawler.spiders import util
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from twisted.web._newclient import ResponseNeverReceived
from twisted.python.failure import Failure
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from crawler.spiders import util

conn = util.set_redis_server()
db = util.set_mongo_server()


