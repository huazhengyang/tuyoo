# -*- coding:utf-8 -*-
'''
Created on 2017年12月7日

@author: zhaojiangang
'''

from datetime import datetime
import random
from sre_compile import isstring

from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from hall.entity import hallvip, hallitem, datachangenotify, \
    hall_red_packet_const
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import HallShare2Event, UserReceivedCouponEvent, \
    UserGrabRedPacketEvent
from hall.entity.hallshare import HallShareEvent
from hall.entity.hallusercond import UserConditionRegister, UserCondition
from poker.entity.biz.content import TYContentItem, TYContentItemGenerator
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.configure import gdata, configure
from poker.entity.dao import daobase, userdata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


TRIGGLE_ID_TIME = 99990001


# 是否初始化
_inited = False
# 计划好的红包雨
_scheduleRains = []
_scheduleRainMap = {}
_lastScheduleTimestamp = 0
_processTimer = None

# 红包雨状态
_rainStatus = None

# 配置
_conf = None


_update_no1_alias = 'hall_red_packet_rain.update_no1'
_update_no1_script = '''
local no1Key = KEYS[1]
local userId = tonumber(KEYS[2])
local value = tonumber(KEYS[3])
local no1 = redis.call('hmget', no1Key, 'userId', 'value')
local no1UserId = tonumber(no1[1])
local no1Value = tonumber(no1[2])
if not no1UserId or no1Value == nil or value > no1Value then
    redis.call('hmset', no1Key, 'userId', userId, 'value', value)
    return {userId, value}
end
return {no1UserId, no1Value}
'''


_get_danmu_alias = 'hall_red_packet_rain.get_danmu'
_get_danmu_script = '''
local listKey = KEYS[1]
local infoKey = KEYS[2]
local start = tonumber(KEYS[3])
local count = tonumber(KEYS[4])
local delCount = redis.call('hget', infoKey, 'delCount')
if not delCount then
    delCount = 0
end
start = start - delCount
if start < 0 then
    start = 0
end
count = math.max(1, count)
return {start + delCount, delCount, redis.call('lrange', listKey, start, start + count - 1)}
'''


_trim_danmu_alias = 'hall_red_packet_rain.trim_danmu'
_trim_danmu_script = '''
local listKey = KEYS[1]
local infoKey = KEYS[2]
local minCount = tonumber(KEYS[3])
local maxCount = tonumber(KEYS[4])
local len = redis.call('llen', listKey)
if len > maxCount then
    local trimCount = len - minCount
    if trimCount > 0 then
        redis.call('ltrim', listKey, trimCount, -1)
        redis.call('hincrby', infoKey, 'delCount', trimCount)
        return trimCount
    end
end
return 0
'''


class RedPacketRainStopped(TYBizException):
    def __init__(self, message='本次红包雨已经结束'):
        super(RedPacketRainStopped, self).__init__(-1, message)


class RPConf(object):
    '''
    红包配置，用于生成红包
    '''
    def __init__(self):
        # 条件
        self.condition = None
        # 中奖概率
        self.ratio = None
        # 奖励列表(weightStart, weightStop, itemGen)
        self.rewards = []
        # 总权重
        self.totalWeight = 0
    
    def decodeFromDict(self, d):
        cond = d.get('condition')
        if cond:
            self.condition = UserConditionRegister.decodeFromDict(cond)
        
        self.ratio = d.get('ratio')
        if not isinstance(self.ratio, (int, float)) or self.ratio < 0 or self.ratio > 1:
            raise TYBizConfException(d, 'RPConf.rewards.item.ratio must be float >=0 and <= 1')
        
        for rewardD in d.get('rewards', []):
            weight = rewardD.get('weight')
            if not isinstance(weight, int) or weight < 0:
                raise TYBizConfException(rewardD, 'RPConf.rewards.item.weight must be int >= 0')
            itemGen = TYContentItemGenerator.decodeFromDict(rewardD.get('item'))
            self.rewards.append((self.totalWeight, self.totalWeight + weight, itemGen))
            self.totalWeight += weight
        
        return self
    
    def getReward(self):
        if self.totalWeight > 0:
            ratio = random.random()
            if ratio <= self.ratio:
                value = random.randint(0, self.totalWeight - 1)
                for ws, we, itemGen in self.rewards:
                    if value >= ws and value < we:
                        return itemGen.generate()
        return None

    def getShareHitReward(self):
        if self.totalWeight > 0:
            value = random.randint(0, self.totalWeight - 1)
            for ws, we, itemGen in self.rewards:
                if value >= ws and value < we:
                    return itemGen.generate()
        return None


class Conf(object):
    def __init__(self):
        # 最小间隔时间，只对触发式分享管用
        self.minInterval = 60
        # 触发式分享的delay时间
        self.triggleDelay = 600
        # 红包雨时长
        self.rainDuration = 20
        # 通知配置，需要发给客户端
        self.notifyList = []
        # 资产和价值对应关系
        self.valueMap = {}
        # 定时的时间列表list<times>
        self.rainDateTimes = []
        # 红包配置
        self.rpConfs = []
        # 活动开始时间
        self.startTime = -1
        # 活动结束事件
        self.stopTime = -1
        # 弹幕消息配置
        self.danmuMsg = None
        # 红包雨信息
        self.rainInfos = []
        # 假用户Ids
        self.fakeSwitch = None
        self.fakeUserIds = []
        # 分享配置
        self.share = {}


    def getDaySendTimes(self, timestamp):
        nowDate = datetime.fromtimestamp(timestamp).date()
        for sendTime in self.rainDateTimes:
            if sendTime['dateRange'][0] <= nowDate <= sendTime['dateRange'][1]:
                return sendTime['times']
        return []

    def getDailySendCountRate(self, timestamp):
        nowDate = datetime.fromtimestamp(timestamp).date()
        for sendTime in self.rainDateTimes:
            if sendTime['dateRange'][0] <= nowDate <= sendTime['dateRange'][1]:
                return sendTime.get('redPacketCountRate', 1)
        return 1

    def getFakeUserId(self, index):
        if self.fakeUserIds:
            try:
                return self.fakeUserIds[int(index)]
            except Exception:
                return None
        return None

    def getShareRewardRate(self, dailyGrabCount):
        return self.share.get('grabCountToday', {}).get(str(dailyGrabCount), 1)


