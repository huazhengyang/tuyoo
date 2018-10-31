# -*- coding:utf-8 -*-
'''
Created on 2017年5月4日

@author: wangyonghui
'''
from dizhucomm.core.base import TableCommand, TableState
from dizhucomm.core.state import BaseActions


class DisBandCommand(TableCommand):
    ''' 解散牌桌命令 '''
    def __init__(self, reason):
        super(DisBandCommand, self).__init__()
        self.reason = reason


class FriendActions(BaseActions):
    @classmethod
    def disBandAction(cls, cmd):
        '''
        解散牌桌
        '''
        if not isinstance(cmd, DisBandCommand):
            return TableState.STATE_CONTINUE
        cmd.playMode.clearGame(cmd.table, False, cmd.reason)
        return cmd.table.sm.findStateByName('idle')

