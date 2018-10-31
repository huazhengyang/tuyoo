# -*- coding: utf-8 -*-
"""
Created on 2015年11月18日

@author: zhaojiangang
"""
import json
import random
import time

from datetime import datetime, date, timedelta

import freetime.util.log as ftlog
import poker.entity.dao.gamedata as pkgamedata
import poker.util.timestamp as pktimestamp
from hall.entity import datachangenotify, hallitem
from hall.entity import hallconf
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import UserEvent
from poker.util import sortedlist  # FIXME:
from poker.util import strutil
import hall.client_ver_judge as client_ver_judge
monthCheckinConf = {}


class MonthCheckinException(TYBizException):
    def __init__(self, ec, message):
        super(MonthCheckinException, self).__init__(ec, message)


class AlreadyCheckinException(MonthCheckinException):
    def __init__(self, message='已经签过到'):
        super(AlreadyCheckinException, self).__init__(-1, message)


class SupplementOverException(MonthCheckinException):
    def __init__(self, message='已经达到最大补签次数'):
        super(SupplementOverException, self).__init__(-1, message)


class NotFoundSupplementDateException(MonthCheckinException):
    def __init__(self, message='没有找到可以补签的日期'):
        super(NotFoundSupplementDateException, self).__init__(-1, message)


class InvalidSupplementDateException(MonthCheckinException):
    def __init__(self, message='错误的补签日期'):
        super(InvalidSupplementDateException, self).__init__(-1, message)


class AlreadyGetRewardException(MonthCheckinException):
    def __init__(self, message='奖励已经领取'):
        super(AlreadyGetRewardException, self).__init__(-1, message)


class MonthCheckinStatus(object):
    def __init__(self, userId, curDate):
        self._userId = userId
        # 当前日期
        self._curDate = curDate
        # 签到日期集合，datetime.date
        # list<date>
        self._checkinDateList = []
        # 补签日期列表，datetime.date
        # set<date>
        self._supplementCheckinDateList = []
        # 累计签到天数领奖记录，保存了奖励的ID
        # list<int>
        self._rewardDaysList = []
        # 所有可以补签的日期列表
        self._holeDateList = []

    @property
    def userId(self):
        return self._userId

    @property
    def curDate(self):
        return self._curDate

    @property
    def checkinDateList(self):
        return self._checkinDateList

    @property
    def supplementCheckinDateList(self):
        return self._supplementCheckinDateList

    @property
    def rewardDaysList(self):
        return self._rewardDaysList

    @property
    def supplementCheckinCount(self):
        return len(self._supplementCheckinDateList)

    @property
    def checkinCount(self):
        return len(self.checkinDateList)

    @property
    def allCheckinCount(self):
        return self.checkinCount + self.supplementCheckinCount

    def getLastHoleDate(self):
        '''
        查找离curDate最近的没有签到的日期
        '''
        return self._holeDateList[-1] if self._holeDateList else None

    def isCheckined(self, dateobj):
        '''
        判断是否已经签过到了，包含补签的
        '''
        assert (isinstance(dateobj, date))
        result = -1 != sortedlist.indexOf(self._checkinDateList, dateobj) \
                 or -1 != sortedlist.indexOf(self._supplementCheckinDateList, dateobj)
        return result

    def addCheckinDate(self, checkinDate):
        '''
        增加签到日期
        '''
        assert (isinstance(checkinDate, date))
        if (pktimestamp.isSameMonth(checkinDate, self.curDate)
            and checkinDate <= self.curDate
            and not self.isCheckined(checkinDate)):
            sortedlist.insert(self._checkinDateList, checkinDate)
            return True
        return False

    def addSupplementCheckinDate(self, checkinDate):
        '''
        增加补签日期
        '''
        assert (isinstance(checkinDate, date))
        if (pktimestamp.isSameMonth(checkinDate, self.curDate)
            and checkinDate <= self.curDate
            and not self.isCheckined(checkinDate)):
            sortedlist.insert(self._supplementCheckinDateList, checkinDate)

            return True
        return False

    def addRewardDays(self, days):
        '''
        增加一个累计奖励天数
        '''
        assert (isinstance(days, int))
        if not self.isReward(days):
            sortedlist.insert(self._rewardDaysList, days)
            return True
        return False

    def isReward(self, days):
        '''
        判断是否已经领取了累计days天的奖励
        '''
        assert (isinstance(days, int))
        return -1 != sortedlist.indexOf(self._rewardDaysList, days)

    def adjust(self, curDate):
        assert (isinstance(curDate, date))
        if not pktimestamp.isSameMonth(curDate, self.curDate):
            del self._checkinDateList[:]
            del self._supplementCheckinDateList[:]
            del self._rewardDaysList[:]
            del self._holeDateList[:]
        else:
            self._holeDateList = self._getHoleDateList()[:]
        self._curDate = curDate
        return self

    def _getHoleDateList(self):
        ret = []
        monthStartDate = self.curDate.replace(day=1)
        tdOneDay = timedelta(seconds=86400)
        prevDate = self.curDate.replace()
        while (prevDate >= monthStartDate):
            if not self.isCheckined(prevDate):
                ret.append(prevDate)
            prevDate = prevDate - tdOneDay
        return ret


