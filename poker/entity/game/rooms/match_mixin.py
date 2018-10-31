# -*- coding: utf-8 -*-
"""

"""
import json
from datetime import date, datetime
import time
from datetime import timedelta
from freetime.util.cron import FTCron
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
import copy
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import userchip, sessiondata, daobase, userdata
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.util import strutil
from poker.util import tools
from poker.entity.game.plugin import TYPluginCenter

class TYMatchMixin(object, ):
    """

    """
    CACHED_RANK_LIST_N = 100
    MATCH_STATE_IDLE = 0
    MATCH_STATE_READY = 1
    MATCH_STATE_SIGNIN = 2
    MATCH_STATE_CHECK_START = 4
    MATCH_STATE_START = 5
    MATCH_STATE_FINAL = 6
    matchStateStrs = {MATCH_STATE_IDLE: 'IDLE', MATCH_STATE_READY: 'READY', MATCH_STATE_SIGNIN: 'SIGNIN', MATCH_STATE_START: 'START', MATCH_STATE_FINAL: 'FINAL'}

    def getStateStr(self):
        pass

    def playingRankingKey(self):
        """

        """
        pass

    def clearPlayingRanking(self):
        pass

    def getRank(self, userId):
        """

        """
        pass

    def getScore(self, userId):
        pass

    def incrScore(self, userId, scoreDelta):
        pass

    def getPlayingPlayersN(self):
        pass

    def getPlayingRankList(self, withScore=True):
        pass

    def zhanKuangKey(self):
        """

        """
        pass

    def clearZhanKuang(self):
        pass

    def getZhanKuang(self, userId):
        pass

    def setZhanKuang(self, userId, zhanKuangDict):
        pass

    def needCancelMatchTimedelta(self):
        pass

    def setMatchStateReady(self):
        """

        """
        pass

    def initRankCache(self):
        pass

    def initMatch(self):
        pass

    def _getMatchStartTimesKey(self):
        """

        """
        pass

    def getMatchStartTime(self):
        pass

    def getMatchEndTime(self, startTimeStamp=0):
        pass

    def getSigninTime(self, startTimeStamp=0):
        """
        获取可报名时间段配置。
        配置项为 matchConf 中的 timeConf 里的
            signinBeforeStart
            signinBeforeEnd
        如果未配置或配置了0，则使用当前时间~比赛结束
        """
        pass

    def refreshMatchConf(self):
        pass

    def calcNextStartTime(self, timestamp=None):
        pass

    def refreshMatchStartTime(self, matchMinutes=60):
        pass

    def cacheRankList(self):
        pass

    def _isMatchClosed(self):
        pass

    def _makeMatchStartTimeDesc(self, start_timestamp, connector='%n'):
        pass

    def _getRewardAndDesc(self, rankingOrder):
        """

        """
        pass

    def prepareNewMatch(self):
        pass

    def cancelMatch(self, isRestart=False, rankList=None):
        pass

    def stopMatch(self):
        pass

    def checkStartMatch(self):
        pass

    def doGetMatchStatus(self, userId):
        pass

    def doGetDescription(self, userId):
        pass

    def doGetRankList(self, userId, msg):
        pass

    def doSignin(self, userId, signinParams):
        pass

    def doSignout(self, userId):
        pass

    def rewardWinners(self, rankList=None):
        pass