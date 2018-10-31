# -*- coding:utf-8 -*-
'''
Created on 2018年4月13日

@author: wangyonghui
'''
from dizhu.games.normalbase.table import DizhuTableNormalBase, DizhuTableCtrlNormalBase
from dizhu.games.segmentmatch.tableproto import DizhuTableProtoSegment


class DizhuTableSegmentMatch(DizhuTableNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableSegmentMatch, self).__init__(room, tableId, dealer)
        self.segmentSection = None


class DizhuTableCtrlSegmentMatch(DizhuTableCtrlNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlSegmentMatch, self).__init__(room, tableId, dealer)

    def _makeTable(self, tableId, dealer):
        return DizhuTableSegmentMatch(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoSegment(self)
