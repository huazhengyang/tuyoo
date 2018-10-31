# coding: utf8
'''
Created on 2017年6月20日

@author: wangjifa
'''

from datetime import time, datetime
from sre_compile import isstring

from dizhu.activities.toolbox import UserBag
from dizhu.entity import dizhu_util, dizhuled
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity.led_util import LedUtil
from dizhucomm.entity.events import UserTableWinloseEvent
from hall.entity import hallvip
from hall.entity.hallitem import TYOpenItemEvent
from hall.game import TGHall
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.configure import configure, gdata
from poker.entity.dao import daobase, userdata, sessiondata, gamedata
from poker.entity.events.tyevent import EventConfigure, EventHeartBeat
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import timestamp as pktimestamp, strutil


class RewardState(object):
    ST_NO_REWARD = 0
    ST_HAS_REWARD = 1
    ST_GAIN_REWARD = 2


class ScoreDibaoConf(object):
    # 低保配置

    def __init__(self):
        self.score = None
        self.playCount = None
        self.rewardMail = None
        self.desc = None
        self.img = None
        self.rewardItems = None

    def decodeFromDict(self, d):
        self.score = d.get('score')
        if not isinstance(self.score, int):
            raise TYBizConfException(d, 'ScoreDiBaoConf.score must be int')

        self.playCount = d.get('playCount')
        if not isinstance(self.playCount, int):
            raise TYBizConfException(d, 'ScoreDiBaoConf.playCount must be int')

        self.rewardMail = d.get('rewardMail', '')
        if not isstring(self.rewardMail):
            raise TYBizConfException(d, 'ScoreDiBaoConf.rewardMail must be string')

        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'ScoreDiBaoConf.desc must be string')

        self.img = d.get('img', '')
        if not isstring(self.img):
            raise TYBizConfException(d, 'ScoreDiBaoConf.img must be string')

        self.rewardItems = TYContentItem.decodeList(d.get('items', []))
        return self


class ScoreRankingDefine(object):
    # 排行榜配置
    zeroTime = time()

    def __init__(self, rankId):
        self.rankId = rankId
        self.switch = None
        self.desc = None
        self.tips = None
        self.rankLimit = None
        self.rewardLimit = None
        self.exchangeRate = None
        self.playCounts = None
        self.playCountsDecayRate = None
        self.beginTime = self.zeroTime
        self.endTime = self.zeroTime
        self.winsPlusRate = None
        self.monthCardPlus = None
        self.monthCardItem = None
        self.honorCardItem = None
        self.honorCardPlus = None
        self.openRoomIds = None
        self.rules = None
        self.vipPlusRateMap = None
        self.dibaoConf = None

    def findVipPlusRate(self, vipLevel):
        return self.vipPlusRateMap.get(vipLevel, 0)

    def isOutOfTime(self, timestamp=None):
        timestamp = pktimestamp.getCurrentTimestamp() if not timestamp else timestamp
        t = datetime.fromtimestamp(timestamp).time()
        return (self.beginTime != self.zeroTime and t < self.beginTime) or (
        self.endTime != self.zeroTime and t >= self.endTime)

    def decodeFromDict(self, d):
        self.switch = d.get('switch')
        if not isinstance(self.switch, int) or self.switch not in (0, 1):
            raise TYBizConfException(d, 'ScoreRankingDefine.switch must be bool int')

        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'ScoreRankingDefine.desc must be string')

        self.tips = d.get('tips', '')
        if not isstring(self.tips):
            raise TYBizConfException(d, 'ScoreRankingDefine.tips must be string')

        self.rankLimit = d.get('rankLimit')
        if not isinstance(self.rankLimit, int):
            raise TYBizConfException(d, 'ScoreRankingDefine.rankLimit must be int')

        self.rewardLimit = d.get('rewardLimit')
        if not isinstance(self.rewardLimit, int):
            raise TYBizConfException(d, 'ScoreRankingDefine.rewardLimit must be int')

        self.exchangeRate = d.get('exchangeRate')
        if not isinstance(self.exchangeRate, (float, int)) or self.exchangeRate <= 0:
            raise TYBizConfException(d, 'ScoreRankingConf.exchangeRate must be float')

        self.playCounts = d.get('playCounts')
        if not isinstance(self.playCounts, int):
            raise TYBizConfException(d, 'ScoreRankingDefine.playCounts must be int')

        self.playCountsDecayRate = d.get('playCountsDecayRate')
        if not isinstance(self.playCountsDecayRate, (float, int)) or self.playCountsDecayRate <= 0:
            raise TYBizConfException(d, 'ScoreRankingConf.playCountsDecayRate must be float')

        timeStr = d.get('beginTime')
        if timeStr:
            try:
                self.beginTime = datetime.strptime(timeStr, '%H:%M').time()
            except:
                raise TYBizConfException(d, 'ScoreRankingConf.beginTime must be time str')

        if timeStr:
            timeStr = d.get('endTime')
            try:
                self.endTime = datetime.strptime(timeStr, '%H:%M').time()
            except:
                raise TYBizConfException(d, 'ScoreRankingConf.endTime must be time str')

        # endTime必须比beginTime大
        if (self.beginTime and self.endTime and self.endTime < self.beginTime):
            raise TYBizConfException(d, 'ScoreRankingConf.endTime must > beginTime')

        self.winsPlusRate = d.get('winsPlusRate')
        if not isinstance(self.winsPlusRate, (float, int)):
            raise TYBizConfException(d, 'ScoreRankingConf.winsPlusRate must be float')

        self.monthCardPlus = d.get('monthCardPlus')
        if self.monthCardPlus:
            if not isinstance(self.monthCardPlus, (float, int)):
                raise TYBizConfException(d, 'ScoreRankingConf.monthCardPlus must be float')
        else:
            self.monthCardPlus = 0

        self.monthCardItem = d.get('monthCardItem')
        if self.monthCardItem:
            if not isstring(self.monthCardItem):
                raise TYBizConfException(d, 'ScoreRankingConf.monthCardItem must be str')

        self.honorCardItem = d.get('honorCardItem')
        if self.honorCardItem:
            if not isstring(self.honorCardItem):
                raise TYBizConfException(d, 'ScoreRankingConf.honorCardItem must be str')
        self.honorCardPlus = d.get('honorCardPlus')
        if self.honorCardPlus:
            if not isinstance(self.honorCardPlus, (float, int)):
                raise TYBizConfException(d, 'ScoreRankingConf.honorCardPlus must be float')
        else:
            self.honorCardPlus = 0

        self.vipPlusRateMap = {}
        for level, plusRate in d.get('vipPlusRate', {}).iteritems():
            try:
                level = int(level)
            except:
                raise TYBizConfException(d, 'ScoreRankingConf.vipPlusRate.level must be int string')

            if not isinstance(plusRate, (int, float)):
                raise TYBizConfException(d, 'ScoreRankingConf.vipPlusRate.rate must be float')
            self.vipPlusRateMap[level] = plusRate

        self.openRoomIds = d.get('openRoomIds', [])
        if not isinstance(self.openRoomIds, list):
            raise TYBizConfException(d, 'ScoreRankingConf.openRoomIds must be int list')

        dibaoConf = d.get('dibao')
        if dibaoConf:
            self.dibaoConf = ScoreDibaoConf().decodeFromDict(dibaoConf)

        self.rules = d.get('rules', [])
        if not isinstance(self.rules, list):
            raise TYBizConfException(d, 'ScoreRankingConf.rules must be list')

        return self


