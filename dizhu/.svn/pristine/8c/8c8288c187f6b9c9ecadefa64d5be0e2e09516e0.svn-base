# -*- coding:utf-8 -*-
'''
Created on 2017年3月7日

@author: zhaojiangang
'''
from dizhu.games.free.tableproto import DizhuTableProtoNormalFree
from dizhu.games.normalbase.table import DizhuTableNormalBase, \
    DizhuTableCtrlNormalBase


class DizhuTableNormalFree(DizhuTableNormalBase):
    def __init__(self, room, tableId, playMode):
        super(DizhuTableNormalFree, self).__init__(room, tableId, playMode)

    @property
    def replayMatchType(self):
        return 2
    
class DizhuTableCtrlNormalFree(DizhuTableCtrlNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlNormalFree, self).__init__(room, tableId, dealer)

    def _makeTable(self, tableId, playMode):
        return DizhuTableNormalFree(self.room, tableId, playMode)

    def _makeProto(self):
        return DizhuTableProtoNormalFree(self)

