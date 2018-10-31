# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
import dizhu.games.arenamatch.dealer as dealer
from dizhu.games.arenamatch.table import DizhuTableCtrlArenaMatch
from dizhu.tupt.ob import obsystem
from dizhu.games.matchutil import BanHelper
from dizhucomm.core.events import GameRoundFinishEvent
from dizhucomm.room.tableroom import DizhuTableRoom
from poker.entity.game.rooms.room import TYRoom
import freetime.util.log as ftlog


class DizhuTableRoomArenaMatch(DizhuTableRoom):
    def __init__(self, roomDefine):
        super(DizhuTableRoomArenaMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self._dealer = dealer.DIZHU_DEALER_DICT[self.roomConf['playMode']]
        
    def newTable(self, tableId):
        tableCtrl = DizhuTableCtrlArenaMatch(self, tableId, self._dealer)
        tableCtrl.setupTable()
        obsystem.setupTable(tableCtrl.table)
        tableCtrl.table.on(GameRoundFinishEvent, self._onGameRoundFinish)
        return tableCtrl

    def _onGameRoundFinish(self, event):
        # 如果用户是托管结束的，增加其托管次数
        BanHelper.onGameRoundFinish(event)

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
                ftlog.debug('DizhuTableRoomArenaMatch.leaveRoom',
                            'gameId=', self.gameId,
                            'userId=', userId,
                            'seat=', seat,
                            'tableId=', ctrTable.table.tableId,
                            )

            if seat:
                try:
                    ctrTable.table.quit(seat)
                except Exception, e:
                    ftlog.warn('DizhuTableRoomArenaMatch.leaveRoom',
                               'gameId=', self.gameId,
                               'userId=', userId,
                               'tableId=', ctrTable.table.tableId,
                               'e=', e)
                return True
            else:
                ftlog.warn('DizhuTableRoomArenaMatch.leaveRoom',
                           'gameId=', self.gameId,
                           'userId=', userId,
                           'tableId=', ctrTable.table.tableId,
                           'Player not in seat')
                return False
        return True


