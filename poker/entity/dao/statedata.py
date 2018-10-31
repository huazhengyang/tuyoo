# -*- coding: utf-8 -*-
"""
Created on 2016-7-7
@author: wuyongsheng
说明：因为，活动需要添加小红点，标记用户是否查看了该活动
    所以，创建一个key，用来存储用户的活动列表，标明用户的活动状态
"""
from poker.entity.dao import daoconst, daobase
from poker.util import strutil

def getStateAttrs(uid, gameid, attrlist, filterKeywords=False):
    """
    获取用户状态属性列表
    """
    pass

def setStateAttrs(uid, gameid, attrlist, valuelist):
    """
    设置用户状态属性列表
    """
    pass

def delStateAttr(uid, gameid, attrname):
    pass

def delStateAttrs(uid, gameid, attrlist):
    pass

def getStateAttr(uid, gameid, attrname, filterKeywords=False):
    """
    获取用户状态属性
    """
    pass

def getAllAttrs(uid, gameid, key):
    pass

def getStateAttrJson(uid, gameid, attrname, defaultVal=None):
    """
    获取用户状态属性
    """
    pass

def setStateAttr(uid, gameid, attrname, value):
    """
    设置用户状态属性
    """
    pass

def getStateAttrInt(uid, gameid, attrname):
    """
    获取用户状态属int
    """
    pass

def setnxStateAttr(uid, gameid, attrname, value):
    pass

def isStateExists(uid, gameid):
    """
    判定当前的状态数据是否存在
    """
    pass