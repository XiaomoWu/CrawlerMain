# -*- coding: UTF-8 -*-  
from ctypes import *
import sys
import os
import hashlib
import httplib
import urllib
import string
import zlib
import binascii
import random

reload(sys)					
sys.setdefaultencoding('utf8')	

UUDLL=os.path.join(os.path.dirname(__file__), 'UUWiseHelper_64.dll')   
print(UUDLL)  
dll='C://Users/Ross/OneDrive/SNT/VSSln/CrawlerXQ/uudama/UUWiseHelper_64.dll'
UU = windll.LoadLibrary(dll)
  