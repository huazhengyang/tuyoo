# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的队列/班车

@author: zhaol
"""
from freetime.util import log as ftlog
from poker.entity.dao import gamedata

class MixedRoomQueue(object, ):
    """
    快速赛比赛阶段s
    """

    def __init__(self):
        pass

    @property
    def gameId(self):
        pass

    def setGameId(self, gameId):
        pass

    @property
    def playMode(self):
        pass

    def setPlayMode(self, playMode):
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

    def findPlayer(self, userId):
        """
        寻找玩家
        """
        pass

    def addPlayer(self, player):
        """
        向队列添加玩家
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
    def busDriveNumber(self):
        pass

    def initConfig(self, config):
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

    def selfDrive(self):
        """
        自有队列班车发车
        返回结果为一桌一桌已经分好的玩家
        """
        pass

    def getEloRank(self, player):
        """
        获取player的elo等级分
        """
        pass

    def mixedDrive(self, count):
        """
        班车发车
        混房发车
        返回剩余班车中所有的人
        待分桌
        """
        pass

    def printPlayers(self):
        pass
if (__name__ == '__main__'):
    pass