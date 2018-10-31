# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
from dizhucomm.core.events import GameReadyEvent, OutCardEvent, \
    GameRoundOverEvent, GameRoundAbortEvent, SeatOnlineChanged, TuoguanEvent
from dizhucomm.replay.codec import BaseCodec
from dizhucomm.replay.gameround import GameReadyOp, GameChatOp, GameRobotOp, \
    GameShowOp, GameNextOp, GameCallOp, GameJiabeiOp, GameStartOp, GameWildCardOp, \
    GameOutCardOp, GameAbortOp, GameWinloseOp
from dizhucomm.servers.util.rpc import comm_table_remote
from freetime.util import log as ftlog
from poker.entity.biz import bireport


class GameReadyOpCodecDictComplain(BaseCodec):
    def __init__(self, gameRound=None):
        self.gameRound = gameRound
        
    def encode(self, op):
        seats = []
        for i, seat in enumerate(self.gameRound.seats):
            seats.append({
                'seatIndex':i,
                'userId':seat.userId,
                'cards':op.seatCards[i]
            })
        return {
            'action':op.action,
            'baseCards':op.baseCards,
            'seats':seats,
            'baseMulti':self.gameRound.roomMulti,
            'roomFee':self.gameRound.roomFee
        }
        
class GameChatOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'isFace':op.isFace,
            'voiceIdx':op.voiceIdx,
            'msg':op.msg
        }
    
class GameRobotOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'isRobot':op.isRobot
        }
        
class GameShowOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'showMulti':op.showMulti
        }

class GameNextOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'nextSeatIndex':op.seatIndex,
            'grab':op.grab
        }
    
class GameCallOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'call':op.call
        }

class GameJiabeiOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'jiabei':op.jiabei
        }
 
class GameStartOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'dizhuseatIndex':op.dizhuSeatIndex,
            'seatCards':op.seatCards
        }
        
class GameWildCardOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'wildCard':op.wildCard,
            'seatCards':op.seatCards
        }
    
class GameOutCardOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'outCards':op.outCards
        }

class GameAbortOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action
        }
    
class GameWinloseOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        winlose = {}
        winlose['zhadanMulti'] = pow(2, op.winloseDetail.bombCount)
        winlose['chuntianMulti'] = 2 if op.winloseDetail.isChuntian else 1,
        winlose['mingpaiMulti'] = op.winloseDetail.showMulti
        winlose['baseCardMulti'] = op.winloseDetail.baseCardMulti
        winlose['callMulti'] = op.winloseDetail.callMulti
        winloses = []
        for seatWinloseDetail in op.winloseDetail.seatWinloseDetails:
            winloses.append({
                'deltaChip':seatWinloseDetail.deltaChip,
                'finalChip':seatWinloseDetail.finalChip
            })
        winlose['winloses'] = winloses
        return {
            'action':op.action,
            'winlose':winlose
        }

class SeatCodecDictComplain(BaseCodec):
    def encode(self, obj):
        return {
            'uid':obj.userId,
            'name':obj.userName,
            'sex':obj.sex,
            'vip':obj.vipLevel,
            'chip':obj.chip,
            'score':obj.score,
            'img':obj.headUrl,
            'wItems':obj.wearedItems
        }
    
class GameReplayRoundCodecDictComplain(BaseCodec):
    def __init__(self):
        self.gameReadyCodec = GameReadyOpCodecDictComplain()
        self.opCodecMap = {
            GameReadyOp.ACTION:self.gameReadyCodec,
            GameChatOp.ACTION:GameChatOpCodecDictComplain(),
            GameRobotOp.ACTION:GameRobotOpCodecDictComplain(),
            GameShowOp.ACTION:GameShowOpCodecDictComplain(),
            GameNextOp.ACTION:GameNextOpCodecDictComplain(),
            GameCallOp.ACTION:GameCallOpCodecDictComplain(),
            GameJiabeiOp.ACTION:GameJiabeiOpCodecDictComplain(),
            GameStartOp.ACTION:GameStartOpCodecDictComplain(),
            GameWildCardOp.ACTION:GameWildCardOpCodecDictComplain(),
            GameOutCardOp.ACTION:GameOutCardOpCodecDictComplain(),
            GameAbortOp.ACTION:GameAbortOpCodecDictComplain(),
            GameWinloseOp.ACTION:GameWinloseOpCodecDictComplain()
        }
    
    def encode(self, obj):
        self.gameReadyCodec.gameRound = obj
        return {
            'roomId':obj.roomId,
            'matchId':obj.matchId,
            'tableId':obj.tableId,
            'number':obj.roundId,
            'ops':self._encodeOps(obj.ops)
        }
    
    def findOpCodec(self, action):
        return self.opCodecMap.get(action)
    
    def _encodeOps(self, ops):
        opsDicts = []
        for op in ops:
            codec = self.findOpCodec(op.action)
            if not codec:
                ftlog.warn('GameReplayRoundCodecDictComplain._encodeOps UnknownAction',
                           'action=', op.action)
                continue
            opsDicts.append(codec.encode(op))
        return opsDicts
    
