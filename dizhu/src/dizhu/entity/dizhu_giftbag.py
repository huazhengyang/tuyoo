# -*- coding=utf-8 -*-
"""
Created on 2017年7月13日

@author: wangjifa
"""

from dizhu.entity import dizhupopwnd
from dizhu.entity.dizhu_score_ranking import addUserScoreByGiftBox
from dizhu.servers.util.rpc import new_table_remote
from hall.game import TGHall
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.store.store import TYOrderDeliveryEvent
from poker.entity.configure import configure, gdata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.util import timestamp as pktimestamp, strutil
from sre_compile import isstring


class GiftBagConf(object):
    def __init__(self):
        self.productIds = None
        self.type = None
        self.limitHour = None
        self.multi = None
        self.reward = None
        self.openTimes = None
        self.roomId = None
        self.winBuy = None

    def decodeFromDict(self, d):
        self.productIds = d.get('productIds', [])
        if self.productIds and not isinstance(self.productIds, list):
            raise TYBizConfException(d, 'GiftBagConf.productId must be list')

        self.type = d.get('type')
        if self.type and not isstring(self.type):
            raise TYBizConfException(d, 'GiftBagConf.type must be str')

        self.limitHour = d.get('limitHour')
        if self.limitHour and not isinstance(self.limitHour, (int, float)):
            raise TYBizConfException(d, 'GiftBagConf.limitHour must be int or float')

        self.multi = d.get('multi')
        if self.multi and not isinstance(self.multi, (int, float)):
            raise TYBizConfException(d, 'GiftBagConf.multi must be int or float')

        self.reward = d.get('reward')
        if self.reward and not isinstance(self.reward, dict):
            raise TYBizConfException(d, 'GiftBagConf.reward must be dict')

        self.openTimes = d.get('openTimes', [])
        if self.openTimes and not isinstance(self.openTimes, list):
            raise TYBizConfException(d, 'GiftBagConf.openTimes must be list')

        self.roomId = d.get('roomId', [])
        if self.roomId and not isinstance(self.roomId, list):
            raise TYBizConfException(d, 'GiftBagConf.roomId must be list')

        self.winBuy = d.get('winBuy', [])
        if self.winBuy and not isinstance(self.winBuy, list):
            raise TYBizConfException(d, 'GiftBagConf.winBuy must be list')

        if ftlog.is_debug():
            ftlog.debug('GiftBagConf decodeFromDict ',
                        'productIds=', self.productIds,
                        'type=', self.type,
                        'limitHour=', self.limitHour,
                        'multi=', self.multi,
                        'reward=', self.reward,
                        'openTimes=', self.openTimes,
                        'roomId=', self.roomId)
        return self

    def toDict(self):
        return {
            'productIds': self.productIds,
            'type': self.type,
            'limitHour': self.limitHour,
            'multi': self.multi,
            'reward': self.reward,
            'openTimes': self.openTimes,
            'roomId': self.roomId
        }



class GiftBag(object):
    def __init__(self):
        self.conf = {}

    def decodeFromDict(self, d):
        for buffConf in d.values():
            buffConf = GiftBagConf().decodeFromDict(buffConf)
            self.conf[buffConf.type] = buffConf
        return self

    def getWinBuySwitch(self, buffType, stopWinStreak):
        for buffConf in self.conf.values():
            if buffType == buffConf.type:
                if stopWinStreak in buffConf.winBuy:
                    return True
        return False

_giftBagConf = GiftBag()

def initialize():
    TGHall.getEventBus().subscribe(TYOrderDeliveryEvent, onOrderDelivery)
    pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    _reloadConf()

def _onConfChanged(event):
    if event.isChanged(['game:6:ddz.buffgift:0']):
        _reloadConf()

def _reloadConf():
    global _giftBagConf
    d = configure.getGameJson(DIZHU_GAMEID, 'ddz.buffgift', {})
    conf = GiftBag().decodeFromDict(d)
    _giftBagConf = conf


def onOrderDelivery(event):
    # 收到礼包事件后给玩家加buff
    productId = event.orderDeliveryResult.order.productId
    if not productId:
        return False

    hallGameId = strutil.getGameIdFromHallClientId(event.orderDeliveryResult.order.clientId)
    if hallGameId != DIZHU_GAMEID:
        return False

    giftBuff = None
    for buff in _giftBagConf.conf.values():
        if productId in buff.productIds:
            giftBuff = buff
            break
    if not giftBuff:
        return False

    expireTime = pktimestamp.getCurrentTimestamp() + (giftBuff.limitHour * 3600) if giftBuff.limitHour else 0

    ret = False
    if giftBuff.type in ['winStreakBuff', 'loseStreakBuff']:
        # 给玩家加buff(winStreakBuff 连胜奖励翻3倍)(loseStreakBuff 下次赢牌奖励翻2倍)
        new_table_remote.setUserGiftBuff(event.userId, str(giftBuff.type), expireTime)
        ret = True
    elif giftBuff.type == 'stopWinStreakBuff':
        # 给玩家发奖 额外加500排行榜积分
        rankingScore = giftBuff.reward['rankingScore'] if giftBuff.reward else None
        rankId = giftBuff.reward['rankId'] if giftBuff.reward else None
        ret = addUserScoreByGiftBox(event.userId, rankId, rankingScore) if rankingScore and rankId else False

    if ftlog.is_debug():
        ftlog.debug('gift bag onOrderDelivery',
                    'userId=', event.userId,
                    'productId=', productId,
                    'buffType=', giftBuff.type,
                    'expireTime=', expireTime,
                    'ret=', ret)
    return ret

