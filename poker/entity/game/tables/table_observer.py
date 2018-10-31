# -*- coding: utf-8 -*-
__author__ = ['Zhaoqh"Zhouhao" <zhouhao@tuyoogame.com>']

class TYObserver(object, ):
    """
    玩家基类
    玩家table.players和座位table.seats是一一对应的
    此类主要是为了保持玩家再当前桌子的上的一些基本用户数据, 避免反复查询数据库
    注: 再游戏逻辑中, 不区分机器人和真实玩家
    """

    def __init__(self, table, seatIndex):
        pass

    @property
    def seatId(self):
        pass

    @property
    def seatIndex(self):
        pass

    @property
    def userId(self):
        pass