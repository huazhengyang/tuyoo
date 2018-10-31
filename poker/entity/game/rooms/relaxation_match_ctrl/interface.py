# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""

class MatchRewards(object, ):

    def sendRewards(self, player, rankRewards):
        """

        """
        pass

class TableController(object, ):

    def notifyTableSendQuickStart(self, table, player):
        """
        发送快速开始，并将该用户置为在该桌子上
        """
        pass

    def notifyTableClearTable(self, table):
        """
        清理桌子
        """
        pass

    def notifyUpdateMatchInfo(self, table):
        """
        通知桌子，比赛信息改变
        """
        pass

    def notifyMatchOver(self, table):
        """
        通知桌位上还有玩家的桌子，比赛已经结束
        """
        pass

class PlayerNotifier(object, ):

    def notifyMatchOver(self, player, rankRewards):
        """
        通知用户比赛结束了
        """
        pass

    def notifyMatchRank(self, player):
        """
        通知比赛排行榜
        """
        pass

    def notifyMatchRankGuest(self, userId):
        """
        通知比赛排行榜,非参赛玩家
        """
        pass

class PlayerSortApi(object, ):

    def cmpByScore(self, p1, p2):
        """
        比赛过程临时排名api
        """
        pass

    def overCmpByScore(self, p1, p2):
        """
        比赛结束后最终排名api
        """
        pass