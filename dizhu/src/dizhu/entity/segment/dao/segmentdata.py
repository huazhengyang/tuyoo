# -*- coding: utf-8 -*-
'''
Created on 2018-5-5
@author: wangyonghui
'''

from poker.entity.dao import daobase
from poker.util import strutil


HKEY_SEGMENTDATA = 'segmentdata:'


def delSegmentAttr(uid, gameid, attrname):
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HDEL', HKEY_SEGMENTDATA + str(gameid) + ':' + str(uid), attrname)

def getSegmentAttr(uid, gameid, attrname, filterKeywords=False):
    '''
    获取用户游戏属性
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = daobase.executeUserCmd(uid, 'HGET', HKEY_SEGMENTDATA + str(gameid) + ':' + str(uid), attrname)
    if value and filterKeywords:
        return daobase.filterValue(attrname, value)
    return value

def getSegmentAttrJson(uid, gameid, attrname, defaultVal=None):
    '''
    获取用户游戏属性
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = getSegmentAttr(uid, gameid, attrname)
    value = strutil.loads(value, False, True, defaultVal)
    return value


def setSegmentAttr(uid, gameid, attrname, value):
    '''
    设置用户游戏属性
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HSET', HKEY_SEGMENTDATA + str(gameid) + ':' + str(uid), attrname, value)


def getGameAttrInt(uid, gameid, attrname):
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = getSegmentAttr(uid, gameid, attrname)
    if not isinstance(value, (int, float)):
        return 0
    return int(value)

