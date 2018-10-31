# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛报名费

@author: zhaol

"""
from freetime.entity.msg import MsgPack
from poker.protocol import router
from datetime import datetime
import time
from poker.entity.configure import gdata
from random import choice
from freetime.util import log as ftlog
from poker.entity.dao import userdata

class AsyncCommonArenaMessage(object, ):

    def __init__(self):
        pass

    def init(self, gameId, roomId, matchId):
        """
        初始化
        """
        pass

    @property
    def gameId(self):
        pass

    def setGameId(self, gameId):
        pass

    @property
    def roomId(self):
        pass

    def setRoomId(self, roomId):
        pass

    @property
    def matchId(self):
        pass

    def setMatchId(self, matchId):
        pass

    def matchChallengeFail(self, userId, matchId, code, info):
        """
        比赛报名成功
        """
        pass

    def matchChallengeSucc(self, userId, matchId):
        """
        比赛报名成功
        """
        pass

    def matchSignInSucc(self, userId):
        """
        比赛报名成功
        """
        pass

    def matchSignOutSucc(self, userId):
        """
        比赛报名成功
        """
        pass

    def matchBackFail(self, userId, code, info):
        """
        回到比赛失败
        """
        pass

    def matchReviveSucc(self, userId):
        """
        比赛复活成功
        """
        pass

    def matchReviveFail(self, userId, code, info):
        """
        比赛复活成功
        """
        pass

    def matchResumeFail(self, userId, code, info):
        """
        比赛保存成功
        """
        pass

    def matchSignInFail(self, userId, code, info, loc=''):
        """
        比赛报名成功
        """
        pass

    def matchSignOutFail(self, userId, code, info):
        """
        比赛报名成功
        """
        pass

    def matchEnterSucc(self, userId):
        """
        比赛报名成功
        """
        pass

    def matchDes(self, userId, name, desc, feesDes, ranksDes, stagesDes, his, condition, timeRange, matchIntroduce, saveInfo):
        """
        获取比赛详情
        """
        pass

    def matchTableClear(self, tableId):
        """
        解散牌桌
        """
        pass

    def matchTableStart(self, baseChip, cardCount, riseCount, users):
        """
        比赛报名成功
        """
        pass

    def matchUserGiveup(self, users, shadowRoomId, tableId):
        """
        比赛报名成功
        """
        pass

    def matchSaveFail(self, userId, code, info):
        """
        比赛保存成功
        """
        pass

    def matchSaveSucc(self, userId, matchId, saveInfo):
        """
        比赛保存成功
        """
        pass

    def _isNewUser(self, userId):
        """
        是否是新用户,创建时间在 24 小时以内的算新用户
        """
        pass

    def matchUpdateWait(self, userId, stageIndex, rank, rankName, isLevelUp, cardCount, tableRank, state, reConnect=False):
        """
        比赛报名成功
        """
        pass

    def matchAdjustRank(self, userId, stageIndex, rank, rankName):
        """
        比赛报名成功
        """
        pass

    def matchGiveUpSucc(self, userId):
        """
        比赛报名成功
        """
        pass

    def matchGiveUpFail(self, userId, code, info):
        """
        比赛报名成功
        """
        pass

    def matchOver(self, userId, rank, info, winLoose, rewardDesc, matchName, matchUserCount, rewardInfo=[], feeIndex=0):
        """
        比赛报名成功
        """
        pass

    def createMsgPackResult(self, cmd, action=None):
        """

        """
        pass
if (__name__ == '__main__'):
    pass