class RedPacket(object):
    '''
    红包
    '''
    def __init__(self, rainTime, value=None, reward=None, grabTime=None):
        # 该红包雨开始时间
        self.rainTime = rainTime
        # 该红包价值
        self.value = value
        # 红包奖励内容
        self.reward = reward
        # 抢红包时间
        self.grabTime = grabTime
    
    def fromDict(self, d):
        self.value = d['value']
        self.reward = TYContentItem.decodeFromDict(d['reward'])
        self.grabTime = d['grabTime']
        return self
    
    def toDict(self):
        return {
            'value':self.value,
            'reward':self.reward.toDict(),
            'grabTime':self.grabTime
        }


class RPRain(object):
    '''
    一场红包雨信息
    '''
    def __init__(self, gameId=None, triggleId=None, rainTime=None, duration=None, isTiming=None):
        # 哪个游戏触发的
        self.gameId = gameId
        # 触发点Id
        self.triggleId = triggleId
        # 开始下雨时间
        self.rainTime = rainTime
        # 持续时间（单位秒）
        self.duration = duration
        # 是否是定时触发的
        self.isTiming = isTiming
        # 假用户第一
        self.fakeNo1UserInfo = None

    def isRainning(self, timestamp):
        return timestamp >= self.rainTime and timestamp <= self.rainTime + self.duration
    
    def isFinished(self, timestamp):
        return timestamp >= self.rainTime + self.duration
    
    def toDict(self):
        return {
            'gameId':self.gameId,
            'triggleId':self.triggleId,
            'rainTime':self.rainTime,
            'duration':self.duration,
            'isTiming':self.isTiming
        }
    
    def fromDict(self, d):
        self.gameId = d['gameId']
        self.triggleId = d['triggleId']
        self.rainTime = d['rainTime']
        self.duration = d['duration']
        self.isTiming = d['isTiming']
        return self


class RPRainNo1(object):
    '''
    一场红包雨的第一名
    '''
    def __init__(self, userId=None, userAttrs=None, userGains=None):
        self.userId = userId
        self.userAttrs = userAttrs if userAttrs is not None else {}
        self.userGains = userGains
    
    def fromDict(self, d):
        self.userId = d['userId']
        self.userAttrs = d['userAttrs']
        self.userGains = UserGains().fromDict(d['userGains'])
        return self

    def toDict(self):
        return {
            'userId':self.userId,
            'userAttrs':self.userAttrs,
            'userGains':self.userGains.toDict()
        }


class RPRainStatus(object):
    '''
    红包雨状态，包含最后结束的那场雨和下一场雨
    '''
    class HistoryItem(object):
        def __init__(self, rain, no1, fakeNo1):
            self.rain = rain
            self.no1 = no1
            self.fakeNo1 = fakeNo1

    def __init__(self):
        # 历史记录
        self.histories = []
        # 当前这场雨(可能还没开始下)
        self.curRain = None
    
    def toDict(self):
        d = {}
        if self.curRain:
            d['cur'] = self.curRain.toDict()
        if self.histories:
            histories = []
            for item in self.histories:
                itemD = {'rain':item.rain.toDict()}
                if item.no1:
                    itemD['no1'] = item.no1.toDict()
                if item.fakeNo1:
                    itemD['fno1'] = item.fakeNo1.toDict()
                histories.append(itemD)
            d['histories'] = histories
        return d
    
    def fromDict(self, d):
        cur = d.get('cur')
        if cur:
            self.curRain = RPRain().fromDict(cur)
        
        histories = d.get('histories', [])
        for item in histories:
            rain = RPRain().fromDict(item['rain'])
            no1D = item.get('no1')
            no1 = RPRainNo1().fromDict(no1D) if no1D else None
            fno1D = item.get('fno1')
            fno1 = RPRainNo1().fromDict(fno1D) if fno1D else None
            self.histories.append(RPRainStatus.HistoryItem(rain, no1, fno1))
        
        return self


class UserStatics(object):
    '''
    用户红包收入及次数统计
    '''
    def __init__(self, totalValue=0, totalTimes=0):
        self.totalValue = totalValue
        self.totalTimes = totalTimes

    def fromDict(self, d):
        self.totalValue = d['totalValue']
        self.totalTimes = d['totalTimes']
        return self

    def toDict(self):
        return {
            'totalValue':self.totalValue,
            'totalTimes':self.totalTimes
        }


class UserGains(object):
    '''
    用户在一场红包雨中的收获
    '''
    def __init__(self, rainTime=None):
        # 哪场雨
        self.rainTime = rainTime
        # 本场雨抢到的红包
        self.packets = []
        # 总价值
        self.value = 0
        
    def add(self, redPacket):
        self.packets.append(redPacket)
        self.value += redPacket.value
        
    def toDict(self):
        return {
            'rainTime':self.rainTime,
            'packets':[p.toDict() for p in self.packets]
        }
    
    def fromDict(self, d):
        self.rainTime = d['rainTime']
        for p in d.get('packets', []):
            rp = RedPacket(self.rainTime).fromDict(p)
            self.add(rp)
        return self
    

