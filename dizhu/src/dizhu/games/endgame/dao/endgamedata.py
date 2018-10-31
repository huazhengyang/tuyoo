# -*- coding: utf-8 -*-
'''
Created on 2018年7月13日

@author: wangyonghui
'''
from poker.entity.dao import daobase

HKEY_ENDGAME_DATA = 'endgamedata:'

def getEndgameAttr(uid, gameid, attrname, filterKeywords=False):
    '''
    获取用户游戏属性
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = daobase.executeUserCmd(uid, 'HGET', HKEY_ENDGAME_DATA + str(gameid) + ':' + str(uid), attrname)
    if value and filterKeywords:
        return daobase.filterValue(attrname, value)
    return value

def setEndgameAttr(uid, gameid, attrname, value):
    '''
    设置用户游戏属性
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HSET', HKEY_ENDGAME_DATA + str(gameid) + ':' + str(uid), attrname, value)


def delEndgameAttr(uid, gameid, attrname):
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HDEL', HKEY_ENDGAME_DATA + str(gameid) + ':' + str(uid), attrname)
