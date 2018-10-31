# -*- coding:utf-8 -*-
'''
Created on 2016-07-12

@author: luwei
'''
from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.game import TGHall
from poker.entity.dao import daobase
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.util import strutil


class ActivityModel(object):
    def __init__(self, userId):
        self.userId = userId
        self.maxChargedMoney = 0
    
    def fromDict(self, d):
        self.maxChargedMoney = d.get('maxChargedMoney', 0)
        return self
    
    def toDict(self):
        return {'maxChargedMoney': self.maxChargedMoney}
    
class MaxChargeRecorder(ActivityNew):
    TYPE_ID = 'ddz.act.max_charge_recorder'
    
    def init(self):
        ftlog.debug('MaxChargeRecorder.init', 'actId=', self.actId)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, self._onChargeNotify)

    def cleanup(self):
        ftlog.debug('MaxChargeRecorder.cleanup', 'actId=', self.actId)
        TGHall.getEventBus().unsubscribe(ChargeNotifyEvent, self._onChargeNotify)
    
    def loadModel(self, userId):
        jstr = None
        ret = ActivityModel(userId)
        try:
            jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (DIZHU_GAMEID, userId), self.actId)
            if jstr:
                return ret.fromDict(strutil.loads(jstr))
        except:
            ftlog.error('MaxChargeRecorder.loadModel BadData',
                        'userId=', userId,
                        'jstr=', jstr)
        return ret

    def saveModel(self, model):
        if ftlog.is_debug():
            ftlog.debug('MaxChargeRecorder.saveModel', 
                        'actId=', self.actId,
                        'userId=', model.userId,
                        'maxChargedMoney=', model.maxChargedMoney)
        
        jstr = strutil.dumps(model.toDict())
        daobase.executeUserCmd(model.userId, 'hset', 'act:%s:%s' % (DIZHU_GAMEID, model.userId), self.actId, jstr)

    def _onChargeNotify(self, event):
        # 判断充值的是地主的包
        user_gameid = strutil.getGameIdFromHallClientId(event.clientId)
        ftlog.debug('MaxChargeRecorder._onChargeNotify:',
                    'actId=', self.actId,
                    'userId=', event.userId, 
                    'user_gameid=', user_gameid)
#         if user_gameid != DIZHU_GAMEID:
#             return

        # 判断活动是否过期
        if self.checkTime(event.timestamp) != 0:
            ftlog.debug('MaxChargeRecorder._onChargeNotify:',
                        'actId=', self.actId,
                        'userId=', event.userId, 
                        'outdate=true')
            return 
        
        model = self.loadModel(event.userId)
        
        ftlog.debug('MaxChargeRecorder._onChargeNotify:',
                    'actId=', self.actId,
                    'userId=', event.userId, 
                    'event.rmbs=', event.rmbs,
                    'model.maxChargedMoney=', model.maxChargedMoney)

        if event.rmbs > model.maxChargedMoney:
            model.maxChargedMoney = event.rmbs
            self.saveModel(model)
            