class UserStatus(object):
    '''
    用户状态，保存了如下信息
    1. 用户红包雨的总收入统计
    2. 用户最后参与的日期，以及当天每场红包雨抢到的红包
    '''

    class Share(object):
        def __init__(self, timestamp=0, shareCount=0, count=0):
            self.timestamp = timestamp
            self.shareCount = shareCount
            self.count = count

        def fromDict(self, d):
            self.timestamp = d.get('timestamp', 0)
            self.shareCount = d.get('shareCount', 0)
            self.count = d.get('count', 0)
            return self

        def toDict(self):
            return {
                'timestamp': self.timestamp,
                'shareCount': self.shareCount,
                'count': self.count,
            }

    def __init__(self, userId):
        # 哪个用户
        self.userId = userId
        # 总统计
        self.totalStatics = UserStatics()
        # 最后参与日期
        self.date = None
        # 当天的统计
        self.dayStatics = UserStatics()
        # 当天在每场雨中的收获map<rainTime, UserGains>
        self.dayGainsMap = {}
        # 分享后必得奖标志{timestamp, shareCount, count}
        self.dayShareMap = UserStatus.Share()
    
    def adjust(self, curDate):
        if curDate != self.date:
            self.date = curDate
            self.dayStatics = UserStatics()
            self.dayGainsMap = {}
            return True
        return False
    
    def findUserGains(self, rainTime):
        return self.dayGainsMap.get(rainTime)
    
    def addRedPacket(self, redPacket):
        userGains = self._addRedPacket(redPacket)
        self.totalStatics.totalTimes += 1
        self.totalStatics.totalValue += redPacket.value
        return userGains
    
    def _addRedPacket(self, redPacket):
        userGains = self.findUserGains(redPacket.rainTime)
        if not userGains:
            userGains = UserGains(redPacket.rainTime)
            self.dayGainsMap[userGains.rainTime] = userGains
        userGains.add(redPacket)
        self.dayStatics.totalTimes += 1
        self.dayStatics.totalValue += redPacket.value
        return userGains
        
    def fromDict(self, d):
        self.totalStatics.fromDict(d['totalStatics'])
        self.date = datetime.strptime(d['date'], '%Y%m%d').date()
        self.dayStatics.fromDict(d['dayStatics'])
        for userGainsD in d.get('dayGains', []):
            userGains = UserGains().fromDict(userGainsD)
            self.dayGainsMap[userGains.rainTime] = userGains
        self.dayShareMap = UserStatus.Share().fromDict(d.get('dayShare', {}))
        return self
    
    def toDict(self):
        return {
            'totalStatics':self.totalStatics.toDict(),
            'date':self.date.strftime('%Y%m%d'),
            'dayStatics':self.dayStatics.toDict(),
            'dayGains':[ug.toDict() for ug in self.dayGainsMap.values()],
            'dayShare':self.dayShareMap.toDict()
        }


def getRainStatus():
    return _rainStatus


def getConf():
    return _conf


def loadAndAdjustUserStatus(userId, timestamp):
    '''
    加载并调整用户红包雨状态
    '''
    status = loadUserStatus(userId)
    status.adjust(datetime.fromtimestamp(timestamp).date())
    return status


def loadUserStatus(userId):
    '''
    加载用户红包雨状态
    '''
    jstr = daobase.executeUserCmd(userId, 'hget', 'redPacketRain:%s:%s' % (HALL_GAMEID, userId), 'status')
    if jstr:
        try:
            d = strutil.loads(jstr)
            return UserStatus(userId).fromDict(d)
        except:
            ftlog.error('hall_red_packet_rain.loadUserStatus',
                        'userId=', userId,
                        'jstr=', jstr)
    
    return UserStatus(userId)


def saveUserStatus(status):
    '''
    保存用户红包雨状态
    '''
    d = status.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(status.userId, 'hset', 'redPacketRain:%s:%s' % (HALL_GAMEID, status.userId), 'status', jstr)


def findRain(rainTime):
    '''
    根据下雨时间查找红包雨
    '''
    return _scheduleRainMap.get(rainTime)


def scheduleRain(gameId, triggleId, timestamp=None):
    '''
    安排一场红包雨，运行于CT
    @param gameId: 哪个游戏
    @param triggleId: 触发ID
    @param timestamp: 当前时间
    @return: RPRain or None
    '''
    if gdata.serverType() != gdata.SRV_TYPE_CENTER:
        raise TYBizException()
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    rainTime = timestamp + _conf.triggleDelay
    return _scheduleRain(gameId, triggleId, rainTime, _conf.rainDuration, False)


DANMU_MSG = '${userName}抢到一个红包，获得${content}'
DANMU_MIN_COUNT = 100
DANMU_MAX_COUNT = 500
DANMU_GET_COUNT = 30
DANMU_FLOW_CTRL_COUNT_PER_SECOND = 20

RANK_MIN_COUNT = 100
RANK_MAX_COUNT = 200


_innerProcessNo1 = {
    'rainTime':0,
    'no1Value':0
}


_danmuFlowCtrl = {
    'rainTime':0,
    'count':0,
    'ts':0
}


def buildNo1Key(rainTime):
    return 'redPacketRain.no1:%s:%s' % (HALL_GAMEID, rainTime)

def buildFakeNo1UserIndex():
    return 'redPacketRain.fakeNo1Index:%s' % HALL_GAMEID


def buildDanmuListKey(rainTime):
    return 'redPacketRain.danmu.list:%s:%s' % (HALL_GAMEID, rainTime)


def buildDanmuInfoKey(rainTime):
    return 'redPacketRain.danmu.info:%s:%s' % (HALL_GAMEID, rainTime)


def _addPacketDanmu(userId, redPacket):
    # 流控
    timestamp = pktimestamp.getCurrentTimestamp()
    # 不在一秒内，或者不是一场红包雨，清空流控
    if (_danmuFlowCtrl['rainTime'] != redPacket.rainTime
        or _danmuFlowCtrl['ts'] != timestamp):
        if ftlog.is_debug():
            ftlog.debug('hall_red_packet_rain._addPacketDanmu ResetFlowCtrl',
                       'userId=', userId,
                       'rainTime=', redPacket.rainTime,
                       'timestamp=', timestamp,
                       'reward=', (redPacket.reward.assetKindId, redPacket.reward.count),
                       'dmfcTimestamp=', _danmuFlowCtrl['ts'],
                       'dmfcCount=', _danmuFlowCtrl['count'],
                       'dmfcRainTime=', _danmuFlowCtrl['rainTime'])
        
        _danmuFlowCtrl['rainTime'] = redPacket.rainTime
        _danmuFlowCtrl['ts'] = timestamp
        _danmuFlowCtrl['count'] = 0
    
    _danmuFlowCtrl['count'] += 1
    
    if _danmuFlowCtrl['count'] > DANMU_FLOW_CTRL_COUNT_PER_SECOND:
        ftlog.info('hall_red_packet_rain._addPacketDanmu FilterFlowCtrl',
                   'userId=', userId,
                   'rainTime=', redPacket.rainTime,
                   'timestamp=', timestamp,
                   'reward=', (redPacket.reward.assetKindId, redPacket.reward.count),
                   'dmfcTimestamp=', _danmuFlowCtrl['ts'],
                   'dmfcCount=', _danmuFlowCtrl['count'],
                   'dmfcRainTime=', _danmuFlowCtrl['rainTime'])
        return
    
    name = userdata.getAttr(userId, 'name')
    name = str(name) if name is not None else ''
    content = hallitem.buildContent(redPacket.reward.assetKindId, redPacket.reward.count, True)
    danmuMsg = strutil.replaceParams(_conf.danmuMsg, {'userName':name, 'content':content})
    jstr = strutil.dumps({'uid':userId, 'msg':danmuMsg})
    daobase.executeRePlayCmd('rpush', buildDanmuListKey(redPacket.rainTime), jstr)
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_rain._addPacketDanmu',
                    'userId=', userId,
                    'rainTime=', redPacket.rainTime,
                    'reward=', (redPacket.reward.assetKindId, redPacket.reward.count))