class MonthCheckinConf(object):
    def __init__(self):
        # 签到奖励, TYContent
        self.checkinRewardContent = None
        # 补签奖励, TYContent
        self.supplementCheckinRewardContent = None
        # 补签需要什么
        self.supplementCheckinConsumeContent = None
        # 累计签到奖励列表list<(days, rewardContent)>
        self.daysRewardList = None
        # 最大补签次数
        self.maxSupplementCheckinCount = None


class MonthCheckinEvent(UserEvent):
    def __init__(self, userId, gameId, status):
        super(MonthCheckinEvent, self).__init__(userId, gameId)
        self.status = status


class MonthCheckinOkEvent(MonthCheckinEvent):
    def __init__(self, userId, gameId, status, checkinDate):
        super(MonthCheckinOkEvent, self).__init__(userId, gameId, status)
        self.checkinDate = checkinDate


class MonthSupCheckinOkEvent(MonthCheckinEvent):
    def __init__(self, userId, gameId, status, checkinDate):
        super(MonthSupCheckinOkEvent, self).__init__(userId, gameId, status)
        self.checkinDate = checkinDate


class DaysRewardGotEvent(MonthCheckinEvent):
    def __init__(self, userId, gameId, status, days):
        super(DaysRewardGotEvent, self).__init__(userId, gameId, status)
        self.days = days


def strToDate(datestr):
    return datetime.strptime(datestr, '%Y%m%d').date()


def dateToStr(dateobj):
    return dateobj.strftime('%Y%m%d')


_monthCheckinConf = None


def _loadStatus(userId):
    try:
        d = gamedata.getGameAttrJson(userId, HALL_GAMEID, 'monthCheckin')
        if d:
            status = MonthCheckinStatus(userId, strToDate(d['ut']))
            for datestr in d.get('cl', []):
                dateobj = strToDate(datestr)
                status.addCheckinDate(dateobj)
            for datestr in d.get('scl', []):
                dateobj = strToDate(datestr)
                status.addSupplementCheckinDate(dateobj)
            for days in d.get('rdl', []):
                status.addRewardDays(int(days))
            status.gotDaysRewardSet = set(d.get('rdl', []))
            return status
    except:
        ftlog.error()
    return None


def _saveStatus(status):
    d = {
        'ut': dateToStr(status.curDate),
        'cl': [dateToStr(d) for d in status.checkinDateList],
        'scl': [dateToStr(d) for d in status.supplementCheckinDateList],
        'rdl': status.rewardDaysList
    }
    jstr = json.dumps(d)
    ftlog.debug('_saveStatus ut =', d['ut']
               , 'cl =', d['cl']
               , 'scl =', d['scl']
               , 'rdl =', d['rdl'])
    gamedata.setGameAttr(status.userId, HALL_GAMEID, 'monthCheckin', jstr)
    gamedata.setGameAttr(status.userId, HALL_GAMEID, 'checkinVer', 1)


