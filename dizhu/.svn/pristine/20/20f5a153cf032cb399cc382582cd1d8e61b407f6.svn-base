# -*- coding=utf-8 -*-

'''
Created on 2014年2月24日

@author: zjgzzz@126.com
'''
from dizhucomm.entity.events import UserTableEvent


class MyFTFinishEvent(UserTableEvent):
    def __init__(self, gameId, userId, roomId, tableId, ftId):
        super(MyFTFinishEvent, self).__init__(gameId, userId, roomId, tableId)
        self.ftId = ftId