def _trimDanmu(rainTime):
    trimCount = daobase.executeRePlayLua(_trim_danmu_alias, 4,
                                         buildDanmuListKey(rainTime),
                                         buildDanmuInfoKey(rainTime),
                                         DANMU_MIN_COUNT,
                                         DANMU_MAX_COUNT)
    
    if ftlog.is_debug():
        ftlog.info('hall_red_packet_rain._trimDanmu',
                   'rainTime=', rainTime,
                   'trimCount=', trimCount)


def getRainInfo(userId, clientId, rainTime):
    idx = random.randint(0, len(_conf.rainInfos) - 1)
    return _conf.rainInfos[idx]


def getShareInfo(userId):
    timestamp = pktimestamp.getCurrentTimestamp()
    status = loadAndAdjustUserStatus(userId, timestamp)
    doubleReward = 1 if status.dayShareMap.count > 0 else 0
    pointId = _conf.share.get('pointId', 0)
    return pointId, doubleReward
    

def _sendRedPacket(userId, redPacket):
    try:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, _, _ = userAssets.addAsset(HALL_GAMEID,
                                              redPacket.reward.assetKindId,
                                              redPacket.reward.count,   
                                              pktimestamp.getCurrentTimestamp(),
                                              'HALL_RP_RAIN_GRAB',
                                              redPacket.rainTime)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, assetKind.keyForChangeNotify)
        
        ftlog.info('hall_red_packet_rain._sendRedPacket',
                   'userId=', userId,
                   'rainTime=', redPacket.rainTime,
                   'reward=', (redPacket.reward.assetKindId, redPacket.reward.count))
    except:
        ftlog.error('hall_red_packet_rain._sendRedPacket',
                    'userId=', userId,
                    'rainTime=', redPacket.rainTime,
                    'reward=', (redPacket.reward.assetKindId, redPacket.reward.count))


def grabRedPacket(userId, clientId, rainTime, timestamp=None):
    '''
    用户抢红包，运行在UT进程中
    '''
    from hall.game import TGHall
    global _rainStatus
    
    curRain = _rainStatus.curRain
    valueMap = _conf.valueMap
    
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    
    if (not curRain
        or rainTime != curRain.rainTime
        or not curRain.isRainning(timestamp)):
        raise RedPacketRainStopped()
    
    status = loadAndAdjustUserStatus(userId, curRain.rainTime)
    
    redPacket = _grabRedPacket(status, curRain, valueMap, clientId, timestamp)
    
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_rain.grabRedPacket',
                    'userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', timestamp,
                    'redPacket=', (redPacket.reward.assetKindId, redPacket.reward.count, redPacket.value) if redPacket else None)
    
    if redPacket:
        ftlog.info('hall_red_packet_rain.grabRedPacket',
                   'userId=', userId,
                   'clientId=', clientId,
                   'timestamp=', timestamp,
                   'redPacket=', (redPacket.reward.assetKindId, redPacket.reward.count, redPacket.value) if redPacket else None)
        
        _sendRedPacket(userId, redPacket)
        
        # 记录用户抢到红包，并以value值作为score设置到排行榜
        userGains = status.addRedPacket(redPacket)
        saveUserStatus(status)
        
        # 更新no1
        _updateNo1(userId, userGains)
        
        # 添加弹幕
        _addPacketDanmu(userId, redPacket)

        TGHall.getEventBus().publishEvent(UserGrabRedPacketEvent(userId, HALL_GAMEID, redPacket))
        
        if redPacket.reward.assetKindId == hallitem.ASSET_COUPON_KIND_ID:
            TGHall.getEventBus().publishEvent(UserReceivedCouponEvent(HALL_GAMEID,
                                                                      userId,
                                                                      redPacket.reward.count,
                                                                      hall_red_packet_const.RP_SOURCE_RP_RAIN))
        
    return redPacket
    

def getDanmu(userId, rainTime, danmuPos):
    start = max(0, danmuPos)
    realStart, _delCount, danmuList = daobase.executeRePlayLua(_get_danmu_alias, 4,
                                                               buildDanmuListKey(rainTime),
                                                               buildDanmuInfoKey(rainTime),
                                                               start, DANMU_GET_COUNT)
    
    ret = []
    for danmu in danmuList:
        try:
            d = strutil.loads(danmu)
            ret.append((d['uid'], d['msg']))
        except:
            ftlog.error('hall_red_packet_rain.getDanmu',
                        'userId=', userId,
                        'rainTime=', rainTime,
                        'danmuPos=', danmuPos,
                        'danmu=', danmu)
    nextPos = realStart + len(danmuList) if danmuList else realStart
    
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_rain.getDanmu',
                    'userId=', userId,
                    'rainTime=', rainTime,
                    'danmuPos=', danmuPos,
                    'realStart=', realStart,
                    'danmuCount=', len(danmuList),
                    'nextPos=', nextPos)
        
    return nextPos, ret


def getFakeNo1UserId():
    key = buildFakeNo1UserIndex()
    index = daobase.executeRePlayCmd('get', key)
    if isinstance(index, int):
        index = int(index) + 1
    else:
        index = 0
    daobase.executeRePlayCmd('set', key, index)
    userId = _conf.getFakeUserId(index)
    return userId


def getRainResult(userId, rainTime):
    '''
    获取红包雨结果
    '''
    if not _rainStatus.histories:
        return None, None, None
    
    historyItem = _rainStatus.histories[-1]
    
    if historyItem.rain.rainTime != rainTime:
        return None, None, None
    
    userStatus = loadUserStatus(userId)
    
    return historyItem.rain, historyItem.fakeNo1 if historyItem.fakeNo1 else historyItem.no1, userStatus.findUserGains(rainTime) if userStatus else None