def exchangeBiEvent(buffType):
    if buffType == 'winStreakBuff':
        # 地主 连胜任务奖励事件id
        return 'DIZHU_WINSTREAK_BUFF_REWARD'
    elif buffType == 'loseStreakBuff':
        # 地主 连败任务奖励事件id
        return 'DIZHU_LOSESTREAK_BUFF_REWARD'
    return buffType

def giftBuffSettle(userId, roomId, assetKindId, count, buffType):
    timeStamp = pktimestamp.getCurrentTimestamp()
    buffExpireTime, _ = new_table_remote.getUserGiftBuff(userId, str(buffType))
    if timeStamp <= buffExpireTime:
        for buffConf in _giftBagConf.conf.values():
            if buffType != buffConf.type:
                continue
            count = count * (buffConf.multi - 1)
            if count <= 0:
                continue
            if buffConf.type == 'loseStreakBuff':
                new_table_remote.setUserGiftBuff(userId, str(buffConf.type), 0)
            new_table_remote.sendGiftBuffReward(userId, roomId, assetKindId, count, exchangeBiEvent(buffType))
            if ftlog.is_debug():
                ftlog.debug('giftBuffSettle userId=', userId,
                            'roomId=', roomId,
                            'assetKindId=', assetKindId,
                            'count=', count,
                            'str=', buffConf.type)
            return buffConf.multi
    return -1


def onTableWinLose(userId, roomId, clientId, isWin, winStreak, loseStreak, stopWinStreak, isBuyInGift):
    # 胜负事件触发
    bigRoomId = gdata.getBigRoomId(roomId)
    task = None
    if isWin:
        buffType = 'winStreakBuff'
        ret = isEjectGiftBuff(userId, winStreak, bigRoomId, buffType)
        if ret:
            task = dizhupopwnd.generateDizhuWinStreakBuffGift(userId, clientId)
    elif stopWinStreak > 0:
        buffType = 'stopWinStreakBuff'
        ret = isEjectGiftBuff(userId, stopWinStreak, bigRoomId, buffType)
        if ret:
            task = dizhupopwnd.generateDizhuStopWinStreakGift(userId, clientId)

            if _giftBagConf.getWinBuySwitch(buffType, stopWinStreak):
                sendWinBuyTodotask(userId, clientId, bigRoomId)
    else:
        buffType = 'loseStreakBuff'
        ret = isEjectGiftBuff(userId, loseStreak, bigRoomId, buffType)
        if ret:
            task = dizhupopwnd.generateDizhuLoseStreakBuffGift(userId, clientId)

    # 若满足 1.未触发以上三个礼包 2.有春天或满贯 3.非升段 4.无buff 弹出连胜礼包
    if isBuyInGift and not task:
        expireTime, _ = new_table_remote.getUserGiftBuff(userId, buffType)
        if expireTime <= pktimestamp.getCurrentTimestamp():
            task = dizhupopwnd.generateDizhuWinStreakBuffGift(userId, clientId)
            if task:
                ret = True

    if ftlog.is_debug():
        ftlog.debug('GiftBag onTableWinLose userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'clientId=', clientId,
                    'isWin=', isWin,
                    'winStreak=', winStreak,
                    'loseStreak=', loseStreak,
                    'stopWinStreak=', stopWinStreak,
                    'buffType=', buffType,
                    'isBuyInGift=', isBuyInGift,
                    'ret=', ret, 'task=', task.toDict() if task else None)
    return ret, task


def isEjectGiftBuff(userId, times, bigRoomId, buffType):
    for buffConf in _giftBagConf.conf.values():
        if buffConf.type == buffType:
            if ftlog.is_debug():
                ftlog.debug('isEjectGiftBuff buffConf', buffConf.toDict(), 'userId=', userId, 'times=', times,
                            'bigRoomId=', bigRoomId, 'buffType=', buffType)
            if times in buffConf.openTimes and bigRoomId in buffConf.roomId:
                expireTime, isEjected = new_table_remote.getUserGiftBuff(userId, buffType)
                if times == buffConf.openTimes[0] and isEjected:
                    return False
                elif times == buffConf.openTimes[0] and not isEjected:
                    new_table_remote.setUserGiftBuff(userId, buffType, 0)
                    return True
                elif expireTime > pktimestamp.getCurrentTimestamp():
                    return False
                return True
    return False


def checkUserGiftBuff(userId):
    timeStamp = pktimestamp.getCurrentTimestamp()
    winStreakBuffExpireTime, _ = new_table_remote.getUserGiftBuff(userId, 'winStreakBuff')
    winSteakBuff = True if timeStamp <= winStreakBuffExpireTime else False
    loseStreakBuffExpireTime, _ = new_table_remote.getUserGiftBuff(userId, 'loseStreakBuff')
    loseStreakBuff = True if timeStamp <= loseStreakBuffExpireTime else False
    return winSteakBuff, loseStreakBuff


def sendWinBuyTodotask(userId, clientId, bigRoomId):
    from hall.entity import hallpopwnd
    from hall.entity.todotask import TodoTaskHelper
    todotask = hallpopwnd.makeTodoTaskWinBuy(DIZHU_GAMEID, userId, clientId, bigRoomId)
    if todotask:
        todotask.setParam('delay', 3)
        TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, todotask)