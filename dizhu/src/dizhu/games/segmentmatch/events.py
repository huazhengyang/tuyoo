# -*- coding:utf-8 -*-
'''
Created on 2018年4月20日

@author: wangyonghui
'''

from dizhucomm.entity.events import UserTableEvent
from poker.entity.events.tyevent import UserEvent


class SegmentTableWinloseEvent(UserTableEvent):
    '''
    针对段位赛的事件
    '''
    def __init__(self, gameId, userId, roomId, tableId, winlose, **kwargs):
        super(SegmentTableWinloseEvent, self).__init__(gameId, userId, roomId, tableId)
        self.winlose = winlose
        self.kwargs = kwargs


class SegmentRecoverEvent(UserEvent):
    '''
    针对段位赛的事件
    '''
    def __init__(self, userId, gameId):
        super(SegmentRecoverEvent, self).__init__(userId, gameId)
