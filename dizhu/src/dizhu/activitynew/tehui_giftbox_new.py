# -*- coding:utf-8 -*-
'''
Created on 2016-07-12

@author: luwei
'''
from dizhu.activities.toolbox import UserBag
from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.game import TGHall
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.util import strutil
from sre_compile import isstring


class GiftboxEntry(object):
    def __init__(self, d):
        super(GiftboxEntry, self).__init__()
        self._itemId = d.get('itemId')
        self._rmb = d.get('rmb', 0)
        self._reward = d.get('reward')
        
        if not isstring(self._itemId):
            raise TYBizConfException(d, 'config field `itemId` error')
        if not isinstance(self._rmb, int):
            raise TYBizConfException(d, 'config field `rmb` error')
        if not isinstance(self._reward, dict):
            raise TYBizConfException(d, 'config field `reward` error')

        ftlog.debug('GiftboxEntry.init:',
                    'itemId=', self._itemId,
                    'rmb=', self._rmb,
                    'reward=', self._reward)
        
    def checkCondition(self, userId, charged_rmb):
        ftlog.debug('GiftboxEntry.checkCondition:begin',
                    'userId=', userId,
                    'charged_rmb=', charged_rmb,
                    'itemId=', self._itemId)
        if not UserBag.isHaveAssets(userId, self._itemId, DIZHU_GAMEID):
            ftlog.debug('GiftboxEntry.checkCondition:',
                        'userId=', userId, 
                        'item not found')
            return False
        if charged_rmb < self._rmb:
            ftlog.debug('GiftboxEntry.checkCondition:',
                        'userId=', userId, 
                        'charged_rmb < rmblimit')
            return False 
        return True

    def sendRewardToUser(self, userId, mail, intActId, charged_rmb):
        ftlog.debug('GiftboxEntry.sendRewardToUser:begin',
                    'userId=', userId,
                    'mail=', mail,
                    'charged_rmb=', charged_rmb)

        # 将礼包道具消耗掉，
        ok = UserBag.consumeAssetsIfEnough(userId, self._itemId, 1, 'ACTIVITY_REWARD', DIZHU_GAMEID, intActId)
        if not ok:
            ftlog.debug('GiftboxEntry.sendRewardToUser:consumeitem',
                        'userId=', userId,
                        'ok=', ok)
            return False
        
        if mail and self._reward.get('desc'):
            desc = self._reward.get('desc')
            mail = strutil.replaceParams(mail, {'rewardContent':desc})
        else:
            mail = None
        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, self._reward, 'ACTIVITY_REWARD', mail, intActId)
        ftlog.info('GiftboxEntry:sendRewardToUser:',
                   'gameId=', DIZHU_GAMEID, 
                   'userId=', userId, 
                   'itemId=', self._itemId, 
                   'charged_rmb=', charged_rmb, 
                   'reward=', self._reward)
        return True

class TeHuiGiftboxNew(ActivityNew):
    TYPE_ID = 'ddz.act.tuihuigift_new'
    
    def __init__(self):
        super(TeHuiGiftboxNew, self).__init__()
        self._mail = None
        self._gifts = [];

    def init(self):
        ftlog.debug('TeHuiGiftboxNew.init')
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, self._onChargeNotify)
    
    def cleanup(self):
        ftlog.debug('TeHuiGiftboxNew.cleanup')
        TGHall.getEventBus().unsubscribe(ChargeNotifyEvent, self._onChargeNotify)

    def _decodeFromDictImpl(self, d):
        ftlog.debug('TeHuiGiftboxNew._decodeFromDictImpl, d=', d)
        self._mail = d.get('mail', '')
        gifts = d.get('gifts', [])
        if not isinstance(gifts, list):
            raise TYBizConfException(d, 'config field `gifts` error')

        self._entries = []
        for conf in gifts:
            if not isinstance(conf, dict):
                raise TYBizConfException(d, 'config field `gifts` item error')
            entry = GiftboxEntry(conf)
            self._entries.append(entry)
        return self
    
    def _onChargeNotify(self, event):
        ftlog.debug('TeHuiGiftboxNew._onChargeNotify, event=', event.__dict__)
        userId = event.userId
        
        if self.checkTime(event.timestamp) != 0:
            ftlog.debug('TeHuiGiftboxNew._onChargeNotify: ',
                        'userId=', userId, 
                        'outdate=true')
            return 
                
        for entry in self._entries:
            if entry.checkCondition(userId, event.rmbs):
                entry.sendRewardToUser(userId, self._mail, self.intActId, event.rmbs)
                