def getpreDays():
    nowdate = datetime.now().date()
    preDate = nowdate + timedelta(days=-1)
    preDate1 = nowdate + timedelta(days=-2)
    preDate2 = nowdate + timedelta(days=-3)
    return dateToStr(preDate), dateToStr(preDate1), dateToStr(preDate2)


# 前三天均有领取登录奖励
def getSignDays(userId):
    status = _loadStatus(userId)
    if not status:
        return False
    preDate, preDate1, preDate2 = getpreDays()
    dList = [d.strftime('%Y%m%d') for d in status.checkinDateList]
    ftlog.info('getSignDays preDate =', preDate,
               'preDate1 =', preDate1,
               'preDate2 =', preDate2,
               'dList =', dList,
               'userId =', userId)
    if preDate in dList and preDate1 in dList and preDate2 in dList:
        return True
    else:
        return False


# 是否充值，首充标记
def isFirstRecharged(userId):
    return pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'first_recharge') > 0


# 获取总的游戏时长
def getSumGameTime(userId):
    return pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'totaltime') or 0


# 利用每日游戏时长反作弊
def antiCheatWithTodayTime(userId):
    todoayTime = pkgamedata.getGameAttrJson(userId, HALL_GAMEID, 'todaytime', {})
    dayCount = 0
    totalTime = 0
    for (_, value) in todoayTime.items():
        totalTime += value
        dayCount += 1

    if ftlog.is_debug():
        ftlog.debug('antiCheatWithTodayTime userId =', userId, ' daysWithRecord = ', dayCount,
                    ' gameTimeInDaysWithRecord = ', totalTime)

    cheatDays = hallconf._getHallPublic('cheatDays')
    cheatGameTime = hallconf._getHallPublic('gameTime')
    if ftlog.is_debug():
        ftlog.debug('antiCheatWithTodayTime cheatDays = ', cheatDays, ' cheatGameTime = ', cheatGameTime)

    if dayCount >= cheatDays and totalTime < cheatGameTime:
        return True
    else:
        return False


def isScriptDoGetReward(userId):
    isRecharged = isFirstRecharged(userId)
    return antiCheatWithTodayTime(userId) and not isRecharged


#     nowSignDays = getSignDays(userId)
#     nowGameTime = getSumGameTime(userId)
#     gameTime = hallconf._getHallPublic('gameTime')
#     ftlog.debug('isScriptDoGetReward',
#                 'gameTime =', gameTime,
#                 'nowSignDays =', nowSignDays,
#                 'isRecharged =', isRecharged,
#                 'nowGameTime =', nowGameTime,
#                 'userId =', userId)
#     # 登陆天数>=3 不充值 游戏时长<600
#     if nowSignDays and not isRecharged and nowGameTime < gameTime:
#         ftlog.debug('isScriptDoGetReward return true')
#         return True
#     else:
#         ftlog.debug('isScriptDoGetReward return false')
#         return False

def getConf():
    global _monthCheckinConf
    _monthCheckinConf = hallconf.getMonthCheckinConf()
    return _monthCheckinConf


# 3.9新增对特殊日期的支持
def getNowSpecailDate(nowDate):
    conf = getConf()
    specailDate = conf.get('sepcailDate', {})
    result = {}
    ftlog.debug('getNowSpecailDate.specailDate=', specailDate)
    nowYear = nowDate[0:4]
    nowMonth = int(nowDate[4:6])
    nowDay = nowDate[6:8]
    ftlog.debug('getNowSpecailDate.nowDate=', nowDate,
                'nowYear=', nowYear,
                'nowMonth=', nowMonth,
                'nowDay=', nowDay)
    for (k, v) in specailDate.items():
        month = int(k[4:6])
        year = k[0:4]
        day = k[6:8]
        ftlog.debug('getNowSpecailDate.k=', k,
                    'v=', v,
                    'month=', month,
                    'year=', year,
                    'day=', day)
        if nowYear == year:
            if nowMonth in [month, month - 1, month + 1]:
                result[k] = v
    ftlog.debug('getNowSpecailDate.result=', result)
    return result


