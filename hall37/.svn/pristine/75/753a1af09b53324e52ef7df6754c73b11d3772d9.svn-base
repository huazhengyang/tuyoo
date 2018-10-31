# -*- coding: utf-8 -*-
'''
Created on 2017年4月5日

@author: zqh
'''
from copy import deepcopy

import freetime.util.log as ftlog
from hall.entity import hallvip
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.dao import gamedata, sessiondata
from hall.entity.iploc import iploc
from poker.util import strutil
from poker.entity.configure import configure, pokerconf


_DEBUG = 0

from hall.servers.util import gamelistipfilter

def _isOutOfBeijingIp(userId, clientId):
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    if not conf.get('enableIpCheck', 0):
        return 1

#     intClientId = pokerconf.clientIdToNumber(clientId)
#     if intClientId not in conf.get('filterClientIds', []):
#         return 1

    passHall = conf.get('passHall', [])
    if passHall:
        for ph in passHall:
            if clientId.find(ph) > 0:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, clientId, ph, 'passHall !')
                return 1

    passClientVer = conf.get('passClientVer', 0)
    if passClientVer > 0:
        _, cver, _ = strutil.parseClientId(clientId)
        if cver < passClientVer:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, clientId, passClientVer, 'passClientVer !')
            return 1

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBeijingIp(ipstr):
        if _DEBUG:
            ftlog.debug('gamelistipfilter', userId, ipstr, 'enableIpCheck !')
        return 1

    passTotalPlayTime = conf.get('passTotalPlayTime', 0)
    if passTotalPlayTime > 0:
        totalTime = gamelistipfilter._getPlayTimes(userId)
        if totalTime >= passTotalPlayTime:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, totalTime, passTotalPlayTime, 'passTotalPlayTime !')
            return 1
    
    passVipLevel = conf.get('passVipLevel', 0)
    if passVipLevel > 0:
        vipLevel = gamelistipfilter._getVIpLevel(userId)
        if vipLevel >= passVipLevel:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, vipLevel, passVipLevel, 'passVipLevel !')
            return 1

    if _DEBUG:
        ftlog.debug('filtergamelist go filter !', userId, ipstr)
    return 0

gamelistipfilter._isOutOfBeijingIp = _isOutOfBeijingIp
