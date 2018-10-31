# -*- coding:utf-8 -*-
"""
Created on 2017年7月21日

@author: wangjifa
"""

from datetime import time, datetime, timedelta
from sre_compile import isstring

from dizhu.activities.toolbox import UserBag
from dizhu.activitynew.activity import ActivityNew
from dizhu.entity import dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.entity.events import UserTableWinloseEvent
from hall.entity import hallitem
from hall.entity.hallevent import HallShare2Event
from hall.entity.hallshare import HallShareEvent
from hall.entity.todotask import TodoTaskHelper, TodoTaskDownloadApkPromote
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata, pokerconf, configure
from poker.util import strutil
from poker.util import timestamp as pktimestamp
from poker.entity.dao import daobase, sessiondata, userdata
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import EventHeartBeat, ChargeNotifyEvent, MatchWinloseEvent

import freetime.util.log as ftlog


class RewardState(object):
    ST_NO_REWARD = 0
    ST_HAS_REWARD = 1
    ST_GAIN_REWARD = 2

class UserData(object):
    def __init__(self, userId, rankId, issueNum):
        self.userId = userId
        self.rankId = rankId
        self.issueNum = issueNum
        self.name = ''
        self.score = 0
        self.rank = 0
        self.chargeScore = 0
        self.roundScoreList = []
        self.rewardStu = 0
        self.dibaoStu = 0
        self.todayShareScore = 0

    def toDict(self):
        return {'name': self.name,
                'score': self.score,
                'rank': self.rank,
                'charge': self.chargeScore,
                'share': self.todayShareScore,
                'round': self.roundScoreList,
                'stu': self.rewardStu,
                'dibao': self.dibaoStu}

    def fromDict(self, d):
        self.name = d.get('name', '')
        self.score = d.get('score', 0)
        self.rank = d.get('rank', 0)
        self.chargeScore = d.get('charge', 0)
        self.todayShareScore = d.get('share', 0)
        self.roundScoreList = d.get('round', [])
        self.rewardStu = d.get('stu', 0)
        self.dibaoStu = d.get('dibao', 0)
        return self

def buildUserDataKey(rankId, issueNum):
    return 'activityScoreRank.userData:%s:%s:%s' % (DIZHU_GAMEID, rankId, issueNum)

def buildRankListKey(rankId, issueNum):
    return 'activityScoreRank.rankList:%s:%s:%s' % (DIZHU_GAMEID, rankId, issueNum)

def buildActivityRankInfoKey():
    return 'activityScoreRank.rankInfo:%s' % DIZHU_GAMEID

def saveUserData(userData):
    # 存储用户数据
    key = buildUserDataKey(userData.rankId, userData.issueNum)
    jstr = strutil.dumps(userData.toDict())
    ret = daobase.executeRePlayCmd('hset', key, userData.userId, jstr)
    if ftlog.is_debug():
        ftlog.debug('activityScoreRank saveUserData userId=', userData.userId,
                    'rankId=', userData.rankId,
                    'issueNum=', userData.issueNum,
                    'jstr=', jstr, 'ret=', ret)
    return ret