# 3.9新增，点击之后气泡的展示
def doMessage(userId, gameId, clientId, state, isFirst):
    '''
        首先根据clientid获取游戏ID，拿到配置
        然后分类处理，是normal还是click,还是特殊日期
        最后根据配置取到消息，下发,
        返回一条消息
    '''
    conf = getAllLabelConf(clientId)
    ftlog.debug('doMessage.userId=', userId,
                'gameId=', gameId,
                'clientId=', clientId,
                'state=', state,
                'isFirst=', isFirst)
    message = ''
    if state == 'normal':
        if isFirst:
            isSpecail, result = checkSpecailDate(conf.get('childSpecail', {}))
            if isSpecail:
                message = result
            else:
                message = getNormalOrClickMessage(conf.get('childNormal', {}))
        else:
            message = getNormalOrClickMessage(conf.get('childNormal', {}))
    elif state == 'click':
        message = getNormalOrClickMessage(conf.get('childClick', {}))
    ftlog.debug('doMessage.userId=', userId,
               'gameId=', gameId,
               'state=', state,
               'message=', message)
    result = {}
    result['message'] = message
    return result


def checkSpecailDate(conf):
    # 检测从当前日期往后3天内是否有特殊日期，有返回 1 message 没有返回 0 none
    nowdate = datetime.now().date().strftime('%Y%m%d')
    ftlog.debug('checkSpecailDate.nowdate=', nowdate,
               'conf=', conf)
    a = 0
    b = ''
    if nowdate in conf:
        # 存在，当天是特殊日期
        a = 1
        b = conf.get(nowdate, "")
    ftlog.debug('checkSpecailDate.nowdate=', nowdate,
               'a=', a,
               'b=', b)
    return a, b


def getNormalOrClickMessage(conf):
    # 根据配置随机出来一条消息，返回
    ftlog.debug('getNormalMessage.conf=', conf)
    items = []
    probability = []
    allWeight = 0
    for k, v in enumerate(conf):
        ftlog.debug('getNormalOrClickMessage.k=', k,
                    'v=', v)
        items.append(v.get('message', ''))
        allWeight += v.get('weight', 0)
    for _k, v in enumerate(conf):
        probability.append(v.get('weight', 0) / (allWeight * 1.0))
    ftlog.debug('getNormalOrClickMessage.items=', items,
               'probability=', probability,
               'allWeight=', allWeight)
    return random_pick(items, probability)


def random_pick(items, probability):
    x = random.randint(0, 1)
    cumulative_probability = 0
    ret = 0
    for item, item_probability in zip(items, probability):
        cumulative_probability += item_probability
        ret = item
        if x < cumulative_probability:
            break
    ftlog.debug('random_pick.ret=', ret)
    return ret


def getAllLabelConf(clientId):
    conf = getConf()
    childGameId = strutil.getGameIdFromHallClientId(clientId)
    checkinClickLabel = conf.get('checkinClickLabel', {})
    checkinNormalLabel = conf.get('checkinNormalLabel', {})
    specailDayLabel = conf.get('specailDayLabel', {})
    ftlog.debug('getAllLabelConf.childGameId=', childGameId,
                'checkinClickLabel=', checkinClickLabel,
                'checkinNormalLabel=', checkinNormalLabel,
                'specailDayLabel=', specailDayLabel)
    childNormal = checkinNormalLabel.get(str(childGameId), {})
    childClick = checkinClickLabel.get(str(childGameId), {})
    childSpecail = specailDayLabel.get(str(childGameId), {})
    ftlog.debug('getAllLabelConf.childNormal=', childNormal,
                'childClick=', childClick,
                'childSpecail=', childSpecail)
    return {'childNormal': childNormal, 'childClick': childClick, 'childSpecail': childSpecail}


def loadStatus(userId, nowDate=None):
    '''
    返回用户的签到状态
    @param userId: 用户ID
    @param timestamp: 当前时间戳
    @return: MonthCheckinStatus
    '''
    status = _loadStatus(userId)
    nowDate = nowDate or datetime.now().date()
    if not status:
        return MonthCheckinStatus(userId, nowDate)
    return status.adjust(nowDate)


