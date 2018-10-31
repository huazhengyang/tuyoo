# -*- coding:utf-8 -*-
'''
Created on 2017年12月13日

@author: zhaojiangang
'''
from hall.servers.util.red_packet_rain_handler import RedPacketRainTcpHandler
from poker.entity.biz.exceptions import TYBizException
from poker.protocol.rpccore import markRpcCall
from hall.entity.hallconf import HALL_GAMEID


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def _testGrab(userId, clientId, rainTime):
    try:
        mo = RedPacketRainTcpHandler._doGrab(HALL_GAMEID, userId, clientId, rainTime)
        return 0, mo.pack()
    except TYBizException, e:
        return -1, e.message
    

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def _testGetResult(userId, clientId, rainTime):
    try:
        mo = RedPacketRainTcpHandler._doGetResult(HALL_GAMEID, userId, clientId, rainTime)
        return 0, mo.pack()
    except TYBizException, e:
        return -1, e.message


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def _testGetNextRain(userId, clientId):
    try:
        mo = RedPacketRainTcpHandler._doGetNextRain(HALL_GAMEID, userId, clientId)
        return 0, mo.pack()
    except TYBizException, e:
        return -1, e.message
    

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def _testGetDanmu(userId, clientId, rainTime, danmuPos):
    try:
        mo = RedPacketRainTcpHandler._doGetDanmu(HALL_GAMEID, userId, clientId, rainTime, danmuPos)
        return 0, mo.pack()
    except TYBizException, e:
        return -1, e.message


