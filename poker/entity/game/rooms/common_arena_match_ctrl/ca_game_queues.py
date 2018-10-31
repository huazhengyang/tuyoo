# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛所有的队列/班车s

@author: zhaol

"""
from poker.entity.game.rooms.common_arena_match_ctrl.ca_game_queue import CommonArenaQueue
from poker.entity.game.rooms.common_arena_match_ctrl.ca_game_player import CommonArenaPlayer
from freetime.util import log as ftlog

class CommonArenaQueues(object, ):
    """
    快速赛比赛阶段s
    """

    def __init__(self):
        pass

    @property
    def firstQueue(self):
        """
        首轮队列
        """
        pass

    def setFirstQueue(self, queue):
        pass

    @property
    def otherQueue(self):
        """
        其他轮次队列
        """
        pass

    def setOtherQueue(self, queue):
        pass

    def initConfig(self, config):
        """
        初始化
        """
        pass

    def addPlayer(self, player, firstIndex):
        """
        比赛玩家添加到队列中
        """
        pass

    def removePlayer(self, player, firstIndex):
        """
        清除玩家
        """
        pass

    def setTableMaxSeat(self, maxSeat):
        """
        设置每桌人数
        """
        pass

    def deltaTick(self, tick):
        """
        更新队列超时
        """
        pass
if (__name__ == '__main__'):
    pass