def checkin(userId, gameId, clientId, nowDate=None):
    '''
    用户签到
    @param userId: 用户ID
    @param nowDate: 当前日期
    @return: MonthCheckinStatus
    '''
    from hall.game import TGHall

    nowDate = nowDate or datetime.now().date()
    status = loadStatus(userId, nowDate)

    if not status.addCheckinDate(nowDate):
        raise AlreadyCheckinException()
    if isScriptDoGetReward(userId):
        raise AlreadyCheckinException('亲，签到奖励准备中，请玩几把再来领取吧！')
    _saveStatus(status)

    # 领取累计奖励
    _, clientVer, _ = strutil.parseClientId(clientId)

    if clientVer < client_ver_judge.client_ver_397:
        userToGetGift(userId, gameId, 0)
    else:
        checkinReward = hallconf.getMonthCheckinConf().get('checkinReward', {})
        userToGetGiftV401(userId, gameId, 0,checkinReward)

    if clientVer <= 3.76:
        # 自动领奖
        days = status.allCheckinCount
        getDaysReward(userId, days, gameId, nowDate)

    TGHall.getEventBus().publishEvent(MonthCheckinOkEvent(userId, gameId, status, nowDate))

    ftlog.debug('checkin userId =', userId
               , 'gameId =', gameId
               , 'clientId =', clientId)
    return status

def userToGetGift(userId, gameId, state):
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    if state == 0:
        changed = []
        assetKind, _addCount, _final = userAssets.addAsset(9999, 'user:chip', 500, int(time.time()), 'HALL_CHECKIN', 0)
        if assetKind.keyForChangeNotify:
            changed.append(assetKind.keyForChangeNotify)
        datachangenotify.sendDataChangeNotify(gameId, userId, changed)
    changed = []
    assetKind, _addCount, _final = userAssets.addAsset(9999, 'item:4167', 1, int(time.time()), 'HALL_CHECKIN', 0)
    if assetKind.keyForChangeNotify:
        changed.append(assetKind.keyForChangeNotify)

    # 更新退出提醒
    changed.append('exit_remind')
    datachangenotify.sendDataChangeNotify(gameId, userId, changed)

def userToGetGiftV401(userId, gameId, state,Reward):
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    # if state == 0:
    #     changed = []
    #     assetKind, _addCount, _final = userAssets.addAsset(9999, 'user:chip', 500, int(time.time()), 'HALL_CHECKIN', 0)
    #     if assetKind.keyForChangeNotify:
    #         changed.append(assetKind.keyForChangeNotify)
    #     datachangenotify.sendDataChangeNotify(gameId, userId, changed)
    # changed = []
    # assetKind, _addCount, _final = userAssets.addAsset(9999, 'item:4167', 1, int(time.time()), 'HALL_CHECKIN', 0)
    # if assetKind.keyForChangeNotify:
    #     changed.append(assetKind.keyForChangeNotify)

    changed=set()
    if Reward:
        items = TYContentRegister.decodeFromDict(Reward)
        assetList = userAssets.sendContent(gameId
                                           , items
                                           , 1
                                           , True
                                           , pktimestamp.getCurrentTimestamp()
                                           , 'HALL_CHECKIN'
                                           , 0)
        # 通知更新
        changed = TYAssetUtils.getChangeDataNames(assetList)
    # 更新退出提醒
    changed.add('exit_remind')
    datachangenotify.sendDataChangeNotify(gameId, userId, changed)