class ScoreRankConf(object):
    '''
    积分榜总配置
    '''

    def __init__(self):
        self.closed = None
        self.historyLen = None
        self.fameHallLen = None
        self.rewardMail = None
        self.minVer = None
        self.refreshInterval = None
        self.cacheCount = None
        self.rankingDefineMap = {}
        self.roomId2RankDefine = {}
        self.ledItems = None

    def findRankingDefine(self, rankId):
        return self.rankingDefineMap.get(rankId)

    def rankDefineForRoomId(self, roomId):
        return self.roomId2RankDefine.get(roomId)

    def decodeFromDict(self, d):
        self.closed = d.get('closed')
        if not isinstance(self.closed, int) or self.closed not in (0, 1):
            raise TYBizConfException(d, 'ScoreRankConf.closed must be bool int')

        self.ledItems = d.get('ledItems', [])
        if not isinstance(self.ledItems, list):
            raise TYBizConfException(d, 'ScoreRankConf.ledItems must be list')

        self.historyLen = d.get('historyLen')
        if not isinstance(self.historyLen, int) or self.historyLen < 0:
            raise TYBizConfException(d, 'ScoreRankConf.historyLen must be int')

        self.fameHallLen = d.get('fameHallLen')
        if not isinstance(self.fameHallLen, int) or self.fameHallLen < 0:
            raise TYBizConfException(d, 'ScoreRankConf.fameHallLen must be int')

        self.rewardMail = d.get('rewardMail', '')
        if not isstring(self.rewardMail):
            raise TYBizConfException(d, 'ScoreRankConf.rewardMail must be string')

        self.minVer = d.get('minVer')
        if not isinstance(self.minVer, (float, int)):
            raise TYBizConfException(d, 'ScoreRankConf.minVer must be float')

        self.refreshInterval = d.get('refreshInterval')
        if not isinstance(self.refreshInterval, int):
            raise TYBizConfException(d, 'ScoreRankConf.refreshInterval must be int')

        self.cacheCount = d.get('cacheCount')
        if not isinstance(self.cacheCount, int):
            raise TYBizConfException(d, 'ScoreRankConf.cacheCount must be int')

        for rankId, rankingConf in d.get('ranks', {}).iteritems():
            rankingDefine = ScoreRankingDefine(rankId).decodeFromDict(rankingConf)
            self.rankingDefineMap[rankId] = rankingDefine

        for rankingDefine in self.rankingDefineMap.values():
            for roomId in rankingDefine.openRoomIds:
                foundRankDefine = self.rankDefineForRoomId(roomId)
                if not foundRankDefine:
                    self.roomId2RankDefine[roomId] = rankingDefine
                elif foundRankDefine and foundRankDefine != rankingDefine:
                    raise TYBizConfException(d, 'ScoreRankConf roomId already in rankingId: %s' % (foundRankDefine.rankId))
        
        return self


_scoreRankConf = ScoreRankConf()


class UserData(object):
    def __init__(self, userId, rankId, issueNum):
        self.userId = userId
        self.rankId = rankId
        self.issueNum = issueNum
        self.score = 0
        self.playCount = 0
        self.dibaoRewardState = RewardState.ST_NO_REWARD
        self.rewardState = RewardState.ST_NO_REWARD
        self.rank = 0
        self.name = ''
        self.purl = ''
        self.lastTimeStamp = 0
        self.todayPlayCount = 0

    def deltaScore(self, delta):
        self.score = max(self.score + int(delta), 0)
        return self.score

    def toDict(self):
        return {
            'score':self.score,
            'playCount':self.playCount,
            'dbrwst':self.dibaoRewardState,
            'rwst':self.rewardState,
            'rank':self.rank,
            'name':self.name,
            'purl':self.purl,
            'lastTime': self.lastTimeStamp,
            'todayCount': self.todayPlayCount
        }
    
    def fromDict(self, d):
        self.score = d.get('score', 0)
        self.playCount = d.get('playCount', 0)
        self.dibaoRewardState = d.get('dbrwst', 0)
        self.rewardState = d.get('rwst', 0)
        self.rank = d.get('rank', 0)
        self.name = d.get('name', '')
        self.purl = d.get('purl')
        self.lastTimeStamp = d.get('lastTime', 0)
        self.todayPlayCount = d.get('todayCount', 0)
        return self


