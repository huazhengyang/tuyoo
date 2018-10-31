# -*- coding:utf-8 -*-
'''
Created on 2018年8月10日

@author: wangyonghui
'''

from poker.entity.dao import daobase

HKEY_TREASURE_CHEST = 'treasureChest'


def saveUserTreasureChest(uid, gameid, value):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'SET', HKEY_TREASURE_CHEST + ':' + str(gameid) + ':' + str(uid), value)


def loadUserTreasureChest(uid, gameid):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'GET', HKEY_TREASURE_CHEST + ':' + str(gameid) + ':' + str(uid))