def loadUserData(userId, rankId, issueNum):
    jstr = None
    try:
        key = buildUserDataKey(rankId, issueNum)
        jstr = daobase.executeRePlayCmd('hget', key, userId)
        if ftlog.is_debug():
            ftlog.debug('activityScoreRank loadUserData userId=', userId,
                        'rankId=', rankId, 'issueNum=', issueNum, 'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return UserData(userId, rankId, issueNum).fromDict(d)
    except:
        ftlog.error('loadUserData userId=', userId, 'rankId=', rankId, 'issueNum=', issueNum, 'jstr=', jstr)
    return None

def loadOrCreateUserData(userId, rankId, issueNum):
    ret = loadUserData(userId, rankId, issueNum)
    if not ret:
        ret = UserData(userId, rankId, issueNum)
    return ret

def removeRankUserData(rankId, issueNum):
    key = buildUserDataKey(rankId, issueNum)
    ret = daobase.executeRePlayCmd('del', key)
    ftlog.info('activityScoreRank delAllUserData key=', key, ' ret=', ret)


class ActivityScoreRankingInfo(object):
    """
    某个排行榜信息，记录目前该排行榜有哪些期号
    """
    ST_OPEN = 0
    ST_FINISH = 1
    ST_SETTLEMENT = 2

    class Item(object):
        def __init__(self, issueNum, state):
            self.issueNum = issueNum
            self.state = state

    def __init__(self, rankId):
        self.rankId = rankId
        self.items = []

    @property
    def itemCount(self):
        return len(self.items)

    def addIssue(self, issueNum):
        if self.findItem(issueNum):
            return False
        self.items.append(ActivityScoreRankingInfo.Item(issueNum, self.ST_OPEN))
        return True

    def findItem(self, issueNum):
        for item in self.items:
            if str(item.issueNum) == str(issueNum):
                return item
        return None

    def fromDict(self, d):
        for itemD in d.get('items', []):
            issueNum = itemD.get('issn')
            state = itemD.get('st')
            item = ActivityScoreRankingInfo.Item(issueNum, state)
            self.items.append(item)
        return self

    def toDict(self):
        items = []
        for item in self.items:
            items.append({'issn': item.issueNum, 'st': item.state})
        return {'items': items}

def loadActivityScoreRankingInfo(rankId):
    jstr = None
    try:
        key = buildActivityRankInfoKey()
        jstr = daobase.executeRePlayCmd('hget', key, rankId)
        if ftlog.is_debug():
            ftlog.debug('loadRankingInfo rankId=', rankId, 'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return ActivityScoreRankingInfo(rankId).fromDict(d)
    except:
        ftlog.error('loadActivityScoreRankingInfo rankId=', rankId, 'jstr=', jstr)
    return ActivityScoreRankingInfo(rankId)

def saveActivityScoreRankingInfo(rankingInfo):
    d = rankingInfo.toDict()
    jstr = strutil.dumps(d)
    key = buildActivityRankInfoKey()
    daobase.executeRePlayCmd('hset', key, rankingInfo.rankId, jstr)
    ftlog.info('saveActivityScoreRankingInfo rankId=', rankingInfo.rankId, 'jstr=', jstr)


def insertRankList(rankId, issueNum, userId, score, rankLimit):
    assert (rankLimit > 0)
    try:
        key = buildRankListKey(rankId, issueNum)
        daobase.executeRePlayCmd('zadd', key, score, userId)
        removed = daobase.executeRePlayCmd('zremrangebyrank', str(key), 0, -rankLimit - 1)
        if ftlog.is_debug():
            ftlog.debug('insert activityScoreRank',
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'userId=', userId,
                        'score=', score,
                        'rankLimit=', rankLimit,
                        'removed=', removed)
    except:
        ftlog.error('insert activityScoreRank',
                    'rankId=', rankId,
                    'issueNum=', issueNum,
                    'userId=', userId,
                    'score=', score,
                    'rankLimit=', rankLimit)

def removeRanklist(rankId, issueNum):
    key = buildRankListKey(rankId, issueNum)
    ret = daobase.executeRePlayCmd('del', key)
    ftlog.info('removeRankList rankId=', rankId, 'issueNum=', issueNum, 'key=', key, 'ret=', ret)
    return ret

def getRankList(rankId, issueNum, start, stop):
    key = buildRankListKey(rankId, issueNum)
    return daobase.executeRePlayCmd('zrevrange', key, start, stop)

def getRankListWithScore(rankId, issueNum, start, stop):
    ret = []
    key = buildRankListKey(rankId, issueNum)
    datas = daobase.executeRePlayCmd('zrevrange', key, start, stop, 'withscores')
    if datas:
        for i in xrange(len(datas) / 2):
            userId = int(datas[i * 2])
            score = int(datas[i * 2 + 1])
            ret.append((userId, score))
    return ret

def getUserRank(userId, rankId, issueNum):
    key = buildRankListKey(rankId, issueNum)
    rank = daobase.executeRePlayCmd('zrevrank', key, userId)
    if rank is not None:
        return rank + 1
    return 0


class ScoreUpByRoundAndWins(object):
    def __init__(self):
        self.maxScore = 0
        self.scorePerRound = 0
        self.scorePerWin = 0
        self.openRoomIds = None

    def decodeFromDict(self, d):
        self.maxScore = d.get('maxScore')
        if not isinstance(self.maxScore, int):
            raise TYBizConfException(d, 'ScoreUpByRoundAndWins.maxPlayCount must be int')

        self.scorePerRound = d.get('scorePerRound')
        if not isinstance(self.scorePerRound, int):
            raise TYBizConfException(d, 'ScoreUpByRoundAndWins.scorePerRound must be int')

        self.scorePerWin = d.get('scorePerWin')
        if not isinstance(self.scorePerWin, int):
            raise TYBizConfException(d, 'ScoreUpByRoundAndWins.scorePerWin must be int')

        self.openRoomIds = d.get('openRoomIds', [])
        if not isinstance(self.openRoomIds, list):
            raise TYBizConfException(d, 'ScoreUpByRoundAndWins.openRoomIds must be int list')

        return self

    def toDict(self):
        return {
            'maxScore': self.maxScore,
            'scorePerRound': self.scorePerRound,
            'scorePerWin': self.scorePerWin,
            'openRoomIds': self.openRoomIds
        }


class ScoreUpByCharge(object):
    def __init__(self):
        self.maxScore = None
        self.exchangeRate = None

    def decodeFromDict(self, d):
        self.maxScore = d.get('maxScore')
        if not isinstance(self.maxScore, int):
            raise TYBizConfException(d, 'ScoreUpByCharge.maxScore must be int')

        self.exchangeRate = d.get('exchangeRate')
        if not isinstance(self.exchangeRate, (float, int)):
            raise TYBizConfException(d, 'ScoreUpByCharge.maxScore must be int or float')

        return self


class ScoreUpByGatherItem(object):
    def __init__(self):
        self.itemId = None
        self.itemScore = None

    def decodeFromDict(self, d):
        self.itemId = d.get('itemId')
        if not isstring(self.itemId):
            raise TYBizConfException(d, 'ScoreUpByGatherItem.itemId must be valid string')

        self.itemScore = d.get('score')
        if not isinstance(self.itemScore, (int, float)) or self.itemScore < 0:
            raise TYBizConfException(d, 'ScoreUpByGatherItem. score must be int or float >= 0')
        return self


class ScoreUpByShare(object):
    def __init__(self):
        self.maxShareScore = None
        self.shareId = None
        self.score = None

    def decodeFromDict(self, d):
        self.maxShareScore = d.get('maxShareScore')
        if not isinstance(self.maxShareScore, int):
            raise TYBizConfException(d, 'ScoreUpByShare.maxShareScore must be int')

        self.shareId = d.get('shareId')
        if not isinstance(self.shareId, list):
            raise TYBizConfException(d, 'ScoreUpByShare.shareId must be list')

        self.score = d.get('score')
        if not isinstance(self.score, int):
            raise TYBizConfException(d, 'ScoreUpByShare.score must be int')

        return self


def calcDailyIssueNum(timestamp=None):
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d')

def calcYesterdayIssueNum(timestamp=None):
    ct = timestamp if timestamp else datetime.now()
    ct = ct - timedelta(days=1)
    return int(ct.strftime('%Y%m%d'))


class ActivityScoreRanking(ActivityNew):
    TYPE_ID = 'act_ddz_scoreboard'
    zeroTime = time()

    """
    # 积分加成类型:
    # 局数+指定房间号
    # 胜场+指定房间号
    # 充值+按照商品标价来增加积分
    # 大厅登陆
    # 收集物品
    # 指定shareID的分享
    # 每天金币获得量
    # 使用指定道具获得积分
    # 奖券兑换实物获得积分
    """

    def __init__(self):
        super(ActivityScoreRanking, self).__init__()
        self._scoreUpWay = {}
        self._itemAddition = {}  # 积分道具加成
        self._dailyReward = None
        self._totalReward = None
        self._mail = None
        self._hallGameIds = None
        self._clientIds = None
        self._rules = None
        self._issueNum = None
        self._open = 0
        self._showLimit = None
        self._rewardLimit = None
        self._historyLen = 10
        self._dayOpenTime = self.zeroTime
        self._dayCloseTime = self.zeroTime

        self._dibaoScore = None
        self._dibaoRound = None
        self._dibaoReward = None

    @property
    def itemAddition(self):
        return self._itemAddition

    @property
    def dibaoScore(self):
        return self._dibaoScore

    @property
    def dibaoReward(self):
        return self._dibaoReward

    @property
    def clientIds(self):
        return self._clientIds

    @property
    def issueNum(self):
        return self._issueNum

    @property
    def showLimit(self):
        return self._showLimit

    @property
    def rewardLimit(self):
        return self._rewardLimit

    @property
    def mail(self):
        return self._mail

    @property
    def rules(self):
        return self._rules

    @property
    def historyLen(self):
        return self._historyLen

    def init(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, self.onTableGameRoundFinish)
        TGDizhu.getEventBus().subscribe(MatchWinloseEvent, self.onMatchGameRoundFinish)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, self._onChargeNotify)
        TGHall.getEventBus().subscribe(HallShareEvent, self._onUserShare)
        TGHall.getEventBus().subscribe(HallShare2Event, self._onUserShare)

    def cleanup(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().unsubscribe(UserTableWinloseEvent, self.onTableGameRoundFinish)
        TGDizhu.getEventBus().unsubscribe(MatchWinloseEvent, self.onMatchGameRoundFinish)
        TGHall.getEventBus().unsubscribe(ChargeNotifyEvent, self._onChargeNotify)
        TGHall.getEventBus().unsubscribe(HallShareEvent, self._onUserShare)
        TGHall.getEventBus().unsubscribe(HallShare2Event, self._onUserShare)


    def _decodeFromDictImpl(self, d):
        self._open = d.get('open')
        if not isinstance(self._open, int):
            raise TYBizConfException(d, 'ScoreRankingConf._open must be int')

        self._issueNum = d.get('issueNum')
        if not isinstance(self._issueNum, int):
            raise TYBizConfException(d, 'ScoreRankingConf._issueNum must be int')

        self._itemAddition = d.get('itemAddition')
        if not isinstance(self._itemAddition, dict):
            raise TYBizConfException(d, 'ScoreRankingConf.itemAddition must be dict')

        scoreUpWay = d.get('scoreUpWay')
        if not isinstance(scoreUpWay, dict):
            raise TYBizConfException(d, 'ScoreRankingConf.scoreUpWay must be dict')

        charge = scoreUpWay.get('charge')
        if not isinstance(charge, dict):
            raise TYBizConfException(d, 'ScoreRankingConf.scoreUpWay.charge must be dict')
        self._scoreUpWay['charge'] = ScoreUpByCharge().decodeFromDict(charge)

        share = scoreUpWay.get('share')
        if share and not isinstance(share, dict):
            raise TYBizConfException(d, 'ScoreRankingConf.scoreUpWay.share must be dict')
        self._scoreUpWay['share'] = ScoreUpByShare().decodeFromDict(share)

        roundAndWins = scoreUpWay.get('roundAndWins')
        if roundAndWins:
            if not isinstance(roundAndWins, list):
                raise TYBizConfException(d, 'ScoreRankingConf.roundAndWins must be list')
            ret = []
            for roundConf in roundAndWins:
                ret.append(ScoreUpByRoundAndWins().decodeFromDict(roundConf))
            self._scoreUpWay['roundAndWins'] = ret

        gatherItem = scoreUpWay.get('gatherItem')
        if gatherItem:
            if not isinstance(gatherItem, list):
                raise TYBizConfException(d, 'ScoreRankingConf.gatherItem must be list')
            ret = []
            for gatherConf in gatherItem:
                ret.append(ScoreUpByGatherItem().decodeFromDict(gatherConf))
            self._scoreUpWay['gatherItem'] = ret

        self._rules = d.get('rules', [])
        if not isinstance(self._rules, list):
            raise TYBizConfException(d, 'ScoreRankingConf.rules must be list')

        self._mail = d.get('mail')
        if self._mail and not isstring(self._mail):
            raise TYBizConfException(d, 'ScoreRankingConf.mail must be string')

        self._hallGameIds = d.get('hallGameIds')
        if self._hallGameIds and not isinstance(self._hallGameIds, list):
            raise TYBizConfException(d, 'ScoreRankingConf._hallGameIds must be list')

        self._clientIds = d.get('clientIds')
        if self._clientIds and not isinstance(self._clientIds, list):
            raise TYBizConfException(d, 'ScoreRankingConf._clientIds must be list')

        self._dailyReward = d.get('dailyReward')
        if not isinstance(self._dailyReward, list):
            raise TYBizConfException(d, 'ScoreRankingConf._dailyReward must be list')

        self._totalReward = d.get('totalReward')
        if not isinstance(self._totalReward, list):
            raise TYBizConfException(d, 'ScoreRankingConf._totalReward must be list')

        self._showLimit = d.get('showLimit')
        if not isinstance(self._showLimit, int):
            raise TYBizConfException(d, 'ScoreRankingConf._showLimit must be int')

        self._rewardLimit = d.get('rewardLimit')
        if not isinstance(self._rewardLimit, int):
            raise TYBizConfException(d, 'ScoreRankingConf._rewardLimit must be int')

        self._historyLen = d.get('historyLen')
        if not isinstance(self._historyLen, int):
            raise TYBizConfException(d, 'ScoreRankingConf._historyLen must be int')

        try:
            openTimeStr = d.get('dayOpenTime')
            if openTimeStr:
                self._dayOpenTime = datetime.strptime(openTimeStr, '%H:%M').time()

            closeTimeStr = d.get('dayCloseTime')
            if closeTimeStr:
                self._dayCloseTime = datetime.strptime(closeTimeStr, '%H:%M').time()
        except:
            raise TYBizConfException(d, 'ActivityScoreRanking.dayOpen/CloseTime must be time str')

        self._dibaoScore = d.get('dibaoScore')
        if self._dibaoScore and not isinstance(self._dibaoScore, int):
            raise TYBizConfException(d, 'ScoreRankingConf._dibaoScore must be int')

        self._dibaoRound = d.get('dibaoRound')
        if self._dibaoRound and not isinstance(self._dibaoRound, int):
            raise TYBizConfException(d, 'ScoreRankingConf._dibaoRound must be int')

        self._dibaoReward = d.get('dibaoReward')
        if self._dibaoReward and not isinstance(self._dibaoReward, dict):
            raise TYBizConfException(d, 'ScoreRankingConf._dibaoReward must be dict')

        finalDate = datetime.strptime(str(self._issueNum), '%Y%m%d')
        if self.endTime >= finalDate:
            raise TYBizConfException(d, 'ScoreRankingConf.issueNum must > endTimeDate')

        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRanking decodeFromDict open=', self._open,
                        'actId=', self.actId,
                        'intActId=', self.intActId,
                        'issueNum=', self._issueNum,
                        'showLimit=', self._showLimit,
                        'dibaoScore=', self._dibaoScore)

        return self

    def isOutOfTime(self, timestamp=None):
        timestamp = pktimestamp.getCurrentTimestamp() if not timestamp else timestamp
        t = datetime.fromtimestamp(timestamp).time()
        return (self._dayOpenTime != self.zeroTime and t < self._dayOpenTime) or (
        self._dayCloseTime != self.zeroTime and t >= self._dayCloseTime)

    def checkActivityActive(self, userId, timeStamp=None, clientId=None):
        if not self._open:
            return False

        timeStamp = pktimestamp.getCurrentTimestamp() if not timeStamp else timeStamp
        if self.checkTime(timeStamp) != 0:
            if ftlog.is_debug():
                ftlog.debug('ActivityScoreRanking.checkActivityActive:',
                            'userId=', userId, 'actId=', self.actId, 'checkTime=False')
            return False

        if self.isOutOfTime():
            if ftlog.is_debug():
                ftlog.debug('ActivityScoreRanking.checkActivityActive:',
                            'userId=', userId, 'actId=', self.actId, 'outOfTime')
            return False

        clientId = clientId or sessiondata.getClientId(userId)
        user_gameId = strutil.getGameIdFromHallClientId(clientId)
        intClientId = pokerconf.clientIdToNumber(clientId)

        if user_gameId not in self._hallGameIds:
            return False

        if intClientId not in self._clientIds:
            if ftlog.is_debug():
                ftlog.debug('ActivityScoreRanking.checkActiveFalse: userId=', userId,
                            'intClientId=', intClientId,
                            'clientIds=', self._clientIds)
            return False
        return True

    def _onChargeNotify(self, event):
        # charge 充值增加积分 按照商品标价（钻石）来增加积分
        isOpen = self.checkActivityActive(event.userId)
        if not isOpen:
            return

        diamonds = int(event.diamonds)
        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRanking _onChargeNotify userId=', event.userId,
                        'rmb=', event.rmbs,
                        'productId=', event.productId,
                        'diamonds=', diamonds)

        todayIssueNum = calcDailyIssueNum()
        totalIssueNum = self._issueNum

        chargeConf = self._scoreUpWay.get('charge')

        userData = loadOrCreateUserData(event.userId, self.actId, todayIssueNum)
        scoreDelta = int(round(chargeConf.exchangeRate * diamonds / 10))
        scoreDelta = min(scoreDelta, chargeConf.maxScore - userData.chargeScore)

        name, _ = userdata.getAttrs(event.userId, ['name', 'purl'])

        # 保存日榜玩家信息
        userData.chargeScore += scoreDelta
        userData.score += scoreDelta
        userData.name = '' if name is None else str(name)
        if self._dibaoScore:
            if userData.score >= self._dibaoScore and userData.dibaoStu == RewardState.ST_NO_REWARD:
                userData.dibaoStu = RewardState.ST_HAS_REWARD
        saveUserData(userData)
        insertRankList(self.actId, todayIssueNum, event.userId, userData.score, self.rewardLimit)

        # 保存总榜玩家信息
        totalUserData = loadOrCreateUserData(event.userId, self.actId, totalIssueNum)
        totalUserData.score += scoreDelta
        totalUserData.name = '' if name is None else str(name)
        saveUserData(totalUserData)
        insertRankList(self.actId, totalIssueNum, event.userId, totalUserData.score, self.rewardLimit)

        ftlog.info('ActivityScoreRanking _onChargeNotify',
                   'userId=', event.userId,
                   'diamonds=', diamonds,
                   'scoreDelta=', scoreDelta,
                   'today.score=', userData.score,
                   'total.score=', totalUserData.score)

    def onMatchGameRoundFinish(self, event):
        bigRoomId = gdata.getBigRoomId(event.matchId)
        self._onGameRoundFinish(event.userId, bigRoomId, event.isWin)

    def onTableGameRoundFinish(self, event):
        # 金币桌
        userId = event.userId
        bigRoomId = event.mixConfRoomId or gdata.getBigRoomId(event.roomId)
        isWin = event.winlose.isWin
        self._onGameRoundFinish(userId, bigRoomId, isWin)

    def _onGameRoundFinish(self, userId, bigRoomId, isWin):
        isOpen = self.checkActivityActive(userId)
        if not isOpen:
            return

        roundConf = None
        for conf in self._scoreUpWay.get('roundAndWins', {}):
            if bigRoomId in conf.openRoomIds:
                roundConf = conf
                break

        if not roundConf:
            if ftlog.is_debug():
                ftlog.debug('ActivityScoreRanking _onGameRoundFinish userId=', userId,
                            'bigRoomId=', bigRoomId, 'not in activity',
                            'conf=', self._scoreUpWay.get('roundAndWins', {}))
            return

        todayIssueNum = calcDailyIssueNum()
        totalIssueNum = self._issueNum

        scoreDelta = roundConf.scorePerRound
        if isWin:
            scoreDelta += roundConf.scorePerWin

        # 道具积分加成
        if self._itemAddition.get('open'):
            rate = self.itemAddition.get('rate', 1)
            itemId = self.itemAddition.get('itemId')
            # 判断用户有没有道具
            if itemId and rate and UserBag.getAssetsCount(userId, itemId):
                if ftlog.is_debug():
                    ftlog.debug('ActivityScoreRanking _onGameRoundFinish scoreAddition userId=', userId,
                                'roomId=', bigRoomId,
                                'winLose=', isWin,
                                'scoreDelta=', scoreDelta,
                                'additionScore=', int(round(scoreDelta * rate)),
                                'finalScoreDelta=', scoreDelta + int(round(scoreDelta * rate)))
                scoreDelta += int(round(scoreDelta * rate))

        name, purl = userdata.getAttrs(userId, ['name', 'purl'])

        # 日榜
        userData = loadOrCreateUserData(userId, self.actId, todayIssueNum)

        maxRoundScore = 0
        if userData.roundScoreList:
            for index in range(len(userData.roundScoreList)):
                if bigRoomId in userData.roundScoreList[index].get('openRoomList'):
                    maxRoundScore = userData.roundScoreList[index].get('score', 0)
                    del userData.roundScoreList[index]
                    break

        scoreDelta = min(scoreDelta, roundConf.maxScore - maxRoundScore)
        userData.score += scoreDelta
        maxRoundScore += scoreDelta
        userData.name = name
        userData.roundScoreList.append({'score': maxRoundScore, 'openRoomList': roundConf.openRoomIds})
        if self._dibaoScore:
            if userData.score >= self._dibaoScore and userData.dibaoStu == RewardState.ST_NO_REWARD:
                userData.dibaoStu = RewardState.ST_HAS_REWARD
                if ftlog.is_debug():
                    ftlog.debug('ActivityScoreRanking _onGameRoundFinish userId=', userData.toDict())
        saveUserData(userData)
        insertRankList(self.actId, todayIssueNum, userId, userData.score, self.rewardLimit)

        # 总榜
        totalUserData = loadOrCreateUserData(userId, self.actId, totalIssueNum)
        totalUserData.score += scoreDelta
        totalUserData.name = name
        saveUserData(totalUserData)
        insertRankList(self.actId, totalIssueNum, userId, totalUserData.score, self.rewardLimit)

        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRanking _onGameRoundFinish userId=', userId,
                        'roomId=', bigRoomId,
                        'winLose=', isWin,
                        'scoreDelta=', scoreDelta)

    def _onUserShare(self, event):
        shareId = 0
        # 兼容新老分享
        if isinstance(event, HallShare2Event):
            shareId = event.sharePointId
        elif isinstance(event, HallShareEvent):
            shareId = event.shareid
        if not shareId:
            return

        isOpen = self.checkActivityActive(event.userId)
        if not isOpen:
            return

        shareConf = self._scoreUpWay.get('share')
        if not shareConf:
            return

        todayIssueNum = calcDailyIssueNum()
        totalIssueNum = self._issueNum
        if shareId in shareConf.shareId:
            userData = loadOrCreateUserData(event.userId, self.actId, todayIssueNum)
            if userData.todayShareScore < shareConf.maxShareScore:
                userData.todayShareScore += shareConf.score
                userData.score += shareConf.score
                if self._dibaoScore:
                    if userData.score >= self._dibaoScore and userData.dibaoStu == RewardState.ST_NO_REWARD:
                        userData.dibaoStu = RewardState.ST_HAS_REWARD
                saveUserData(userData)
                insertRankList(self.actId, todayIssueNum, event.userId, userData.score, self.rewardLimit)

                totalUserData = loadOrCreateUserData(event.userId, self.actId, totalIssueNum)
                totalUserData.score += shareConf.score
                saveUserData(totalUserData)
                insertRankList(self.actId, totalIssueNum, event.userId, totalUserData.score, self.rewardLimit)

        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRanking._onUserShare userId=', event.userId,
                        'shareId=', shareId,
                        'rankId=', self.actId,
                        'issueNum=', todayIssueNum)

    def getRewardByRank(self, rank, issueNum):
        rewardList = self._totalReward if int(issueNum) == int(self.issueNum) else self._dailyReward
        if rewardList:
            for reward in rewardList:
                if reward.get('start') <= rank <= reward.get('end'):
                    return {
                        'img': reward.get('img', ''),
                        'desc': reward.get('desc', ''),
                        'items': reward.get('items', [])
                    }
        return None

    def getNextRewardByRank(self, rank, issueNum):
        rewardList = self._totalReward if issueNum == self.issueNum else self._dailyReward
        if not rank:
            return rewardList[-1].get('end', 500), rewardList[-1].get('desc', '')

        if rewardList:
            nextLevelRank = rewardList[0].get('end', 1)
            rewardDesc = rewardList[0].get('desc', '')
            for reward in rewardList:
                if reward.get('start') <= rank <= reward.get('end'):
                    return nextLevelRank, rewardDesc
                rewardDesc = reward.get('desc', '')
                nextLevelRank = reward.get('end', 1)
        return 1, ''

    def getUserReward(self, userId, rankId):
        rewardList = []
        rankingInfo = loadActivityScoreRankingInfo(rankId)
        if rankingInfo.itemCount > 0:
            for info in rankingInfo.items:
                hisIssue = info.get('issn')
                state = info.get('st')
                if state != ActivityScoreRankingInfo.ST_SETTLEMENT:
                    continue
                userData = loadUserData(userId, rankId, hisIssue)
                if userData and userData.rewardStu == RewardState.ST_HAS_REWARD:
                    reward = self.getRewardByRank(userData.rank, hisIssue)
                    rewardList.append(reward)
        return rewardList

    def getUserRewardInfo(self, userId, rankId):
        # 玩家获取奖励信息
        myRewardInfo = []
        rankingInfo = loadActivityScoreRankingInfo(rankId)
        for item in rankingInfo.items:
            if item.state != ActivityScoreRankingInfo.ST_OPEN :
                issueNum = item.issueNum
                userData = loadOrCreateUserData(userId, rankId, issueNum)
                rank = getUserRank(userId, rankId, item.issueNum)
                reward = self.getRewardByRank(rank, item.issueNum)
                rewardStu = userData.rewardStu
                if not reward and userData.dibaoStu != RewardState.ST_NO_REWARD:
                    reward = self._dibaoReward
                    rewardStu = userData.dibaoStu

                info = {'issueNum': item.issueNum,
                        'score': userData.score,
                        'rank': rank,
                        'desc': reward.get('desc') if reward else u'无',
                        'state': rewardStu}
                myRewardInfo.append(info)
        myRewardInfo.sort(key=lambda obj: int(obj.get('issueNum', 0)), reverse=False)
        return myRewardInfo

    def gainUserReward(self, userId, rankId):
        # 玩家领取奖励
        rewardList = []
        rankingInfo = loadActivityScoreRankingInfo(rankId)
        if rankingInfo.itemCount > 0:
            for info in rankingInfo.items:
                hisIssue = info.issueNum
                userData = loadOrCreateUserData(userId, rankId, hisIssue)

                reward = None
                if userData.rewardStu == RewardState.ST_HAS_REWARD:
                    userData.rewardStu = RewardState.ST_GAIN_REWARD
                    reward = self.getRewardByRank(userData.rank, hisIssue)
                elif userData.dibaoStu == RewardState.ST_HAS_REWARD:
                    userData.dibaoStu = RewardState.ST_GAIN_REWARD
                    reward = self._dibaoReward

                if not reward:
                    ftlog.warn('activity_score_ranking gainUserReward',
                               'rankId=', rankId,
                               'userId=', userId,
                               'issueNum=', hisIssue,
                               'rank=', userData.rank,
                               'userData=', userData.toDict(), 'reward is Null')
                    continue

                saveUserData(userData)

                contentItems = TYContentItem.decodeList(reward.get('items'))
                assetList = dizhu_util.sendRewardItems(userId,
                                                       contentItems,
                                                       self._mail,
                                                       'DIZHU_ACTIVITY_SCORE_RANKLIST_REWARD',
                                                       self.intActId)

                ftlog.info('activity_score_ranking gainUserReward',
                           'userId=', userId,
                           'rankId=', rankId,
                           'rewards=', [(atp[0].kindId, atp[1]) for atp in assetList])

                rewardList.append(reward)

        return rewardList