def _grabRedPacket(status, curRain, valueMap, clientId, timestamp):
    '''
    用户抢红包
    '''
    # 根据规则决定是否能中红包
    rpConfs = _conf.rpConfs
    for _, rpConf in enumerate(rpConfs):
        if (rpConf.condition and not rpConf.condition.check(HALL_GAMEID, status.userId, clientId, timestamp, redPacketRainStatus=status)):
            continue

        reward = rpConf.getReward()

        # 分享必中奖励
        if status.dayShareMap.count > 0:
            reward = rpConf.getShareHitReward()

        if reward:
            if reward.assetKindId == 'user:coupon':
                # 周期系数
                countRate = _conf.getDailySendCountRate(timestamp)
                # 分享的加倍系数
                shareRate = _conf.getShareRewardRate(status.dayStatics.totalTimes)
                status.dayShareMap.count -= 1

                if ftlog.is_debug():
                    ftlog.debug('_grabRedPacket status=', status.toDict(), 'dayStatics.totalTimes',
                                status.dayStatics.totalTimes, 'count=', status.dayShareMap.count, 'shareRate=',
                                shareRate, 'reward=', reward)

                reward = TYContentItem.decodeFromDict(
                    {
                        'itemId': 'user:coupon',
                        'count': int(reward.count * countRate * shareRate) or 1
                    }
                )
            return RedPacket(curRain.rainTime, valueMap[reward.assetKindId] * reward.count, reward, timestamp)
        return None
    return None


def _addRain(rain):
    '''
    添加一场红包雨
    '''
    global _scheduleRains
    _scheduleRains.append(rain)
    _scheduleRains.sort(key=lambda rain: rain.rainTime)
    _scheduleRainMap[rain.rainTime] = rain


def _loadRainStatus():
    '''
    加载红包雨状态
    '''
    jstr = daobase.executeRePlayCmd('hget', 'redPacketRain:%s' % (HALL_GAMEID), 'status')
    if jstr:
        try:
            d = strutil.loads(jstr)
            return RPRainStatus().fromDict(d)
        except:
            ftlog.error('hall_red_packet_rain._loadRainStatus',
                        'jstr=', jstr)
    
    return RPRainStatus()


def _saveRainStatus(status):
    '''
    保存红包雨状态
    '''
    jstr = strutil.dumps(status.toDict())
    daobase.executeRePlayCmd('hset', 'redPacketRain:%s' % (HALL_GAMEID), 'status', jstr)
    
    ftlog.info('hall_red_packet_rain._saveRainStatus',
               'jstr=', jstr)


def _scheduleRain(gameId, triggleId, rainTime, duration, isTiming):
    '''
    安排一场红包雨
    '''
    if findRain(rainTime):
        if ftlog.is_debug():
            ftlog.debug('Already exists for rainTime: %s' % (rainTime))
        return None
    
    # 需要检查最小间隔时间内是否有红包雨
    for rain in _scheduleRains:
        if (rainTime >= rain.rainTime - _conf.minInterval
            and rainTime <= rain.rainTime + _conf.minInterval):
            if ftlog.is_debug():
                ftlog.debug('MinInterval exists for rainTime: %s' % (rain.rainTime))
            return None
    
    rain = RPRain(gameId, triggleId, rainTime, duration, isTiming)
    _addRain(rain)
    
    if rain == _scheduleRains[0]:
        # 下一场红包雨有变化，重新记录下一场红包雨
        _rainStatus.curRain = rain
        _saveRainStatus(_rainStatus)
    
    ftlog.info('ScheduleRain', (gameId, triggleId, rainTime, duration, isTiming))
    
    if ftlog.is_debug():
        ftlog.debug('ScheduleList', [(r.gameId, r.triggleId, r.rainTime, r.isTiming) for r in _scheduleRains])

    return rain


def _updateNo1(userId, userGains):
    if (_innerProcessNo1['rainTime'] == userGains.rainTime
        and userGains.value < _innerProcessNo1['value']):
        return
    
    no1UserId, value = daobase.executeRePlayLua(_update_no1_alias, 3,
                                                buildNo1Key(userGains.rainTime),
                                                userId,
                                                userGains.value)
    
    if ftlog.is_debug():
        ftlog.debug('Update no1', no1UserId, value)

    if userGains.rainTime == _innerProcessNo1['rainTime']:
        _innerProcessNo1['value'] = userGains.value
        _innerProcessNo1['rainTime'] = userGains.rainTime


def _loadRainNo1(rainTime):
    userId, _value = daobase.executeRePlayCmd('hmget', buildNo1Key(rainTime), 'userId', 'value')
    if userId:
        userStatus = loadAndAdjustUserStatus(userId, rainTime)
        if userStatus:
            userGains = userStatus.findUserGains(rainTime)
            if userGains:
                name, purl = userdata.getAttrs(userId, ['name', 'purl'])
                name = str(name) if name else ''
                purl = str(purl) if purl else ''
                vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
                return RPRainNo1(userId, {'name':name, 'purl':purl, 'vipLevel':vipLevel}, userGains)
    return None


def _removeHistory(item):
    # 删除排行榜
    keys = [buildNo1Key(item.rain.rainTime),
            buildDanmuListKey(item.rain.rainTime),
            buildDanmuInfoKey(item.rain.rainTime)]
    daobase.executeRePlayCmd('del', *keys)

    ftlog.info('Remove rain', (item.rain.gameId, item.rain.triggleId, item.rain.rainTime, item.rain.isTiming))


def _genFakeNo1(rainTime):
    if _conf.fakeSwitch == 1:
        fakeUserId = getFakeNo1UserId()
        if fakeUserId:
            userdata.checkUserData(fakeUserId)
            nameFake, purlFake = userdata.getAttrs(fakeUserId, ['name', 'purl'])
            nameFake = str(nameFake) if nameFake else ''
            purlFake = str(purlFake) if purlFake else ''
            vipLevelFake = hallvip.userVipSystem.getUserVip(fakeUserId).vipLevel.level
            reward = TYContentItem.decodeFromDict({'itemId': 'user:coupon', 'count': 488800})
            redPacket = RedPacket(rainTime, _conf.valueMap['user:coupon'] * 488800, reward, pktimestamp.getCurrentTimestamp())
            userGains = UserGains(rainTime)
            userGains.add(redPacket)
            return RPRainNo1(fakeUserId, {'name': nameFake, 'purl': purlFake, 'vipLevel': vipLevelFake}, userGains)
    return None


