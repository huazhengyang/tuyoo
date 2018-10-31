# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import urllib
from twisted.web import client
from freetime.aio import http
import freetime.util.log as ftlog
from poker.util import strutil
client.HTTPClientFactory.noisy = False

def webgetJson(httpurl, datas={}, appKey=None, timeout=3):
    """
    调用远程HTTP接口, 并返回JSON结果
    """
    pass

def webget(httpurl, querys={}, appKey=None, postdata_='', method_='POST', headers_={}, cookies={}, connect_timeout=3, timeout=3, needresponse=True, codeKey='code', appKeyTail=None, filterParams=[], connector='&', retrydata=None):
    """
    调用远程HTTP接口, 并返回JSON结果
    """
    pass

def webgetGdss(httpurl, querys={}, postdata_='', method_='POST', headers_={}, cookies={}, connect_timeout=6, timeout=6, needresponse=True):
    pass