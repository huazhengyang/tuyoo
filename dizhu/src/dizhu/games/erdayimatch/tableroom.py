# -*- coding:utf-8 -*-
'''
Created on 2017年01月19日

@author: luwei
'''
from dizhu.games.erdayimatch import dealer
from dizhu.games.erdayimatch.table import DizhuTableCtrlErdayiMatch
from dizhucomm.room.tableroom import DizhuTableRoom
from poker.entity.game.rooms.room import TYRoom
import freetime.util.log as ftlog


class DizhuTableRoomErdayiMatch(DizhuTableRoom):
    def __init__(self, roomDefine):
        super(DizhuTableRoomErdayiMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self._dealer = dealer.DDZDEALER_ERDAYI_MATCH

    def newTable(self, tableId):
        tableCtrl = DizhuTableCtrlErdayiMatch(self, tableId, self._dealer)
        tableCtrl.setupTable()
        return tableCtrl

    def quickStart(self, userId, tableId, isNextBuyin):
        raise NotImplementedError

    def leaveRoom(self, userId, tableId, reason):
        '''
        玩家离开房间
        '''
        canQuit = self.roomConf.get('canQuit', 0)
        if reason == TYRoom.LEAVE_ROOM_REASON_ACTIVE and canQuit and tableId:
            seat = None
            ctrTable = self.findTable(tableId)
            for s in ctrTable.table.seats:
                if s.userId == userId:
                    seat = s
                    break

            if ftlog.is_debug():
                ftlog.debug('DizhuTableRoomErdayiMatch.leaveRoom',
                            'gameId=', self.gameId,
                            'userId=', userId,
                            'seat=', seat,
                            'tableId=', ctrTable.table.tableId,
                            )

            if seat:
                try:
                    ctrTable.table.quit(seat)
                except Exception, e:
                    ftlog.warn('DizhuTableRoomErdayiMatch.leaveRoom',
                               'gameId=', self.gameId,
                               'userId=', userId,
                               'tableId=', ctrTable.table.tableId,
                               'e=', e)
                return True
            else:
                ftlog.warn('DizhuTableRoomErdayiMatch.leaveRoom',
                           'gameId=', self.gameId,
                           'userId=', userId,
                           'tableId=', ctrTable.table.tableId,
                           'Player not in seat')
                return False
        return True



