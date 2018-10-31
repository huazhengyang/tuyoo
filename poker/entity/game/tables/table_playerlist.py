# -*- coding: utf-8 -*-
"""
Created on 2015年7月7日

@author: zqh
"""
from poker.entity.game.tables.table_player import TYPlayer

class TYPlayerList(object, ):
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

    def getList(self):
        pass