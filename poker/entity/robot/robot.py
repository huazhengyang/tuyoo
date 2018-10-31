# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import random
from freetime.util import log as ftlog
from freetime.util.metaclasses import Singleton
from poker.entity.robot.robotevent import RobotEvent
from poker.entity.configure import gdata
TEST_ROBOT = False
MAX_ROBOT_UID = 10000

class TYRobotManager(object, ):
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def callUpRobot(self, msg, roomId, tableId, userCount, seatCount, users):
        """
        唤醒机器人 (由TABLE进程SEND命令触发, 无需响应)
        检查该桌子是否需要进入机器人
        具体的机器人进入策略由各个游戏自己负责
        """
        pass

    def callUpRobotsToMatch(self, msg, roomId, robotCount):
        """
        唤醒机器人参加比赛
        """
        pass

    def shutDownRobot(self, msg, roomId, tableId, userCount, seatCount, users):
        """
        关闭机器人 (由TABLE进程SEND命令触发, 无需响应)
        检查该桌子是否需要关闭机器人
        具体的机器人关闭策略由各个游戏自己负责
        """
        pass

    def getRobotDetail(self, msg):
        """
        取得当前游戏中机器人的运行状态 (由其他进程QUERY命令触发, 必须响应有效值)
        例如: 机器人的个数, 各个队列的长度等
        具体的内容由各个游戏自己负责
        """
        pass

    def onHeartBeat(self, event):
        pass

    def isAllRobotOnTable(self, seats):
        pass

    def popFreeRobotUser(self):
        pass

    def _processRobotEvent(self, evt):
        pass

    def _callUpRobot(self, msg, roomId, tableId, userCount, seatCount, users):
        """
        唤醒机器人 (由TABLE进程SEND命令触发, 无需响应)
        检查该桌子是否需要进入机器人
        具体的机器人进入策略由各个游戏自己负责
        """
        pass

    def _shutDownRobot(self, msg, roomId, tableId, userCount, seatCount, users):
        """
        斗地主目前全部是打完一局换桌, 那么再地主的机器人里面, 就不必处理shutdown消息
        机器人, 接收到game_win后, 自动的离开, 断开连接
        """
        pass