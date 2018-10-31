# -*- coding:utf-8 -*-
'''
Created on 2017年4月15日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hallvip import TYUserVip, TYUserVipLevelUpEvent, \
    TYUserVipExpChangedEvent, TYUserVipSystemImpl
from hall.game import TGHall
from poker.entity.biz.item.item import TYAssetUtils


def addUserVipExp(self, gameId, userId, toAddExp, eventId, intEventParam):
    '''
    增加vip经验值
    @param gameId: 在那个gameId中增加的经验值，用于统计 
    @param toAddExp: 要增加的经验值
    @param eventId: 导致经验值增加的事件ID
    @param intEventParam: eventId相关参数
    @return: TYUserVip
    '''
    assert(toAddExp >= 0)
    vipExp = self._vipDao.incrVipExp(userId, toAddExp)
    oldVipExp = vipExp - toAddExp
    oldVipLevel = self._vipSystem.findVipLevelByVipExp(oldVipExp)
    newVipLevel = self._vipSystem.findVipLevelByVipExp(vipExp)
    
    ftlog.info('TYUserVipSystemImpl.addUserVipExp gameId=', gameId, 'userId=', userId,
               'oldExp=', oldVipExp, 'newExp=', vipExp,
               'oldLevel=', oldVipLevel.level, 'newLevel=', newVipLevel.level)
    
    userVip = TYUserVip(userId, vipExp, newVipLevel)
    if oldVipLevel.level != newVipLevel.level:
        nextVipLevel = oldVipLevel.nextVipLevel
        assetList = []
        while (nextVipLevel and nextVipLevel.level <= newVipLevel.level):
            subContentList = self._sendRewardContent(gameId, userVip, nextVipLevel)
            if subContentList:
                assetList.extend(subContentList)
            nextVipLevel = nextVipLevel.nextVipLevel
        changeDataNames = TYAssetUtils.getChangeDataNames(assetList)
        changeDataNames.add('vip')
        changeDataNames.add('decoration')
        datachangenotify.sendDataChangeNotify(gameId, userId, changeDataNames)
        TGHall.getEventBus().publishEvent(TYUserVipLevelUpEvent(gameId, userId, oldVipLevel,
                                                                userVip, assetList,
                                                                eventId, intEventParam))
    else:
        datachangenotify.sendDataChangeNotify(gameId, userId, 'vip')
        TGHall.getEventBus().publishEvent(TYUserVipExpChangedEvent(gameId, userId, userVip, oldVipExp))
    return userVip


TYUserVipSystemImpl.addUserVipExp = addUserVipExp