def _processScheduleRains(timestamp):
    '''
    处理计划表中的红包雨
    '''
    firstRemoved = None
    
    while _scheduleRains and _scheduleRains[0].isFinished(timestamp):
        removed = _scheduleRains.pop(0)
        _scheduleRainMap.pop(removed.rainTime, None)
        if not firstRemoved:
            firstRemoved = removed
    
    if firstRemoved:
        fakeNo1 = _genFakeNo1(firstRemoved.rainTime)
        historyItem = RPRainStatus.HistoryItem(firstRemoved, _loadRainNo1(firstRemoved.rainTime), fakeNo1)
        _rainStatus.histories.append(historyItem)
        _rainStatus.curRain = _scheduleRains[0] if _scheduleRains else None
        ftlog.info('RainFinished',
                   'rain=', (removed.gameId, removed.triggleId, removed.rainTime, removed.isTiming),
                   'no1=', (historyItem.no1.userId, historyItem.no1.userGains.value) if historyItem.no1 else None,
                   'fakeNo1=', (historyItem.fakeNo1.userId, historyItem.fakeNo1.userGains.value) if historyItem.fakeNo1 else None,)
        while len(_rainStatus.histories) > 2:
            item = _rainStatus.histories.pop(0)
            _removeHistory(item)
        _saveRainStatus(_rainStatus)
        

def _processInCT():
    '''
    在CT中处理，计划、删除红包雨
    '''
    global _lastScheduleTimestamp
    
    nowTimestamp = pktimestamp.getCurrentTimestamp()
    nowDT = datetime.fromtimestamp(nowTimestamp)
    
    # 今天没有处理过(重新加载配置后重置_lastProcessTime为None)，则处理
    if (not isStop(nowTimestamp)
        and (not _lastScheduleTimestamp or not pktimestamp.is_same_day(nowTimestamp, _lastScheduleTimestamp))):
        # 排期今天需要下的红包雨
        timeList = _conf.getDaySendTimes(nowTimestamp)  # 获取当天红包雨的时间
        for t in timeList:
            rainTime = pktimestamp.datetime2Timestamp(datetime.combine(nowDT.date(), t))
            if nowTimestamp <= rainTime:
                _scheduleRain(HALL_GAMEID, TRIGGLE_ID_TIME, rainTime, _conf.rainDuration, True)
        _lastScheduleTimestamp = nowTimestamp

    _processScheduleRains(pktimestamp.getCurrentTimestamp())
    
    for rain in _scheduleRains:
        if rain.isRainning(nowTimestamp):
            _trimDanmu(rain.rainTime)


def isStop(nowTimestamp):
    '''
    红包雨活动是否结束
    '''
    if _conf.startTime != -1 and nowTimestamp < _conf.startTime:
        return True
    
    if _conf.stopTime != -1 and nowTimestamp >= _conf.stopTime:
        return True
    
    return False


def _processInUT():
    '''
    在UT中处理红包雨状态信息
    '''
    # 获取红包雨状态信息
    global _rainStatus
    _rainStatus = _loadRainStatus()
    
    ftlog.info('updateRainStatus',
               'lastFinishRain=', (_rainStatus.histories[0].rain.gameId,
                                   _rainStatus.histories[0].rain.triggleId,
                                   _rainStatus.histories[0].rain.rainTime,
                                   _rainStatus.histories[0].rain.duration,
                                   _rainStatus.histories[0].rain.isTiming) if _rainStatus.histories else None,
               'curRain=', (_rainStatus.curRain.gameId,
                            _rainStatus.curRain.triggleId,
                            _rainStatus.curRain.rainTime,
                            _rainStatus.curRain.duration,
                            _rainStatus.curRain.isTiming) if _rainStatus.curRain else None)


