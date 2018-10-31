# -*- coding:utf-8 -*-
'''
Created on 2017年2月15日

@author: zhaojiangang
'''
from dizhucomm.core.events import GameReadyEvent, GameStartEvent, CallEvent, \
    CurOpSeatMoveEvent, NongminJiabeiEvent, DizhuJiabeiEvent, OutCardEvent, \
    ShowCardEvent, ThrowEmojiEvent, TuoguanEvent, ChatEvent, GameRoundOverEvent, \
    GameRoundAbortEvent
from dizhucomm.replay import gameround
from dizhucomm.replay.gameround import GameReplayRound, SeatWinloseDetail, \
    WinloseDetail
from freetime.util import log as ftlog
from poker.util import timestamp as pktimestamp
from dizhucomm.playmodes.laizi import WildCardEvent
from dizhucomm.core.playmode import GameRound


class ReplayTable(object):
    def __init__(self, tableCtrl):
        # 桌子
        self._tableCtrl = tableCtrl
        # 当前GameRound
        self._curRound = None
        # map<roundId, (GameRound, set<userId>)>
        self._roundMap = {}
    
    @property
    def table(self):
        return self._tableCtrl.table
    
    @property
    def curRound(self):
        return self._curRound
    
    def findGameRoundInfo(self, roundId):
        return self._roundMap.get(roundId)
    
    def findGameRound(self, roundId):
        gameRoundInfo = self.findGameRoundInfo(roundId)
        return gameRoundInfo[0] if gameRoundInfo else None
    
    def _onGameReady(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameReady',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])

        seats = []
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
        gameRound = GameReplayRound(event.table.gameRound.roundNum,
                                    event.table.roomId,
                                    event.table.tableId,
                                    event.table.room.matchId,
                                    event.table.replayMatchType,
                                    event.table.room.roomConf['name'],
                                    event.table.room.roomConf['playMode'],
                                    event.table.runConf.grab,
                                    event.table.runConf.roomMutil,
                                    event.table.runConf.roomFee,
                                    seats,
                                    pktimestamp.getCurrentTimestamp())
        gameRound.gameReady(event.seatCards, event.baseCards)
        self._curRound = gameRound
        self._roundMap[event.table.gameRound.roundId] = (gameRound, set())

    def _onGameStart(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameStart',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        seatCards = []
        for seat in event.table.seats:
            seatCards.append(seat.status.cards[:])
        self._curRound.gameStart(event.table.gameRound.dizhuSeat.seatIndex,
                                 seatCards,
                                 event.table.gameRound.baseCards,
                                 event.table.gameRound.baseCardMulti,
                                 event.table.playMode.calcTotalMulti(event.table.gameRound))
    
    def _onCall(self, event):
        assert(self._curRound.number== event.table.gameRound.roundNum)
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onCall',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'callValue=', event.callValue)
        self._curRound.call(event.seat.seatIndex,
                       event.callValue,
                       event.table.playMode.calcTotalMulti(event.table.gameRound),
                       event.table.gameRound.rangpai)
    
    def _onWildCard(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onWildCard', 
                        'tableId=', event.table.tableId,
                        'wildCard=', event.wildCard,
                        'wildCardBig=', event.wildCardBig)
        
        seatCards = []
        for seat in event.table.seats:
            seatCards.append(seat.status.cards[:])
        self._curRound.wildCard(event.wildCardBig, seatCards, event.table.gameRound.baseCards[:])

    def _onCurOpSeatMove(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onCurOpSeatMove',
                        'tableId=', event.table.tableId,
                        'curRoundId=', self._curRound.roundId,
                        'roundId=', event.table.gameRound.roundId)
        grab = 1 if not event.table.gameRound.dizhuSeat and event.table.gameRound.callList else 0
        self._curRound.next(event.curOpSeat.seatIndex, grab, event.optime)
        
    def _onOutCard(self, event):
        cards = event.validCards.cards[:] if event.validCards else []
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onOutCard',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'cards=', cards)
        self._curRound.outCard(event.seat.seatIndex,
                               cards,
                               event.table.playMode.calcTotalMulti(event.table.gameRound))
    
    def _onNongminJiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onNongminJiabei',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'multi=', event.multi)
        self._curRound.jiabei(event.seat.seatIndex, 1 if event.multi > 1 else 0)

    def _onDizhuJiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onDizhuJiabei',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'multi=', event.multi)
        self._curRound.jiabei(event.seat.seatIndex, 1 if event.multi > 1 else 0)

    def _onThrowEmoji(self, event):
        if self._curRound:
            if ftlog.is_debug():
                ftlog.debug('ReplayTable._onThrowEmoji',
                            'tableId=', event.table.tableId,
                            'seatFrom=', (event.seatFrom.userId, event.seatFrom.seatId),
                            'seatTo=', (event.seatTo.userId, event.seatTo.seatId),
                            'emojiId=', event.emojiId,
                            'deltaChip=', event.deltaChip,
                            'finalChip=', event.finalChip)
            self._curRound.sendSmilies(event.seatFrom.seatIndex,
                                       event.seatTo.seatIndex,
                                       event.emojiId,
                                       event.count,
                                       event.deltaChip,
                                       event.finalChip)
                
    def _onTuoguan(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onTuoguan',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'isTuoguan=', event.isTuoguan)
        self._curRound.robot(event.seat.seatIndex, 1 if event.isTuoguan else 0)
    
    def _onShowCards(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onShowCards',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId))
        self._curRound.show(event.seat.seatIndex,
                            event.table.gameRound.showMulti,
                            event.table.playMode.calcTotalMulti(event.table.gameRound))
    
    def _onChat(self, event):
        if self._curRound:
            if ftlog.is_debug():
                ftlog.debug('ReplayTable._onChat',
                            'tableId=', event.table.tableId,
                            'seat=', (event.seat.userId, event.seat.seatId),
                            'isFace=', event.isFace,
                            'voiceIdx=', event.voiceIdx,
                            'msg=', event.msg)
            self._curRound.chat(event.seat.seatIndex, event.isFace, event.voiceIdx, event.msg)

    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        seatWinloseDetails = []
        for sst in event.gameResult.seatStatements:
            skillInfo = sst.skillscoreInfo
            seatWinloseDetails.append(SeatWinloseDetail({
                                            'score':skillInfo['score'],
                                            'level':skillInfo['level'],
                                            'premax':skillInfo['premaxscore'],
                                            'curmax':skillInfo['curmaxscore'],
                                            'add':skillInfo['addScore']
                                        },
                                        sst.seat.status.totalMulti,
                                        sst.winStreak,
                                        sst.delta,
                                        sst.final))
            
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
                                      event.table.runConf.gslam,
                                      seatWinloseDetails)
        self._curRound.gameWinlose(winloseDetail)
        self._curRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
        self._clearReplayRound()
        
    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('ReplayTable._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
#         self._curRound.gameAbort()
        if not event.table.room.isMatch:
            self._curRound.gameAbort()
        else:
            seatWinloseDetails = []
            for sst in event.gameResult.seatStatements:
                skillInfo = sst.skillscoreInfo
                seatWinloseDetails.append(SeatWinloseDetail({
                                                'score':skillInfo['score'],
                                                'level':skillInfo['level'],
                                                'premax':skillInfo['premaxscore'],
                                                'curmax':skillInfo['curmaxscore'],
                                                'add':skillInfo['addScore']
                                            },
                                            sst.seat.status.totalMulti,
                                            sst.winStreak,
                                            sst.delta,
                                            sst.final))
                
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
                                          event.table.runConf.gslam,
                                          seatWinloseDetails)
            self._curRound.gameWinlose(winloseDetail)
        self._curRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
        self._clearReplayRound()
        
    def _clearReplayRound(self):
        toRemove = []
        for roundId, (gameRound, _) in self._roundMap.iteritems():
            delta = pktimestamp.getCurrentTimestamp() - (gameRound.gameOverTimestamp or 0)
            if delta > 120:
                toRemove.append(roundId)
        for roundId in toRemove:
            ftlog.info('ReplayTable._clearReplayRound',
                       'tableId=', self._tableCtrl.tableId,
                       'roundId=', roundId)
            del self._roundMap[roundId]
    
    def setupTable(self):
        self.table.on(GameReadyEvent, self._onGameReady)
        self.table.on(GameStartEvent, self._onGameStart)
        
        self.table.on(CallEvent, self._onCall)
        self.table.on(WildCardEvent, self._onWildCard)
        self.table.on(CurOpSeatMoveEvent, self._onCurOpSeatMove)
        
        self.table.on(NongminJiabeiEvent, self._onNongminJiabei)
        self.table.on(DizhuJiabeiEvent, self._onDizhuJiabei)

        self.table.on(OutCardEvent, self._onOutCard)
        self.table.on(ShowCardEvent, self._onShowCards)
        
        self.table.on(ThrowEmojiEvent, self._onThrowEmoji)
        self.table.on(TuoguanEvent, self._onTuoguan)
        self.table.on(ChatEvent, self._onChat)
        
        self.table.on(GameRoundOverEvent, self._onGameRoundOver)
        self.table.on(GameRoundAbortEvent, self._onGameRoundAbort)


