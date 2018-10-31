# -*- coding:utf-8 -*-
'''
Created on 2017年2月13日

@author: zhaojiangang
'''
from dizhu.games.normal.tableproto import DizhuTableProtoNormal
from dizhu.games.normalbase.table import DizhuTableNormalBase,\
    DizhuTableCtrlNormalBase


class DizhuTableNormal(DizhuTableNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableNormal, self).__init__(room, tableId, dealer)

class DizhuTableCtrlNormal(DizhuTableCtrlNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlNormal, self).__init__(room, tableId, dealer)
    
    def _makeTable(self, tableId, dealer):
        return DizhuTableNormal(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoNormal(self)
