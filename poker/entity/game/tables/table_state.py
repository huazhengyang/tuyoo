# -*- coding: utf-8 -*-
"""
Created on 2015年7月7日

@author: zqh
"""
from poker.util import strutil

class TYTableState(object, ):
    """
    为了兼容老版Table（_stat是list类型）， TYTableState需要实现list的部分函数, 即可以按list的方式进行数据的操作
    Note： 如果直接继承list的话，在redis化时，没有覆写的函数会出现致数据不一致的问题， 所以不推荐。
    table.state一旦建立, 其数据存储为list形式(便于redis化), 基本上其数据的个数将不再发生变化
    注意约定: 此列表中第0个字段为桌子的int值状态
    """
    INDEX_TABLE_STATE = 0
    TABLE_STATE_IDEL = 10

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
        将stateList (list类型) 数据更新到TYTableState类属性
        TYTableState子类可以通过覆写此函数来扩展属性,
        此方法通常再初始化桌子状态时调用
        """
        pass

    @property
    def state(self):
        pass

    @state.setter
    def state(self, state):
        pass