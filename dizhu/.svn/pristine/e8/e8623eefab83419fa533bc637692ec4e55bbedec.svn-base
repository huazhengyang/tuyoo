# -*- coding:utf-8 -*-
'''
Created on 2017年2月3日

@author: zhaojiangang
'''
from dizhucomm.core.events import TableEvent

class FTBindEvent(TableEvent):
    def __init__(self, table, ftTable):
        super(FTBindEvent, self).__init__(table)
        self.ftTable = ftTable
        
class FTUnbindEvent(TableEvent):
    def __init__(self, table, ftTable):
        super(FTUnbindEvent, self).__init__(table)
        self.ftTable = ftTable

class FTDisbindEvent(TableEvent):
    def __init__(self, table, returnFee, reason):
        super(FTDisbindEvent, self).__init__(table)
        self.returnFee = returnFee
        self.reason = reason

class FTDisbindTimeoutEvent(TableEvent):
    def __init__(self, table):
        super(FTDisbindTimeoutEvent, self).__init__(table)
        
class FTContinueEvent(TableEvent):
    def __init__(self, table, seat):
        super(FTContinueEvent, self).__init__(table)
        self.seat = seat
        
class FTContinueErrorEvent(TableEvent):
    def __init__(self, table, seat, ec, errmsg):
        super(FTContinueErrorEvent, self).__init__(table)
        self.seat = seat
        self.ec = ec
        self.errmsg = errmsg
        
class FTContinueTimeoutEvent(TableEvent):
    def __init__(self, table):
        super(FTContinueTimeoutEvent, self).__init__(table)
