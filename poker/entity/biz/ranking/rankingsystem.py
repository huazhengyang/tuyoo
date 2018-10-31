# -*- coding: utf-8 -*-
"""
Created on 2015年4月13日

@author: zhaojiangang
"""
from datetime import date, datetime
import json
from sre_compile import isstring
import time
import freetime.util.log as ftlog
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.ranking.dao import TYRankingUserScoreInfo
from poker.entity.biz.ranking.exceptions import TYRankingConfException, TYRankingUnknownException
import poker.util.timestamp as pktimestamp
_DEBUG = 0
debug = ftlog.info

class TYTimeCycle(object, ):

    def __init__(self, startTime, endTime):
        pass

    def inCycle(self, nt):
        pass

    def buildIssueNumber(self):
        pass

class TYRankingInputTypes:
    CHIP = 'chip'
    DASHIFEN = 'dashifen'
    DASHIFEN_INCR = 'dashifen_incr'
    WINCHIP = 'winChip'
    PK = 'pk'
    CHARM = 'charm'
    DZFCWINCHIP = 'dzfcWinChip'
    FANTASY = 'fantasy'
    TOPHANDSSCORE = 'topHandsScore'
    OPI = 'opi'
    JIFEN = 'jifen'
    MTT = 'mtt'
    SNG = 'sng'
    MTTSNG = 'mttsng'
    WINCHIP_DRAGON = 'winchip_dragon'
    CHIP_DRAGON = 'chip_dragon'
    CHARM_DRAGON = 'charm_dragon'
    COUPON_BAOHUANG = 'coupon_baohuang'
    CHAMPION_BAOHUANG = 'champion_baohuang'
    INVITE_BAOHUANG = 'invite_baohuang'
    MAJIANG_LUKY_RAFFLE = 'majiang_luky_raffle'
    MAJIANG_TABLE_RAFFLE = 'majiang_table_raffle'
    VIP_CLOWN = 'vip_clown'
    CHIP_CLOWN = 'chip_clown'
    WINCHIP_CLOWN = 'winchip_clown'
    TRACTOR_TG = 'tractor_tg'
    EXP = 'exp'

class TYRankingOpTypes:
    NORMAL = 'normal'
    INCR = 'incr'
    MAX = 'max'
    TYPES = set([NORMAL, INCR, MAX])
    NEED_RECORD_SCORE_TYPES = set([INCR, MAX])

class TYRankingCycle(TYConfable, ):

    def __init__(self, startTime=0, endTime=0):
        pass

    def getCurrentCycle(self, timestamp=None):
        """
        @param nt: 当前时间戳
        @return: TYTimeCycle
        """
        pass

    def inCollectCycle(self, timeCycle, timestamp):
        pass

    def decodeFromDict(self, d):
        pass

    def _getCurrentCycle(self, timestamp):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYRankingCycleDay(TYRankingCycle, ):
    TYPE_ID = 'day'

    def __init__(self, startTime=0, endTime=0):
        pass

    def _getCurrentCycle(self, timestamp):
        pass

class TYRankingCycleWeek(TYRankingCycle, ):
    TYPE_ID = 'week'

    def __init__(self, startTime=0, endTime=0):
        pass

    def _getCurrentCycle(self, timestamp):
        pass

class TYRankingCycleMonth(TYRankingCycle, ):
    TYPE_ID = 'month'

    def __init__(self, startTime=0, endTime=0):
        pass

    def _getCurrentCycle(self, timestamp):
        pass

class TYRankingCycleLife(TYRankingCycle, ):
    TYPE_ID = 'life'

    def __init__(self, startTime=0, endTime=0):
        pass

    def _getCurrentCycle(self, timestamp):
        pass

class TYRankingCycleRegister(TYConfableRegister, ):
    _typeid_clz_map = {TYRankingCycleDay.TYPE_ID: TYRankingCycleDay, TYRankingCycleWeek.TYPE_ID: TYRankingCycleWeek, TYRankingCycleMonth.TYPE_ID: TYRankingCycleMonth, TYRankingCycleLife.TYPE_ID: TYRankingCycleLife}

class TYRankingRankReward(object, ):

    def __init__(self):
        pass

    @classmethod
    def decodeFromDict(self, d):
        pass

class TYRankingStatus(object, ):
    STATE_NORMAL = 0
    STATE_FINISH = 1
    STATE_REWARDS = 2

    class Item(object, ):

        def __init__(self, issueNumber, timeCycle, state):
            pass

    def __init__(self, rankingDefine, totalNumber, historyList):
        pass

    def getLastItem(self):
        pass

    def addItem(self, issueNumber, timeCycle):
        pass

    def count(self):
        pass

    def removeFront(self):
        pass

class TYRankingScoreCalc(TYConfable, ):

    def calcScore(self, oldScore, opScore):
        """
        根据老的socre和当前操作的score
        """
        pass

    def decodeFromDict(self, d):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYRankingScoreCalcRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYRankingDefine(TYConfable, ):

    def __init__(self):
        pass

    def getPicByRank(self, rank):
        pass

    def isSupportGameId(self, gameId):
        pass

    def isSupportInputType(self, inputType):
        pass

    def isSupport(self, gameId, inputType):
        pass

    def getCurrentIssueNumber(self, timestamp=None):
        pass

    def inCollectCycle(self, timeCycle, nt):
        pass

    def getCurrentCycle(self, timestamp=None):
        pass

    def getRewardsByRank(self, rank):
        pass

    def getHasRewardMaxRank(self):
        pass

    def decodeFromDict(self, d):
        pass

class TYRankingUser(object, ):

    def __init__(self, userId, score, rank):
        pass