class UserRankInfo(object):
    '''
    用户某个排行榜信息
    '''

    def __init__(self, userId, rankId):
        self.userId = userId
        self.rankId = rankId
        # 所有期号
        self.issues = []

    @property
    def issueCount(self):
        return len(self.issues)

    def issueIndex(self, issueNum):
        try:
            return self.issues.index(issueNum)
        except ValueError:
            return -1

    def addIssue(self, issueNum):
        if -1 == self.issueIndex(issueNum):
            self.issues.append(issueNum)
            return True
        return False

    def removeFront(self):
        assert (self.issueCount > 0)
        return self.issues.pop(0)

    def toDict(self):
        return {'issues': self.issues}

    def fromDict(self, d):
        for issueNum in d.get('issues', []):
            self.issues.append(issueNum)
        return self


class ScoreRankingInfo(object):
    '''
    某个排行榜信息，记录目前该排行榜有哪些期号
    '''
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
        self.items.append(ScoreRankingInfo.Item(issueNum, self.ST_OPEN))
        return True

    def findItem(self, issueNum):
        for item in self.items:
            if item.issueNum == issueNum:
                return item
        return None

    def fromDict(self, d):
        for itemD in d.get('items', []):
            issueNum = itemD.get('issn')
            state = itemD.get('st')
            item = ScoreRankingInfo.Item(issueNum, state)
            self.items.append(item)
        return self

    def toDict(self):
        items = []
        for item in self.items:
            items.append({'issn': item.issueNum, 'st': item.state})
        return {'items': items}


class FameHall(object):
    '''
    名人堂
    '''

    class Item(object):
        def __init__(self, issueNum, no1):
            self.issueNum = issueNum
            self.no1 = no1

    def __init__(self, rankId):
        self.rankId = rankId
        self.items = []

    def findItem(self, issueNum):
        for item in self.items:
            if item.issueNum == issueNum:
                return item
        return None

    def setNo1(self, issueNum, no1):
        item = self.findItem(issueNum)
        if not item:
            item = FameHall.Item(issueNum, no1)
            self.items.append(item)
            self._sort()
            return True
        return False

    def trim(self, keepCount):
        removed = []
        while len(self.items) > keepCount:
            item = self.items.pop(0)
            removed.append(item)
        return removed

    def toDict(self):
        items = []
        for item in self.items:
            items.append({'issn': item.issueNum, 'no1': item.no1})
        return {'items': items}

    def fromDict(self, d):
        for item in d.get('items', []):
            issueNum = item.get('issn')
            no1 = item.get('no1')
            self.items.append(FameHall.Item(issueNum, no1))
        self._sort()
        return self

    def _sort(self):
        self.items.sort(cmp=lambda x, y: compareIssueNum(x.issueNum, y.issueNum))


def buildRankInfoKey():
    return 'roomRank.rankInfo:%s' % (DIZHU_GAMEID)


def buildUserDataKey(userId, rankId):
    return 'roomRank.userData:%s:%s:%s' % (DIZHU_GAMEID, userId, rankId)


def buildUserRankInfoKey(userId):
    return 'roomRank.userRankInfo:%s:%s' % (DIZHU_GAMEID, userId)


def buildRanklistKey(rankId, issueNum):
    return 'roomRank.rankList:%s:%s:%s' % (DIZHU_GAMEID, rankId, issueNum)


def buildFameHallKey():
    return 'roomRank.fameHall:%s' % (DIZHU_GAMEID)


def calcIssueNum(timestamp=None):
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    timestamp = pktimestamp.getWeekStartTimestamp(timestamp)
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d')


def calcTimeStampDate(timestamp=None):
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d')


