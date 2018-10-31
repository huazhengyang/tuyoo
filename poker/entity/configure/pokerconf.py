# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
每个配置项必须是JSON格式
"""
from poker.entity.configure import configure

def getIntegrate():
    pass
getConfigGameIds = configure.getConfigGameIds

def getCmds():
    pass

def getOldCmds():
    pass
clientIdToNumber = configure.clientIdToNumber
numberToClientId = configure.numberToClientId

def productIdToNumber(productId):
    """
    转换商品ID字符串定义至INTEGER_ID的定义
    """
    pass

def giftIdToNumber(giftId):
    """
    转换礼物ID字符串定义至INTEGER_ID的定义
    """
    pass

def biEventIdToNumber(eventName):
    """
    取得事件ID字符串对应的INTEGER_ID的定义
    """
    pass

def activityIdToNumber(activityName):
    """
    取得活动ID字符串对应的NTEGER_ID的定义
    """
    pass

def getConnLogoutMsg(errorCode, defaultVal):
    """
    关闭TCP连接时, 通知客户端的error消息内容
    """
    pass

def isOpenMoreTable(clientId):
    """
    判定一个clientId是否支持多开
    目前都不支持
    """
    pass