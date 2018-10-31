# -*- coding: utf-8 -*-
"""
Created on 2014年2月20日

@author: zjgzzz@126.com
"""
import freetime.util.log as ftlog
from poker.entity.configure import pokerconf
from poker.entity.dao import userdata
from poker.entity.dao.daoconst import UserSessionSchema
from poker.util import strutil

def getClientId(userId):
    """
    取得用户的当前的客户端ID
    """
    pass

def getCityZip(userId):
    pass

def getCityName(userId):
    pass

def getClientIp(userId):
    pass

def getGameId(userId):
    pass

def getDeviceId(userId):
    pass

def getConnId(userId):
    pass

def getClientIdInfo(userId):
    """
    取得用户的当前的客户端ID的分解信息
    返回: 客户端的OS, 客户端的版本, 客户端的渠道, 客户端ID
    """
    pass

def getClientIdMainChannel(clientId):
    pass

def _parseClientIdNum(clientId):
    pass

def getClientIdNum(userId, clientId=None):
    """
    取得用户的当前的客户端ID的数字ID
    """
    pass

def getClientIdSys(userId):
    pass

def getClientIdVer(userId):
    pass

def getClientIdChanel(userId):
    pass