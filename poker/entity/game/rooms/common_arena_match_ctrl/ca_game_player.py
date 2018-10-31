# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的玩家对象
@author: zhaol

"""
from freetime.util import log as ftlog

class CommonArenaPlayer(object, ):
    STATE_SIGNIN = 0
    STATE_WAIT = 1
    STATE_PLAYING = 2
    STATE_WINLOSE = 3
    STATE_RISE = 4
    STATE_OVER = 5

    def __init__(self):
        pass

    @property
    def score(self):
        """
        比赛积分
        """
        pass

    def setScore(self, score):
        pass

    @property
    def roomId(self):
        pass

    def setRoomId(self, roomId):
        pass

    @property
    def tableId(self):
        """
        比赛时候的牌桌ID
        """
        pass

    def setTableId(self, tableId):
        pass

    @property
    def waitTime(self):
        """
        进入队列的等待时间
        """
        pass

    def setWaitTime(self, time):
        pass

    def deltaWaitTime(self, delta):
        """
        改变等待时间
        """
        pass

    @property
    def isGiveUp(self):
        """
        弃赛
        """
        pass

    def setGiveUp(self, giveUp):
        pass

    @property
    def state(self):
        """
        用户比赛状态
        """
        pass

    def setState(self, state):
        pass

    def getObject(self):
        """
        获取player的对象
        """
        pass

    @property
    def enterTime(self):
        """
        用户进入比赛时间
        """
        pass

    def setEnterTime(self, eTime):
        pass

    @property
    def signFee(self):
        """
        用户进入比赛的报名费
        
        报名费不符合条件的进不来
        """
        pass

    def setSignFee(self, fee):
        pass

    @property
    def stageIndex(self):
        """
        当前比赛阶段/轮次
        """
        pass

    def setStageIndex(self, index):
        pass

    @property
    def userId(self):
        """
        用户ID
        """
        pass

    def setUserId(self, userId):
        pass

    @property
    def matchId(self):
        """
        比赛ID，用户统计，及区分混房的不同比赛
        """
        pass

    def setMatchId(self, matchId):
        pass

    @property
    def rank(self):
        """
        比赛名次
        """
        pass

    def setRank(self, rank):
        pass

    @property
    def rankName(self):
        """
        比赛排名字符串描述
        """
        pass

    def setRankName(self, name):
        pass