# -*- coding:utf-8 -*-
'''
Created on 2017年6月15日

@author: wangyonghui
'''
from dizhucomm.replay import gameround
from dizhucomm.replay.gameround import GameReplayRound, SeatWinloseDetail, \
    WinloseDetail
from dizhucomm.table.replay import ReplayTable
from freetime.util import log as ftlog
from poker.util import timestamp as pktimestamp
from dizhucomm.core.playmode import GameRound


class ReplayTableMix(ReplayTable):
    def __init__(self, tableCtrl):
        super(ReplayTableMix, self).__init__(tableCtrl)

    def _onGameReady(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameReady',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])

        seats = []
        self.names = []
        self.grabs = []
        self.roomMutils = []
        self.roomFees = []
        for seat in event.table.seats:
            player = seat.player
            seats.append(gameround.Seat(player.userId,
                                        player.datas.get('name', ''),
                                        player.datas.get('sex', 0),
                                        player.datas.get('vipInfo', {}).get('level', 0),
                                        player.datas.get('chip', 0),
                                        player.score,
                                        player.datas.get('purl', ''),
                                        player.datas.get('wearedItems', [])))
            self.names.append(player.mixConf.get('name'))
            self.grabs.append(player.mixConf.get('tableConf').get('grab'))
            self.roomMutils.append(player.mixConf.get('roomMutil'))
            self.roomFees.append(player.mixConf.get('roomFee'))
        gameRound = GameReplayRound(event.table.gameRound.roundNum,
                                    event.table.roomId,
                                    event.table.tableId,
                                    event.table.room.matchId,
                                    event.table.replayMatchType,
                                    self.names[0],
                                    event.table.room.roomConf['playMode'],
                                    self.grabs[0],
                                    self.roomMutils[0],
                                    self.roomFees[0],
                                    seats,
                                    pktimestamp.getCurrentTimestamp())
        gameRound.gameReady(event.seatCards, event.baseCards)
        self._curRound = gameRound
        self._roundMap[event.table.gameRound.roundId] = (gameRound, set())

    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        seatWinloseDetails = []
        for sst in event.gameResult.seatStatements:
            skillInfo = sst.skillscoreInfo
            seatWinloseDetails.append(SeatWinloseDetail({
                'score': skillInfo['score'],
                'level': skillInfo['level'],
                'premax': skillInfo['premaxscore'],
                'curmax': skillInfo['curmaxscore'],
                'add': skillInfo['addScore']
            },
                sst.seat.status.totalMulti,
                sst.winStreak,
                sst.delta,
                sst.final))
        gslams = []
        seatIndex = 0
        for index, seat in enumerate(event.table.seats):
            if event.gameResult.gameRound.dizhuSeat == seat:
                seatIndex = index
            gslams.append(seat.player.mixConf.get('tableConf').get('gslam'))
        winloseDetail = WinloseDetail(event.gameResult.gameRound.result,
                                      event.gameResult.gameRound.bombCount,
                                      event.gameResult.gameRound.isChuntian,
                                      event.gameResult.gameRound.showMulti,
                                      event.gameResult.gameRound.baseCardMulti,
                                      event.gameResult.gameRound.rangpaiMulti,
                                      event.gameResult.gameRound.callMulti,
                                      event.gameResult.gameRound.totalMulti,
                                      1 if event.gameResult.gameRound.result == GameRound.RESULT_DIZHU_WIN else 0,
                                      1 if event.gameResult.slam else 0,
                                      gslams[seatIndex],
                                      seatWinloseDetails)

        # 这里已地主视角 复写replay gameRound
        self._curRound.roomName = self.names[seatIndex]
        self._curRound.grab = self.grabs[seatIndex]
        self._curRound.roomMulti = self.roomMutils[seatIndex]
        self._curRound.roomFee = self.roomFees[seatIndex]

        self._curRound.gameWinlose(winloseDetail)
        self._curRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
        self._clearReplayRound()

    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        # self._curRound.gameAbort()
        if not event.table.room.isMatch:
            self._curRound.gameAbort()
        else:
            seatWinloseDetails = []
            for sst in event.gameResult.seatStatements:
                skillInfo = sst.skillscoreInfo
                seatWinloseDetails.append(SeatWinloseDetail({
                    'score': skillInfo['score'],
                    'level': skillInfo['level'],
                    'premax': skillInfo['premaxscore'],
                    'curmax': skillInfo['curmaxscore'],
                    'add': skillInfo['addScore']
                },
                    sst.seat.status.totalMulti,
                    sst.winStreak,
                    sst.delta,
                    sst.final))

            gslams = []
            seatIndex = 0
            for index, seat in enumerate(event.table.seats):
                if event.gameResult.gameRound.dizhuSeat == seat:
                    seatIndex = index
                gslams.append(seat.player.mixConf.get('tableConf').get('gslam'))
            winloseDetail = WinloseDetail(event.gameResult.gameRound.result,
                                          event.gameResult.gameRound.bombCount,
                                          event.gameResult.gameRound.isChuntian,
                                          event.gameResult.gameRound.showMulti,
                                          event.gameResult.gameRound.baseCardMulti,
                                          event.gameResult.gameRound.rangpaiMulti,
                                          event.gameResult.gameRound.callMulti,
                                          event.gameResult.gameRound.totalMulti,
                                          1 if event.gameResult.gameRound.result == GameRound.RESULT_DIZHU_WIN else 0,
                                          1 if event.gameResult.slam else 0,
                                          gslams[seatIndex],
                                          seatWinloseDetails)

            # 这里已地主视角 复写replay gameRound
            self._curRound.roomName = self.names[seatIndex]
            self._curRound.grab = self.grabs[seatIndex]
            self._curRound.roomMulti = self.roomMutils[seatIndex]
            self._curRound.roomFee = self.roomFees[seatIndex]

            self._curRound.gameWinlose(winloseDetail)
        self._curRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
        self._clearReplayRound()



