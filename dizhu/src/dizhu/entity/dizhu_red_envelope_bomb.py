# -*- coding=utf-8 -*-
"""
Created on 2017年11月23日

@author: wangyonghui
"""
import copy
import json
import random
import datetime
from dizhu.entity import dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity.led_util import LedUtil
from dizhucomm.entity.events import UserTableWinloseEvent, UserTableOutCardBombEvent
from hall.entity import hallitem, hallusercond, hallvip, hall_red_packet_const
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import UserReceivedCouponEvent
from hall.game import TGHall
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import configure, gdata
import freetime.util.log as ftlog
from poker.entity.dao import daobase, sessiondata, userdata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from dizhu.activities.toolbox import UserBag
from freetime.entity.msg import MsgPack
from poker.protocol import router



class RedEnvelopeBombConf(object):
    def __init__(self):
        self.cond = None
        self.ledCount = 0
        self.open = None
        self.issueNum = None
        self.activeDate = None
        self.dailyCountLimit = None
        self.userDailyCountLimit = None
        self.roomBaseTrigger = None
        self.roomReward = None
        self.rewardsTemplate = None
        self.weekRateControl = None
        self.dailyRateControl = None
        self.rollAdditionPoints = None
        self.dailyPlayCountLimit = None
        self.minVersion = None
        self.reportLocalLog = None


    def decodeFromDict(self, d):
        self.cond = d
        if not isinstance(self.cond, dict):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.cond must be dict')

        self.ledCount = d.get('ledCount', 0)
        if not isinstance(self.ledCount, int):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.cond must be int')

        self.open = d.get('open')
        if self.open not in (0, 1):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.open must be in (0, 1)')

        self.issueNum = d.get('issueNum')
        if not isinstance(self.issueNum, (unicode, str)):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.issueNum must be str')

        self.activeDate = d.get('activeDate')
        if not isinstance(self.activeDate, list) or len(self.activeDate) != 2:
            raise TYBizConfException(d, 'RedEnvelopeBombConf.activeDate must be list and length is 2')
        try:
            activeDateList = []
            for dateStr in self.activeDate:
                activeDateList.append(datetime.datetime.strptime(dateStr, "%Y%m%d").date())
            self.activeDate = activeDateList
        except Exception, e:
            raise TYBizConfException(d, 'RedEnvelopeBombConf.activeDate ' + e.message)

        self.dailyCountLimit = d.get('dailyCountLimit')
        if not isinstance(self.dailyCountLimit, int) or self.dailyCountLimit <= 0:
            raise TYBizConfException(d, 'RedEnvelopeBombConf.dailyCountLimit must be > 0')

        self.userDailyCountLimit = d.get('userDailyCountLimit')
        if not isinstance(self.userDailyCountLimit, dict):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.userDailyCountLimit must be dict')

        self.roomBaseTrigger = d.get('roomBaseTrigger')
        if not isinstance(self.roomBaseTrigger, dict):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.roomBaseTrigger must be dict')

        self.roomReward = d.get('roomReward')
        if not isinstance(self.roomReward, dict):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.roomReward must be dict')

        self.rewardsTemplate = d.get('rewardsTemplate')
        if not isinstance(self.rewardsTemplate, list):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.rewardsTemplate must be list')

        weekRateControl = d.get('weekRateControl')
        if not isinstance(weekRateControl, list):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.weekRateControl must be list')
        try:
            weekRateControlNew = []
            for weekrc in weekRateControl:
                weekrcNew = {}
                assert len(weekrc['dateRange']) == 2, 'RedEnvelopeBombConf.weekRateControl["dateRange"] len = 2'
                weekrcNew['dateRange'] = [datetime.datetime.strptime(dateStr, "%Y%m%d").date() for dateStr in weekrc['dateRange']]
                weekrcNew['rateControl'] = weekrc['rateControl']
                weekrcNew['countRateControl'] = weekrc['countRateControl']
                weekRateControlNew.append(weekrcNew)
            self.weekRateControl = weekRateControlNew
        except Exception, e:
            raise TYBizConfException(d, 'RedEnvelopeBombConf.weekRateControl ' + e.message)

        dailyRateControl = d.get('dailyRateControl')
        if not isinstance(dailyRateControl, list):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.dailyRateControl must be list')
        try:
            dailyRateControlNew = []
            for dailyRC in dailyRateControl:
                dailyRCNew = {}
                assert len(dailyRC['timeRange']) == 2, 'RedEnvelopeBombConf.dailyRateControl["timeRange"] len = 2'
                dailyRCNew['timeRange'] = [datetime.datetime.strptime(t, '%H:%M').time() for t in dailyRC['timeRange']]
                dailyRCNew['rateControl'] = dailyRC['rateControl']
                dailyRCNew['countRateControl'] = dailyRC['countRateControl']
                dailyRateControlNew.append(dailyRCNew)
            self.dailyRateControl = dailyRateControlNew
        except Exception, e:
            raise TYBizConfException(d, 'RedEnvelopeBombConf.dailyRateControl ' + e.message)

        self.rollAdditionPoints = d.get('rollAdditionPoints')
        if not isinstance(self.rollAdditionPoints, dict):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.rollAdditionPoints must be dict')

        self.dailyPlayCountLimit = d.get('dailyPlayCountLimit')
        if not isinstance(self.dailyPlayCountLimit, dict):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.dailyPlayCountLimit must be dict')

        self.minVersion = d.get('minVersion', 0)
        if not isinstance(self.minVersion, (int, float)):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.minVersion must be int or float')

        self.reportLocalLog = d.get('reportLocalLog', 0)
        if not isinstance(self.reportLocalLog, int):
            raise TYBizConfException(d, 'RedEnvelopeBombConf.reportLocalLog must be int')
        return self


