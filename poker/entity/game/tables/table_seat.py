# -*- coding: utf-8 -*-
"""
Created on 2015年7月7日

@author: zqh
"""
from poker.util import strutil

class TYSeat(object, ):
    """
    为了兼容老版Table（seat是list类型）， TYSeat需要实现list的部分函数
    Note： 如果直接继承list的话，在redis化时，没有覆写的函数会出现致数据不一致的问题， 所以不推荐。
    注意约定: 此列表中第0个字段为当前座位的上userId,
            此列表中第1个字段为当前座位的玩家状态,
    """
    INDEX_SEATE_USERID = 0
    INDEX_SEATE_STATE = 1
    SEAT_STATE_IDEL = 0
    SEAT_STATE_WAIT = 10
    SEAT_STATE_READY = 20
    SEAT_STATE_PLAYING = 30

    def __init__(self, table):
        pass

    def __getitem__(self, index):
        pass

    def __setitem__(self, index, value):
        pass

    def __len__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def getDatas(self):
        pass

    def update(self, stateList):
        """
        将 stateList (list类型) 数据更新到TYSeat类属性
        TYSeat子类可以通过覆写此函数来扩展属性,
        此方法通常再初始化桌子状态时调用
        """
        pass

    def replace(self, stateList):
        pass

    @property
    def userId(self):
        pass

    @userId.setter
    def userId(self, userId):
        pass

    @property
    def state(self):
        pass

    @state.setter
    def state(self, state):
        pass

    def isEmptySeat(self):
        pass

    def isPlayingSeat(self):
        pass

    def setPlayingState(self):
        pass

    def isWaitingSeat(self):
        pass

    def setWaitingState(self):
        pass