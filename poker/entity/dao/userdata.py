# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from poker.entity.dao import daoconst
from poker.entity.dao.daoconst import UserDataSchema
from poker.servers.util.direct import dbuser

def checkUserData(userId, clientId=None, appId=0, session={}):
    """
    检查给出的用userId数据是否存在，
    如果在冷数据中则进行导入,
    当用户进行登录时,调用此方法, 因此再此方法中建立该用户的session数据缓冲
    数据缓冲由dbuser层进行处理,即在UT进程中进程缓冲
    """
    pass

def updateUserDataAuthorTime(userId):
    """
    更新用户的认证时间
    """
    pass

def updateUserDataAliveTime(userId):
    """
    更新用户的CONN链接活动时间
    """
    pass

def updateUserGameDataAuthorTime(userId, gameId):
    """
    更新用户的BINDGAME活动时间
    """
    pass

def getSessionData(userId):
    """
    取得用户的session数据
    """
    pass

def setSessionData(userId, session):
    """
    设置用户的session数据
    """
    pass

def clearUserCache(userId):
    """
    其他外部系统,例如SDK改变用户数据时, 通知本系统进行缓存的清理, 重新加载用户数据
    """
    pass

def getAttrs(userId, filedList):
    """
    取得用户的主账户数据
    """
    pass

def setAttrs(userId, datas):
    """
    设置用户的主账户数据
    """
    pass

def setnxAttr(userId, filed, value):
    pass

def _setAttrsForce(userId, datas):
    """
    强制设置用户属性列表, 此方法由框架内部调用, 其他代码不允许调用
    """
    pass

def delAttr(userId, field):
    """
    设置用户属性
    """
    pass

def incrAttr(userId, field, value):
    """
    INCR用户属性
    """
    pass

def incrAttrLimit(userId, field, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode):
    """
    INCR用户属性
    参考: incr_chip_limit
    """
    pass

def getAttr(userId, field):
    """
    获取用户属性值
    """
    pass

def getAttrInt(userId, field):
    """
    获取用户属性值
    """
    pass

def setAttr(userId, field, value):
    """
    设置用户属性
    """
    pass

def getExp(uid):
    """
    取得用户的经验值
    """
    pass

def incrExp(userId, detalExp):
    """
    调整用户的经验值
    """
    pass

def getCharm(uid):
    """
    取得用户的魅力值
    """
    pass

def incrCharm(userId, detalCharm):
    """
    调整用户的魅力值
    """
    pass