def loadRankingInfo(rankId):
    jstr = None
    try:
        key = buildRankInfoKey()
        jstr = daobase.executeRePlayCmd('hget', key, rankId)
        if ftlog.is_debug():
            ftlog.debug('loadRankingInfo rankId=', rankId, 'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return ScoreRankingInfo(rankId).fromDict(d)
    except:
        ftlog.error('loadRankingInfo rankId=', rankId, 'jstr=', jstr)

    return ScoreRankingInfo(rankId)


def saveRankingInfo(rankingInfo):
    d = rankingInfo.toDict()
    jstr = strutil.dumps(d)
    key = buildRankInfoKey()
    daobase.executeRePlayCmd('hset', key, rankingInfo.rankId, jstr)
    if ftlog.is_debug():
        ftlog.debug('saveRankingInfo rankId=', rankingInfo.rankId, 'jstr=', jstr)


def loadFameHall(rankId):
    jstr = None
    try:
        key = buildFameHallKey()
        jstr = daobase.executeRePlayCmd('hget', key, rankId)
        if ftlog.is_debug():
            ftlog.debug('loadFameHall rankId=', rankId, 'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return FameHall(rankId).fromDict(d)
    except:
        ftlog.error('loadFameHall rankId=', rankId, 'jstr=', jstr)

    return FameHall(rankId)


def saveFameHall(fameHall):
    d = fameHall.toDict()
    jstr = strutil.dumps(d)
    key = buildFameHallKey()
    daobase.executeRePlayCmd('hset', key, fameHall.rankId, jstr)
    if ftlog.is_debug():
        ftlog.debug('saveFameHall rankId=', fameHall.rankId, 'jstr=', jstr)


def setFameHall(rankingDefine, issueNum, no1):
    fameHall = loadFameHall(rankingDefine.rankId)
    fameHall.setNo1(issueNum, no1)
    removedItems = fameHall.trim(getConf().fameHallLen)
    saveFameHall(fameHall)
    ftlog.info('dizhu_score_ranking.setFameHall',
               'rankId=', rankingDefine.rankId,
               'issueNum=', issueNum,
               'no1=', no1,
               'removedIssues=', [item.issueNum for item in removedItems])


def getRankRewardsConf(rankId, issueNum, clientId):
    tc = configure.getTcContentByGameId('score.ranklist', None, DIZHU_GAMEID, clientId, None)
    if tc:
        rankRewardsConf = tc.get(rankId)
        if rankRewardsConf:
            return rankRewardsConf.get(issueNum, [])
    return None


def findRankRewardsByRank(rankId, issueNum, clientId, rank):
    '''
    根据期号、clientId、名次查找奖励
    '''
    rankRewardsConf = getRankRewardsConf(rankId, issueNum, clientId)
    if rankRewardsConf:
        for rankReward in rankRewardsConf:
            if rank >= rankReward['begin'] and rank <= rankReward['end']:
                return rankReward
    return None


def clearRankingIssueNum(rankId, issueNum):
    # 删除排行榜
    removeRanklist(rankId, issueNum)


def compareIssueNum(n1, n2):
    return cmp(int(n1), int(n2))


def scoreRankingBiReoprt(rankId, issueNum, userId, rank, score, *arglist, **argdict):
    '''
    排行榜结算的的标准本地日志文件汇报
    @:param rankId: 0 1 对应万元榜 千元榜
    @:param issueNum: 榜单对应的期号
    @:param userId: 玩家userId
    @:param score: 玩家结算时的积分
    @:param rank: 玩家结算时的排行
    @:param arglist:
    @:param argdict:
    '''
    from poker.entity.biz.bireport import _report, reportGameEvent
    alist = [DIZHU_GAMEID, rankId, issueNum, userId, rank, score]
    alist.extend(arglist)
    _report(alist, argdict, 1)
    reportGameEvent('DIZHU_SCORE_RANKLIST_RANK', userId, DIZHU_GAMEID, 0, 0, 0, 0, 0, 0, alist, '')
    #eventId, user_id, gameId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, finalTableChip=0, finalUserChip=0,
    #arglist=[], argdict={}, logtag='game_event'
    if ftlog.is_debug():
        ftlog.debug('scoreRankingBiReoprt userId=', userId,
                    'rankId=', rankId, 'issueNum=', issueNum,
                    'rank=', rank, 'score=', score)


def settlementRanking(rankingDefine, issueNum):
    '''
    给排行榜某一期结算
    @param rankingDefine: 排行榜配置
    @param issueNum: 哪一期结算
    '''
    count = 0
    processCountPerTime = 100
    limit = rankingDefine.rewardLimit
    rank = 0
    no1 = None
    while count < limit:
        stop = min(count + processCountPerTime - 1, limit - 1)
        userIds = getRanklist(rankingDefine.rankId, issueNum, count, stop)
        count = stop + 1
        for userId in userIds:
            rank += 1
            userData = loadUserData(userId, rankingDefine.rankId, issueNum)
            if not userData:
                ftlog.warn('settlementRanking NoUserData',
                           'rankId=', rankingDefine.rankId,
                           'issueNum=', issueNum,
                           'userId=', userId,
                           'rank=', rank)
                continue

            if rank == 1 and not no1:
                no1 = userData

            if userData.rewardState == RewardState.ST_NO_REWARD:
                userData.rewardState = RewardState.ST_HAS_REWARD
                userData.rank = rank
                saveUserData(userData)

                scoreRankingBiReoprt(rankingDefine.rankId, issueNum, userId, rank, userData.score)

                ftlog.info('settlementRanking',
                           'rankId=', rankingDefine.rankId,
                           'issueNum=', issueNum,
                           'userId=', userId,
                           'rank=', rank,
                           'score=', userData.score)

    if ftlog.is_debug():
        ftlog.debug('settlementRanking issueNum=', issueNum, 'rewardLimit=', limit)
    return no1


def processRankings(timestamp=None):
    rankingDefines = _scoreRankConf.rankingDefineMap.values()
    for rankingDefine in rankingDefines:
        processRanking(rankingDefine, timestamp)


def processRanking(rankingDefine, timestamp=None):
    '''
    处理ranking
    1. 该结束的结束
    2. 该发奖的发奖
    3. 过期的期号删除
    '''
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    curIssueNum = calcIssueNum(timestamp)

    rankingInfo = loadRankingInfo(rankingDefine.rankId)

    changed = False
    curItem = rankingInfo.findItem(curIssueNum)
    if not curItem:
        if not _scoreRankConf.closed:
            if ftlog.is_debug():
                ftlog.debug('processRanking curIssueNum=', curIssueNum, 'closed=', _scoreRankConf.closed)
            changed = True
            rankingInfo.addIssue(curIssueNum)

    # 结束/发奖
    for item in rankingInfo.items:
        if ftlog.is_debug():
            ftlog.debug('processRanking item.state=', item.state,
                        'item.issueNum=', item.issueNum,
                        'compareIssueNum=', compareIssueNum(item.issueNum, curIssueNum),
                        'curIssueNum=', curIssueNum)
        if (item.state == ScoreRankingInfo.ST_OPEN
            and compareIssueNum(item.issueNum, curIssueNum) < 0):
            changed = True
            item.state = ScoreRankingInfo.ST_FINISH
            ftlog.info('processRankingInfo finishIssue',
                       'rankId=', rankingInfo.rankId,
                       'issueNum=', item.issueNum,
                       'curIssueNum=', curIssueNum)
            
            # 结算
            no1UserData = settlementRanking(rankingDefine, item.issueNum)
            if no1UserData:
                no1 = {
                    'uid':no1UserData.userId,
                    'score':no1UserData.score,
                    'name':no1UserData.name,
                    'purl':no1UserData.purl,
                }
                setFameHall(rankingDefine, item.issueNum, no1)

            item.state = ScoreRankingInfo.ST_SETTLEMENT
            ftlog.info('processRankingInfo settleIssue',
                       'rankId=', rankingInfo.rankId,
                       'issueNum=', item.issueNum)

    # 删除过期的已经结算的数据
    while rankingInfo.itemCount > (_scoreRankConf.historyLen + 1):
        item = rankingInfo.items[0]
        if item.state == ScoreRankingInfo.ST_SETTLEMENT:
            changed = True
            ftlog.info('processRankingInfo removeIssue',
                       'rankId=', rankingInfo.rankId,
                       'issueNum=', item.issueNum)
            clearRankingIssueNum(rankingInfo.rankId, item.issueNum)
            rankingInfo.items.pop(0)
            break


    if changed:
        saveRankingInfo(rankingInfo)
        ftlog.info('processRankingInfo saveRankingInfo',
                   'rankId=', rankingInfo.rankId,
                   'issues=', [(item.issueNum, item.state) for item in rankingInfo.items])

def removeUserData(userId, rankId, issueNum):
    '''
    删除用户指定排行榜指定期号的数据
    '''
    key = buildUserDataKey(userId, rankId)
    ret = daobase.executeRePlayCmd('hdel', key, issueNum)
    ftlog.info('removeUserData userId=', userId,
               'rankId=', rankId,
               'issueNum=', issueNum,
               'ret=', ret)
    return ret
    
def saveUserData(userData):
    '''
    存储用户数据
    '''
    key = buildUserDataKey(userData.userId, userData.rankId)
    jstr = strutil.dumps(userData.toDict())
    ret = daobase.executeRePlayCmd('hset', key, userData.issueNum, jstr)

    ftlog.info('saveUserData userId=', userData.userId,
               'rankId=', userData.rankId,
               'issueNum=', userData.issueNum,
               'userData=', jstr,
               'ret=', ret)
    return ret

def loadUserData(userId, rankId, issueNum):
    jstr = None
    try:
        key = buildUserDataKey(userId, rankId)
        jstr = daobase.executeRePlayCmd('hget', key, issueNum)
        if ftlog.is_debug():
            ftlog.debug('loadUserData userId=', userId,
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return UserData(userId, rankId, issueNum).fromDict(d)
    except:
        ftlog.error('loadUserData userId=', userId,
                    'rankId=', rankId,
                    'issueNum=', issueNum,
                    'jstr=', jstr)
    return None


def loadOrCreateUserData(userId, rankId, issueNum):
    '''
    加载指定排行榜指定期号的用户数据
    '''
    ret = loadUserData(userId, rankId, issueNum)
    if not ret:
        ret = UserData(userId, rankId, issueNum)
        ftlog.info('dizhu_score_ranking.CreateUserData',
                   'userId=', userId,
                   'rankId=', rankId,
                   'issueNum=', issueNum,
                   'curTime=', pktimestamp.getCurrentTimestamp(),
                   'userData=', ret)
    return ret


def loadUserRankInfo(userId, rankId):
    jstr = None
    try:
        key = buildUserRankInfoKey(userId)
        jstr = daobase.executeRePlayCmd('hget', key, rankId)
        if ftlog.is_debug():
            ftlog.debug('loadUserRankInfo userId=', userId,
                        'rankId=', rankId,
                        'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return UserRankInfo(userId, rankId).fromDict(d)
    except:
        ftlog.error('loadUserRankInfo userId=', userId, 'rankId=', rankId, 'jstr=', jstr)

    return UserRankInfo(userId, rankId)


def saveUserRankInfo(userRankInfo):
    key = buildUserRankInfoKey(userRankInfo.userId)
    jstr = strutil.dumps(userRankInfo.toDict())
    ret = daobase.executeRePlayCmd('hset', key, userRankInfo.rankId, jstr)
    if ftlog.is_debug():
        ftlog.debug('saveUserRankInfo userId=', userRankInfo.userId,
                    'rankId=', userRankInfo.rankId,
                    'jstr=', jstr,
                    'ret=', ret)
    return ret


def removeRanklist(rankId, issueNum):
    key = buildRanklistKey(rankId, issueNum)
    daobase.executeRePlayCmd('del', key)
    ftlog.info('removeRanklist rankId=', rankId, 'issueNum=', issueNum)


def insertRanklist(rankId, issueNum, userId, score, rankLimit):
    assert (rankLimit > 0)
    try:
        key = buildRanklistKey(rankId, issueNum)
        daobase.executeRePlayCmd('zadd', key, score, userId)
        removed = daobase.executeRePlayCmd('zremrangebyrank', str(key), 0, -rankLimit - 1)
        if ftlog.is_debug():
            ftlog.debug('insertRanklist',
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'userId=', userId,
                        'score=', score,
                        'rankLimit=', rankLimit,
                        'removed=', removed)
    except:
        ftlog.error('insertRanklist',
                    'rankId=', rankId,
                    'issueNum=', issueNum,
                    'userId=', userId,
                    'score=', score,
                    'rankLimit=', rankLimit)


def getRanklist(rankId, issueNum, start, stop):
    key = buildRanklistKey(rankId, issueNum)
    return daobase.executeRePlayCmd('zrevrange', key, start, stop)


def getUserRank(userId, rankId, issueNum):
    key = buildRanklistKey(rankId, issueNum)
    rank = daobase.executeRePlayCmd('zrevrank', key, userId)
    if rank is not None:
        return rank + 1
    return -1


def getRanklistWithScore(rankId, issueNum, start, stop):
    ret = []
    try:
        key = buildRanklistKey(rankId, issueNum)
        datas = daobase.executeRePlayCmd('zrevrange', key, start, stop, 'withscores')
        if datas:
            for i in xrange(len(datas) / 2):
                userId = int(datas[i * 2])
                score = int(datas[i * 2 + 1])
                ret.append((userId, score))
        if ftlog.is_debug():
            ftlog.debug('getRanklistWithScore',
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'start=', start,
                        'stop=', stop,
                        'dataLen=', len(datas))
    except:
        ftlog.error('getRanklistWithScore',
                    'rankId=', rankId,
                    'issueNum=', issueNum,
                    'start=', start,
                    'stop=', stop)
    return ret


def removeUserHistory(userRankInfo, keepCount):
    """
    删除用户历史记录
    @param userRankInfo: 用户排行榜信息
    @param keepCount: 保留几期历史
    """
    removeCount = 0
    while (userRankInfo.issueCount > keepCount + 1):
        issueNum = userRankInfo.removeFront()
        ret = removeUserData(userRankInfo.userId, userRankInfo.rankId, issueNum)
        removeCount += ret
        ftlog.info('removeUserHistory userId=', userRankInfo.userId,
                   'rankId=', userRankInfo.rankId,
                   'issueNum=', issueNum,
                   'ret=', ret,
                   'removeCount=', removeCount)
    return removeCount


def updateUserData(userData, rankLimit):
    '''
    更新用户数据同时更新排行榜
    @param userData: 用户数据
    @param rankLimit: 排行榜入榜数量限制
    '''
    userRankInfo = loadUserRankInfo(userData.userId, userData.rankId)
    if userRankInfo.addIssue(userData.issueNum):
        removeUserHistory(userRankInfo, _scoreRankConf.historyLen)
        saveUserRankInfo(userRankInfo)

    saveUserData(userData)
    insertRanklist(userData.rankId, userData.issueNum, userData.userId, userData.score, rankLimit)


def calcUserScore(userId, rankingDefine, playCount, chipDelta, winStreak, vipLevel):
    '''
    根据参数计算积分
    '''
    score = chipDelta * rankingDefine.exchangeRate
    if playCount >= rankingDefine.playCounts:
        score *= rankingDefine.playCountsDecayRate

    # 月卡加成
    monthCardPlus = 0
    if rankingDefine.monthCardItem and UserBag.isHaveAssets(userId, rankingDefine.monthCardItem) and chipDelta > 0:
        monthCardPlus = rankingDefine.monthCardPlus

    # 荣耀月卡加成
    honorCardPlus = 0
    if rankingDefine.honorCardItem and UserBag.isHaveAssets(userId, rankingDefine.honorCardItem) and chipDelta > 0:
        honorCardPlus = rankingDefine.honorCardPlus

    if chipDelta > 0:
        winsPlusRate = rankingDefine.winsPlusRate if winStreak > 1 else 0
        vipPlusRate = rankingDefine.findVipPlusRate(vipLevel)
        score *= (1 + vipPlusRate + winsPlusRate + monthCardPlus + honorCardPlus)
    return int(round(score))


def checkDibaoGainRewardCond(dibaoConf, userData):
    return userData.score >= dibaoConf.score and userData.playCount >= dibaoConf.playCount


def addUserScoreByGiftBox(userId, rankId, scoreDelta, issueNum = None):
    # 礼包增加积分的接口
    issueNum = calcIssueNum() if not issueNum else issueNum
    userData = loadOrCreateUserData(userId, rankId, issueNum)
    userData.score += scoreDelta
    name, purl = userdata.getAttrs(userId, ['name', 'purl'])
    userData.name = '' if name is None else str(name)
    userData.purl = '' if purl is None else str(purl)
    rankingDefine = _scoreRankConf.findRankingDefine(rankId)
    ret = False
    if rankingDefine:
        updateUserData(userData, rankingDefine.rankLimit)
        ret = True
    ftlog.info('addUserScoreByGiftBox userId=', userId,
               'rankId=', rankId,
               'scoreDelta=', scoreDelta,
               'issueNum=', issueNum, 'ret=', ret)
    return ret


def fillScoreRankListInfo(roomId, userId, delta):
    conf = getConf()
    if not conf or conf.closed:
        return None

    bigRoomId = gdata.getBigRoomId(roomId)
    rankConf = conf.rankDefineForRoomId(bigRoomId)
    if not rankConf:
        return None

    clientVer = SessionDizhuVersion.getVersionNumber(userId)
    if clientVer < conf.minVer or rankConf.switch != 1:
        return None

    if rankConf.isOutOfTime():
        return {"open": 0, "info": rankConf.tips}

    issueNum = calcIssueNum()
    userData = loadOrCreateUserData(userId, rankConf.rankId, issueNum)

    # vip积分加成
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel
    vipScoreUp = rankConf.findVipPlusRate(int(vipLevel.level)) if delta > 0 else 0

    # 连胜加成
    winStreak = gamedata.getGameAttrInt(userId, DIZHU_GAMEID, 'winstreak')
    winsPlus = rankConf.winsPlusRate if winStreak > 1 else 0

    # 月卡加成
    monthCardPlus = 0
    if rankConf.monthCardItem and UserBag.isHaveAssets(userId, rankConf.monthCardItem) and delta > 0:
        monthCardPlus = rankConf.monthCardPlus

    # 荣耀月卡加成
    honorCardPlus = 0
    if rankConf.honorCardItem and UserBag.isHaveAssets(userId, rankConf.honorCardItem) and delta > 0:
        honorCardPlus = rankConf.honorCardPlus

    # 金币转换积分的比例
    exchangeRate = rankConf.exchangeRate
    # 胜场积分缩减 后台结算后胜场加1，前端结算积分后胜场已加1，前端展示时取未加1的显示
    decayRate = 1
    todayPlayCount = userData.todayPlayCount - 1 if userData.todayPlayCount > 0 else 0
    if rankConf.playCounts and rankConf.playCountsDecayRate:
        decayRate = rankConf.playCountsDecayRate if todayPlayCount >= rankConf.playCounts else 1

    # 积分结果四舍五入
    scoreUp = (1 + vipScoreUp + winsPlus + monthCardPlus + honorCardPlus) if delta > 0 else 1
    score = int(round(delta * decayRate * exchangeRate * scoreUp))

    rate = [
        {"key": "VIP", "value": vipScoreUp},
        {"key": "月卡", "value": monthCardPlus},
        {"key": "连胜", "value": winsPlus},
        {"key": "荣耀月卡", "value": honorCardPlus}
    ]
    d ={"open": 1,
        "rankId": rankConf.rankId,
        "delta": score,
        "rate": rate,
        "info": rankConf.tips}

    if ftlog.is_debug():
        ftlog.debug('fillScoreRankListInfo roomId=', roomId,
                    'rankId=', rankConf.rankId,
                    'exchangeRate=', exchangeRate,
                    'todayPlayCountDecayRate=', decayRate,
                    'honorCardPlus=', honorCardPlus,
                    'sst.delta=', delta,
                    'global.winStreak=', winStreak,
                    'todayPlayCount=', userData.todayPlayCount,
                    'rate=', rate,
                    'd=', d)
    return d


def updateUserScore(userId, roomId, chipDelta, winStreak, clientId=None, timestamp=None):
    """
    根据chipDelta计算积分并更新用户数据及排行
    """
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    rankingDefine = _scoreRankConf.rankDefineForRoomId(roomId)
    if not rankingDefine:
        if ftlog.is_debug():
            ftlog.debug('updateUserScore NoRankingForRoom',
                        'userId=', userId,
                        'roomId=', roomId,
                        'chipDelta=', chipDelta,
                        'winStreak=', winStreak,
                        'timestamp=', timestamp,
                        'clientId=', clientId)
        return

    issueNum = calcIssueNum(timestamp)
    userData = loadOrCreateUserData(userId, rankingDefine.rankId, issueNum)

    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel

    lastPlayDate = calcTimeStampDate(userData.lastTimeStamp)
    todayDate = calcTimeStampDate(timestamp)
    if todayDate > lastPlayDate:
        userData.todayPlayCount = 0
        ftlog.info('rankingInfoDailyLog userId=', userId,
                   'roomId=', roomId,
                   'rankId=', rankingDefine.rankId,
                   'issueNum=', issueNum,
                   'userInfo=', userData.toDict())

    userData.lastTimeStamp = timestamp

    scoreDelta = calcUserScore(userId, rankingDefine, userData.todayPlayCount, chipDelta, winStreak, vipLevel.level)

    # 结算时玩家积分修改
    userData.score = int(max(0, userData.score + scoreDelta))
    userData.playCount += 1
    userData.todayPlayCount += 1
    
    if (rankingDefine.dibaoConf
        and userData.dibaoRewardState == RewardState.ST_NO_REWARD
        and checkDibaoGainRewardCond(rankingDefine.dibaoConf, userData)):
        userData.dibaoRewardState = RewardState.ST_HAS_REWARD
        ftlog.info('updateUserScore.userDiBaoSatisfied userId=', userId,
                   'rankId=', rankingDefine.rankId, 'issueNum=', issueNum,
                   'score=', userData.score,
                   'rewardState=', userData.dibaoRewardState)

    name, purl = userdata.getAttrs(userId, ['name', 'purl'])
    userData.name = '' if name is None else str(name)
    userData.purl = '' if purl is None else str(purl)

    if ftlog.is_debug():
        ftlog.debug('updateUserScore',
                    'userId=', userId,
                    'roomId=', roomId,
                    'chipDelta=', chipDelta,
                    'winStreak=', winStreak,
                    'timestamp=', timestamp,
                    'issueNum=', issueNum,
                    'scoreDelta=', scoreDelta,
                    'playCount=', userData.playCount,
                    'todayPlayCount=', userData.todayPlayCount,
                    'userName=', userData.name if userData.name else 'error',
                    'userPurl=', userData.purl if userData.purl else 'error')

    updateUserData(userData, rankingDefine.rankLimit)


def gainUserRanklistReward(userId, rankId, issueNum, clientId=None):
    # 发放周榜奖励
    userData = loadUserData(userId, rankId, issueNum)
    if not userData:
        raise TYBizException(-1, '没有找到用户数据')

    if userData.rewardState == RewardState.ST_NO_REWARD:
        raise TYBizException(-1, '本期没有奖励可领取')

    if userData.rewardState == RewardState.ST_GAIN_REWARD:
        raise TYBizException(-1, '已经领取了奖励')

    clientId = clientId or sessiondata.getClientId(userId)
    rankRewards = findRankRewardsByRank(rankId, issueNum, clientId, userData.rank)
    if not rankRewards:
        if ftlog.is_debug():
            ftlog.debug('gainUserRanklistReward rankReward is None. userId=', userId,
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'clientId=', clientId)
        # TODO warn or error
        raise TYBizException(-1, '未取到对应奖励配置')

    userData.rewardState = RewardState.ST_GAIN_REWARD
    saveUserData(userData)

    contentItems = TYContentItem.decodeList(rankRewards.get('items'))
    assetList = dizhu_util.sendRewardItems(userId, contentItems, _scoreRankConf.rewardMail, 'DIZHU_SCORE_RANKLIST', int(rankId))
    
    ftlog.info('gainUserRanklistReward',
               'userId=', userId,
               'rankId=', rankId,
               'issueNum=', issueNum,
               'rank=', userData.rank,
               'rewards=', [(atp[0].kindId, atp[1]) for atp in assetList])
    return assetList


def gainDibaoReward(userId, rankId, issueNum):
    # 发放低保奖励
    rankingDefine = _scoreRankConf.findRankingDefine(rankId)
    if not rankingDefine:
        raise TYBizException(-1, '排行榜不存在')

    userData = loadUserData(userId, rankId, issueNum)

    if not userData or not rankingDefine.dibaoConf:
        raise TYBizException(-1, '没有奖励可以领取')

    if userData.dibaoRewardState == RewardState.ST_NO_REWARD:
        raise TYBizException(-1, '没有奖励可以领取')

    if userData.dibaoRewardState == RewardState.ST_GAIN_REWARD:
        raise TYBizException(-1, '已经领取了奖励')
    
    if (userData.score >= rankingDefine.dibaoConf.score
        and userData.playCount >= rankingDefine.dibaoConf.playCount
        and rankingDefine.dibaoConf.rewardItems):
        userData.dibaoRewardState = RewardState.ST_GAIN_REWARD
        saveUserData(userData)

        ftlog.info('gainDibaoReward dibaoReward Sended. userId=', userData.userId,
                   'rankId=', rankId,
                   'issueNum=', issueNum,
                   'rewardItems=', rankingDefine.dibaoConf.rewardItems)
        return dizhu_util.sendRewardItems(userId, rankingDefine.dibaoConf.rewardItems, rankingDefine.dibaoConf.rewardMail, 'DIZHU_SCORE_RANKLIST_DIBAO', int(rankId))
        
    raise TYBizException(-1, '没有奖励可以领取')


def findRankingDefine(rankId):
    return _scoreRankConf.findRankingDefine(rankId)


_inited = False
_prevProcessRankingTime = 0
_processRankingInterval = 10


def _reloadConf():
    global _scoreRankConf
    d = configure.getGameJson(DIZHU_GAMEID, 'score.ranklist', {}, 0)
    conf = ScoreRankConf().decodeFromDict(d)
    _scoreRankConf = conf
    ftlog.info('dizhu_score_ranking._reloadConf successed',
               'rankIds=', _scoreRankConf.rankingDefineMap.keys())

def _onConfChanged(event):
    if _inited and event.isChanged('game:6:score.ranklist:0'):
        ftlog.debug('dizhu_score_ranking._onConfChanged')
        _reloadConf()


def _onOpenItemEvent(event):
    # TYOpenItemEvent(gameId, userBag.userId, item, assetItemList)
    if _scoreRankConf.closed:
        return
    userName = userdata.getAttrs(event.userId, ['name'])[0]
    boxName = event.item.itemKind.displayName
    for assetItemTuple in event.gotAssetList:
        # 0 - assetItem, 1 - count, 2 - final
        assetItem = assetItemTuple[0]
        if assetItem.kindId in _scoreRankConf.ledItems:
            # 冠军发送Led通知所有其他玩家
            ledText = dizhuled._mk_open_box_rich_text(
                userName,
                boxName,
                assetItem.displayName
            )
            LedUtil.sendLed(ledText, 'global')

def getConf():
    return _scoreRankConf


def _initialize(isCenter):
    ftlog.debug('dizhu_score_ranking._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        subscribeScoreRankList()
        TGHall.getEventBus().subscribe(TYOpenItemEvent, _onOpenItemEvent)
        if isCenter:
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)

    ftlog.debug('dizhu_score_ranking._initialize end')


def onTimer(evt):
    global _prevProcessRankingTime
    timestamp = pktimestamp.getCurrentTimestamp()
    if not _prevProcessRankingTime or timestamp - _prevProcessRankingTime > _processRankingInterval:
        _prevProcessRankingTime = timestamp
        processRankings(timestamp)


def subscribeScoreRankList():
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, _fillUpdateUserScore)


def _fillUpdateUserScore(event):
    from poker.entity.dao import gamedata
    winStreak = gamedata.getGameAttrInt(event.userId, DIZHU_GAMEID, 'winstreak')
    bigRoomId = gdata.getBigRoomId(event.roomId)

    if not _scoreRankConf:
        return False

    if ftlog.is_debug():
        ftlog.debug('_fillUpdateUserScore userId=', event.userId,
                    'bigRoomId=', bigRoomId,
                    '_scoreRankConf=', _scoreRankConf,
                    'closed=', _scoreRankConf.closed)

    if _scoreRankConf.closed:
        return False

    clientVer = SessionDizhuVersion.getVersionNumber(event.userId)
    if clientVer < _scoreRankConf.minVer:
        if ftlog.is_debug():
            ftlog.debug('_fillUpdateUserScore version too low. userId=', event.userId,
                        'clientVer=', clientVer,
                        'minVer=', _scoreRankConf.minVer)
        return False

    if ftlog.is_debug():
        ftlog.debug('_fillUpdateUserScore userId=', event.userId, 'clientVer=', clientVer)

    rankingDefine = _scoreRankConf.rankDefineForRoomId(bigRoomId)
    if not rankingDefine:
        if ftlog.is_debug():
            ftlog.debug('_fillUpdateUserScore NoRankingForRoom userId=', event.userId,
                        'roomId=', event.roomId,
                        'chipDelta=', event.winlose.deltaChip,
                        'winStreak=', winStreak)
        return False

    timestamp = pktimestamp.getCurrentTimestamp()
    if rankingDefine.isOutOfTime(timestamp):
        if ftlog.is_debug():
            ftlog.debug('_fillUpdateUserScore outOfTime userId=', event.userId,
                        'roomId=', event.roomId,
                        'curTimeStamp=', timestamp)
        return False

    updateUserScore(event.userId, bigRoomId, event.winlose.deltaChip, winStreak)