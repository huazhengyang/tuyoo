# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from datetime import datetime
import os, stackless, urllib
from twisted.internet import defer, reactor
from twisted.internet.defer import succeed
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.util import strutil
from freetime.core.tasklet import FTTasklet
TRACE_RESPONSE = 0
CONTENT_TYPE_JSON = {'Content-Type': 'application/json;charset=UTF-8'}
CONTENT_TYPE_HTML = {'Content-Type': 'text/html;charset=UTF-8'}
CONTENT_TYPE_PLAIN = {'Content-Type': 'application/octet-stream', 'Content-Disposition': 'attachment'}
CONTENT_TYPE_GIF = {'Content-Type': 'image/gif'}
_http_path_methods = {}
_path_webroots = []

def isHttpTask():
    """
    判定当前是否是HTTP请求引发的tasklet
    """
    pass

def getRequest():
    """
    取得当前HTTP请求的原始的request对象
    """
    pass

def getClientIp():
    """
    取得当前HTTP请求的远程IP地址(以考虑nginx进行代理的模式, nginx代理时需设定:x-real-ip头)
    """
    pass

def getHeader(headName):
    """
    取得HTTP请求头的值
    """
    pass

def getPath():
    """
    取得当前HTTP请求的路径
    """
    pass

def getRawData():
    """
    取得当前HTTP请求的数据内容(全体数据信息)
    """
    pass

def getParamStr(key, defaultVal=None):
    """
    取得当前HTTP请求的一个参数值
    """
    pass

def getParamInt(key, defaultVal=0):
    """
    取得当前HTTP请求的一个参数的int值
    """
    pass

def getParamFloat(key, defaultVal=0.0):
    """
    取得当前HTTP请求的一个参数的float值
    """
    pass

def getMsgPack(keys=None):
    """
    将当前的HTTP请求的路径和参数内容, 转换为一个MsgPack
    """
    pass

def getDict():
    """
    将当前的HTTP请求的所有参数内容, 转换为一个dict
    """
    pass

def setParam(key, val):
    """
    设置当前HTTP请求参数的键值对
    注: 此方法仅在某些特殊需求下才会被调用
    """
    pass

def getBody():
    """
    取得当前HTTP的POST发送的BODY的字符串
    """
    pass

def doRedirect(redirectUrl):
    """
    对当前的HTTP请求进行302转向处理
    """
    pass

def doFinish(content, fheads, debugreturn=True):
    """
    完结当前的HTTP的请求, 并发送响应数据
    """
    pass

def __stringifyResponse(isjsonp, content, content_type=''):
    """
    序列化响应的数据内容
    """
    pass

def _checkRequestParams(apiobj, paramkeys):
    """
    检查校验HTTP请求的输入参数
    """
    pass

def handlerHttpRequest(httprequest):
    """
    HTTP请求处理总入口
    """
    pass

def addWebRoot(webroot):
    """
    添加静态资源查找路径
    """
    pass

def __handlerHttpStatic(httprequest):
    """
    HTTP请求静态资源
    """
    pass

def __loadResource(fpath):
    pass

class __StringProducer(object, ):
    """
    代理服务使用的HTTP BODY的产生器
    """
    implements(IBodyProducer)

    def __init__(self, body):
        pass

    def startProducing(self, consumer):
        pass

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

def doProxy(httpurl, datas, headers_=None, timeout=3):
    """
    进行HTTP的代理协议处理
    """
    pass

def _createLinkString(rparam):
    pass

def checkHttpParamCode(appKey, codeKey='code'):
    pass