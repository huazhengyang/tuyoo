# -*- coding:utf-8 -*-
'''
Created on 2016-07-12

@author: luwei
@note: 此活动用于
    1.记录玩家牌局分享次数
    2.每天第一次牌局分享时，给发送配置的奖励
'''
from datetime import datetime
from sre_compile import isstring

from dizhu.activities.toolbox import UserBag
from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.replay import replay_service
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.entity.hallshare import HallShareEvent
from hall.game import TGHall
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.dao import daobase
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class ActivityModel(object):
    def __init__(self, userId):
        self.userId = userId
        
        self.shareDay = 0
        self.shareCounter = 0
    
    def fromDict(self, d):
        self.shareDay = d.get('shareDay')
        self.shareCounter = d.get('shareCounter', 0)
        return self
    
    def toDict(self):
        return {'shareDay':self.shareDay, 'shareCounter':self.shareCounter}
    
    def incrShareCount(self, ct=None):
        if ct == None:
            ct = datetime.now()
        
        # 不是同一天，则清零当天分享次数
        cday = pktimestamp.formatTimeDayInt(ct)
        if self.shareDay != cday:
            self.shareDay = cday
            self.shareCounter = 0
        self.shareCounter += 1
        
    def hasTodayShared(self):
        ''' 今天是否已经分享过 '''
        cday = pktimestamp.formatTimeDayInt(None)
        return (self.shareDay == cday) and (self.shareCounter > 0)

    def getTodaySharedCount(self):
        ''' 今天分享的次数 '''
        cday = pktimestamp.formatTimeDayInt(None)
        if self.shareDay == cday:
            return self.shareCounter if self.shareCounter > 0 else 0
        return 0

class TableShareRecorder(ActivityNew):
    TYPE_ID = 'ddz.act.table_share_recorder'
    
    def __init__(self):
        super(self.__class__, self).__init__()
        self.prizeList = []
        self.mail = None
        
    def init(self):
        ftlog.debug('TableShareRecorder.init', 'actId=', self.actId)
        # 监听用户牌局分享事件
        TGHall.getEventBus().subscribe(HallShareEvent, self.onEventTableShare)

    def cleanup(self):
        ftlog.debug('TableShareRecorder.cleanup', 'actId=', self.actId)
        TGHall.getEventBus().unsubscribe(HallShareEvent, self.onEventTableShare)
    
    def loadModel(self, userId):
        jstr = None
        ret = ActivityModel(userId)
        try:
            jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (DIZHU_GAMEID, userId), self.actId)
            if jstr:
                return ret.fromDict(strutil.loads(jstr))
        except:
            ftlog.error('TableShareRecorder.loadModel BadData',
                        'userId=', userId,
                        'jstr=', jstr)
        return ret

    def saveModel(self, model):
        if ftlog.is_debug():
            ftlog.debug('TableShareRecorder.saveModel', 
                        'actId=', self.actId,
                        'userId=', model.userId,
                        'model=', model.toDict())
        
        jstr = strutil.dumps(model.toDict())
        daobase.executeUserCmd(model.userId, 'hset', 'act:%s:%s' % (DIZHU_GAMEID, model.userId), self.actId, jstr)

    def hasTodayShared(self, userId):
        ''' 今天是否已经分享过 '''
        model = self.loadModel(userId)
        return model.hasTodayShared()

    def getTodaySharedCount(self, userId):
        ''' 今天分享的次数 '''
        model = self.loadModel(userId)
        return model.getTodaySharedCount()

    def onEventTableShare(self, event):
        if ftlog.is_debug():
            ftlog.debug('TableShareRecorder.onEventTableShare:', 
                        'userId=', event.userId,
                        'event.shareid=', event.shareid,
                        'event.shareLoc=', event.shareLoc,
                        'replay_service.getAllShareIds=', replay_service.getAllShareIds())
        
        # 确认是牌局分享的
        if event.shareid not in replay_service.getAllShareIds():
            return
        
        # 判断活动是否过期
        if self.checkTime(event.timestamp) != 0:
            if ftlog.is_debug():
                ftlog.debug('TableShareRecorder.onEventTableShare:',
                            'actId=', self.actId,
                            'userId=', event.userId, 
                            'outdate=true')
            return 
        
        model = self.loadModel(event.userId)
        model.incrShareCount()
        self.saveModel(model)
        
        # 每天第一次分享发送奖励
        if model.shareCounter == 1:
            self.sendPrizeToUser(event.userId)
                
    def sendPrizeToUser(self, userId):
        if ftlog.is_debug():
            ftlog.debug('TableShareRecorder.sendPrizeToUser', 
                        'userId=', userId,
                        'prizeList=', self.prizeList)
        for prize in self.prizeList:
            prizeContent = hallitem.buildContent(prize['itemId'], prize['count'], True)
            mail = strutil.replaceParams(self.mail, {'prizeContent': prizeContent})
            UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, prize, 'ACTIVITY_REWARD', mail, self.intActId)
            ftlog.info('TableShareRecorder.sendPrizeToUser',
                       'userId=', userId,
                       'prize=', prize)
    
    def _decodeFromDictImpl(self, d):
        if ftlog.is_debug():
            ftlog.debug('TableShareRecorder._decodeFromDictImpl', d)
        
        self.prizeList = d.get('prizeList', [])
        if not isinstance(self.prizeList, list):
            raise TYBizConfException(d, 'TableShareRecorder.prizeList must be list')

        self.mail = d.get('mail')
        if self.mail and not isstring(self.mail):
            raise TYBizConfException(d, 'TableShareRecorder.mail must be string or null')

        return self
