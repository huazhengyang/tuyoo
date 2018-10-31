# -*- coding:utf-8 -*-
'''
Created on 2017年11月24日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hall_timecycle import HallTimeCycleLife, HallTimeCycleDay, \
    HallTimeCycleRegister
from hall.entity.hallconf import HALL_GAMEID
from hall.game import TGHall
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure
from poker.entity.dao import userdata, daobase
from poker.entity.events.tyevent import EventUserLogin, ChargeNotifyEvent, \
    GameOverEvent, EventConfigure, UserEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class YYBGiftBeforeGainEvent(UserEvent):
    def __init__(self, userId, gameId, kindId):
        super(YYBGiftBeforeGainEvent, self).__init__(userId, gameId)
        self.kindId = kindId


class YYBGiftStatus(object):
    def __init__(self, kind):
        # 类型
        self.kind = kind
        # 完成时间, 0表示没有完成
        self.finishTime = 0
        # 领取时间, 0表示没有领取
        self.gainTime = 0
        # 最后更新时间
        self.lastUpdateTime = 0
    
    @property
    def kindId(self):
        return self.kind.kindId
    
    @property
    def isFinished(self):
        return self.finishTime != 0
    
    @property
    def isGain(self):
        return self.gainTime != 0
    
    def fromDict(self, d):
        self.finishTime = d['ft']
        self.gainTime = d['gt']
        self.lastUpdateTime = d['lut']
        self._fromDict(d)
        return self
    
    def toDict(self):
        d = {
            'ft':self.finishTime,
            'gt':self.gainTime,
            'lut':self.lastUpdateTime
        }
        self._toDict(d)
        return d
    
    def isSameCycle(self, timestamp):
        return self.lastUpdateTime and self.kind.cycle.isSameCycle(timestamp, self.lastUpdateTime)
        
    def adjust(self, timestamp):
        if not self.isSameCycle(timestamp):
            self.finishTime = 0
            self.gainTime = 0
            self.lastUpdateTime = timestamp
            self._reset(timestamp)
            return True
        return False
    
    def processEvent(self, event, timestamp):
        # 没有完成时或者完成了但不在一个周期
        if ((not self.finishTime or not self.isSameCycle(timestamp))
            and (not self.kind.gameIds or event.gameId in self.kind.gameIds)
            and self._processEvent(event, timestamp)):
            return True
        return False
        
    def _processEvent(self, event, timestamp):
        return False
    
    def _fromDict(self, d):
        pass
    
    def _toDict(self, d):
        pass
    
    def _reset(self, timestamp):
        pass
    

class YYBGiftKind(TYConfable):
    eventTypes = []
                  
    def __init__(self):
        # 种类ID
        self.kindId = None
        # 奖励内容
        self.rewardContent = None
        # 礼包周期
        self.cycle = None
        # 处理哪个游戏的
        self.gameIds = []
    
    def newStatusForDecode(self):
        return self._newStatus()

    def newStatus(self, timestamp):
        status = self._newStatus()
        status.adjust(timestamp)
        return status
    
    def decodeFromDict(self, d):
        self.kindId = d.get('kindId')
        if not isinstance(self.kindId, int):
            raise TYBizConfException(d, 'YYBGiftKind.kindId must be int')
        self.rewardContent = TYContentRegister.decodeFromDict(d['reward'])
        self._decodeFromDict(d)
        return self
    
    def _newStatus(self):
        raise NotImplementedError
    
    def _decodeFromDict(self, d):
        pass


class YYBNewUserGiftStatus(YYBGiftStatus):
    def __init__(self, kind):
        super(YYBNewUserGiftStatus, self).__init__(kind)

    def _processEvent(self, event, timestamp):
        if (isinstance(event, EventUserLogin)
            and event.isCreate):
            self.finishTime = timestamp
            self.gainTime = 0
            return True
        return False


class YYBNewUserGift(YYBGiftKind):
    TYPE_ID = 'yyb.gift:newUser'
    
    eventTypes = [EventUserLogin]
    
    def __init__(self):
        super(YYBNewUserGift, self).__init__()
        self.cycle = HallTimeCycleLife()
        self.gameIds = [9999]

    def _newStatus(self):
        return YYBNewUserGiftStatus(self)


class YYBDailyLoginGiftStatus(YYBGiftStatus):
    def __init__(self, kind):
        super(YYBDailyLoginGiftStatus, self).__init__(kind)

    def _processEvent(self, event, timestamp):
        # 同一周期不做处理
        if (isinstance(event, EventUserLogin)
            and not self.kind.cycle.isSameCycle(self.finishTime, timestamp)):
            self.finishTime = timestamp
            self.gainTime = 0
            return True
        return False


class YYBDailyLoginGift(YYBGiftKind):
    '''
    每日登录礼包，每天只处理一次
    '''
    TYPE_ID = 'yyb.gift:dailyLogin'
    
    eventTypes = [EventUserLogin]
    
    def __init__(self):
        super(YYBDailyLoginGift, self).__init__()
        self.cycle = HallTimeCycleDay()
        self.gameIds = [9999]
        
    def _newStatus(self):
        return YYBDailyLoginGiftStatus(self)


class YYBExclusiveGiftStatus(YYBGiftStatus):
    def __init__(self, kind):
        super(YYBExclusiveGiftStatus, self).__init__(kind)
        self.minCharge = 15
        
    def _processEvent(self, event, timestamp):
        # 充值达到chargeTotal
        if (isinstance(event, (EventUserLogin, ChargeNotifyEvent))
            and userdata.getAttrInt(event.userId, 'chargeTotal') >= self.minCharge):
            self.finishTime = timestamp
            self.gainTime = 0
            return True
        return False


class YYBExclusiveGift(YYBGiftKind):
    '''
    应用宝专属礼包
    '''
    TYPE_ID = 'yyb.gift:exclusive'
    
    eventTypes = [EventUserLogin, ChargeNotifyEvent]
    
    def __init__(self):
        super(YYBExclusiveGift, self).__init__()
        self.cycle = HallTimeCycleLife()
    
    def _newStatus(self):
        return YYBExclusiveGiftStatus(self)


class YYBDDZRoundGiftStatus(YYBGiftStatus):
    def __init__(self, kind):
        super(YYBDDZRoundGiftStatus, self).__init__(kind)
        self.progress = 0
    
    def _fromDict(self, d):
        self.progress = d.get('prog', 0)

    def _toDict(self, d):
        d['prog'] = self.progress
    
    def _reset(self, timestamp):
        self.progress = 0
    
    def _processEvent(self, event, timestamp):
        # 每次进度+1
        if isinstance(event, (GameOverEvent, EventUserLogin)):
            if isinstance(event, GameOverEvent):
                self.progress += 1
            if self.progress >= self.kind.nRound:
                self.finishTime = timestamp
                self.gainTime = 0
            return True
        return False


class YYBDDZRoundGift(YYBGiftKind):
    '''
    斗地主N局礼包
    '''
    TYPE_ID = 'yyb.gift:ddzRound'
    
    eventTypes = [GameOverEvent]
    
    def __init__(self):
        super(YYBDDZRoundGift, self).__init__()
        self.cycle = HallTimeCycleDay()
        self.nRound = 0
        self.gameIds = [6]
    
    def _decodeFromDict(self, d):
        self.nRound = d.get('round')
        if not isinstance(self.nRound, int) or self.nRound <= 0:
            raise TYBizConfException('YYBDDZRoundGift.round must be int > 0')
    
    def _newStatus(self):
        return YYBDDZRoundGiftStatus(self)


class YYBBackGiftStatus(YYBGiftStatus):
    def __init__(self, kind):
        super(YYBBackGiftStatus, self).__init__(kind)
    
    def _processEvent(self, event, timestamp):
        # 
        if isinstance(event, EventUserLogin):
            lastAuthTime, authTime = userdata.getAttrs(event.userId, ['lastAuthorTime', 'authorTime'])
            if lastAuthTime and authTime:
                try:
                    if pktimestamp.getTimeStrDiff(lastAuthTime, authTime) >= self.kind.nBackDays * 86400:
                        self.finishTime = timestamp
                        self.gainTime = 0
                        return True
                except:
                    ftlog.error('YYBBackGiftStatus._processEvent',
                                'userId=', event.userId,
                                'times=', [lastAuthTime, authTime])
                    return False
        return False


class YYBBackGift(YYBGiftKind):
    '''
    回流礼包
    '''
    TYPE_ID = 'yyb.gift:back30Day'
    
    eventTypes = [EventUserLogin]
    
    def __init__(self):
        super(YYBBackGift, self).__init__()
        self.cycle = HallTimeCycleLife()
        self.nBackDays = 30
    
    def _newStatus(self):
        return YYBBackGiftStatus(self)


class YYBVPlusGiftStatus(YYBGiftStatus):
    def __init__(self, kind):
        super(YYBVPlusGiftStatus, self).__init__(kind)
    
    def _processEvent(self, event, timestamp):
        if (isinstance(event, YYBGiftBeforeGainEvent)
            and event.kindId == self.kindId):
            self.finishTime = timestamp
            self.gainTime = 0
            return True
        return False


class YYBVPlusGift(YYBGiftKind):
    '''
    '''
    TYPE_ID = 'yyb.gift:vplus'
    
    eventTypes = [YYBGiftBeforeGainEvent]
    
    def __init__(self):
        super(YYBVPlusGift, self).__init__()
        self.cycle = None
        
    def _decodeFromDict(self, d):
        self.cycle = HallTimeCycleRegister.decodeFromDict(d['cycle'])
        
    def _newStatus(self):
        return YYBVPlusGiftStatus(self)

 
class YYBGiftKindRegister(TYConfableRegister):
    _typeid_clz_map = {
        YYBNewUserGift.TYPE_ID:YYBNewUserGift,
        YYBDailyLoginGift.TYPE_ID:YYBDailyLoginGift,
        YYBExclusiveGift.TYPE_ID:YYBExclusiveGift,
        YYBDDZRoundGift.TYPE_ID:YYBDDZRoundGift,
        YYBBackGift.TYPE_ID:YYBBackGift,
        YYBVPlusGift.TYPE_ID:YYBVPlusGift
    }


# map<kindId, YYBGiftKind>
_giftKindMap = {}
_inited = False


STATE_GAIN = 0
STATE_UNCONFORM = 1
STATE_ALREADY_GAIN = 2 


def findGiftKind(kindId):
    return _giftKindMap.get(kindId)


def sendReward(userId, status):
    from hall.entity import hallitem

    if status.kind.rewardContent:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContent(HALL_GAMEID, status.kind.rewardContent, 1, True,
                                           pktimestamp.getCurrentTimestamp(),
                                           'YYB_GIFT_REWARD', status.kindId)
        ftlog.info('hall_yyb_gifts.sendReward',
                   'userId=', userId,
                   'kindId=', status.kindId,
                   'rewards=', [(atup[0].kindId, atup[1]) for atup in assetList])
    
        changedDataNames = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, changedDataNames)
        return assetList
    
    return None


def calcState(status):
    if not status:
        return STATE_UNCONFORM
    
    if not status.isFinished:
        return STATE_UNCONFORM
    
    if status.isGain:
        return STATE_ALREADY_GAIN
    
    return STATE_GAIN


def gainUserGift(userId, kindId, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    status = loadAndInitUserGiftStatus(userId, kindId, timestamp)
    if status:
        _processEvent(YYBGiftBeforeGainEvent(userId, HALL_GAMEID, kindId), status, timestamp)
    state = calcState(status)
    
    reward = None
    if state == STATE_GAIN:
        status.gainTime = status.lastUpdateTime = timestamp
        _saveUserGiftStatus(userId, status)
        # 发送奖励
        reward = sendReward(userId, status)
    return state, reward


def _decodeUserGiftStatus(giftKind, data):
    d = strutil.loads(data)
    status = giftKind.newStatusForDecode()
    status.fromDict(d)
    return status


def _loadAllUserGiftStatus(userId):
    ret = {}
    datas = daobase.executeUserCmd(userId, 'hgetall', 'yyb.gifts:%s' % (userId))
    if datas:
        for i in xrange(len(datas) / 2):
            try:
                kindId = int(datas[i * 2])
                data = datas[i * 2 + 1]
                
                if ftlog.is_debug():
                    ftlog.debug('hall_yyb_gifts._loadAllUserGiftStatus',
                                'userId=', userId,
                                'kindId=', kindId,
                                'data=', data)
                    
                giftKind = findGiftKind(kindId)
                if not giftKind:
                    ftlog.warn('UnknownYYBGiftKind',
                               'userId=', userId,
                               'kindId=', kindId,
                               'data=', data)
                    continue
                status = _decodeUserGiftStatus(giftKind, data)
                ret[kindId] = status
            except:
                ftlog.warn('BadYYBGiftKindData',
                           'userId=', userId,
                           'kindId=', data[i * 2],
                           'data=', data[i * 2 + 1])
    return ret


def loadAndInitUserGiftStatus(userId, kindId, timestamp):
    giftKind = findGiftKind(kindId)
    if not giftKind:
        ftlog.warn('UnknownYYBGiftKind',
                   'userId=', userId,
                   'kindId=', kindId)
        return None
    jstr = daobase.executeUserCmd(userId, 'hget', 'yyb.gifts:%s' % (userId), kindId)
    if jstr:
        status = _decodeUserGiftStatus(giftKind, jstr)
        status.adjust(timestamp)
    else:
        status = giftKind.newStatus(timestamp)
    return status


def _saveUserGiftStatus(userId, status):
    d = status.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(userId, 'hset', 'yyb.gifts:%s' % (userId), status.kindId, jstr)
    if ftlog.is_debug():
        ftlog.debug('hall_yyb_gifts._saveUserGiftStatus',
                    'userId=', userId,
                    'kindId=', status.kindId,
                    'jstr=', jstr)


def _initUserGiftStatusMap(userGiftStatusMap, timestamp):
    '''
    初始化用户的应用宝礼包数据，如果没有的礼包重新生成
    '''
    giftKinds = _giftKindMap.values()
    for giftKind in giftKinds:
        status = userGiftStatusMap.get(giftKind.kindId)
        if not status:
            status = giftKind.newStatus(timestamp)
            userGiftStatusMap[giftKind.kindId] = status
        else:
            status.adjust(timestamp)
    
    return userGiftStatusMap


def loadAndInitUserGifts(userId, timestamp):
    userGiftStatusMap = _loadAllUserGiftStatus(userId)
    return _initUserGiftStatusMap(userGiftStatusMap, timestamp)


def _handleEvent(event):
    timestamp = pktimestamp.getCurrentTimestamp()
    userGiftStatusMap = loadAndInitUserGifts(event.userId, timestamp)

    if ftlog.is_debug():
        ftlog.debug('hall_yyb_gifts._handleEvent',
                    'eventType=', type(event),
                    'timestamp=', timestamp,
                    'status=', userGiftStatusMap.keys())
    for status in userGiftStatusMap.values():
        _processEvent(event, status, timestamp)


def _processEvent(event, status, timestamp):
    if type(event) in status.kind.eventTypes:
        if status.processEvent(event, timestamp):
            ftlog.info('hall_yyb_gifts._processEvent',
                       'userId=', event.userId,
                       'kindId=', status.kindId,
                       'status=', status.toDict(),
                       'state=', calcState(status))
            _saveUserGiftStatus(event.userId, status)


def _registerEvents(giftKinds):
    for giftKind in giftKinds:
        for eventType in giftKind.eventTypes:
            TGHall.getEventBus().subscribe(eventType, _handleEvent)


def _unregisterEvents(giftKinds):
    for giftKind in giftKinds:
        for eventType in giftKind.eventTypes:
            TGHall.getEventBus().unsubscribe(eventType, _handleEvent)


def _reloadConf():
    global _giftKindMap
    giftKindMap = {}
    conf = configure.getGameJson(HALL_GAMEID, 'yyb.gifts', {}, 0)
    for giftKindD in conf.get('gifts', []):
        giftKind = YYBGiftKindRegister.decodeFromDict(giftKindD)
        if giftKind.kindId in giftKindMap:
            raise TYBizConfException(giftKindD, 'Duplicate kindId %s' % (giftKind.kindId))
        giftKindMap[giftKind.kindId] = giftKind
    
    if _giftKindMap:
        _unregisterEvents(_giftKindMap.values())
    
    _giftKindMap = giftKindMap
    
    if _giftKindMap:
        _registerEvents(_giftKindMap.values())
    
    ftlog.info('hall_yyb_fits._reloadConf',
               'giftKinds=', giftKindMap.keys())
    

def _onConfChanged(event):
    if _inited and event.isModuleChanged('yyb.gifts'):
        ftlog.debug('hall_yyb_gifts._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.debug('hall_yyb_gifts initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_yyb_gifts initialize end')
        

