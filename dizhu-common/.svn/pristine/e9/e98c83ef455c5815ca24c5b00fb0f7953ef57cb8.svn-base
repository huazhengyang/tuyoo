# -*- coding:utf-8 -*-
'''
Created on 2017年2月14日

@author: zhaojiangang
'''
import math
import random

from dizhucomm import playmodes
from dizhucomm.core.const import CallResult
from dizhucomm.core.exceptions import BadCallException
from dizhucomm.core.playmode import PlayMode, GameRound
from dizhucomm.core.policies import CallPolicy, SendCardsPolicy
from dizhucomm.playmodes import cardcenter
from freetime.util import log as ftlog

class CallPolicyErdou(CallPolicy):
    def call(self, table, callValue, oper):
        '''
        玩家叫地主
        @return: (CallResult, NextCallSeat)
        '''
        gameRound = table.gameRound
        seats = gameRound.seats
        assert(len(seats) == 2)
        assert(gameRound.curOpSeat)
        # 有状态机控制，必须<5
        assert(len(gameRound.callList) < 5)
        # 必须是0, 或则1
        # 老版本是当前的倍数或者当前+1
        if callValue < 0 or callValue > math.pow(2, len(gameRound.callList)) * table.runConf.firstCallValue:
            raise BadCallException()
        
        callValue = min(callValue, 1)
        gameRound.addCall(gameRound.curOpSeat, callValue)
        if callValue > 0:
            if len(gameRound.effectiveCallList) == 1:
                gameRound.callMulti = table.runConf.firstCallValue
            else:
                if table.runConf.rangpaiMultiType == 1:
                    gameRound.callMulti += 1
                else:
                    gameRound.callMulti *= 2

        # 还有人没叫
        if len(gameRound.callList) < 2:
            return CallResult.CALLING, gameRound.curOpSeat.next
        
        # 所有人都叫过地主了, 如果没人叫则流局
        if not gameRound.lastEffectiveCall:
            return CallResult.ABORT, None
        
        if callValue > 0:
            gameRound.rangpai = gameRound.rangpai+1
            
        # 有人不叫或者叫过5次以上就结束
        if callValue == 0 or len(gameRound.callList) >= 5:
            gameRound.dizhuSeat = gameRound.lastEffectiveCall[0]
            return CallResult.FINISH, None
        
        # 有人已经放弃了叫地主
        if gameRound.callList[-2][1] == 0:
            gameRound.dizhuSeat = gameRound.lastEffectiveCall[0]
            return CallResult.FINISH, None
        
        return CallResult.CALLING, gameRound.curOpSeat.next

class SendCardsPolicyErdou(SendCardsPolicy):
    '''
    发牌策略
    '''
    _cards = [0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12,
              13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25,
              26, 27, 30, 31, 32, 33, 34, 35, 36, 37, 38,
              39, 40, 43, 44, 45, 46, 47, 48, 49, 50, 51,
              52, 53]
    
    def sendCards(self, table):
        seats = table.gameRound.seats
        assert(len(seats) == 2)
        cards = self._cards[:]
        random.shuffle(cards)
        seats[0].status.cards = cards[0:17]
        seats[1].status.cards = cards[17:34]
        table.gameRound.baseCards = cards[34:37]
        kickOutCards = [2, 3, 15, 16, 28, 29, 41, 42]
        kickOutCards.extend(cards[37:])
        table.gameRound.kickoutCards = kickOutCards

class PlayModeErdou(PlayMode):
    def __init__(self, name=playmodes.PLAYMODE_ERDOU, cardRule=cardcenter.cardRuleNormal, seatCount=2):
        super(PlayModeErdou, self).__init__(name, cardRule, seatCount)

    def _calcRangpaiMulti(self, gameRound):
        if ftlog.is_debug():
            ftlog.debug('PlayModeErdou._calcRangpaiMulti',
                        'tableId=', gameRound.table.tableId,
                        'result=', gameRound.result,
                        'cardCount=', len(gameRound.curOpSeat.status.cards),
                        'rangpai=', gameRound.rangpai)
        if gameRound.result == GameRound.RESULT_NONGMIN_WIN:
            cardCount = len(gameRound.curOpSeat.status.cards)
            if cardCount < gameRound.rangpai:
                return gameRound.rangpai - cardCount + 1
        return 1
    
    def _isGameOver(self, table):
        if table.gameRound.curOpSeat == table.gameRound.dizhuSeat:
            return len(table.gameRound.curOpSeat.status.cards) == 0
        else:
            return len(table.gameRound.curOpSeat.status.cards) <= table.gameRound.rangpai


PLAY_MODE_ERDOU = PlayModeErdou()