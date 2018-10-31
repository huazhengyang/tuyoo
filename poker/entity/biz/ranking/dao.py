# -*- coding: utf-8 -*-
"""
Created on 2015年7月2日

@author: zhaojiangang
"""

class TYRankingUserScoreInfo(object, ):

    def __init__(self, score=None, issueNumber=None):
        pass

class TYRankingUserScoreInfoDao(object, ):

    def loadScoreInfo(self, rankingId, userId):
        """
        获取用户的scoreInfo
        """
        pass

    def saveScoreInfo(self, rankingId, userId, scoreInfo):
        """
        保存用户的scoreInfo
        """
        pass

class TYRankingDao(object, ):

    def loadRankingStatusData(self, rankingId):
        """
        加载ranking信息
        """
        pass

    def removeRankingStatus(self, rankingId):
        """
        删除ranking信息
        """
        pass

    def saveRankingStatusData(self, rankingId, data):
        """
        保存ranking信息
        """
        pass

    def removeRankingList(self, rankingId, issueNumber):
        """
        删除raking榜单
        """
        pass

    def setUserScore(self, rankingId, issueNumber, userId, score, totalN):
        """
        设置用户积分
        @return: rank
        """
        pass

    def removeUser(self, rankingId, issueNumber, userId):
        """
        删除用户
        """
        pass

    def getUserRankWithScore(self, rankingId, issueNumber, userId):
        """
        获取用户排名和积分
        @return: (rank, score)
        """
        pass

    def getTopN(self, rankingId, issueNumber, topN):
        """
        获取topN
        @return: [userId1, score1, userId2, score2,...] 
        """
        pass