def _reloadConf():
    unScheduleRains = []
    scheduleRains = []
    scheduleRainMap = {}
    newConf = Conf()
    
    global _conf
    global _rainStatus
    global _scheduleRains
    global _scheduleRainMap
    global _lastScheduleTimestamp
    
    conf = configure.getGameJson(HALL_GAMEID, 'red_packet_rain', {}, 0)
    if conf:
        newConf.danmuMsg = conf.get('danmuMsg')
        if not newConf.danmuMsg or not isstring(newConf.danmuMsg):
            raise TYBizConfException(conf, 'RedPacketRain.danmuMsg must be not empty str')
        
        startTimeStr = conf.get('startTime')
        if startTimeStr:
            try:
                newConf.startTime = datetime.strptime(startTimeStr, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(conf, 'RedPacketRain.startTime must be datetime str')
            
        stopTimeStr = conf.get('stopTime')
        if stopTimeStr:
            try:
                newConf.stopTime = datetime.strptime(stopTimeStr, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(conf, 'RedPacketRain.stopTime must be datetime str')

        newConf.minInterval = conf.get('minInterval')
        if not isinstance(newConf.minInterval, int) or newConf.minInterval <= 0:
            raise TYBizConfException(conf, 'RedPacketRain.minInterval must be int > 0')
        
        newConf.rainDuration = conf.get('rainDuration', 20)
        if not isinstance(newConf.rainDuration, int) or newConf.rainDuration <= 0 or newConf.rainDuration > 50:
            raise TYBizConfException(conf, 'RedPacketRain.rainDuration must > 0 and <= 50')
        
        newConf.triggleDelay = conf.get('triggleDelay')
        if not isinstance(newConf.triggleDelay, int) or newConf.triggleDelay <= 0:
            raise TYBizConfException(conf, 'RedPacketRain.triggleDelay must be int > 0')
    
        newConf.notifyList = conf.get('notifyList')
        if not newConf.notifyList or not isinstance(newConf.notifyList, list):
            raise TYBizConfException(conf, 'RedPacketRain.notifyList must be list')
        
        for notify in newConf.notifyList:
            presetTime = notify.get('time')
            if not isinstance(presetTime, int) or presetTime < 0:
                raise TYBizConfException(conf, 'RedPacketRain.notifyList.item.time must be int')
            
            info = notify.get('info')
            if not isstring(info):
                raise TYBizConfException(conf, 'RedPacketRain.notifyList.item.info must be string')
        
        newConf.rainInfos = conf.get('rainInfos')
        if not newConf.rainInfos or not isinstance(newConf.rainInfos, list):
            raise TYBizConfException(conf, 'RedPacketRain.rainInfos must be list')
        
        for info in newConf.rainInfos:
            desc = info.get('desc', '')
            if not isstring(desc):
                raise TYBizConfException(conf, 'RedPacketRain.rainInfos.item.desc must be string')
            url = info.get('url', '')
            if not isstring(url):
                raise TYBizConfException(conf, 'RedPacketRain.rainInfos.item.url must be string')
        
        for itemId, value in conf.get('values').iteritems():
            if not isstring(itemId):
                raise TYBizConfException(conf, 'RedPacketRain.values.item.key must be string')
            if not isinstance(value, int):
                raise TYBizConfException(conf, 'RedPacketRain.values.item.value must be int')
            newConf.valueMap[itemId] = value

        fakeUserIds = conf.get('fakeUserIds', [])
        if fakeUserIds:
            newConf.fakeUserIds = fakeUserIds
        fakeSwitch = conf.get('fakeSwitch', 0)
        newConf.fakeSwitch = fakeSwitch

        rainDateTimes = conf.get('rainDateTimes', [])
        if not isinstance(rainDateTimes, list):
            raise TYBizConfException(conf, 'RedPacketRain.rainDateTimes must be list')

        rainDateTimesNew = []
        for rainTime in rainDateTimes:
            rainTimeNew = {}
            try:
                rainTimeNew['redPacketCountRate'] = rainTime['redPacketCountRate']
                assert len(rainTime['dateRange']) == 2, 'RedPacketRain.rainDateTimes["dateRange"] len = 2'
                rainTimeNew['dateRange'] = [datetime.strptime(dateStr, "%Y%m%d").date() for dateStr in rainTime['dateRange']]
                rainTimeNew['times'] = [datetime.strptime(timeStr, '%H:%M:%S').time() for timeStr in rainTime['times']]
                rainDateTimesNew.append(rainTimeNew)
            except:
                raise TYBizConfException(newConf.rainDateTimes, 'RedPacketRain.rainDateTimes.item must be time str 时:分:秒 or date 年月日')
        newConf.rainDateTimes = rainDateTimesNew

        shareConf = conf.get('share', {})
        if shareConf and not isinstance(shareConf, dict):
            raise TYBizConfException(conf, 'RedPacketRain.share must be dict')
        newConf.share = shareConf

        rpConfs = conf.get('redPackets')
        if not rpConfs or not isinstance(rpConfs, list):
            raise TYBizConfException(conf, 'RedPacketRain.redPackets must be not empty list')
        
        for rpConf in rpConfs:
            newConf.rpConfs.append(RPConf().decodeFromDict(rpConf))
        
        # 检查是否有红包奖励没有配置value
        for pc in newConf.rpConfs:
            if pc.rewards:
                for _, _, itemGen in pc.rewards:
                    value = newConf.valueMap.get(itemGen.assetKindId)
                    if value is None:
                        raise TYBizConfException(conf, 'Not set value for assetKindId %s' % (itemGen.assetKindId))
    
        timestamp = pktimestamp.getCurrentTimestamp()
        
        # 只有CT进程处理定时的红包雨
        if gdata.serverType() == gdata.SRV_TYPE_CENTER:
            for scheduleRain in _scheduleRains:
                # 正在下雨的不删除
                if not scheduleRain.isTiming or scheduleRain.isRainning(timestamp):
                    scheduleRains.append(scheduleRain)
                    scheduleRainMap[scheduleRain.rainTime] = scheduleRain
                else:
                    unScheduleRains.append(scheduleRain)
    
    _lastScheduleTimestamp = None
    _conf = newConf
    _scheduleRains = scheduleRains
    _scheduleRainMap = scheduleRainMap

    if gdata.serverType() == gdata.SRV_TYPE_CENTER:
        _processInCT()
        # 保存当前红包雨
        _rainStatus.curRain = _scheduleRains[0] if _scheduleRains else None
        _saveRainStatus(_rainStatus)

    ftlog.info('RedPacketRainScheduler.reloadConf',
               'valueMap=', _conf.valueMap,
               'minInterval=', _conf.minInterval,
               'rainDuration=', _conf.rainDuration,
               'scheduleRains=', [(si.gameId, si.triggleId, si.rainTime, si.isTiming) for si in _scheduleRains],
               'unScheduleRains=', [(si.gameId, si.triggleId, si.rainTime, si.isTiming) for si in unScheduleRains])


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:red_packet_rain:0'):
        _reloadConf()


def _initialize():
    global _inited
    global _processTimer
    global _rainStatus
    
    if not _inited:
        _inited = True
        
        daobase.loadLuaScripts(_update_no1_alias, _update_no1_script)
        daobase.loadLuaScripts(_get_danmu_alias, _get_danmu_script)
        daobase.loadLuaScripts(_trim_danmu_alias, _trim_danmu_script)
        
        _rainStatus = _loadRainStatus()
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        if gdata.serverType() == gdata.SRV_TYPE_CENTER:
            _processTimer = FTLoopTimer(1, -1, _processInCT)
            _processTimer.start()
        elif gdata.serverType() == gdata.SRV_TYPE_UTIL:
            _processTimer = FTLoopTimer(1, -1, _processInUT)
            _processTimer.start()

            #pkeventbus.globalEventBus.subscribe(HallShare2Event, _onUserShare)
            from hall.game import TGHall
            TGHall.getEventBus().subscribe(HallShare2Event, _onUserShare2)
            TGHall.getEventBus().subscribe(HallShareEvent, _onUserShare)


def _onUserShare(event):
    changeUserShareInfo(event.userId, event.shareid)

def _onUserShare2(event):
    changeUserShareInfo(event.userId, event.sharePointId)

def changeUserShareInfo(userId, sharePointId):
    shareIds = _conf.share.get('shareIds', [])
    if sharePointId not in shareIds:
        return

    currTimeStamp = pktimestamp.getCurrentTimestamp()
    userStatus = loadAndAdjustUserStatus(userId, currTimeStamp)

    if userStatus.dayShareMap.timestamp - currTimeStamp < 86400:
        # 分享有效期内
        if not userStatus.dayShareMap.timestamp:
            userStatus.dayShareMap.timestamp = currTimeStamp
        if userStatus.dayShareMap.shareCount < _conf.share.get('dailyCount', 0):
            userStatus.dayShareMap.count += 1
        userStatus.dayShareMap.shareCount += 1
        ftlog.info('hall_red_packet_rain.changeUserShareInfo userId=', userId,
                   'sharePointId=', sharePointId,
                   'userStatus=', userStatus.toDict())
    else:
        # 过期
        userStatus.dayShareMap.timestamp = currTimeStamp
        userStatus.dayShareMap.shareCount = 1
        userStatus.dayShareMap.count = 1

    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_rain.changeUserShareInfo userId=', userId,
                    'sharePointId=', sharePointId, 'userStatus=', userStatus.toDict())
    saveUserStatus(userStatus)


class UserConditionRedPacketRainGrabCountToday(UserCondition):
    '''
    玩家当天抢到的红包数量
    '''
    TYPE_ID = 'user.cond.redPacketRain.grabCountToday'
    
    def __init__(self):
        super(UserConditionRedPacketRainGrabCountToday, self).__init__()
        self.start = None
        self.stop = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        userStatus = kwargs.get('redPacketRainStatus')
        if not userStatus:
            userStatus = loadAndAdjustUserStatus(userId, timestamp)
        startCond = self.start < 0 or userStatus.dayStatics.totalTimes >= self.start
        stopCond = self.stop < 0 or userStatus.dayStatics.totalTimes < self.stop
        if ftlog.is_debug():
            ftlog.debug('UserConditionRedPacketRainGrabCountToday.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'times=', userStatus.dayStatics.totalTimes,
                        'conf=', (self.start, self.stop),
                        'ret=', (startCond, stopCond))
        return startCond and stopCond
    
    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int) or self.start < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabCountToday.start must be int >= -1')
        self.stop = d.get('stop', -1)
        if not isinstance(self.stop, int) or self.stop < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabCountToday.stop must be int >= -1')
        if self.stop != -1 and self.stop < self.start:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabCountToday.stop must >= start')
        return self


