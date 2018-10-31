# -*- coding:utf-8 -*-
'''
Created on 2016年12月1日

@author: zhaojiangang
'''
from dizhucomm.utils.obser import EventBase


class TableEvent(EventBase):
    def __init__(self, table):
        super(TableEvent, self).__init__()
        self.table = table


class RoomEvent(EventBase):
    def __init__(self, room):
        super(RoomEvent, self).__init__()
        self.room = room


class SeatOnlineChanged(TableEvent):
    def __init__(self, table, seat):
        super(SeatOnlineChanged, self).__init__(table)
        self.seat = seat
        
class SitdownEvent(TableEvent):
    def __init__(self, table, seat, player, isNextBuyin=False):
        super(SitdownEvent, self).__init__(table)
        self.seat = seat
        self.player = player
        self.isNextBuyin = isNextBuyin
        
class StandupEvent(TableEvent):
    def __init__(self, table, seat, player, reason):
        super(StandupEvent, self).__init__(table)
        self.seat = seat
        self.player = player
        self.reason = reason

class GiveupEvent(TableEvent):
    def __init__(self, table, seat):
        super(GiveupEvent, self).__init__(table)
        self.seat = seat
        
class SeatReadyEvent(TableEvent):
    def __init__(self, table, seat):
        super(SeatReadyEvent, self).__init__(table)
        self.seat = seat
          
class GameReadyEvent(TableEvent):
    def __init__(self, table, seatCards, baseCards, firstCallSeat):
        super(GameReadyEvent, self).__init__(table)
        self.seatCards = seatCards
        self.baseCards = baseCards
        self.firstCallSeat = firstCallSeat
        
class CurOpSeatMoveEvent(TableEvent):
    def __init__(self, table, prevOpSeat, curOpSeat, optime, autoOp):
        super(CurOpSeatMoveEvent, self).__init__(table)
        self.prevOpSeat = prevOpSeat
        self.curOpSeat = curOpSeat
        self.optime = optime
        self.autoOp = autoOp
        
class CallEvent(TableEvent):
    def __init__(self, table, seat, callValue, oper, callResult):
        super(CallEvent, self).__init__(table)
        self.seat = seat
        self.callValue = callValue
        self.oper = oper
        self.callResult = callResult
        
class CallTimeoutEvent(TableEvent):
    def __init__(self, table, seat):
        super(CallTimeoutEvent, self).__init__(table)
        self.seat = seat

class GameStartEvent(TableEvent):
    def __init__(self, table):
        super(GameStartEvent, self).__init__(table)
        
class OutCardEvent(TableEvent):
    '''
    @param prevCards: 出牌之前的牌型
    '''
    def __init__(self, table, seat, validCards, prevCards, oper):
        super(OutCardEvent, self).__init__(table)
        self.seat = seat
        self.validCards = validCards
        self.prevCards = prevCards
        self.oper = oper

class GameClearEvent(TableEvent):
    def __init__(self, table, reason):
        super(GameClearEvent, self).__init__(table)
        self.reason = reason
        
class OutCardTimeoutEvent(TableEvent):
    def __init__(self, table, seat):
        super(OutCardTimeoutEvent, self).__init__(table)
        self.seat = seat

class GameRoundFinishEvent(TableEvent):
    def __init__(self, table, gameResult):
        super(GameRoundFinishEvent, self).__init__(table)
        self.gameResult = gameResult
        
class GameRoundAbortEvent(TableEvent):
    def __init__(self, table, gameResult):
        super(GameRoundAbortEvent, self).__init__(table)
        self.gameResult = gameResult

class GameRoundOverEvent(TableEvent):
    def __init__(self, table, gameResult):
        super(GameRoundOverEvent, self).__init__(table)
        self.gameResult = gameResult
        
class TuoguanEvent(TableEvent):
    ''' 托管事件 '''
    def __init__(self, table, seat, isTuoguan, oper, location=0):
        # location  1: 叫地主时托管， 2： 出牌时托管
        super(TuoguanEvent, self).__init__(table)
        self.seat = seat
        self.isTuoguan = isTuoguan
        self.oper = oper
        self.location = location

