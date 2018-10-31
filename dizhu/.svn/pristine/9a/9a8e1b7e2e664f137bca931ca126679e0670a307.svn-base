# -*- coding:utf-8 -*-
'''
Created on 2016年8月20日

@author: zhaojiangang
'''

from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.utils import TimeCycleRegister
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.todotask import TodoTaskHelper
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import pokerconf, configure
from poker.entity.dao import sessiondata, daobase
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

class PlayGameTodotask(ActivityNew):
    TYPE_ID = 'ddz.act.play_game_todotask'

    def __init__(self):
        super(PlayGameTodotask, self).__init__()
        self._cycle = None
        self._condition = None
        # item = (playRound, TodotaskFactory)
        self._playRounds = None
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
                ftlog.debug('PlayGameTodotask.isSupportedClient BadClientId clientId=', clientId,
                            'intClientId=', intClientId)
            return False
        
        conf = configure.getGameJson(DIZHU_GAMEID, 'playgame.todotask', {}, intClientId)
        if ftlog.is_debug():
            ftlog.debug('PlayGameTodotask.isSupportedClient clientId=', clientId,
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
                ftlog.debug('PlayGameTodotask._handleTableWinlose NotSupportedClientId gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        hallGameId = strutil.getGameIdFromHallClientId(clientId)
        if hallGameId not in self._hallGameIds:
            if ftlog.is_debug():
                ftlog.debug('PlayGameTodotask._handleTableWinlose NotSupportedHallGameId gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        if not self._condition.check(event.gameId, event.userId, clientId, event.timestamp):
            if ftlog.is_debug():
                ftlog.debug('PlayGameTodotask._handleTableWinlose CheckCond gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds)
            return
        
        status = self.loadStatus(event.userId, event.timestamp)
        status.playRound += 1
        status.lastUpdateTime = event.timestamp
        self.saveStatus(status)
        
        todotaskFac = self._findTodotaskByPlayRound(status.playRound)
        if todotaskFac:
            todotask = todotaskFac.newTodoTask(event.gameId, event.userId, clientId)
            if not todotask:
                ftlog.warn('PlayGameTodotask._handleTableWinlose CreateTodotask gameId=', event.gameId,
                            'userId=', event.userId,
                            'clientId=', clientId,
                            'actId=', self.actId,
                            'hallGameIds=', self._hallGameIds,
                            'playRound=', status.playRound,
                            'todotaskFac=', todotaskFac)
                return
    
            TodoTaskHelper.sendTodoTask(event.gameId, event.userId, todotask)        
            
    def _findTodotaskByPlayRound(self, playRound):
        for playRoundConf, todotaskFac in self._playRounds:
            if playRoundConf == playRound:
                return todotaskFac
        return None
    
    def _decodeFromDictImpl(self, d):
        from hall.entity import hallpopwnd
        self._cycle = TimeCycleRegister.decodeFromDict(d.get('cycle'))
        self._condition = UserConditionRegister.decodeFromDict(d.get('condition'))
        playRounds = d.get('playRounds', [])
        if not playRounds or not isinstance(playRounds, list):
            raise TYBizConfException(d, 'PlayGameTodotask.playRounds must be not empty list')
        self._playRounds = []
        for item in playRounds:
            if not item or not isinstance(item, dict):
                raise TYBizConfException(d, 'PlayGameTodotask.playRounds.item must be not empty dict')
            playRound = item.get('playRound')
            if not isinstance(playRound, int):
                raise TYBizConfException(d, 'PlayGameTodotask.playRounds.item.playRound must be int')
            todotaskFac = hallpopwnd.decodeTodotaskFactoryByDict(item.get('todotask'))
            self._playRounds.append((playRound, todotaskFac))
        self._hallGameIds = d.get('hallGameIds', [])
        if not isinstance(self._hallGameIds, list):
            raise TYBizConfException(d, 'PlayGameTodotask.hallGameIds must be list')
        for hallGameId in self._hallGameIds:
            if not isinstance(hallGameId, int):
                raise TYBizConfException(d, 'PlayGameTodotask.hallGameIds must be int list')
        return self