class ActivityScoreRankingHandler(TYActivity):
    TYPE_ID = 'act_ddz_scoreboard'

    ACTION_GET_RANK_INFO = 'scoreboardActivity'
    ACTION_GET_REWARD_INFO = 'scoreboardActivity_rewardInfo'
    ACTION_GAIN_REWARD = 'scoreboardActivity_gainReward'
    ACTION_GET_USER_ITEM_INFO = 'scoreboardActivity_getUserItemInfo'

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRankingHandler.__init__',
                        'clientConfig=', clientConfig,
                        'serverConfig=', serverConfig)

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        action = msg.getParam("action")
        clientId = msg.getParam('clientId')
        activityType = msg.getParam('type')

        intClientId = pokerconf.clientIdToNumber(clientId)
        actIdList = getActIdList()
        actId = ''

        for actConf in actIdList:
            intClientIdList = actConf.get('clientIds')
            if intClientId in intClientIdList:
                actId = actConf.get('actId')
                break

        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRankingHandler.handleRequest',
                        'userId=', userId, 'action=', action,
                        'clientId=', clientId, 'intClientId=', intClientId,
                        'activityType=', activityType, 'actId=', actId,
                        'msg=', msg)
        if actId:
            from dizhu.activitynew import activitysystemnew
            scoreActivity = activitysystemnew.findActivity(actId)
            if scoreActivity:
                if self.ACTION_GET_REWARD_INFO == action:
                    return self.getRewardInfo(userId, scoreActivity)
                elif self.ACTION_GAIN_REWARD == action:
                    return self.gainReward(userId, scoreActivity)
                elif self.ACTION_GET_USER_ITEM_INFO == action:
                    return self.getUserItemInfo(userId, scoreActivity) or {'code': -1, 'info': 'activity not inited'}

                clientId = clientId or sessiondata.getClientId(userId)
                return self.getRankInfo(userId, clientId, scoreActivity, activityType)

        return {'code': -1, 'info': 'activity not inited'}

    @classmethod
    def getUserItemInfo(cls, userId, scoreActivity):
        additionConf = scoreActivity.itemAddition

        itemId = additionConf.get('itemId')
        assetKind = hallitem.itemSystem.findAssetKind(itemId)
        if not itemId or not assetKind:
            return

        remainTime = 0
        owned = False
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        item = userBag.getItemByKindId(int(itemId.split(':')[-1]))
        if item:
            owned = True
            currentTimestamp = pktimestamp.getCurrentTimestamp()
            if item.expiresTime:
                remainTime = item.expiresTime - currentTimestamp
        todoTask = None
        todoTaskConf = additionConf.get('todoTask')
        if todoTaskConf:
            todoTask = TodoTaskDownloadApkPromote(todoTaskConf.get('url'))
            todoTask.setParam('action', todoTaskConf.get('params', {}).get('action'))
            todoTask.setParam('func', todoTaskConf.get('params', {}).get('func'))
        if ftlog.is_debug():
            ftlog.debug('ActivityScoreRankingHandler.getUserItemInfo',
                        'userId=', userId,
                        'todoTask=', todoTask,
                        'todoTaskStr=', TodoTaskHelper.encodeTodoTasks(todoTask) if todoTask else None,
                        'owned=', owned,
                        'remainTime=', remainTime,
                        'additionConf=', additionConf)

        return {
            'open': additionConf.get('open', 0),
            'owned': owned,
            'todoTask':  TodoTaskHelper.encodeTodoTasks(todoTask) if todoTask else None,
            'rate': additionConf.get('rate', 0) + 1,
            'remainTime': remainTime
        }

    @classmethod
    def getRankInfo(cls, userId, clientId, scoreActivity, activityType=None):
        retInfo = {}
        todayIssueNum = calcDailyIssueNum()
        todayUserData = loadOrCreateUserData(userId, scoreActivity.actId, todayIssueNum)

        totalIssueNum = scoreActivity.issueNum
        totalUserData = loadOrCreateUserData(userId, scoreActivity.actId, totalIssueNum)

        # ﻿今日积分，今日排名，总积分，总排名，还差xx名，拿xx奖励
        myTodayRank = todayUserData.rank or getUserRank(userId, scoreActivity.actId, todayIssueNum)
        myTotalRank = totalUserData.rank or getUserRank(userId, scoreActivity.actId, totalIssueNum)

        # 上一名的奖励
        nextRank, nextDesc = scoreActivity.getNextRewardByRank(myTodayRank, todayIssueNum)

        # 上一名的积分
        nextScore = 0
        todayRankList = getRankListWithScore(scoreActivity.actId, todayIssueNum, 0, -1)
        for i, (rankUserId, score) in enumerate(todayRankList):
            if i + 1 == nextRank:
                nextScore = score
                break

        nextRewardScore = max(0, nextScore - todayUserData.score)
        if todayUserData.score < scoreActivity.dibaoScore:
            nextRewardScore = scoreActivity.dibaoScore - todayUserData.score
            nextDesc = scoreActivity.dibaoReward.get('desc', u'低保奖励')

        retInfo['userInfo'] = {"todayScore": todayUserData.score,
                               "todayRank": myTodayRank,
                               "totalScore": totalUserData.score,
                               "totalRank": myTotalRank,
                               "nextRewardDesc": nextDesc,
                               "nextRewardScore": nextRewardScore,
                               "dailyRewardState": todayUserData.rewardStu if todayUserData.rewardStu else 0}

        # 今日排行。昨日排行。总排行。（名次，名称，积分，奖励desc）
        if activityType == 'totalRank':
            reqIssueNum = scoreActivity.issueNum
        elif activityType == 'yesterdayRank':
            reqIssueNum = calcYesterdayIssueNum()
        else:
            reqIssueNum = todayIssueNum

        rankInfo = []
        rankList = getRankList(scoreActivity.actId, reqIssueNum, 0, scoreActivity.showLimit - 1)
        if rankList:
            for rankUserId in rankList:
                rankUserData = loadOrCreateUserData(rankUserId, scoreActivity.actId, reqIssueNum)
                rank = rankUserData.rank or getUserRank(rankUserId, scoreActivity.actId, reqIssueNum)
                reward = scoreActivity.getRewardByRank(rank, reqIssueNum)
                rankUserInfo = {'name': rankUserData.name,
                                'score': rankUserData.score,
                                'desc': reward.get('desc', "") if reward else ""}
                rankInfo.append(rankUserInfo)

        if ftlog.is_debug():
            ftlog.debug('activity getRankInfo userId=', userId,
                        'clientId=', clientId,
                        'activityType=', activityType,
                        'reqIssueNum=', reqIssueNum,
                        'userInfo=', retInfo['userInfo'],
                        'rankInfo=', rankInfo)

        retInfo['rankInfo'] = rankInfo
        retInfo['type'] = activityType
        return retInfo

    @classmethod
    def getRewardInfo(cls, userId, scoreActivity):
        rewardInfo = scoreActivity.getUserRewardInfo(userId, scoreActivity.actId) if scoreActivity else None
        if ftlog.is_debug():
            ftlog.debug('activityGetRewardInfo userId=', userId, 'rankId=', scoreActivity.actId, 'rewardInfo=', rewardInfo)

        luckyCardCount = UserBag.getAssetsCount(userId, 'item:4167')
        return {'rewardInfo': rewardInfo, 'luckyCardCount': luckyCardCount}

    @classmethod
    def gainReward(cls, userId, scoreActivity):
        rewardList = scoreActivity.gainUserReward(userId, scoreActivity.actId) if scoreActivity else '-1'
        if ftlog.is_debug():
            ftlog.debug('activityGainReward userId=', userId, 'rankId=', scoreActivity.actId, 'rewardList=', rewardList)
        return {'gainReward': rewardList}



