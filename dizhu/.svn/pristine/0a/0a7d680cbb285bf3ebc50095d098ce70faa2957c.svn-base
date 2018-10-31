# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''

from dizhu.servers.table.rpc import match_table_room_remote
from dizhucomm.room.base import DizhuRoom
from dizhucomm.utils.msghandler import MsgHandler
import freetime.util.log as ftlog
from matchcomm.matchs.custom_match.room import CustomMatchRoomMixin


class DizhuCtrlRoomCustomMatch(DizhuRoom, MsgHandler, CustomMatchRoomMixin):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomCustomMatch, self).__init__(roomDefine)
        self.initStageMatch()
    
    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        if tableId == self.roomId * 10000:
            match = self.matchArea.findMatchByUserId(userId)
            if match:
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomCustomMatch.doCheckUserLoc',
                                'gameId=', gameId,
                                'userId=', userId,
                                'tableId=', tableId,
                                'clientId=', clientId,
                                'ret=', (self.matchArea.conf.seatId, 0))
                return self.matchArea.conf.seatId, 0
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomCustomMatch.doCheckUserLoc',
                        'gameId=', gameId,
                        'userId=', userId,
                        'tableId=', tableId,
                        'clientId=', clientId,
                        'ret=', (-1, 0))
        return -1, 0

    def leaveRoom(self, userId, shadowRoomId, tableId, reason):
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomCustomMatch.leaveRoom',
                        'roomId=', self.roomId,
                        'shadowRoomId=', shadowRoomId,
                        'userId=', userId,
                        'tableId=', tableId,
                        'reason=', reason)
        if shadowRoomId:
            return match_table_room_remote.leaveRoom(self.gameId, userId, shadowRoomId, tableId, reason)
        return True


