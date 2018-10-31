# -*- coding:utf-8 -*-
'''
Created on 2018年1月11日

@author: zhaojiangang
'''

import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
import poker.entity.dao.gamedata as pkgamedata


def _onUserLogin(gameId, userId, clientId, isCreate, isDayfirst):
    from hall.entity import hallsubmember
    ftlog.debug('hallitem._onUserLogin gameId=', gameId,
               'userId=', userId,
               'clientId=', clientId,
               'isCreate=', isCreate,
               'isDayfirst', isDayfirst)
    if not hallitem._inited:
        return
    
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    userBag = userAssets.getUserBag()
    if isCreate:
        pkgamedata.setGameAttr(userId, HALL_GAMEID, 'flag.item.trans', 1)
        hallitem._initUserBag(gameId, userId, clientId, userBag)
    else:
        if pkgamedata.setnxGameAttr(userId, HALL_GAMEID, 'flag.item.trans', 1) == 1:
            if not hallitem._tranformItems(gameId, userId, clientId, userBag):
                hallitem._initUserBag(gameId, userId, clientId, userBag)
        hallsubmember.checkSubMember(gameId, userId, timestamp, 'LOGIN_CHECK_SUBMEM', 0, userAssets)
    userBag.processWhenUserLogin(gameId, isDayfirst, timestamp)


hallitem._onUserLogin = _onUserLogin