def supplementCheckin(userId, gameId, clientId, supplementDate=None, nowDate=None):
    '''
    用户补签
    @param userId: 用户ID
    @param supDate: 补签日期，如果为None则表示补签最近一天
    @param nowDate: 当前日期
    @return: MonthCheckinStatus
    '''
    from hall.game import TGHall

    nowDate = nowDate or datetime.now().date()
    status = loadStatus(userId, nowDate)
    if isScriptDoGetReward(userId):
        raise AlreadyCheckinException('亲，签到奖励准备中，请玩几把再来领取吧！')
    # 检查最大补签数
    if status.supplementCheckinCount >= getConf().get("maxSupplementCheckinCount"):
        raise SupplementOverException()

    if supplementDate:
        if not pktimestamp.isSameMonth(supplementDate, status.curDate):
            raise InvalidSupplementDateException()
    else:
        holeDateList = status._getHoleDateList()
        if not holeDateList:
            raise AlreadyCheckinException()
        supplementDate = holeDateList[0]

    if not status.addSupplementCheckinDate(supplementDate):
        raise AlreadyCheckinException()

    # 减少抽奖卡，消耗成功之后，发放奖励。
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()

    _, consumeCount, _final = userAssets.consumeAsset(gameId, 'item:4168', 1,
                                                      timestamp, 'HALL_CHECKIN', 0)
    if consumeCount < 1:
        result = {}
        result["lessCard"] = "您的补签卡不足"
        return 1, result
    datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
    _saveStatus(status)

    # 领取累计奖励
    _, clientVer, _ = strutil.parseClientId(clientId)

    if clientVer < client_ver_judge.client_ver_397:
        userToGetGift(userId, gameId, 0)
    else:
        supplementCheckinReward = hallconf.getMonthCheckinConf().get('supplementCheckinReward', {})
        userToGetGiftV401(userId, gameId, 0,supplementCheckinReward)

    if clientVer <= 3.76:
        # 自动领奖
        days = status.allCheckinCount
        getDaysReward(userId, days, gameId, nowDate)

    TGHall.getEventBus().publishEvent(MonthSupCheckinOkEvent(userId, gameId, status, nowDate))

    ftlog.debug('supplementCheckin userId =', userId
               , 'gameId =', gameId
               , 'clientId =', clientId
               , 'noeDate =', nowDate)
    return 0, status


def getSupplementCheckinCardCount(userId, gameId):
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()
    count = userAssets.balance(gameId, 'item:4168', timestamp)
    ftlog.debug('getSupplementCheckinCardCount.userId=', userId,
                'gameId=', gameId,
                'count', count)
    return count


def getMonthRange():
    import calendar
    day_now = time.localtime()
    _, monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
    return monthRange


def getDaysReward(userId, days, gameId, nowDate=None):
    '''
    领取累计签到奖励
    @param userId: 用户ID
    @param days: 领取累计几天的奖励, 40表示满月的
    @param nowDate: 当前日期
    @return: MonthCheckinStatus
    '''
    nowDate = nowDate or datetime.now().date()
    status = loadStatus(userId, nowDate)
    if not status.addRewardDays(days):
        raise AlreadyGetRewardException()
    # TODO 发放累计奖励
    # 对days进行判断，是否满月，如果满月，设置days=40
    if isScriptDoGetReward(userId):
        raise AlreadyCheckinException('亲，签到奖励准备中，请玩几把再来领取吧！')

    _saveStatus(status)

    dayRewards = hallconf.getMonthCheckinConf().get('daysRewards', {})
    dayToGift(days, dayRewards, userId, gameId, status)

    ftlog.debug('getDaysReward userId =', userId
               , 'days =', days
               , 'gameId =', gameId
               , 'nowDate =', nowDate)
    return status


def dayToGift(days, rewards, userId, gameId, status):
    monthRange = getMonthRange()
    ftlog.debug('dayToGift userId =', userId
               , 'days =', days
               , 'gameId =', gameId
               , 'monthRange =', monthRange)
    for _k, v in enumerate(rewards):
        if v.get('days', 0) > monthRange:
            if monthRange == days:
                reward = v.get('reward', {})
                items = reward.get("items", [])
                sendGiftToUser(items, userId, gameId)
        else:
            if v.get('days', 0) == days:
                reward = v.get('reward', {})
                items = reward.get("items", [])
                sendGiftToUser(items, userId, gameId)


def sendGiftToUser(item, userId, gameId):
    ftlog.debug('dayToGift userId =', userId
               , 'item =', item
               , 'gameId =', gameId
               , 'userId =', userId)
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    for _k, v in enumerate(item):
        changed = []
        assetKind, _addCount, _final = userAssets.addAsset(9999, v.get("itemId"), v.get("count"), int(time.time()),
                                                           'HALL_CHECKIN', 0)
        if assetKind.keyForChangeNotify:
            changed.append(assetKind.keyForChangeNotify)
        datachangenotify.sendDataChangeNotify(gameId, userId, changed)
