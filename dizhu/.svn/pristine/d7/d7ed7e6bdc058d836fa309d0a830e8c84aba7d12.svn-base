# -*- coding:utf-8 -*-
'''
Created on 2018年4月13日

@author: wangyonghui
'''
from dizhu.games.normalbase.table import DizhuTableNormalBase, DizhuTableCtrlNormalBase
from dizhu.games.segmentmatch_ai.tableproto import DizhuTableProtoSegmentAI


class DizhuTableSegmentMatchAI(DizhuTableNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableSegmentMatchAI, self).__init__(room, tableId, dealer)
        self.segmentSection = None


class DizhuTableCtrlSegmentMatchAI(DizhuTableCtrlNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlSegmentMatchAI, self).__init__(room, tableId, dealer)

    def _makeTable(self, tableId, dealer):
        return DizhuTableSegmentMatchAI(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoSegmentAI(self)
