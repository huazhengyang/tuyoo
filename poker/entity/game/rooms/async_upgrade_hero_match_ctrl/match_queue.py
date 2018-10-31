# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的队列/班车

@author: zhaol
"""
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_player import AsyncUpgradeHeroMatchPlayer
from freetime.util import log as ftlog

class AsyncUpgradeHeroMatchQueue(object, ):
    """
    快速赛比赛阶段s
    """

    def __init__(self):
        pass

    @property
    def msgSender(self):
        """
        消息发送器
        """
        pass

    def setMsgSender(self, sender):
        pass

    @property
    def tableMaxSeat(self):
        """
        每桌的分配人数
        """
        pass

    def setTableMaxSeat(self, tableMax):
        """
        设置每桌的分配人数
        """
        pass

    @property
    def players(self):
        """
        队列玩家集合
        """
        pass

    def setPlayers(self, players):
        """
        设置玩家集合
        """
        pass

    def addPlayer(self, player):
        """
        向队列添加玩家
        """
        pass

    def findPlayer(self, userId):
        """
        队列中是否有此用户
        """
        pass

    def removePlayer(self, player):
        """
        将玩家从队列中移除
        """
        pass

    @property
    def waitTime(self):
        """
        队列等待时间
        """
        pass

    def setWaitTime(self, wt):
        pass

    @property
    def busDriveTime(self):
        """
        班车分配的超时时间
        """
        pass

    def setBusDruveTime(self, bt):
        pass

    @property
    def waitNumber(self):
        """
        班车的人数
        """
        pass

    def setWaitNumber(self, number):
        """
        设置班车人数
        队列中超过这个人数，则发班车
        """
        pass

    @property
    def hasrobot(self):
        """
        是否有机器人
        """
        pass

    def setHasRobot(self, hasrobot):
        """

        """
        pass

    @property
    def busDriveNumber(self):
        pass

    def initConfig(self, config, hasrobot=0):
        """
        根据配置初始化
        """
        pass

    def deltaTick(self, dt):
        """
        修改一个改变时间，如果等待时间降低至0，或者队列人数满足要求，则分配班车组桌
        """
        pass

    def isDriveBus(self):
        """
        是否发班车
        """
        pass

    def drive(self):
        """
        班车发车
        """
        pass

    def enterTable(self, players, usersArr):
        """
        进桌
        """
        pass

    def printPlayers(self):
        pass
if (__name__ == '__main__'):
    config = {'waitTime': 10, 'busNumber': 16}
    queue = AsyncUpgradeHeroMatchQueue()
    queue.initConfig(config)
    p1 = AsyncUpgradeHeroMatchPlayer()
    p1.setUserId(10001)
    p1.setEnterTime(1510040962)
    p1.setStageIndex(0)
    queue.addPlayer(p1)
    p2 = AsyncUpgradeHeroMatchPlayer()
    p2.setUserId(10002)
    p2.setEnterTime(1510040942)
    p2.setStageIndex(0)
    queue.addPlayer(p2)
    queue.deltaTick((-10))
    if queue.isDriveBus():
        queue.drive()