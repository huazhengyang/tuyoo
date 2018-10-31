# -*- coding:utf-8 -*-
'''
Created on 2017年3月7日

@author: zhaojiangang
'''
from dizhu.games.free.table import DizhuTableCtrlNormalFree
from dizhu.games.normalbase.tableroom import DizhuPlayerNormalBase, \
    DizhuTableRoomNormalBase


class DizhuPlayerNormalFree(DizhuPlayerNormalBase):
    def __init__(self, room, userId):
        super(DizhuPlayerNormalFree, self).__init__(room, userId)

class DizhuTableRoomNormalFree(DizhuTableRoomNormalBase):
    def __init__(self, roomDefine):
        super(DizhuTableRoomNormalFree, self).__init__(roomDefine)

    def _makeTableCtrl(self, tableId, dealer):
        return DizhuTableCtrlNormalFree(self, tableId, dealer)
    
    def _makePlayer(self, userId):
        return DizhuPlayerNormalFree(self, userId)


