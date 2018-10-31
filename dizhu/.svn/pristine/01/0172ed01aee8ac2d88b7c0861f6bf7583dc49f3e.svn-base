# -*- coding:utf-8 -*-
'''
Created on 2016年11月28日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.gameplays.game_events import MyFTFinishEvent
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import daobase
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class ActivityModel(object):
    def __init__(self, userId):
        self.userId = userId
        self.lastFinishTime = 0
        self.finishCount = 0
    
    def fromDict(self, d):
        self.lastFinishTime = d.get('lastFinishTime', 0)
        self.finishCount = d.get('finishCount', 0)
        return self
    
    def toDict(self):
        return {'lastFinishTime':self.lastFinishTime, 'finishCount':self.finishCount}
    
class FTTableFinishRecorder(ActivityNew):
    TYPE_ID = 'ddz.act.fttable_finish_recorder'
    
    def __init__(self):
        super(self.__class__, self).__init__()
        self.rewardContent = None
        self.mail = None
        
    def init(self):
        from dizhu.game import TGDizhu
        ftlog.debug('FTTableFinishRecorder.init', 'actId=', self.actId)
        # 监听用户牌局分享事件
        TGDizhu.getEventBus().subscribe(MyFTFinishEvent, self._onEvent)

    def cleanup(self):
        from dizhu.game import TGDizhu
        ftlog.debug('FTTableFinishRecorder.cleanup', 'actId=', self.actId)
        TGDizhu.getEventBus().unsubscribe(MyFTFinishEvent, self._onEvent)
    
    def adjust(self, model, timestamp):
        if not pktimestamp.is_same_day(timestamp, model.lastFinishTime):
            model.lastFinishTime = timestamp
            model.finishCount = 0
        return model
    
    def loadModel(self, userId, timestamp=None):
        jstr = None
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        ret = ActivityModel(userId)
        try:
            jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (DIZHU_GAMEID, userId), self.actId)
            if jstr:
                ret.fromDict(strutil.loads(jstr))
        except:
            ftlog.error('FTTableFinishRecorder.loadModel BadData',
                        'actId=', self.actId,
                        'userId=', userId,
                        'jstr=', jstr)
        return self.adjust(ret, timestamp)

    def saveModel(self, model):
        if ftlog.is_debug():
            ftlog.debug('FTTableFinishRecorder.saveModel', 
                        'actId=', self.actId,
                        'userId=', model.userId,
                        'model=', model.toDict())
        
        jstr = strutil.dumps(model.toDict())
        daobase.executeUserCmd(model.userId, 'hset', 'act:%s:%s' % (DIZHU_GAMEID, model.userId), self.actId, jstr)

    def _onEvent(self, event):
        self._handleEvent(event)
        
    def _handleEvent(self, event):
        if ftlog.is_debug():
            ftlog.debug('FTTableFinishRecorder._handleEvent', 
                        'userId=', event.userId,
                        'ftId=', event.ftId,
                        'roomId=', event.roomId,
                        'tableId=', event.tableId)
        
        # 判断活动是否过期
        if self.checkTime(event.timestamp) != 0:
            if ftlog.is_debug():
                ftlog.debug('FTTableFinishRecorder._handleEvent OutDate',
                            'userId=', event.userId, 
                            'actId=', self.actId)
            return 
        
        model = self.loadModel(event.userId)
        model.finishCount += 1
        self.saveModel(model)
        
        # 每天第一次分享发送奖励
        if model.finishCount == 1:
            self.sendRewards(event.userId, event.timestamp)
                
    def sendRewards(self, userId, timestamp):
        if ftlog.is_debug():
            ftlog.debug('FTTableFinishRecorder.sendRewards', 
                        'userId=', userId,
                        'rewardContent=', self.rewardContent)
        
        if not self.rewardContent:
            return
        
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContent(DIZHU_GAMEID,
                                           self.rewardContent,
                                           1,
                                           True,
                                           timestamp,
                                           'ACTIVITY_REWARD',
                                           self.intActId)
        
        changed = None
        if assetList:
            changed = TYAssetUtils.getChangeDataNames(assetList)
        if self.mail:
            mail = strutil.replaceParams(self.mail, {'rewardContent':TYAssetUtils.buildContentsString(assetList)})
            pkmessage.sendPrivate(HALL_GAMEID, userId, 0, mail)
            if not changed:
                changed = set(['message'])
        if changed:
            datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, changed)

        ftlog.info('FTTableFinishRecorder.sendRewards',
                   'userId=', userId,
                   'rewards=', [(at[0].kindId, at[1]) for at in assetList])
        
    def _decodeFromDictImpl(self, d):
        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.rewardContent = TYContentRegister.decodeFromDict(rewardContent)

        self.mail = d.get('mail', '')
        if not isstring(self.mail):
            raise TYBizConfException(d, 'FTTableFinishRecorder._decodeFromDictImpl mail must be string')
        return self