class UserConditionRedPacketRainGrabValueToday(UserCondition):
    '''
    玩家当天抢到的红包数量
    '''
    TYPE_ID = 'user.cond.redPacketRain.grabValueToday'
    
    def __init__(self):
        super(UserConditionRedPacketRainGrabValueToday, self).__init__()
        self.start = None
        self.stop = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        userStatus = kwargs.get('redPacketRainStatus')
        if not userStatus:
            userStatus = loadAndAdjustUserStatus(userId, timestamp)
        startCond = self.start < 0 or userStatus.dayStatics.totalValue >= self.start
        stopCond = self.stop < 0 or userStatus.dayStatics.totalValue < self.stop
        if ftlog.is_debug():
            ftlog.debug('UserConditionRedPacketRainGrabValueToday.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'value=', userStatus.dayStatics.totalValue,
                        'conf=', (self.start, self.stop),
                        'ret=', (startCond, stopCond))
        return startCond and stopCond
    
    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int) or self.start < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabValueToday.start must be int >= -1')
        self.stop = d.get('stop', -1)
        if not isinstance(self.stop, int) or self.stop < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabValueToday.stop must be int >= -1')
        if self.stop != -1 and self.stop < self.start:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabValueToday.stop must >= start')
        return self


class UserConditionRedPacketRainGrabCountTotal(UserCondition):
    '''
    玩家累计抢到的红包数量
    '''
    TYPE_ID = 'user.cond.redPacketRain.grabCountTotal'
    
    def __init__(self):
        super(UserConditionRedPacketRainGrabCountTotal, self).__init__()
        self.start = None
        self.stop = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        userStatus = kwargs.get('redPacketRainStatus')
        if not userStatus:
            userStatus = loadAndAdjustUserStatus(userId, timestamp)
        startCond = self.start < 0 or userStatus.totalStatics.totalTimes >= self.start
        stopCond = self.stop < 0 or userStatus.totalStatics.totalTimes < self.stop
        if ftlog.is_debug():
            ftlog.debug('UserConditionRedPacketRainGrabCountTotal.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'times=', userStatus.totalStatics.totalTimes,
                        'conf=', (self.start, self.stop),
                        'ret=', (startCond, stopCond))
        return startCond and stopCond
    
    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int) or self.start < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabCountTotal.start must be int >= -1')
        self.stop = d.get('stop', -1)
        if not isinstance(self.stop, int) or self.stop < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabCountTotal.stop must be int >= -1')
        if self.stop != -1 and self.stop < self.start:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabCountTotal.stop must >= start')
        return self


class UserConditionRedPacketRainGrabValueTotal(UserCondition):
    '''
    玩家累计抢到的红包数量
    '''
    TYPE_ID = 'user.cond.redPacketRain.grabValueTotal'
    
    def __init__(self):
        super(UserConditionRedPacketRainGrabValueTotal, self).__init__()
        self.start = None
        self.stop = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        userStatus = kwargs.get('redPacketRainStatus')
        if not userStatus:
            userStatus = loadAndAdjustUserStatus(userId, timestamp)
        startCond = self.start < 0 or userStatus.totalStatics.totalValue >= self.start
        stopCond = self.stop < 0 or userStatus.totalStatics.totalValue < self.stop
        if ftlog.is_debug():
            ftlog.debug('UserConditionRedPacketRainGrabValueTotal.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'value=', userStatus.totalStatics.totalValue,
                        'conf=', (self.start, self.stop),
                        'ret=', (startCond, stopCond))
        return startCond and stopCond
    
    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int) or self.start < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabValueTotal.start must be int >= -1')
        self.stop = d.get('stop', -1)
        if not isinstance(self.stop, int) or self.stop < -1:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabValueTotal.stop must be int >= -1')
        if self.stop != -1 and self.stop < self.start:
            raise TYBizConfException(d, 'UserConditionRedPacketRainGrabValueTotal.stop must >= start')
        return self


def _registerClasses():
    UserConditionRegister.registerClass(UserConditionRedPacketRainGrabCountToday.TYPE_ID, UserConditionRedPacketRainGrabCountToday)
    UserConditionRegister.registerClass(UserConditionRedPacketRainGrabValueToday.TYPE_ID, UserConditionRedPacketRainGrabValueToday)
    
    UserConditionRegister.registerClass(UserConditionRedPacketRainGrabCountTotal.TYPE_ID, UserConditionRedPacketRainGrabCountTotal)    
    UserConditionRegister.registerClass(UserConditionRedPacketRainGrabValueTotal.TYPE_ID, UserConditionRedPacketRainGrabValueTotal)



