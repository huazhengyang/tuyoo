# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
from dizhu.games.custom_match import dealer
from dizhu.games.custom_match.table import DizhuTableCtrlCustomMatch
from dizhucomm.room.tableroom import DizhuTableRoom
import freetime.util.log as ftlog
from poker.entity.game.rooms.room import TYRoom


class DizhuTableRoomCustomMatch(DizhuTableRoom):
    def __init__(self, roomDefine):
        super(DizhuTableRoomCustomMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self._dealer = dealer.DIZHU_DEALER_DICT[self.roomConf['playMode']]

    def newTable(self, tableId):
        tableCtrl = DizhuTableCtrlCustomMatch(self, tableId, self._dealer)
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
                ftlog.debug('DizhuTableRoomCustomMatch.leaveRoom',
                            'gameId=', self.gameId,
                            'userId=', userId,
                            'seat=', seat,
                            'tableId=', ctrTable.table.tableId,
                            )

            if seat:
                try:
                    ctrTable.table.quit(seat)
                except Exception, e:
                    ftlog.warn('DizhuTableRoomCustomMatch.leaveRoom',
                               'gameId=', self.gameId,
                               'userId=', userId,
                               'tableId=', ctrTable.table.tableId,
                               'e=', e)
                return True
            else:
                ftlog.warn('DizhuTableRoomCustomMatch.leaveRoom',
                           'gameId=', self.gameId,
                           'userId=', userId,
                           'tableId=', ctrTable.table.tableId,
                           'Player not in seat')
                return False
        return True


