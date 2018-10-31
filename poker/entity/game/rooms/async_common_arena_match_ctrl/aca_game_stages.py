# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的轮次/阶段对象们
@author: zhaol

{
    "index": 1,
    "base_chip": 10,
    "cardCount": 1,
    "name": "128进64",
    "riseUserCount": 64,
    "scoreInit": 0,
    "scoreIntoRate": 1,
    "totalUserCount": 128
}

"""
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_game_stage import AsyncCommonArenaStage
import poker.util.timestamp as pktimestamp

class AsyncCommonArenaStages(object, ):
    """
    快速赛比赛阶段s
    """

    def __init__(self):
        pass

    @property
    def stages(self):
        """
        所有的比赛阶段
        """
        pass

    def setStages(self, stages):
        pass

    def initConfig(self, config):
        """
        根据配置初始化比赛阶段
        """
        pass

    def getStage(self, index):
        """
        根据索引获取比赛阶段
        """
        pass

    def getFirstStageIndex(self):
        """
        获取第一个比赛阶段的索引
        """
        pass

    def getFirstStage(self):
        """
        获取第一阶段
        """
        pass

    def getLastStageIndex(self):
        """
        获取最后一个赛段的索引
        """
        pass

    def getInitScore(self):
        """
        获取本场比赛的初始积分
        """
        pass

    def getNextStage(self, stageIndex):
        """
        获取下一个赛段
        """
        pass

    def findStageByIndex(self, stageIndex):
        """
        根据index查找赛制阶段
        """
        pass

    def getBaseChip(self):
        """
        获取底注
        """
        pass

    def getCardCount(self):
        """
        获取每个赛段的局数
        """
        pass

    def getTotalUserCount(self):
        """
        获取比赛的参赛人数
        """
        pass

    def getDesc(self):
        """
        获取阶段描述
        """
        pass

    def setMatchId(self, matchId):
        """
        设置比赛ID
        """
        pass

    def deltaTick(self, delta):
        """
        定期保存每轮次的输赢记录
        """
        pass
if (__name__ == '__main__'):
    pass