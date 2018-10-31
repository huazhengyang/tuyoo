# -*- coding:utf-8 -*-
'''
Created on 2018年9月20日

@author: wangyonghui
'''
from dizhu.games.normal_ai.tableproto import DizhuTableProtoNormalAI
from dizhu.games.normalbase.table import DizhuTableNormalBase, \
    DizhuTableCtrlNormalBase


class DizhuTableNormalAI(DizhuTableNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableNormalAI, self).__init__(room, tableId, dealer)


class DizhuTableCtrlNormalAI(DizhuTableCtrlNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlNormalAI, self).__init__(room, tableId, dealer)

    def _makeTable(self, tableId, dealer):
        return DizhuTableNormalAI(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoNormalAI(self)
