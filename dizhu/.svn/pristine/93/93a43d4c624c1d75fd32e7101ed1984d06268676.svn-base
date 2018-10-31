# -*- coding:utf-8 -*-
'''
Created on 2016-07-12

@author: luwei
'''
from dizhu.activities.toolbox import UserBag
from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity import hallvip
from hall.entity.hallvip import TYUserVipLevelUpEvent
from hall.game import TGHall
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventUserLogin
from poker.util import strutil


class ActivityModel(object):
    def __init__(self):
        self.itemSendMap = {}
    
    def fromDict(self, d):
        self.itemSendMap = d or {}
        return self
    
    def toDict(self):
        return self.itemSendMap
    
    def loadModel(self, userId, key):
        jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (DIZHU_GAMEID, userId), key)
        if jstr:
            return self.fromDict(strutil.loads(jstr))
        return None
    
    def saveModel(self, userId, key):
        jstr = strutil.dumps(self.toDict())
        daobase.executeUserCmd(userId, 'hset', 'act:%s:%s' % (DIZHU_GAMEID, userId), key, jstr)


class VipGiftEntry(object):
    def __init__(self, d):
        super(VipGiftEntry, self).__init__()
        self._vipFloor = d.get('vipFloor', 0)
        self._vipCeil = d.get('vipCeil')
        self._reward = d.get('reward')
        
        if not isinstance(self._vipFloor, int):
            raise TYBizConfException(d, 'config field `vipFloor` error')
        if self._vipCeil != None and not isinstance(self._vipCeil, int):
            raise TYBizConfException(d, 'config field `vipCeil` error')
        if not isinstance(self._reward, dict):
            raise TYBizConfException(d, 'config field `reward` error')
        
        ftlog.debug('VipGiftEntry.init:',
                    'vipFloor=', self._vipFloor,
                    'vipCeil=', self._vipCeil,
                    'reward=', self._reward)

    def getVipLevel(self, userId):
        viplvl = 0
        info = hallvip.userVipSystem.getUserVip(userId)
        if info :
            viplvl = info.vipLevel.level or 0
        return viplvl
    
    def checkCondition(self, userId, key):        
        # 判断是否发送过
        actmodel = ActivityModel()
        actmodel.loadModel(userId, key)
        itemId = self._reward.get('itemId')
        ftlog.debug('VipGiftEntry.checkCondition:send',
                    'userId=', userId,
                    'key=', key,
                    'itemId=', itemId,
                    'itemSendMap=', actmodel.itemSendMap)
        if itemId in actmodel.itemSendMap:
            return False
         
        # 取得vip等级
        viplvl = self.getVipLevel(userId)        
        ftlog.debug('VipGiftEntry.checkCondition:viplvl',
                    'userId=', userId,
                    'viplvl=', viplvl,
                    'vipFloor=', self._vipFloor,
                    'vipCeil=', self._vipCeil)

        # [vipFloor,vipCeil]
        if viplvl >= self._vipFloor:
            # 若存在上限，则判断上限值，否则直接返回True
            if not self._vipCeil:
                return True
            return viplvl <= self._vipCeil

        return False
 
    def sendRewardToUser(self, userId, mail, intActId, key):
        reward = self._reward

        if mail and reward.get('desc'):
            rewardContent = reward.get('desc')
            mail = strutil.replaceParams(mail, {'rewardContent': rewardContent})
        else:
            mail = None
        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, reward, 'ACTIVITY_REWARD', mail, intActId)
        
        # 记录发放过的道具
        rewardItemId = reward.get('itemId')
        actmodel = ActivityModel()
        actmodel.loadModel(userId, key)
        actmodel.itemSendMap[rewardItemId] = 1
        actmodel.saveModel(userId, key)

        ftlog.info('VipGiftEntry.sendRewardToUser:',
                   'userId=', userId,
                   'viplevel=', self.getVipLevel(userId),
                   'reward=', reward,
                   'itemSendMap=', actmodel.itemSendMap)
        return True

class VipGiftbox(ActivityNew):
    TYPE_ID = 'ddz.act.vip_giftbox'
    
    def __init__(self):
        super(VipGiftbox, self).__init__()
        self._mail = None
        self._entries = []

    def init(self):
        ftlog.debug('VipGiftbox.init')
        eventbus = TGHall.getEventBus()
        eventbus.subscribe(EventUserLogin, self.onEventHandler)
        eventbus.subscribe(TYUserVipLevelUpEvent, self.onEventHandler)
    
    def cleanup(self):
        ftlog.debug('VipGiftbox.cleanup')
        eventbus = TGHall.getEventBus()
        eventbus.unsubscribe(EventUserLogin, self.onEventHandler)
        eventbus.unsubscribe(TYUserVipLevelUpEvent, self.onEventHandler)

    def buildKey(self):
        return self.actId

    def _decodeFromDictImpl(self, d):
        ftlog.debug('VipGiftbox._decodeFromDictImpl, d=', d)
        # 若mail字段不存在，则不发mail
        self._mail = d.get('mail')
        vipgifts = d.get('vipgifts')
        
        if not isinstance(vipgifts, list):
            raise TYBizConfException(d, 'config field `vipgifts` error')
    
        self._entries = []
        for conf in vipgifts:
            if not isinstance(conf, dict):
                raise TYBizConfException(d, 'config field `vipgifts` item error')
            entry = VipGiftEntry(conf)
            self._entries.append(entry)
        return self
    
    def onEventHandler(self, event):
        ftlog.debug('VipGiftbox.onEventHandler')
        userId = event.userId
        
        if self.checkTime(event.timestamp) != 0:
            ftlog.debug('VipGiftbox.onEventHandler: ',
                        'userId=', userId, 
                        'outdate=true')
            return  
        
        for entry in self._entries:
            if entry.checkCondition(userId, self.buildKey()):
                entry.sendRewardToUser(userId, self._mail, self.intActId, self.buildKey())
                