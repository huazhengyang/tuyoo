# -*- coding:utf-8 -*-
'''
Created on 2016年8月8日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.activitynew.activity import ActivityNew
import freetime.util.log as ftlog
from hall.entity.hallactivity import activity
from hall.entity.hallactivity.activity_play_game_present_gift import \
    TYActivityPlayGamePresentGift
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivityRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.util import strutil
from hall.entity.hallconf import HALL_GAMEID


class ChargeSendPresentNum(ActivityNew):
    TYPE_ID = 'ddz.act.charge_send_present_num'
    
    def __init__(self):
        super(ChargeSendPresentNum, self).__init__()
        self._presentNumActId = None
        self._rate = 1
        self._hallGameIds = None
        
    def init(self):
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, self._onChargeNotify)
    
    def cleanup(self):
        TGHall.getEventBus().unsubscribe(ChargeNotifyEvent, self._onChargeNotify)
    
    def _decodeFromDictImpl(self, d):
        self._presentNumActId = d.get('presentNumActId')
        if not self._presentNumActId or not isstring(self._presentNumActId):
            raise TYBizConfException(d, 'ChargeSendPresentNum.presentNumActId must string')
        self._rate = d.get('sendRate', 1)
        if not isinstance(self._rate, (int, float)) or self._rate <= 0:
            raise TYBizConfException(d, 'ChargeSendPresentNum.rate must int or float > 0')
        self._hallGameIds = d.get('hallGameIds', [])
        if not isinstance(self._hallGameIds, list):
            raise TYBizConfException(d, 'ChargeSendPresentNum.hallGameIds must be list')
        for hallGameId in self._hallGameIds:
            if not isinstance(hallGameId, int):
                raise TYBizConfException(d, 'ChargeSendPresentNum.hallGameIds must be int list')
        return self
    
    def _onChargeNotify(self, event):
        if ftlog.is_debug():
            ftlog.debug('ChargeSendPresentNum._onChargeNotify gameId=', event.gameId,
                        'userId=', event.userId,
                        'clientId=', event.clientId,
                        'presentNumActId=', self._presentNumActId,
                        'rmbs=', event.rmbs,
                        'productId=', event.productId,
                        'hallGameIds=', self._hallGameIds)
        hallGameId = strutil.getGameIdFromHallClientId(event.clientId)
        if hallGameId not in self._hallGameIds:
            if ftlog.is_debug():
                ftlog.debug('ChargeSendPresentNum._onChargeNotify gameId=', event.gameId,
                            'userId=', event.userId,
                            'presentNumActId=', self._presentNumActId,
                            'clientId=', event.clientId,
                            'rmbs=', event.rmbs,
                            'productId=', event.productId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        sendPresentNum = int(self._rate * event.rmbs)
        if sendPresentNum > 0:
            actObj = self._findActObj(event.gameId, event.userId, event.clientId)
            if actObj:
                actObj.addPresentNum(HALL_GAMEID, event.userId, event.clientId, sendPresentNum)
                ftlog.debug('ChargeSendPresentNum._onChargeNotify gameId=', event.gameId,
                           'userId=', event.userId,
                           'presentNumActId=', self._presentNumActId,
                           'clientId=', event.clientId,
                           'rmbs=', event.rmbs,
                           'productId=', event.productId,
                           'rate=', self._rate,
                           'sendPresentNum=', sendPresentNum)
        
    def _findActObj(self, gameId, userId, clientId):
        actConf = activity.activitySystem.getClientActivityConfig(clientId, self._presentNumActId)
        ftlog.debug('ChargeSendPresentNum._findActObj gameId=', gameId,
                   'userId=', userId,
                   'presentNumActId=', self._presentNumActId,
                   'clientId=', clientId,
                   'rate=', self._rate,
                   'actConf=', actConf)
        if actConf and TYActivityRegister.findClass(actConf.get('typeid')) == TYActivityPlayGamePresentGift:
            return activity.activitySystem.generateOrGetActivityObject(actConf)
        return None


