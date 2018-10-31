# -*- coding: utf-8 -*-
'''
Created on Aug 4, 2015

@author: hanwf
@summary: 牌桌弹窗分享
'''
from datetime import datetime

from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from hall.entity import hallshare
from hall.entity.hallusercond import UserConditionAND, UserConditionRegisterDay, \
    UserConditionVipLevel
from hall.entity.todotask import TodoTaskHelper
from poker.entity.dao import gamedata, sessiondata
from poker.protocol import router
import poker.util.timestamp as pktimestamp


GAMEID = 6

class SharePlayground(object):
    eventset = [UserTableWinloseEvent]
    name = "SHARE_PLAYGROUND"
    
    attr_day = 'day'
    attr_round = 'playground'
    
    @classmethod
    def checkConditions(cls, userId, clientId, timestamp):
        cond = UserConditionAND()
        cond.conditions.append(UserConditionRegisterDay(7, -1))
        cond.conditions.append(UserConditionVipLevel(-1, 1))
        return cond.check(DIZHU_GAMEID, userId, clientId, timestamp)
        
    @classmethod
    def wrapDay(cls):
        return ':'.join([cls.name, cls.attr_day])
    
    @classmethod
    def wrapRound(cls):
        return ':'.join([cls.name, cls.attr_round])
    
    @classmethod
    def registerEvents(cls, eventBus):
        ftlog.debug('sendShare share_playground register events')
        for event in cls.eventset:
            eventBus.subscribe(event, cls.handleEvent)
    
    @classmethod
    def isDisable(cls):
        return dizhuconf.getShareConf().get('disable', 0) == 1
        
    @classmethod
    def handleEvent(cls, event):
        try:
            if ftlog.is_debug():
                ftlog.debug('SharePlayground.handleEvent gameId=', event.gameId,
                            'userId=', event.userId,
                            'eventType=', type(event),
                            'isDisable=', cls.isDisable())
            if isinstance(event, UserTableWinloseEvent) and not cls.isDisable():
                clientId = sessiondata.getClientId(event.userId)
                if cls.checkConditions(event.userId, clientId, event.timestamp):
                    Share.sendShare(event.gameId, event.userId, cls)
                else:
                    if ftlog.is_debug():
                        ftlog.debug('SharePlayground.handleEvent CheckConditionsFailed gameId=', event.gameId,
                                    'userId=', event.userId,
                                    'eventType=', type(event))
        except:
            ftlog.exception()
    
    @classmethod
    def handler(cls, userId):
        cls.cycleCheck(userId)
        
        playround = gamedata.incrGameAttr(userId, GAMEID, ':'.join([cls.name, cls.attr_round]), 1)
        
        clientId = sessiondata.getClientId(userId)
        ftlog.debug('sendShare playground handler userId=', userId, 'clientId=', clientId)
        return cls.findShare(clientId, playround), playround

    @classmethod
    def cycleCheck(cls, userId):
        '''
        牌局分享周期检测，1天为周期
        '''
        day_now = datetime.now().date()
        day = gamedata.getGameAttr(userId, GAMEID, cls.wrapDay())
        
        ftlog.debug('sendShare checkCycles day=', day, 'userId=', userId, 'gameId=', GAMEID)
        if not day:
            gamedata.setGameAttr(userId, GAMEID, cls.wrapDay(), day_now.strftime("%Y-%m-%d"))
        else:
            day = datetime.strptime(day, '%Y-%m-%d').date()
            if (day_now - day).days >= 1:
                gamedata.setGameAttr(userId, GAMEID, cls.wrapDay(), day_now.strftime("%Y-%m-%d"))
                gamedata.setGameAttr(userId, GAMEID, cls.wrapRound(), 0)
    
    @classmethod
    def findShare(cls, clientId, playround):
        '''
        @return: share or None
        '''
        shareConf = dizhuconf.getClientShareConf(clientId, {})
        shareId = shareConf.get(cls.name, {}).get(str(playround), None)
        ftlog.debug('sendShare shareConf=', shareConf, "clientId=", clientId, "playround=", playround, "shareId=", shareId)
        if not shareId:
            return None
        return hallshare.findShare(shareId)
        
class Share(object):
    
    @classmethod
    def sendShare(self, gameId, userId, shareLoc):
        '''
        通用活动todotask调用接口
        '''
        try:
            share, playground = shareLoc.handler(userId)         
            if not share:
                if ftlog.is_debug():
                    ftlog.debug('Share.sendShare notFoundShare gameId=', gameId,
                                'userId=', userId,
                                'shareLoc=', shareLoc.name)
                return
            
            if ftlog.is_debug():
                ftlog.debug('Share.sendShare notFoundShare gameId=', gameId,
                            'userId=', userId,
                            'shareLoc=', shareLoc.name,
                            'shareId=', share.shareId,
                            'playground=', playground)
            
            canReward, rewardCount = hallshare.checkCanReward(userId, share, pktimestamp.getCurrentTimestamp())
            if not canReward:
                if ftlog.is_debug():
                    ftlog.debug('Share.sendShare gameId=', gameId,
                                'userId=', userId,
                                'shareLoc=', shareLoc.name,
                                'shareId=', share.shareId,
                                'playground=', playground,
                                'rewardCount=', rewardCount,
                                'maxRewardCount=', share.maxRewardCount)
                return
            
            ftlog.debug('Share.sendShare gameId=', gameId,
                       'userId=', userId,
                       'shareLoc=', shareLoc.name,
                       'shareId=', share.shareId,
                       'playground=', playground,
                       'rewardCount=', rewardCount)
            
            todotask = share.buildTodotask(gameId, userId, shareLoc.name)
            mo = TodoTaskHelper.makeTodoTaskMsg(gameId, userId, todotask)
            router.sendToUser(mo, userId)
        except:
            ftlog.error('Share.sendShare notFoundShare gameId=', gameId,
                        'userId=', userId,
                        'shareLoc=', shareLoc.name)
    
    
    