# -*- coding:utf-8 -*-
'''
Created on 2018年7月23日

@author: wangyonghui
'''

from poker.entity.dao import daobase

HKEY_REWARD_ASYNC = 'rewardAsync:'


def getRewardAsync(uid, gameid):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'GET', HKEY_REWARD_ASYNC + str(gameid) + ':' + str(uid))


def setRewardAsync(uid, gameid, value):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'SET', HKEY_REWARD_ASYNC + str(gameid) + ':' + str(uid), value)
