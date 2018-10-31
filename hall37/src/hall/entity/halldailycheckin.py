# -*- coding=utf-8
'''
Created on 2015年7月6日

@author: zhaojiangang
'''

from datetime import datetime
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallitem, hallconf, datachangenotify
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message import message as pkmessage
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.dao import userdata as pkuserdata
from poker.entity.events.tyevent import UserEvent
from hall.game import TGHall
import poker.entity.dao.gamedata as pkgamedata
from hall.entity.hallconf import HALL_GAMEID

class TYDailyCheckinRewardEvent(UserEvent):
    '''
    每日登陆奖励Event
    '''
    def __init__(self, gameId, userId, rewardContent, actionType=0):
        super(TYDailyCheckinRewardEvent, self).__init__(userId, gameId)
        self.rewardContent = rewardContent
        self.actionType = actionType

class TYDailyCheckinStatus(object):
    def __init__(self, firstCheckinTime=None, lastCheckinTime=None):
        self.firstCheckinTime = firstCheckinTime
        self.lastCheckinTime = lastCheckinTime
        
class TYDailyCheckinDao(object):
    def loadStatus(self, userId):
        try:
            firstDailyCheckin, lastDailyCheckin = pkuserdata.getAttrs(userId, ['firstDailyCheckin', 'lastDailyCheckin'])
            if ftlog.is_debug():
                ftlog.debug('TYDailyCheckinDao.loadStatus userId=', userId,
                            'firstDailyCheckin=', firstDailyCheckin,
                            'lastDailyCheckin=', lastDailyCheckin)
            if firstDailyCheckin and lastDailyCheckin:
                return TYDailyCheckinStatus(int(firstDailyCheckin), int(lastDailyCheckin))
        except:
            ftlog.error()
        return None
    
    def saveStatus(self, userId, status):
        pkuserdata.setAttrs(userId, {'firstDailyCheckin': status.firstCheckinTime, 
                                     'lastDailyCheckin' : status.lastCheckinTime
                                     })
    
class TYDailyCheckin(object):
    def getStates(self, gameId, userId, timestamp=None):
        raise NotImplemented()
    
    def checkin(self, gameId, userId, timestamp=None):
        raise NotImplemented()
    
    def gainCheckinReward(self, gameId, userId, timestamp=None, actionType=0):
        '''
        @return: checkinOk, rewardAssetList, checkinDays
        '''
        raise NotImplemented()
    
