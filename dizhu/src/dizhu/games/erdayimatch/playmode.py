# -*- coding:utf-8 -*-
'''
Created on 2017年2月20日

@author: zhaojiangang
'''
import random
from dizhucomm.core.const import CallResult
from dizhucomm.core.exceptions import BadCallException
from dizhucomm.core.playmode import PlayMode, GameRound
from dizhucomm.core.policies import TuoguanPolicyDefault, FirstCallPolicy, \
    CallPolicy, SendCardsPolicy, GameResult
from dizhucomm.playmodes.base import SettlementPolicyMatch
import freetime.util.log as ftlog
from dizhucomm.playmodes import cardcenter


class CallPolicyErdayi(CallPolicy):
    '''
    叫地主策略
    '''
    _VALID_CALLS = [1, 2, 3]
    
    def call(self, table, callValue, oper):
        curOpSeat = table.gameRound.curOpSeat
        assert(not table.gameRound.callList)
        # AI不能叫地主
        assert(not curOpSeat.player.isAI)
        
        # 必须是1-3分
        if callValue not in self._VALID_CALLS:
            raise BadCallException()
        table.gameRound.addCall(table.gameRound.curOpSeat, callValue)
        table.gameRound.callMulti = callValue
        table.gameRound.dizhuSeat = table.gameRound.curOpSeat
        return CallResult.FINISH, None
    
class FirstCallPolicyErdayi(FirstCallPolicy):
    def chooseFirstCall(self, table):
        seats = []
        for seat in table.seats:
            if seat.player and not seat.player.isAI:
                seats.append(seat)
        return random.choice(seats)

class TuoguanPolicyErdayi(TuoguanPolicyDefault):
    def callValueForTuoguan(self, table, seat):
        assert(not seat.player.isAI)
        return 1

class SendCardPolicyErdayi(SendCardsPolicy):
    def sendCards(self, table):
        for i, seat in enumerate(table.gameRound.seats):
            seat.status.cards = table.matchTableInfo['cards'][i][:]
        table.gameRound.baseCards = table.matchTableInfo['cards'][-1][:]
        table.gameRound.baseCardMulti = 1

class SettlementPolicyErdayiMatch(SettlementPolicyMatch):
    def __init__(self):
        super(SettlementPolicyErdayiMatch, self).__init__()
    
    def _calcWinlose(self, result):
        assert(result.dizhuStatement)
        for sst in result.seatStatements:
            if sst != result.dizhuStatement:
                # 地主输赢本农民的积分
                seatWinlose = sst.seat.status.totalMulti * result.baseScore
                ftlog.debug('SettlementPolicyErdayiMatch._calcWinlose',
                            'roundId=', result.gameRound.roundId,
                            'userId=', sst.seat.userId,
                            'result=', (type(result.gameRound.result), result.gameRound.result),
                            'seatWinlose=', (type(seatWinlose), seatWinlose))
                # 本农民输赢积分
                seatDelta = seatWinlose if result.gameRound.result == GameRound.RESULT_NONGMIN_WIN else -seatWinlose
                sst.delta = seatDelta
                result.dizhuStatement.delta -= seatDelta

    def _forGameAbort(self, gameRound):
        result = GameResult(gameRound)
        # 所有人都输1倍
        for sst in result.seatStatements:
            sst.delta -= result.baseScore
        self._settlement(result)
        return result

class PlayModeErdayi(PlayMode):
    def __init__(self, name='erdayi', cardRule=cardcenter.cardRuleNormal, seatCount=3):
        super(PlayModeErdayi, self).__init__(name, cardRule, seatCount)

PLAYMODE_ERDAYI = PlayModeErdayi()