class AutoPlayEvent(TableEvent):
    '''农民最后一手自动出牌事件'''
    def __init__(self, table, seat, isAutoPlay, oper):
        super(AutoPlayEvent, self).__init__(table)
        self.seat = seat
        self.isAutoPlay = isAutoPlay
        self.oper = oper
        
class StartNongminJiabeiEvent(TableEvent):
    ''' 开始农民加倍事件 '''
    def __init__(self, table):
        super(StartNongminJiabeiEvent, self).__init__(table)
        
class StartDizhuJiabeiEvent(TableEvent):
    ''' 开始地主加倍事件 '''
    def __init__(self, table):
        super(StartDizhuJiabeiEvent, self).__init__(table)

class NongminJiabeiEvent(TableEvent):
    def __init__(self, table, seat, multi, oper):
        super(NongminJiabeiEvent, self).__init__(table)
        self.seat = seat
        self.multi = multi
        self.oper = oper
        
class DizhuJiabeiEvent(TableEvent):
    def __init__(self, table, seat, multi, oper):
        super(DizhuJiabeiEvent, self).__init__(table)
        self.seat = seat
        self.multi = multi
        self.oper = oper
        
class ShowCardEvent(TableEvent):
    def __init__(self, table, seat):
        super(ShowCardEvent, self).__init__(table)
        self.seat = seat

class StartHuanpaiEvent(TableEvent):
    ''' 开始换牌事件 '''
    def __init__(self, table):
        super(StartHuanpaiEvent, self).__init__(table)

class HuanpaiOutcardsEvent(TableEvent):
    ''' 换牌的出牌事件 '''
    def __init__(self, table, seat, outCards, oper):
        super(HuanpaiOutcardsEvent, self).__init__(table)
        self.seat = seat
        self.outCards = outCards
        self.oper = oper

class HuanpaiIncardsEvent(TableEvent):
    ''' 换牌设置得到牌型事件 '''
    def __init__(self, table, seat, incards):
        super(HuanpaiIncardsEvent, self).__init__(table)
        self.seat = seat
        self.incards = incards

class HuanpaiEndEvent(TableEvent):
    def __init__(self, table, turnDirection=0):
        super(HuanpaiEndEvent, self).__init__(table)
        self.turnDirection = turnDirection
        
class ThrowEmojiEvent(TableEvent):
    ''' 互动 扔表情事件 '''
    def __init__(self, table, seatFrom, seatTo, 
                 emojiId, count, deltaChip, finalChip, 
                 charmDeltaFrom, charmDeltaTo, cdTime):
        super(ThrowEmojiEvent, self).__init__(table)
        self.seatFrom = seatFrom
        self.seatTo = seatTo
        self.emojiId = emojiId
        self.count = count
        self.deltaChip = deltaChip
        self.finalChip = finalChip
        self.charmDeltaFrom = charmDeltaFrom
        self.charmDeltaTo = charmDeltaTo
        self.cdTime = cdTime
        
class ChatEvent(TableEvent):
    ''' 聊天 '''
    def __init__(self, table, seat, isFace, voiceIdx, msg):
        super(ChatEvent, self).__init__(table)
        self.seat = seat
        self.isFace = isFace
        self.voiceIdx = voiceIdx
        self.msg = msg

class CardNoteOpenedEvent(TableEvent):
    def __init__(self, table, seat):
        super(CardNoteOpenedEvent, self).__init__(table)
        self.seat = seat

class TableTBoxOpened(TableEvent):
    def __init__(self, table, seat, data):
        super(TableTBoxOpened, self).__init__(table)
        self.seat = seat
        self.data = data


class UserMatchOverEvent(RoomEvent):
    def __init__(self, room, player, rankRewards):
        super(UserMatchOverEvent, self).__init__(room)
        self.player = player
        self.rankRewards = rankRewards

    @property
    def matchId(self):
        return self.room.match.matchId

    @property
    def sequence(self):
        sequence = int(self.player.group.instId.split('.')[1])
        return sequence

    @property
    def playerRank(self):
        return self.player.rank
