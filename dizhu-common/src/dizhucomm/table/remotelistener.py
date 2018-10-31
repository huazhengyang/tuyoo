# -*- coding:utf-8 -*-
'''
Created on 2017年2月28日

@author: zhaojiangang
'''
from dizhucomm.core.events import GameStartEvent, CallEvent
from dizhucomm.servers.util.rpc import comm_table_remote
from freetime.util import log as ftlog

class TableRemoteListener(object):
    def __init__(self, tableCtrl):
        # 所属的桌子
        self._tableCtrl = tableCtrl

    @property
    def table(self):
        return self._tableCtrl.table
            
    def setupTable(self):
        self.table.on(GameStartEvent, self._onGameStart)
        self.table.on(CallEvent, self._onCall)

    def _onGameStart(self, event):
        if ftlog.is_debug():
            ftlog.debug('TableRemoteListener._onGameStart Entry',
                        'gameId=', self._tableCtrl.gameId,
                        'roomId=', self._tableCtrl.roomId,
                        'gameRound=', event.table.gameRound,
                        'seats=', event.table.gameRound.seats,
                        'players=', [seat.player for seat in event.table.gameRound.seats],
                        'roundNum=', event.table.gameRound.roundNum,
                        'tableId=', self._tableCtrl.tableId,
                        'event=', event)
        gameRound = event.table.gameRound
        for seat in gameRound.seats:
            if seat.player and not seat.player.isRobotUser:
                mixConfRoomId = None
                if hasattr(seat.player, 'mixConf'):
                    mixConfRoomId = seat.player.mixConf.get('roomId')

                try:
                    if ftlog.is_debug():
                        ftlog.debug('TableRemoteListener._onGameStart',
                                    'gameId=', self._tableCtrl.gameId,
                                    'roomId=', self._tableCtrl.roomId,
                                    'tableId=', self._tableCtrl.tableId,
                                    'roundNum=', gameRound.roundNum,
                                    'mixConfRoomId=', mixConfRoomId,
                                    'seat=', (seat.userId, seat.seatId),
                                    'dizhuSeat=', (gameRound.dizhuSeat.userId, gameRound.dizhuSeat.seatId))
                    tbinfo = comm_table_remote.doTableGameStart(self._tableCtrl.gameId,
                                                                self._tableCtrl.roomId,
                                                                self._tableCtrl.tableId,
                                                                gameRound.roundNum,
                                                                gameRound.dizhuSeat.userId,
                                                                gameRound.baseCardType,
                                                                gameRound.baseScore,
                                                                seat.userId,
                                                                mixConfRoomId=mixConfRoomId)
                    if tbinfo:
                        seat.player.datas['tbc'] = tbinfo['tbplaycount']
                        seat.player.datas['tbt'] = min(tbinfo['tbplaytimes'], tbinfo['tbplaycount'])
                except:
                    pass
    
    def _onCall(self, event):
        gameRound = event.table.gameRound
        isGrab = event.callValue > 0 and len(gameRound.effectiveCallList) > 1
        if ftlog.is_debug():
            ftlog.debug('TableRemoteListener._onCall',
                        'gameId=', self._tableCtrl.gameId,
                        'roomId=', self._tableCtrl.roomId,
                        'tableId=', self._tableCtrl.tableId,
                        'roundNum=', gameRound.roundNum,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'isGrab=', isGrab)
        
        comm_table_remote.doTableGameCall(self._tableCtrl.gameId,
                                          self._tableCtrl.roomId,
                                          self._tableCtrl.tableId,
                                          event.table.gameRound.roundNum,
                                          event.seat.userId,
                                          event.callValue,
                                          isGrab)


