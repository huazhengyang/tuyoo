# -*- coding:utf-8 -*-
'''
Created on 2016年8月20日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.utils import TimeCycleRegister
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from hall.entity import hallshare
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.todotask import TodoTaskHelper
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import pokerconf, configure
from poker.entity.dao import sessiondata, daobase
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class PlayGameStatus(object):
    def __init__(self, userId):
        self.userId = userId
        self.playRound = 0
        self.lastUpdateTime = 0
    
    def fromDict(self, d):
        self.playRound = d['pr']
        self.lastUpdateTime = d['lut']
        return self
    
    def toDict(self):
        return {'pr':self.playRound, 'lut':self.lastUpdateTime}
    
def loadStatus(userId, actId):
    jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (DIZHU_GAMEID, userId), actId)
    if jstr:
        try:
            d = strutil.loads(jstr)
            return PlayGameStatus(userId).fromDict(d)
        except:
            ftlog.error('play_game_share.loadStatus userId=', userId,
                        'actId=', actId,
                        'jstr=', jstr)
    return None

def saveStatus(actId, status):
    d = status.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(status.userId, 'hset', 'act:%s:%s' % (DIZHU_GAMEID, status.userId), actId, jstr)

class PlayGameShare(ActivityNew):
    TYPE_ID = 'ddz.act.play_game_share'

    def __init__(self):
        super(PlayGameShare, self).__init__()
        self._cycle = None
        self._condition = None
        self._shareLoc = None
        self._shares = None
        self._hallGameIds = None
        
    def init(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, self._onTableWinlose)
    
    def cleanup(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().unsubscribe(UserTableWinloseEvent, self._onTableWinlose)

    def isSupportedClient(self, clientId):
        intClientId = pokerconf.clientIdToNumber(clientId)
        if intClientId == 0:
            if ftlog.is_debug():
                ftlog.debug('PlayGameShare.isSupportedClient BadClientId clientId=', clientId,
                            'intClientId=', intClientId)
            return False
        
        conf = configure.getGameJson(DIZHU_GAMEID, 'share.playgame', {}, intClientId)
        if ftlog.is_debug():
            ftlog.debug('PlayGameShare.isSupportedClient clientId=', clientId,
                        'intClientId=', intClientId,
                        'conf=', conf)
        return True if self.actId in conf.get('acts', []) else False
    
    def loadStatus(self, userId, timestamp=None):
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        status = loadStatus(userId, self.actId)
        if not status:
            status = PlayGameStatus(userId)
        return self._adjustStatus(status, timestamp)
       
    def saveStatus(self, status):
        saveStatus(self.actId, status)
        
    def _adjustStatus(self, status, timestamp):
        if not self._cycle.isSameCycle(status.lastUpdateTime, timestamp):
            status.lastUpdateTime = timestamp
            status.playRound = 0
        return status
        
    def _onTableWinlose(self, event):
        self._handleTableWinlose(event)
    
    def _handleTableWinlose(self, event):
        clientId = sessiondata.getClientId(event.userId)
        
        # 检查这个clientId是否配置了本活动
        if not self.isSupportedClient(clientId):
            if ftlog.is_debug():
                ftlog.debug('PlayGameShare._handleTableWinlose NotSupportedClientId gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        hallGameId = strutil.getGameIdFromHallClientId(clientId)
        if hallGameId not in self._hallGameIds:
            if ftlog.is_debug():
                ftlog.debug('PlayGameShare._handleTableWinlose NotSupportedHallGameId gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        if not self._condition.check(event.gameId, event.userId, clientId, event.timestamp):
            if ftlog.is_debug():
                ftlog.debug('PlayGameShare._handleTableWinlose CheckCond gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        status = self.loadStatus(event.userId, event.timestamp)
        status.playRound += 1
        self.saveStatus(status)
        
        share = self._findShareByPlayRound(status.playRound)
        
        canReward, rewardCount = hallshare.checkCanReward(event.userId, share, event.timestamp)
        if not canReward:
            if ftlog.is_debug():
                ftlog.debug('PlayGameShare._handleTableWinlose NotCanReward gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds,
                            'playRound=', status.playRound,
                            'rewardCount=', rewardCount,
                            'maxRewardCount=', share.maxRewardCount)
            return
        
        ftlog.info('PlayGameShare._handleTableWinlose gameId=', event.gameId,
                   'userId=', event.userId,
                   'clientId=', clientId,
                   'actId=', self.actId,
                   'hallGameIds=', self._hallGameIds,
                   'playRound=', status.playRound,
                   'rewardCount=', rewardCount,
                   'maxRewardCount=', share.maxRewardCount)
        
        todotask = share.buildTodotask(event.gameId, event.userId, self._shareLoc)
        mo = TodoTaskHelper.makeTodoTaskMsg(event.gameId, event.userId, todotask)
        router.sendToUser(mo, event.userId)
            
    def _findShareByPlayRound(self, playRound):
        for s in self._shares:
            if s['playRound'] == playRound:
                return hallshare.findShare(s['shareId'])
        return None
    
    def _decodeFromDictImpl(self, d):
        self._cycle = TimeCycleRegister.decodeFromDict(d.get('cycle'))
        self._condition = UserConditionRegister.decodeFromDict(d.get('condition'))
        self._shareLoc = d.get('shareLoc', 'playGame')
        if not isstring(self._shareLoc):
            raise TYBizConfException(d, 'PlayGameShare.shareLoc must be not empty string')
        self._shares = d.get('shares', [])
        if not self._shares or not isinstance(self._shares, list):
            raise TYBizConfException(d, 'PlayGameShare.shares must be not empty list')
        for s in self._shares:
            if not s or not isinstance(s, dict):
                raise TYBizConfException(d, 'PlayGameShare.shares.item must be not empty dict')
            playRound = s.get('playRound')
            if not isinstance(playRound, int):
                raise TYBizConfException(d, 'PlayGameShare.shares.item.playRound must be int')
            shareId = s.get('shareId')
            if not isinstance(shareId, int):
                raise TYBizConfException(d, 'PlayGameShare.shares.item.shareId must be int')
        self._hallGameIds = d.get('hallGameIds', [])
        if not isinstance(self._hallGameIds, list):
            raise TYBizConfException(d, 'PlayGameShare.hallGameIds must be list')
        for hallGameId in self._hallGameIds:
            if not isinstance(hallGameId, int):
                raise TYBizConfException(d, 'PlayGameShare.hallGameIds must be int list')
        return self