def initialize():
    from poker.entity.events.tyeventbus import globalEventBus
    globalEventBus.subscribe(EventHeartBeat, onTimer)

def onTimer(evt):
    actIdList = getActIdList()
    for actConf in actIdList:
        rankId = actConf.get('actId')
        totalIssueNum = actConf.get('issueNum')
        delDate = actConf.get('delDate')
        processRanking(rankId, totalIssueNum, delDate)

def compareIssueNum(n1, n2):
    return cmp(int(n1), int(n2))

def processRanking(rankId, totalIssueNum, delDate=None, issueNum=None):
    changed = False
    todayIssueNum = calcDailyIssueNum() if not issueNum else issueNum
    rankingInfo = loadActivityScoreRankingInfo(rankId)

    curItem = rankingInfo.findItem(todayIssueNum)
    if not curItem and compareIssueNum(todayIssueNum, totalIssueNum) < 0:
        changed = True
        rankingInfo.addIssue(str(todayIssueNum))

    totalItem = rankingInfo.findItem(totalIssueNum)
    if not totalItem:
        changed = True
        rankingInfo.addIssue(str(totalIssueNum))

    for item in rankingInfo.items:
        if item.state == ActivityScoreRankingInfo.ST_OPEN and (compareIssueNum(item.issueNum, todayIssueNum) < 0 or compareIssueNum(todayIssueNum, totalIssueNum) >= 0):
            item.state = ActivityScoreRankingInfo.ST_SETTLEMENT
            changed = True

            rank = 0
            userIds = getRankList(rankId, item.issueNum, 0, -1)
            for userId in userIds:
                rank += 1

                userData = loadOrCreateUserData(userId, rankId, item.issueNum)
                userData.rank = rank
                if userData.rewardStu == RewardState.ST_NO_REWARD:
                    userData.rewardStu = RewardState.ST_HAS_REWARD
                ftlog.info('activity_scoreRanking rankId=', rankId,
                           'issueNum=', item.issueNum,
                           'userData=', userData.toDict())
                saveUserData(userData)

            ftlog.info('processRanking activity_scoreRanking rankId=', rankId,
                       'issueNum=', item.issueNum,
                       'userIds=', userIds)

    # 删除过期数据
    if delDate and compareIssueNum(todayIssueNum, delDate) >= 0:
        changed = True

        for index in range(len(rankingInfo.items)):
            item = rankingInfo.items.pop()
            if item.state == ActivityScoreRankingInfo.ST_SETTLEMENT:
                removeRankUserData(rankingInfo.rankId, item.issueNum)
                removeRanklist(rankingInfo.rankId, item.issueNum)

        ftlog.info('processRanking data out of date. rankId=', rankingInfo.rankId,
                   'todayIssueNum=', todayIssueNum,
                   'totalIssueNum=', totalIssueNum,
                   'delDate=', delDate,
                   'issues=', [(item.issueNum, item.state) for item in rankingInfo.items])

    if changed:
        saveActivityScoreRankingInfo(rankingInfo)

    if ftlog.is_debug():
        ftlog.debug('processRanking saveRankingInfo rankId=', rankingInfo.rankId,
                    'todayIssueNum=', todayIssueNum, 'totalIssueNum=', totalIssueNum,
                    'delDate=', delDate, 'curDate=', calcDailyIssueNum(),
                    'issues=', [(item.issueNum, item.state) for item in rankingInfo.items])


def getActIdList():
    TYPE_ID = 'act_ddz_scoreboard'

    actConfList = []
    conf = configure.getGameJson(6, 'activity.new', {})
    for actConf in conf.get('activities', []):
        if actConf.get('typeId', '') == TYPE_ID:
            actConfList.append(actConf)
    return actConfList