class TYRankingList(object, ):

    def __init__(self, rankingDefine, issueNumber, timeCycle, rankingUserList):
        pass

class TYRankingSystem(object, ):

    def getRankingDefines(self):
        """
        获取所有排行榜配置
        @return list<TYRankingDefine>
        """
        pass

    def getRankingDefinesForRankingKey(self, rankingKey, templateName):
        """
        获取rankingKey下的tempateName包含的排行榜配置
        @return: list<TYRankingDefine>
        """
        pass

    def processRankings(self, timestamp=None):
        """
        处理所有的排行榜，改创建的创建，改发奖的发奖
        """
        pass

    def findRankingDefine(self, rankingId):
        """
        查找rankingId的排行榜配置
        """
        pass

    def setUserByInputType(self, gameId, inputType, userId, score, timestamp=None):
        """
        更新所有能处理inputType和gameId的排行榜中指定用户的信息
        @return: map<rankingId, rankingUser>
        """
        pass

    def removeUserByInputType(self, gameId, inputType, userId, timestamp=None):
        """
        删除所有能处理inputType的排行榜中指定用户的信息
        """
        pass

    def setUserScore(self, rankingId, userId, score, timestamp=None):
        """
        更新排行榜中指定用户的信息
        @param rankingId: 排行榜ID
        @param rankingUser: 排行榜用户
        @param nt: 用户记录的时间戳，如果为None则用当前时间戳
        @return: TYRankingUser
        """
        pass

    def removeUser(self, rankingId, userId, timestamp=None):
        """
        删除排行榜中userId的用户
        @param rankingId: 排行榜ID
        @param userId: 要删除的用户ID
        @param nt: 时间戳
        """
        pass

    def removeRanking(self, rankingId):
        """
        删除排行榜
        @param rankingId: 要删除的排行榜ID 
        """
        pass

    def getTopN(self, rankingId, topN=None, timestamp=None):
        """
        获取nt所在期排行榜topN用户ID列表
        @param rankingId: 排行榜ID
        @param topN: topN的数量，如果是None表示按照配置的topN返回
        @param nt: 当前时间戳
        @return: TYRankingList or None
        """
        pass

    def getRankingUser(self, rankingId, userId, timestamp=None):
        """
        获取nt所在期排行榜中userId的信息
        @param rankingId: 排行榜ID
        @param topN: topN的数量，如果是None表示按照配置的topN返回
        @param nt: 当前时间戳
        @return: TYRankingUser or None
        """
        pass

class TYRankingSystemImpl(TYRankingSystem, ):

    def __init__(self, scoreInfoDao, rankingDao, rewardSender):
        pass

    def reloadConf(self, conf):
        pass

    def getRankingDefinesForRankingKey(self, rankingKey, templateName):
        """
        获取rankingKey下的tempateName包含的排行榜配置
        @return: list<TYRankingDefine>
        """
        pass

    def getRankingDefines(self):
        """
        获取所有排行榜配置
        return list<TYRankingDefine>
        """
        pass

    def processRankings(self, timestamp=None):
        """
        处理所有的排行榜，改创建的创建，改发奖的发奖
        """
        pass

    def findRankingDefine(self, rankingId):
        """
        查找rankingId的排行榜配置
        """
        pass

    def setUserByInputType(self, gameId, inputType, userId, score, timestamp=None):
        """
        更新所有能处理inputType和gameId的排行榜中指定用户的信息
        @return: map<rankingId, rankingUser>
        """
        pass

    def removeUserByInputType(self, gameId, inputType, userId, timestamp=None):
        """
        删除所有能处理inputType的排行榜中指定用户的信息
        """
        pass

    def setUserScore(self, rankingId, userId, score, timestamp=None):
        """
        更新排行榜中指定用户的信息
        @param rankingId: 排行榜ID
        @param rankingUser: 排行榜用户
        @param nt: 用户记录的时间戳，如果为None则用当前时间戳
        @return: TYRankingUser
        """
        pass

    def removeUser(self, rankingId, userId, timestamp=None):
        """
        删除排行榜中userId的用户
        @param rankingId: 排行榜ID
        @param userId: 要删除的用户ID
        @param nt: 时间戳
        """
        pass

    def removeRanking(self, rankingId):
        """
        删除排行榜
        @param rankingId: 要删除的排行榜ID 
        """
        pass

    def getTopN(self, rankingId, topN=None, timestamp=None):
        """
        获取nt所在期排行榜topN用户ID列表
        @param rankingId: 排行榜ID
        @param topN: topN的数量，如果是None表示按照配置的topN返回
        @param nt: 当前时间戳
        @return: TYRankingList or None
        """
        pass

    def getRankingUser(self, rankingId, userId, timestamp=None):
        """
        获取nt所在期排行榜中userId的信息
        @param rankingId: 排行榜ID
        @param topN: topN的数量，如果是None表示按照配置的topN返回
        @param nt: 当前时间戳
        @return: TYRankingUser or None
        """
        pass

    def _processRanking(self, rankingDefine, timestamp):
        pass

    def _setUserByRankingDefine(self, rankingDefine, userId, score, timestamp):
        pass

    def _getRankingUserByRankingDefine(self, rankingDefine, issueNumber, userId):
        pass

    def _removeUserByRankingDefine(self, rankingDefine, userId, nt=None):
        pass

    def _getTopNByRankingDefine(self, rankingDefine, issueNumber, topN):
        pass

    def _loadOrCreateRankingStatus(self, rankingDefine, nt):
        pass

    def _loadRankingStatus(self, rankingDefine):
        pass

    def _saveRankingStatus(self, status):
        pass

    def _doReward(self, status, item):
        pass

    def _sendReward(self, status, item, rankingUser):
        pass