class RedEnvelopeBomb(object):
    def __init__(self, conf):
        self.conf = conf

    def isActive(self, bigRoomId, timestamp):
        """
        活动是否有效
        """
        now = datetime.datetime.fromtimestamp(timestamp).date()
        if str(bigRoomId) not in self.conf.roomBaseTrigger:
            return False
        return self.conf.open and self.conf.activeDate[0] <= now <= self.conf.activeDate[1]

    def getTableBombReward(self, bigRoomId, timestamp):
        """
        牌桌炸弹奖励, 牌桌一个炸弹就获取炸弹奖励， 如果有在后续roll点来进行分配策略
        """
        rateControl, countRateControl = self._calculateRoomRedEnvelopeRate(bigRoomId, timestamp)
        # 进行概率判断
        ret = self._rateChoice(rateControl)
        if not ret or not countRateControl:
            return None, False

        # 获取奖励
        rewardDict, isDouble = self._getTemplateReward(bigRoomId)
        if not rewardDict:
            return None, False

        rewardDict['count'] = int(round(countRateControl * rewardDict['count'])) or 1

        if ftlog.is_debug():
            ftlog.debug('dizhu_red_envelope_bomb.getTableBombReward',
                        'bigRoomId=', bigRoomId,
                        'reward=', rewardDict,
                        'rateControl=', rateControl,
                        'countRateControl=', countRateControl,
                        'isDouble=', isDouble)
        return rewardDict, isDouble

    def addRewardToUser(self, userId, rewardDict):
        """
        发送奖励, 发送email
        """
        mail = None
        reward = TYContentItem.decodeFromDict(rewardDict)
        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, {'itemId': reward.assetKindId, 'count': reward.count}, 'DDZ_RED_ENVELOPE_BOMB', mail=mail)


    def sendRewardToUsers(self, userIds, rewardList):
        for userId, _ in userIds:
            mo = MsgPack()
            mo.setCmd('dizhu')
            mo.setResult('action', 'red_envelope_bomb')
            mo.setResult('rewardList', rewardList)
            try:
                clientId = sessiondata.getClientId(userId)
            except Exception, e:
                ftlog.error('dizhu_red_envelope_bomb.sendRewardToUsers bad clientId err=', e.message)
                clientId = None
            mo.setResult('tipTop', self._getTipTop(userId, clientId)),
            router.sendToUser(mo, userId)
            if ftlog.is_debug():
                ftlog.debug('dizhu_red_envelope_bomb.sendRewardToUser',
                            'userId=', userId,
                            'mo=', mo.pack())

    def _calculateRoomRedEnvelopeRate(self, bigRoomId, timestamp):
        """计算房间获取红包的数量"""
        try:
            baseRate = self.conf.roomBaseTrigger.get(str(bigRoomId), 0)
            weekRateControl, weekCountRateControl = self._getWeekRate(timestamp)
            dailyRateControl, dailyCountRateControl = self._getDailyRate(timestamp)
            if ftlog.is_debug():
                ftlog.debug('dizhu_red_envelope_bomb._calculateRoomRedEnvelopeCount',
                            'bigRoomId=', bigRoomId,
                            'timestamp=', timestamp,
                            'baseRate=', baseRate,
                            'weekRateControl=', weekRateControl,
                            'weekCountRateControl=', weekCountRateControl,
                            'dailyRateControl=', dailyRateControl,
                            'dailyCountRateControl=', dailyCountRateControl,
                            'finalRate=', baseRate * weekRateControl * dailyRateControl, weekCountRateControl * dailyCountRateControl
                            )

            return baseRate * weekRateControl * dailyRateControl, weekCountRateControl * dailyCountRateControl
        except Exception, e:
            ftlog.warn('dizhu_red_envelope_bomb._calculateRoomRedEnvelopeCount',
                       'bigRoomId=', bigRoomId,
                       'err=', e.message)
            return 1, 1

    def _getWeekRate(self, timestamp):
        """获取周比例控制，返回周控制后得奖概率以及红包数量控制比率"""
        timestampDate = datetime.datetime.fromtimestamp(timestamp).date()
        for weekRate in self.conf.weekRateControl:
            if weekRate['dateRange'][0] <= timestampDate <= weekRate['dateRange'][1]:
                return weekRate.get('rateControl', 1), weekRate.get('countRateControl', 1)
        return 1, 1

    def _getDailyRate(self, timestamp):
        """获取日比例控制，返回日控制后得奖概率以及红包数量控制比率"""
        timestampTime = datetime.datetime.fromtimestamp(timestamp).time()
        for dailyRate in self.conf.dailyRateControl:
            if dailyRate['timeRange'][0] <= timestampTime <= dailyRate['timeRange'][1]:
                return dailyRate.get('rateControl', 1), dailyRate.get('countRateControl', 1)
        return 1, 1

    def _getTipTop(self, userId, clientId):
        """ 获取红包顶端提示，权重选择 """
        if clientId is None:
            return None
        temp = configure.getTcContentByGameId('red.envelope.bomb', None, DIZHU_GAMEID, clientId)
        tipTop = temp.get('tipTop') if temp else None
        if ftlog.is_debug():
            ftlog.debug('dizhu_red_envelope_bomb._getTipTop',
                        'userId=', userId,
                        'clientId=', clientId,
                        'tipTop=', tipTop)
        if tipTop:
            return dizhu_util.getItemByWeight(tipTop)
        return None

    def _rateChoice(self, rate):
        """ 根据概率返回true或false """
        if rate >= 1:
            return True
        if rate <= 0:
            return False
        rateStr = str(rate)
        precision = int(rateStr.split('.')[-1])
        base = 10 ** len(rateStr.split('.')[-1])
        randomInt = random.randint(1, base)

        if ftlog.is_debug():
            ftlog.debug('dizhu_red_envelope_bomb._rateChoice',
                        'rate=', rate,
                        'precision=', precision,
                        'base=', base,
                        'randomInt=', randomInt)


        if randomInt <= precision:
            return True
        return False

    def _getTemplateReward(self, bigRoomId):
        """ 获取模板奖励 """
        templateId = self.conf.roomReward.get(str(bigRoomId))
        if not templateId:
            return None, False

        template = None
        for temp in self.conf.rewardsTemplate:
            if temp.get('id') == templateId:
                template = temp
                break
        if not template:
            return None, False

        try:
            rewards = dizhu_util.getItemByWeight(template['rewards'])
            rewards = copy.deepcopy(rewards)
            rewardsType = rewards['type']
            reward = dizhu_util.getItemByWeight(rewards['items'])
            reward['type'] = rewardsType

            # 红包翻倍判断
            if template.get('doubleBaseRate') and template.get('doubleCount'):
                if reward['type'] == 'redEnvelope' and self._rateChoice(template['doubleBaseRate']):
                    reward['count'] = reward['count'] * template['doubleCount']
                    return reward, True
            return reward, False
        except Exception, e:
            ftlog.warn('dizhu_red_envelope_bomb._getTemplateRewardWithDoubleInfo',
                       'bigRoomId=', bigRoomId,
                       'templateId=', templateId,
                       'template=', template,
                       'err=', e.message)
            return None, False

    def _rollUserPoint(self, userIds, bigRoomId, timestamp):
        """ roll点策略 """
        userRoll = []
        basePoint = self.conf.rollAdditionPoints.get('rollBasePoint', 100)
        for userId, seatId in userIds:
            # 版本过滤
            version = SessionDizhuVersion.getVersionNumber(userId)
            if version < self.conf.minVersion:
                userRoll.append([userId, random.randint(1, basePoint), seatId])
                continue

            # 是否新用户
            clientId = sessiondata.getClientId(userId)
            isNewUser = hallusercond.UserConditionRegisterDay(-1, 1).check(DIZHU_GAMEID, userId, clientId, timestamp)
            # vip 等级
            vipLevel = int(hallvip.userVipSystem.getUserVip(userId).vipLevel.level)
            # 查找用户是否黑脸白脸， 优先级最高
            loseStreak = getRollLoseStreak(self.conf.issueNum, userId)
            point = basePoint
            if loseStreak:
                point += self.conf.rollAdditionPoints.get('badLuck', 10) * loseStreak
                saveRollLoseStreak(self.conf.issueNum, userId, -1)
            if isNewUser:
                point += self.conf.rollAdditionPoints.get('newUser', 10)
            if vipLevel >= 0:
                point += self.conf.rollAdditionPoints.get('vip', {}).get('vip%s' % vipLevel, 0)

            # 判断用户是否到达每日最大领取限额, 如果达到roll点为0
            userCurrentCount, _ = getDailyUserRedEnvelope(self.conf.issueNum, userId, timestamp)
            userCountLimit = self.conf.userDailyCountLimit.get('vip%s' % vipLevel, -1)
            if userCurrentCount >= userCountLimit > 0:
                point = 0

            # 是否超过房间局数上限, 如果达到roll点为0
            pt = getUserPlayCount(self.conf.issueNum, userId, bigRoomId, timestamp)
            ptLimit = self.conf.dailyPlayCountLimit.get(str(bigRoomId))
            if pt and ptLimit and pt > ptLimit:
                point = 0

            roll = [userId, random.randint(1, point) if point >= 1 else 0, seatId]
            userRoll.append(roll)
            if ftlog.is_debug():
                ftlog.debug('dizhu_red_envelope_bomb._rollUserPoint',
                            'userId=', userId,
                            'vipLevel=', vipLevel,
                            'basePoint=', basePoint,
                            'isNewUser=', isNewUser,
                            'loseStreak=', loseStreak,
                            'bigRoomId=', bigRoomId,
                            'point=', point,
                            'userCurrentCount=', userCurrentCount,
                            'userCountLimit=', userCountLimit,
                            'pt=', pt,
                            'ptLmit=', ptLimit,
                            'userRoll=', roll)
        return userRoll


