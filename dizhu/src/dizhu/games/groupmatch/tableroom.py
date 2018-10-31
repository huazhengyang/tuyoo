# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
from dizhu.games.groupmatch import dealer
from dizhu.games.groupmatch.table import DizhuTableCtrlGroupMatch
from dizhu.games.matchutil import BanHelper
from dizhucomm.core.events import GameRoundFinishEvent
from dizhucomm.room.tableroom import DizhuTableRoom
from poker.entity.game.rooms.room import TYRoom
import freetime.util.log as ftlog
from dizhu.tupt.ob import obsystem


class DizhuTableRoomGroupMatch(DizhuTableRoom):
    def __init__(self, roomDefine):
        super(DizhuTableRoomGroupMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self._dealer = dealer.DIZHU_DEALER_DICT[self.roomConf['playMode']]

    def newTable(self, tableId):
        tableCtrl = DizhuTableCtrlGroupMatch(self, tableId, self._dealer)
        tableCtrl.setupTable()
        tableCtrl.table.on(GameRoundFinishEvent, self._onGameRoundFinish)
        obsystem.setupTable(tableCtrl.table)
        return tableCtrl

    def _onGameRoundFinish(self, event):
        # 如果用户是托管结束的，增加其托管次数
        BanHelper.onGameRoundFinish(event)

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
                ftlog.debug('DizhuTableRoomGroupMatch.leaveRoom',
                            'gameId=', self.gameId,
                            'userId=', userId,
                            'seat=', seat,
                            'tableId=', ctrTable.table.tableId,
                            )

            if seat:
                try:
                    ctrTable.table.quit(seat)
                except Exception, e:
                    ftlog.warn('DizhuTableRoomGroupMatch.leaveRoom',
                               'gameId=', self.gameId,
                               'userId=', userId,
                               'tableId=', ctrTable.table.tableId,
                               'e=', e)
                return True
            else:
                ftlog.warn('DizhuTableRoomGroupMatch.leaveRoom',
                           'gameId=', self.gameId,
                           'userId=', userId,
                           'tableId=', ctrTable.table.tableId,
                           'Player not in seat')
                return False
        return True


