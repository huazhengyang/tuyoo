# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的玩家对象
@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.dao import gamedata, userdata
import time

class AsyncUpgradeHeroMatchPlayer(object, ):
    STATE_NONE = 0
    STATE_TABLE_PLAYING = 1
    STATE_WAIT_NEXT = 2
    STATE_BEGIN_CHALLENGE = 3
    STATE_WAIT_BACK = 4
    STATE_GAME_OVER = 5
    STATE_GAME_WIN = 6

    def __init__(self):
        pass

    def canSave(self):
        """
        是否可以保存比赛进度
        """
        pass

    @property
    def gameFlow(self):
        pass

    def setGameFlow(self, gameFlow):
        pass

    def canGiveUp(self):
        """
        是否可以退赛
        """
        pass

    def giveUp(self):
        """
        退赛
        """
        pass

    def signIn(self, firstStageIndex):
        """
        报名成功
        """
        pass

    def resetTableInfo(self):
        """
        充值牌桌信息
        """
        pass

    def challengeSucc(self, nextStageIndex, gameId):
        """
        闯关成功
        :param nextStageIndex:   下一关 index
        :param gameId:
        """
        pass

    def gameWin(self):
        """
        比赛胜利
        """
        pass

    def playerGameFlow(self):
        """
        游戏流局
        阶段不涨，继续打当前的阶段
        """
        pass

    def challengeFail(self, canBack, canBackToNext, gameId):
        """
        闯关失败
        """
        pass

    def playerBack(self):
        """
        玩家复活
        """
        pass

    def playerPlaying(self, roomId, tableId):
        """
        玩家进入牌桌
        """
        pass

    def playerChallenge(self):
        """
        玩家开始挑战
        """
        pass

    def isPlayerChanllengingOrPlaying(self):
        """
        用户是否在挑战
        """
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