# 配置初始化以及配置更新
_redEnvelopeBomb = None
_inited = False

def _reloadConf():
    global _redEnvelopeBomb
    d = configure.getGameJson(DIZHU_GAMEID, 'red.envelope.bomb', {}, 0)
    conf = RedEnvelopeBombConf().decodeFromDict(d)
    _redEnvelopeBomb.conf = conf
    ftlog.info('dizhu_red_envelope_bomb._reloadConf successed weekRateControl=', _redEnvelopeBomb.conf.weekRateControl,
               'dailyRateControl=', _redEnvelopeBomb.conf.dailyRateControl)

def _onConfChanged(event):
    if _inited and event.isChanged('game:6:red.envelope.bomb:0'):
        ftlog.info('dizhu_red_envelope_bomb._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.info('dizhu_red_envelope_bomb._initialize begin')
    global _inited
    global _redEnvelopeBomb
    if not _inited:
        _inited = True
        d = configure.getGameJson(DIZHU_GAMEID, 'red.envelope.bomb', {}, 0)
        conf = RedEnvelopeBombConf().decodeFromDict(d)
        _redEnvelopeBomb = RedEnvelopeBomb(conf)
        subscribeRedEnvelopeBomb()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.info('dizhu_red_envelope_bomb._initialize end, conf=', _redEnvelopeBomb.conf)

def getInstance():
    global _redEnvelopeBomb
    return _redEnvelopeBomb


# 数据库处理
def buildUserRedEnvelopeKey(issue):
    """ 用户获得红包个数 """
    return "red.envelope.bomb.user:6:%s" % issue

def buildUserPlayCountKey(issue):
    """ 用户玩得次数 """
    return "red.envelope.bomb.play:6:%s" % issue

def buildDailyRedEnvelopeKey(issue):
    """ 每日发出红包个数 """
    return "red.envelope.bomb.daily:6:%s" % issue

def buildUserLoseKey(issue):
    """ 用户连输记录 """
    return "red.envelope.bomb.lose:6:%s" % issue



def increaseUserPlayCount(issue, userId, bigRoomId, timestamp):
    """ 每天每个房间玩得局数 """
    try:
        key = buildUserPlayCountKey(issue)
        ret = daobase.executeRePlayCmd('hget', key, userId)
        if ret:
            ret = json.loads(ret)
            if not pktimestamp.is_same_day(timestamp, ret.get('timestamp')):
                daobase.executeRePlayCmd('hdel', key, userId)
                daobase.executeRePlayCmd('hset', key, userId, json.dumps({str(bigRoomId): 1, 'timestamp': timestamp}))
            else:
                ret.setdefault(str(bigRoomId), 0)
                ret[str(bigRoomId)] = ret[str(bigRoomId)] + 1
                ret['timestamp'] = timestamp
                daobase.executeRePlayCmd('hset', key, userId, json.dumps(ret))
        else:
            daobase.executeRePlayCmd('hset', key, userId, json.dumps({str(bigRoomId): 1, 'timestamp': timestamp}))
    except Exception, e:
        ftlog.error('dizhu_red_envelope_bomb.increaseUserPlayCount',
                    'userId=', userId,
                    'err=', e.message)


def getUserPlayCount(issue, userId, bigRoomId, timestamp):
    """ 每天每个房间玩得局数 """
    try:
        key = buildUserPlayCountKey(issue)
        ret = daobase.executeRePlayCmd('hget', key, userId)
        if ret:
            ret = json.loads(ret)
            if ret.get('timestamp') and pktimestamp.is_same_day(timestamp, ret.get('timestamp')):
                return ret.get(str(bigRoomId), 0)
        return 0
    except Exception, e:
        ftlog.error('dizhu_red_envelope_bomb.increaseUserPlayCount',
                    'userId=', userId,
                    'err=', e.message)


def saveUserRedEnvelope(issue, userId, count, timestamp):
    """ 保存用户红包 """
    try:
        key = buildUserRedEnvelopeKey(issue)
        dailyCount, ret = getDailyUserRedEnvelope(issue, userId, timestamp)
        datestr = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
        if dailyCount:
            ret[datestr] += count
        else:
            if ret:
                ret[datestr] = count
            else:
                ret = {datestr: count}
        daobase.executeRePlayCmd('hset', key, userId, json.dumps(ret))
    except Exception, e:
        ftlog.error('dizhu_red_envelope_bomb.saveUserRedEnvelope',
                    'err=', e.message)

def getDailyUserRedEnvelope(issue, userId, timestamp):
    """ 获取每日用户红包 """
    key = buildUserRedEnvelopeKey(issue)
    datestr = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    ret = daobase.executeRePlayCmd('hget', key, userId)
    if not ret:
        return 0, None
    ret = json.loads(ret)
    for k, v in ret.items():
        if k == datestr:
            return v, ret
    return 0, ret


def getTotalUserRedEnvelope(issue, userId):
    """ 获取总用户红包 """
    key = buildUserRedEnvelopeKey(issue)
    ret = daobase.executeRePlayCmd('hget', key, userId)
    if not ret:
        return 0
    return daobase.executeRePlayCmd('hvals', )


def getDailyRedEnvelope(issue, timestamp):
    """ 获取每日发出红包个数 """
    key = buildDailyRedEnvelopeKey(issue)
    datestr = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    return daobase.executeRePlayCmd('hget', key, datestr) or 0

def saveDailyRedEnvelope(issue, timestamp, count):
    """ 保存每日发出红包个数 """
    key = buildDailyRedEnvelopeKey(issue)
    dailyCount = getDailyRedEnvelope(issue, timestamp)
    datestr = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    daobase.executeRePlayCmd('hset', key, datestr, count + dailyCount)

def getTotalRedEnvelope(issue):
    """ 获取总发出红包个数 """
    key = buildDailyRedEnvelopeKey(issue)
    return sum(daobase.executeRePlayCmd('hvals', key) or [0])


def saveRollLoseStreak(issue, userId, loseStreak):
    """ 连输记录 """
    try:
        key = buildUserLoseKey(issue)
        daobase.executeRePlayCmd('hset', key, userId, loseStreak)
    except Exception, e:
        ftlog.error('dizhu_red_envelope_bomb.saveRollLoseStreak',
                    'err=', e.message)

def getRollLoseStreak(issue, userId):
    """ 连输记录 """
    key = buildUserLoseKey(issue)
    ret = daobase.executeRePlayCmd('hget', key, userId)
    return ret if ret else 0


def _processUserPlayCount(event):
    """
    增加玩次数
    """
    if ftlog.is_debug():
        ftlog.debug('dizhu_red_envelope_bomb._processUserPlayCount',
                    'mixConfRoomId=', event.mixConfRoomId,
                    'userId=', event.userId,
                    'roomId=', event.roomId,
                    'tableId=', event.tableId)
    bigRoomId = int(event.mixConfRoomId) if event.mixConfRoomId else gdata.getBigRoomId(event.roomId)
    if not _redEnvelopeBomb.isActive(bigRoomId, pktimestamp.getCurrentTimestamp()):
        return
    version = SessionDizhuVersion.getVersionNumber(event.userId)
    if version < _redEnvelopeBomb.conf.minVersion:
        return
    increaseUserPlayCount(_redEnvelopeBomb.conf.issueNum, event.userId, bigRoomId, pktimestamp.getCurrentTimestamp())

def _processUserOutCardBomb(event):
    """
    用户扔出炸弹的处理函数
    """
    try:
        currentTimeStamp = pktimestamp.getCurrentTimestamp()
        if not _redEnvelopeBomb.isActive(event.bigRoomId, currentTimeStamp):
            if ftlog.is_debug():
                ftlog.debug('dizhu_red_envelope_bomb._processUserOutCardBomb',
                            'mixConfRoomId=', event.mixConfRoomId,
                            'bigRoomId=', event.bigRoomId,
                            'tableId=', event.tableId,
                            'userId=', event.userId,
                            'userIds=', event.userIds,
                            'isActive=', False)
            return

        # 以天为单位每天发送有上限
        dailyCountLimit = _redEnvelopeBomb.conf.dailyCountLimit
        sendDailyTotalCount = getDailyRedEnvelope(_redEnvelopeBomb.conf.issueNum, currentTimeStamp)
        if sendDailyTotalCount >= dailyCountLimit:
            if ftlog.is_debug():
                ftlog.debug('dizhu_red_envelope_bomb._processUserOutCardBomb',
                            'roomId=', event.roomId,
                            'mixConfRoomId=', event.mixConfRoomId,
                            'tableId=', event.tableId,
                            'userId=', event.userId,
                            'userIds=', event.userIds,
                            'sendDailyTotalCount=', sendDailyTotalCount,
                            'dailyCountLimit=', dailyCountLimit)
            return

        # 牌桌炸弹奖励
        roomRewardDict, isDouble = _redEnvelopeBomb.getTableBombReward(event.bigRoomId, currentTimeStamp)
        if roomRewardDict:
            userPoint = _redEnvelopeBomb._rollUserPoint(event.userIds, event.bigRoomId, currentTimeStamp)
            userPoint.sort(key=lambda x: x[1])  # roll点从小到大排序
            totalPoints = sum([up[1] for up in userPoint])
            if not totalPoints:
                return

            baseTotalCount = int(roomRewardDict['count'])
            # 红包
            if roomRewardDict['type'] == 'redEnvelope' and isDouble:
                # roll 点 按比例分
                totalCount = baseTotalCount * 1.0
                rewardList = []
                for up in userPoint:

                    # 过滤版本
                    version = SessionDizhuVersion.getVersionNumber(up[0])
                    if version < _redEnvelopeBomb.conf.minVersion:
                        sendCount = int(round(totalCount * up[1] / totalPoints)) or 1
                        if sendCount and _redEnvelopeBomb.conf.reportLocalLog == 1:
                            roomRewardDict['count'] = sendCount
                            assetKind = hallitem.itemSystem.findAssetKind(roomRewardDict['itemId'])
                            displayRate = assetKind.displayRate
                            rewardInfo = {
                                'name': assetKind.displayName,
                                'count': roomRewardDict['count'],
                                'pic': assetKind.pic,
                                'itemId': roomRewardDict['itemId'],
                                'desc': roomRewardDict.get('desc', ''),
                                'type': roomRewardDict['type'],
                                'displayRate': displayRate
                            }
                            ftlog.info('dizhu_red_envelope_bomb._processUserOutCardBomb userReward',
                                       'userId=', up[0],
                                       'mixConfRoomId=', event.mixConfRoomId,
                                       'bigRoomId=', event.bigRoomId,
                                       'tableId=', event.tableId,
                                       'version=', version,
                                       'rewardInfo=', rewardInfo)
                        continue

                    sendCount = int(round(totalCount * up[1] / totalPoints)) or 1
                    if sendCount:
                        roomRewardDict['count'] = sendCount
                        assetKind = hallitem.itemSystem.findAssetKind(roomRewardDict['itemId'])
                        displayRate = assetKind.displayRate
                        rewardInfo = {
                            'name': assetKind.displayName,
                            'count': roomRewardDict['count'],
                            'pic': assetKind.pic,
                            'itemId': roomRewardDict['itemId'],
                            'desc': roomRewardDict.get('desc', ''),
                            'type': roomRewardDict['type'],
                            'displayRate': displayRate
                        }

                        if _redEnvelopeBomb.conf.reportLocalLog == 1:
                            ftlog.info('dizhu_red_envelope_bomb._processUserOutCardBomb userReward',
                                       'userId=', up[0],
                                       'mixConfRoomId=', event.mixConfRoomId,
                                       'bigRoomId=', event.bigRoomId,
                                       'tableId=', event.tableId,
                                       'version=', version,
                                       'rewardInfo=', rewardInfo)

                        rewardList.append({'userId': up[0], 'seatId': up[2], 'reward': rewardInfo})
                        _redEnvelopeBomb.addRewardToUser(up[0], roomRewardDict)
                        saveDailyRedEnvelope(_redEnvelopeBomb.conf.issueNum, currentTimeStamp, roomRewardDict['count'])
                        saveUserRedEnvelope(_redEnvelopeBomb.conf.issueNum, up[0], roomRewardDict['count'], currentTimeStamp)
                        # 发送led
                        if roomRewardDict['count'] > _redEnvelopeBomb.conf.ledCount:
                            userName = userdata.getAttrs(up[0], ['name'])[0]
                            roomName = event.roomName
                            disCount = roomRewardDict['count'] * 1.0 / displayRate
                            disCount = int(disCount) if disCount.is_integer() else round(disCount, 2)
                            LedUtil.sendLed(_mk_red_envelope_rich_text(userName, roomName, disCount), 'global')

                        # 发送大厅红包券事件
                        TGHall.getEventBus().publishEvent(UserReceivedCouponEvent(HALL_GAMEID,
                                                                                  up[0],
                                                                                  roomRewardDict['count'],
                                                                                  hall_red_packet_const.RP_SOURCE_RP_BOMB))

                    # 修改用户连续，不连续得奖记录
                    saveRollLoseStreak(_redEnvelopeBomb.conf.issueNum, up[0], 0)
                    if ftlog.is_debug():
                        ftlog.debug('dizhu_red_envelope_bomb._processUserOutCardBomb',
                                    'roomId=', event.roomId,
                                    'bigRoomId=', event.bigRoomId,
                                    'tableId=', event.tableId,
                                    'userPoint=', up,
                                    'roomRewardDict=', roomRewardDict)
                if rewardList:
                    _redEnvelopeBomb.sendRewardToUsers(event.userIds, rewardList)
            else:
                winUser = userPoint[-1]
                version = SessionDizhuVersion.getVersionNumber(winUser[0])
                # 发奖
                assetKind = hallitem.itemSystem.findAssetKind(roomRewardDict['itemId'])
                displayRate = assetKind.displayRate
                rewardInfo = {
                    'name': assetKind.displayName,
                    'count': roomRewardDict['count'],
                    'pic': assetKind.pic,
                    'itemId': roomRewardDict['itemId'],
                    'desc': roomRewardDict.get('desc', ''),
                    'type': roomRewardDict['type'],
                    'displayRate': displayRate
                }
                if _redEnvelopeBomb.conf.reportLocalLog == 1:
                    ftlog.info('dizhu_red_envelope_bomb._processUserOutCardBomb userReward',
                               'userId=', winUser[0],
                               'mixConfRoomId=', event.mixConfRoomId,
                               'bigRoomId=', event.bigRoomId,
                               'tableId=', event.tableId,
                               'version=', version,
                               'rewardInfo=', rewardInfo)

                # 过滤版本
                if version < _redEnvelopeBomb.conf.minVersion:
                    return

                rewardList = [{'userId': winUser[0], 'seatId': winUser[2], 'reward': rewardInfo}]
                _redEnvelopeBomb.addRewardToUser(winUser[0], roomRewardDict)
                _redEnvelopeBomb.sendRewardToUsers(event.userIds, rewardList)
                if roomRewardDict['type'] == 'redEnvelope':
                    saveDailyRedEnvelope(_redEnvelopeBomb.conf.issueNum, currentTimeStamp, roomRewardDict['count'])
                    saveUserRedEnvelope(_redEnvelopeBomb.conf.issueNum, winUser[0], roomRewardDict['count'], currentTimeStamp)
                    # 发送led
                    if roomRewardDict['count'] > _redEnvelopeBomb.conf.ledCount:
                        disCount = roomRewardDict['count'] * 1.0 / displayRate
                        disCount = int(disCount) if disCount.is_integer() else round(disCount, 2)
                        userName = userdata.getAttrs(winUser[0], ['name'])[0]
                        roomName = event.roomName
                        LedUtil.sendLed(_mk_red_envelope_rich_text(userName, roomName, disCount), 'global')

                    # 发送大厅红包券事件
                    TGHall.getEventBus().publishEvent(UserReceivedCouponEvent(HALL_GAMEID,
                                                                              winUser[0],
                                                                              roomRewardDict['count'],
                                                                              hall_red_packet_const.RP_SOURCE_RP_BOMB))

                    if ftlog.is_debug():
                        ftlog.debug('dizhu_red_envelope_bomb._processUserOutCardBomb',
                                    'roomId=', event.roomId,
                                    'bigRoomId=', event.bigRoomId,
                                    'tableId=', event.tableId,
                                    'userPoint=', userPoint[-1],
                                    'roomRewardDict=', roomRewardDict)
                # 修改用户连续，不连续得奖记录
                saveRollLoseStreak(_redEnvelopeBomb.conf.issueNum, winUser[0], 0)
                loseUserIds = [u[0] for u in userPoint[:-1]]
                for uid in loseUserIds:
                    loseCount = getRollLoseStreak(_redEnvelopeBomb.conf.issueNum, uid)
                    saveRollLoseStreak(_redEnvelopeBomb.conf.issueNum, uid, loseCount + 1)
    except Exception, e:
        ftlog.error('dizhu_red_envelope_bomb._processUserOutCardBomb',
                    'roomId=', event.roomId,
                    'bigRoomId=', event.bigRoomId,
                    'tableId=', event.tableId,
                    'err=', e.message)

def _mk_red_envelope_rich_text(userName, roomName, count):
    # 纯文本颜色
    RICH_COLOR_PLAIN = 'FFFFFF'
    # 黄色文本
    RICH_COLOR_YELLOW = 'FCF02D'
    return [
        [RICH_COLOR_YELLOW, '喜从天降！'],
        [RICH_COLOR_PLAIN, '恭喜'],
        [RICH_COLOR_YELLOW, userName],
        [RICH_COLOR_PLAIN, '在'],
        [RICH_COLOR_YELLOW, roomName],
        [RICH_COLOR_PLAIN, '中抢到'],
        [RICH_COLOR_YELLOW, str(count)],
        [RICH_COLOR_YELLOW, '红包券！']
    ]


def subscribeRedEnvelopeBomb():
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, _processUserPlayCount)
    TGDizhu.getEventBus().subscribe(UserTableOutCardBombEvent, _processUserOutCardBomb)

