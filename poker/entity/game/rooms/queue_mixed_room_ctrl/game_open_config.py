# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的玩家对象
@author: zhaol

"""
from datetime import datetime

class MixedRoomOpenConfig(object, ):
    INIT_TIME = '00:00'

    def __init__(self):
        pass

    @property
    def startTime(self):
        pass

    def setStartTime(self, sTime):
        pass

    @property
    def endTime(self):
        pass

    def setEndTime(self, eTime):
        pass

    def initConfig(self, config):
        """
        初始化配置
        """
        pass

    def isOpen(self):
        """
        混房是否开放
        """
        pass
if (__name__ == '__main__'):
    room = MixedRoomOpenConfig()
    room.initConfig({'startTime': '17:00', 'endTime': '23:59'})
    print room.isOpen()