class BIReportTable(object):
    def __init__(self, tableCtrl):
        self._tableCtrl = tableCtrl
        self._complainCodec = GameReplayRoundCodecDictComplain()

    @property
    def table(self):
        return self._tableCtrl.table
    
    def setupTable(self):
        self.table.on(GameReadyEvent, self._onGameReady)
        self.table.on(OutCardEvent, self._onOutCard)
        self.table.on(GameRoundOverEvent, self._onGameRoundOver)
        self.table.on(GameRoundAbortEvent, self._onGameRoundAbort)
        self.table.on(SeatOnlineChanged, self._onSeatOnlineChanged)
        self.table.on(TuoguanEvent, self._onTuoguan)

    def _onGameReady(self, event):
        if ftlog.is_debug():
            ftlog.debug('BIReportTable._onGameReady',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        
        userIds = []
        for seat in event.table.seats:
            userIds.append(seat.userId)
            finalTableChip, finalUserChip = comm_table_remote.getUserChips(event.table.gameId,
                                                                           seat.userId,
                                                                           event.table.tableId)
            try:
                roomId = event.table.roomId
                # 金币场混房
                if hasattr(seat.player, 'mixConf') and seat.player.mixConf.get('roomId'):
                    roomId = seat.player.mixConf.get('roomId')
                # 红包赛混房
                if hasattr(seat.player, 'mixId') and seat.player.mixId and seat.player.mixId.isdigit():
                    roomId = int(seat.player.mixId)
                bireport.reportGameEvent('TABLE_START',
                                         seat.userId,
                                         event.table.gameId,
                                         roomId,
                                         event.table.tableId,
                                         event.table.gameRound.roundNum,
                                         0, 0, 0, [],
                                         seat.player.clientId,
                                         finalTableChip, finalUserChip)
            except:
                ftlog.error('BIReportTable._onGameReady',
                            'tableId=', event.table.tableId,
                            'seat=', (seat.userId, seat.seatId))

        # cards = event.seatCards[:]
        # cards.extend(event.baseCards)
        # bireport.tableStart(event.table.gameId,
        #                     event.table.roomId,
        #                     event.table.tableId,
        #                     event.table.gameRound.roundId,
        #                     userIds,
        #                     cards,
        #                     event.table.gameRound.baseCardMulti,
        #                     event.table.gameRound.baseCardType)

    def _onOutCard(self, event):
        cards = event.validCards.cards if event.validCards else []

        if ftlog.is_debug():
            ftlog.debug('BIReportTable._onOutCard',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'cards=', cards)

        bireport.reportCardEvent('TABLE_CARD',
                                 event.seat.userId,
                                 event.table.gameId,
                                 event.table.roomId,
                                 event.table.tableId,
                                 event.table.gameRound.roundNum,
                                 0, 0, 0,
                                 cards,
                                 event.seat.player.clientId,
                                 0, 0)

    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('BIReportTable._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        
        # userIds = []
        # sfeealls = [event.table.gameId, event.table.roomId, event.table.tableId, [], []]
        # for sst in event.gameResult.seatStatements:
        #     userIds.append(sst.seat.userId)
        #     sfeealls[3].append(sst.feeMulti)
        #     sfeealls[3].append(sst.fee)
        #     sfeealls[4].append(sst.seat.userId)
        #     sfeealls[4].append(sst.delta)
        # bireport.tableRoomFee(event.table.gameId, sfeealls)
        # bireport.tableWinLose(event.table.gameId,
        #                       event.table.roomId,
        #                       event.table.tableId,
        #                       event.gameResult.gameRound.roundId,
        #                       userIds,
        #                       self._complainCodec.encode(self._tableCtrl.replay.curRound))
        
        for sst in event.gameResult.seatStatements:
            roomId = event.table.roomId
            kickOutCoin = event.table.room.roomConf.get('kickOutCoin', 0)
            if hasattr(sst.seat.player, 'mixConf') and sst.seat.player.mixConf.get('roomId'):
                roomId = sst.seat.player.mixConf.get('roomId')
                kickOutCoin = sst.seat.player.mixConf.get('kickOutCoin', 0)

            # 红包赛混房
            if hasattr(sst.seat.player, 'mixId') and sst.seat.player.mixId and sst.seat.player.mixId.isdigit():
                roomId = int(sst.seat.player.mixId)
            # 房间内破产标志
            userRoomBust = 0
            if kickOutCoin > 0 and int(sst.final) < kickOutCoin:
                userRoomBust = 1
            if ftlog.is_debug():
                ftlog.debug('BIReportTable._onGameRoundOver',
                            'userId=', sst.seat.userId,
                            'gameId=', event.table.gameId,
                            'roomId=', roomId,
                            'tableId=', event.table.tableId,
                            'userRoomBust=', userRoomBust,
                            'final=', int(sst.final),
                            'chip=', int(sst.seat.player.chip))

            bireport.reportGameEvent('TABLE_WIN',
                                     sst.seat.userId,
                                     event.table.gameId,
                                     roomId,
                                     event.table.tableId,
                                     event.gameResult.gameRound.roundNum,
                                     sst.delta, 1 if sst.isPunish else 0, 0,
                                     [userRoomBust],  # 房间内破产
                                     sst.seat.player.clientId,
                                     int(sst.final),
                                     int(sst.seat.player.chip))
        
    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('BIReportTable._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])


    def _onSeatOnlineChanged(self, event):
        if ftlog.is_debug():
            ftlog.debug('BIReportTable._onSeatOnlineChanged',
                        'tableId=', event.table.tableId,
                        'userId=', event.seat.userId,
                        'seatId=', event.seat.seatId,
                        'online=', event.seat.player.online)
        try:
            roomId = event.table.roomId
            if hasattr(event.seat.player, 'mixConf') and event.seat.player.mixConf.get('roomId'):
                roomId = event.seat.player.mixConf.get('roomId')
            # 红包赛混房
            if hasattr(event.seat.player, 'mixId') and event.seat.player.mixId and event.seat.player.mixId.isdigit():
                roomId = int(event.seat.player.mixId)
            bireport.reportGameEvent('SEAT_ONLINE_CHANGED',
                                     event.seat.userId,
                                     event.table.gameId,
                                     roomId,
                                     event.table.tableId,
                                     event.table.gameRound.roundNum if event.table.gameRound else 0,
                                     0, 1 if event.seat.player.online else 2, 0, [],
                                     event.seat.player.clientId,
                                     0, 0)
        except:
            ftlog.error('BIReportTable._onSeatOnlineChanged',
                        'tableId=', event.table.tableId,
                        'userId=', event.seat.userId,
                        'seatId=', event.seat.seatId,
                        'online=', event.seat.player.online)

    def _onTuoguan(self, event):
        isQuit = 0
        if hasattr(event.seat.player, 'isQuit'):
            isQuit = 1 if event.seat.player.isQuit else 0
        if ftlog.is_debug():
            ftlog.debug('BIReportTable._onTuoguan',
                        'tableId=', event.table.tableId,
                        'userId=', event.seat.userId,
                        'seatId=', event.seat.seatId,
                        'isQuit=', isQuit,
                        'oper=', event.oper,
                        'isTuoguan=', event.isTuoguan,
                        'location=', event.location)
        try:
            roomId = event.table.roomId
            if hasattr(event.seat.player, 'mixConf') and event.seat.player.mixConf.get('roomId'):
                roomId = event.seat.player.mixConf.get('roomId')
            # 红包赛混房
            if hasattr(event.seat.player, 'mixId') and event.seat.player.mixId and event.seat.player.mixId.isdigit():
                roomId = int(event.seat.player.mixId)

            bireport.reportGameEvent('SEAT_TUOGUAN',
                                     event.seat.userId,
                                     event.table.gameId,
                                     roomId,
                                     event.table.tableId,
                                     event.table.gameRound.roundNum if event.table.gameRound else 0,
                                     0, 1 if event.isTuoguan else 0, event.oper, [isQuit, event.location],
                                     event.seat.player.clientId,
                                     0, 0)
        except:
            ftlog.error('BIReportTable._onTuoguan',
                        'tableId=', event.table.tableId,
                        'userId=', event.seat.userId,
                        'seatId=', event.seat.seatId,
                        'isQuit=', isQuit,
                        'oper=', event.oper,
                        'isTuoguan=', event.isTuoguan,
                        'location=', event.location)