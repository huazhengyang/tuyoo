# -*- coding: utf-8 -*-
"""
Created on 2015年7月7日

@author: zqh, zhouhao
"""
from freetime.util import log as ftlog
from poker.entity.game.tables.table_seat import TYSeat

class TYSeatList(object, ):
    """
    为了兼容老版Table（_seat : [[][]]）， TYSeatList需要实现list的部分函数
    Note： 如果直接继承list的话，在redis化时，没有覆写的函数会出现致数据不一致的问题， 所以不推荐。
    注意: 座位数量(table.maxSeatN)初始化后, 就不在发生变化
    """

    def __init__(self, table):
        pass

    def __getitem__(self, index):
        pass

    def __setitem__(self, index, item):
        pass

    def __len__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def findNextSeat(self, seatIndex):
        pass

    def findNextPlayingSeat(self, seatIndex):
        pass

    def findNextSittingSeat(self, seatIndex):
        pass

    def findNextEmptySeat(self, seatIndex):
        pass

    def calcEmptySeatN(self, startSeatIndex, endSeatIndex):
        pass