class TYDailyCheckinImpl(TYDailyCheckin):
    def __init__(self, dao):
        assert(isinstance(dao, TYDailyCheckinDao))
        self._dao = dao
        self._dailyRewards = None
        self._mail = None
        
    def reloadConf(self, conf):
        dailyRewards = []
        rewards = conf.get('rewards')
        if rewards:
            for reward in rewards:
                dailyRewards.append(TYContentRegister.decodeFromDict(reward))
        mail = conf.get('mail', '')
        if not isstring(mail):
            raise TYBizConfException(conf, 'TYDailyCheckinImpl.mail must be string')
        self._mail = mail
        self._dailyRewards = dailyRewards
        ftlog.debug('TYDailyCheckin.reloadConf successed conf=', conf)

    def getDailyRewards(self):
        return self._dailyRewards
    
    def getStates(self, gameId, userId, timestamp=None):
        '''
        @return: list<{'st':state, 'rewards':rewards}>
        '''
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        status = self._dao.loadStatus(userId)
        checkinDays, canCheckin = self.calcCheckinState(status, timestamp)
        states = []
        for i, rewards in enumerate(self._dailyRewards):
            state = 0
            if i < checkinDays:
                state = 2
            elif i == checkinDays:
                state = 1 if canCheckin else 2
            states.append({'st':state, 'rewards':rewards})
        return states
    
    # 是否充值，首充标记    
    def isFirstRecharged(self, userId):
        return pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'first_recharge') > 0
        
    # 利用每日游戏时长反作弊
    def antiCheatWithTodayTime(self, userId):
        todoayTime = pkgamedata.getGameAttrJson(userId, HALL_GAMEID, 'todaytime', {})
        dayCount = 0
        totalTime = 0
        for( _, value ) in todoayTime.items():
            totalTime += value
            dayCount += 1
        
        if ftlog.is_debug():
            ftlog.debug('antiCheatWithTodayTime in daily checkin userId =', userId, ' daysWithRecord = ', dayCount, ' gameTimeInDaysWithRecord = ', totalTime)
            
        cheatDays = hallconf._getHallPublic('cheatDays')    
        cheatGameTime = hallconf._getHallPublic('gameTime')
        if ftlog.is_debug():
            ftlog.debug('antiCheatWithTodayTime in daily checkin cheatDays = ', cheatDays, ' cheatGameTime = ', cheatGameTime)
        
        if dayCount >= cheatDays and totalTime < cheatGameTime:
            return True
        else:
            return False
        
    def isScriptDoGetReward(self, userId):
        isRecharged = self.isFirstRecharged(userId)
        return self.antiCheatWithTodayTime(userId) and not isRecharged
    
    def checkin(self, gameId, userId, timestamp=None):
        '''
        @return: checkinOk, checkinDays
        '''
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        status = self._dao.loadStatus(userId)
        checkinDays, canCheckin = self.calcCheckinState(status, timestamp)
        
        if canCheckin and self.isScriptDoGetReward(userId):
            canCheckin = 0
            
        if ftlog.is_debug():
            ftlog.debug('TYDailyCheckin.checkin gameId=', gameId,
                        'userId=', userId,
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'checkinDays=', checkinDays,
                        'canCheckin=', canCheckin,
                        'firstCheckinTime=', status.firstCheckinTime if status else None,
                        'lastCheckinTime=', status.lastCheckinTime if status else None)
            
        if not canCheckin:
            return 0, checkinDays
        
        if not status:
            status = TYDailyCheckinStatus(timestamp, timestamp)
        else:
            status.lastCheckinTime = timestamp
            if checkinDays == 0:
                status.firstCheckinTime = timestamp
        self._dao.saveStatus(userId, status)
        ftlog.debug('TYDailyCheckin.checkin ok gameId=', gameId,
                   'userId=', userId,
                   'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
        return 1, checkinDays
    
    def gainCheckinReward(self, gameId, userId, timestamp=None, actionType=0):
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        checkinOk, checkinDays = self.checkin(gameId, userId, timestamp)
        if ftlog.is_debug():
            ftlog.debug('TYDailyCheckin.gainCheckinReward gameId=', gameId,
                        'userId=', userId,
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'checkinOk=', checkinOk,
                        'checkinDays=', checkinDays)
        
        if not checkinOk:
            return checkinOk, [], checkinDays
        # 发送奖励
        rewardContent = self.getRewardContent(checkinDays)

        ebus = TGHall.getEventBus()
        ebus.publishEvent(TYDailyCheckinRewardEvent(gameId, userId, rewardContent, actionType))

        if not rewardContent:
            return checkinOk, [], checkinDays
        
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContent(gameId, rewardContent, 1, True,
                                           timestamp, 'NSLOGIN_REWARD2', checkinDays)
        contents = TYAssetUtils.buildContentsString(assetList)
        if self._mail:
            mail = strutil.replaceParams(self._mail, {'rewardContent': contents})
            pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
            datachangenotify.sendDataChangeNotify(gameId, userId, 'message')
            
        ftlog.debug('TYDailyCheckin.gainCheckinReward gameId=', gameId,
                   'userId=', userId,
                   'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                   'reward=', contents)
        return checkinOk, assetList, checkinDays
    
    def getRewardContent(self, checkinDays):
        return self._dailyRewards[checkinDays] if checkinDays >= 0 and checkinDays < len(self._dailyRewards) else None
    
    def calcCheckinState(self, status, timestamp):
        '''
        @return: (checkinDays, canCheckin)
        '''
        # 没签过到
        if not status:
            return 0, 1
        
        diffDays = (pktimestamp.getDayStartTimestamp(timestamp) \
                    - pktimestamp.getDayStartTimestamp(status.lastCheckinTime)) / 86400
        
        # 没有连续签到，重置为0
        if diffDays < 0 or diffDays > 1:
            ftlog.debug('TYDailyCheckin.calcCheckinState firstCheckin=', datetime.fromtimestamp(status.firstCheckinTime).strftime('%Y-%m-%d %H:%M:%S'),
                        'lastCheckin=', datetime.fromtimestamp(status.lastCheckinTime).strftime('%Y-%m-%d %H:%M:%S'),
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'diffDays=', diffDays,
                        'return=', '(0, 1)')
            return 0, 1
        
        # 计算连续签到天数
        checkinDays = max((pktimestamp.getDayStartTimestamp(timestamp) \
                    - pktimestamp.getDayStartTimestamp(status.firstCheckinTime)) / 86400, 0)
            
        canCheckin = 1       
        
        # 今天已经签过到了
        if diffDays == 0:
            canCheckin = 0
        
        # 连续签到满了，重新开始计算
        if checkinDays >= len(self._dailyRewards):
            ftlog.debug('TYDailyCheckin.calcCheckinState firstCheckin=', datetime.fromtimestamp(status.firstCheckinTime).strftime('%Y-%m-%d %H:%M:%S'),
                        'lastCheckin=', datetime.fromtimestamp(status.lastCheckinTime).strftime('%Y-%m-%d %H:%M:%S'),
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'diffDays=', diffDays,
                        'checkinDays=', checkinDays,
                        'return=', '(0, %s)' % (canCheckin))
            return 0, canCheckin
            
        ftlog.debug('TYDailyCheckin.calcCheckinState firstCheckin=', datetime.fromtimestamp(status.firstCheckinTime).strftime('%Y-%m-%d %H:%M:%S'),
                    'lastCheckin=', datetime.fromtimestamp(status.lastCheckinTime).strftime('%Y-%m-%d %H:%M:%S'),
                    'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'diffDays=', diffDays,
                    'checkinDays=', checkinDays,
                    'return=', '(%s, %s)' % (checkinDays, canCheckin))
        return checkinDays, canCheckin 

_inited = False
dailyCheckin = TYDailyCheckin()

def _reloadConf():
    global dailyCheckin
    conf = hallconf.getDailyCheckinConf()
    dailyCheckin.reloadConf(conf)

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:dailycheckin:0'):
        ftlog.debug('HallDailyCheckin._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('HallDailyCheckin initialize begin')
    global _inited
    global dailyCheckin
    if not _inited:
        _inited = True
        dailyCheckin = TYDailyCheckinImpl(TYDailyCheckinDao())
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('HallDailyCheckin initialize end')

    
