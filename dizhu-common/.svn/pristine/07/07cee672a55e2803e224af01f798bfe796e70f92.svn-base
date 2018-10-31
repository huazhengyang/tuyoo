# -*- coding:utf-8 -*-
'''
Created on 2017年1月5日

@author: zhaojiangang
'''
from dizhucomm.core.base import TableState, TableStateMachine
from dizhucomm.core.events import TableEvent
from dizhucomm.core.playmode import PlayMode
from dizhucomm.core.state import TableStatePlaying, TableStateIdle, \
    TableStateCalling, TableStateFinal, TableStateNongminJiabei, \
    TableStateDizhuJiabei
from freetime.util import log as ftlog
from dizhucomm import playmodes
from dizhucomm.playmodes import cardcenter


class LaiziActions(object):
    @classmethod
    def wildCardAction(cls, cmd):
        cmd.playMode.wildCard(cmd.table)
        return TableState.STATE_CONTINUE

class WildCardEvent(TableEvent):
    def __init__(self, table, wildCard, wildCardBig):
        super(WildCardEvent, self).__init__(table)
        self.wildCard = wildCard
        self.wildCardBig = wildCardBig

class TableStatePlayingLaizi(TableStatePlaying):
    def __init__(self):
        super(TableStatePlayingLaizi, self).__init__()
        self._addEntryAction(LaiziActions.wildCardAction)
        
class PlayModeLaizi(PlayMode):
    def __init__(self, name=playmodes.PLAYMODE_LAIZI, cardRule=cardcenter.cardRuleLaizi, seatCount=3):
        super(PlayModeLaizi, self).__init__(name, cardRule, seatCount)

    def wildCard(self, table):
        wildCard = self.cardRule.randomWildPoint()
        gameRound = table.gameRound
        gameRound.wildCard = wildCard
        wildCardBig = self.cardRule.changeCardToWildCard(wildCard, 0)
        gameRound.wildCardBig = wildCardBig
        for seat in gameRound.seats:
            self._changeWildCards(seat.status.cards, wildCardBig)
        self._changeWildCards(gameRound.baseCards, wildCardBig)
        ftlog.info('Table wildCard',
                   'tableId=', table.tableId,
                   'roundId=', gameRound.roundId,
                   'wildCard=', wildCard,
                   'wildCardBig=', wildCardBig,
                   'seatCards=', [seat.status.cards for seat in gameRound.seats],
                   'baseCards=', gameRound.baseCards,
                   'firstCallSeat=', gameRound.firstCallSeat.seatId)
        table.fire(WildCardEvent(table, wildCard, wildCardBig))
        
    def _changeToRealCards(self, table, cards):
        realCards = []
        for c in cards:
            if self.cardRule.isWildCard(c):
                if ftlog.is_debug():
                    ftlog.info('ChangeToRealCards',
                               'tableId=', table.tableId,
                               'roundId=', table.gameRound.roundId,
                               'wildCard=', table.gameRound.wildCard,
                               'card=', c,
                               'realCard=', table.gameRound.wildCardBig)
                c = table.gameRound.wildCardBig
            realCards.append(c)
        return realCards
    
    def _changeWildCards(self, cards, wildCard):
        for i, c in enumerate(cards):
            if self.cardRule.isSamePointCard(c, wildCard):
                cards[i] = wildCard
    
class TableStateMachineLaizi(TableStateMachine):
    def __init__(self):
        super(TableStateMachineLaizi, self).__init__()
        self.addState(TableStateIdle())
        self.addState(TableStateNongminJiabei())
        self.addState(TableStateDizhuJiabei())
        self.addState(TableStateCalling())
        self.addState(TableStatePlayingLaizi())
        self.addState(TableStateFinal())


class PlayModeQuickLaizi(PlayMode):
    def __init__(self, name=playmodes.PLAYMODE_QUICKLAIZI, cardRule=cardcenter.cardRuleQuickLaizi, seatCount=3):
        super(PlayModeQuickLaizi, self).__init__(name, cardRule, seatCount)

    def wildCard(self, table):
        wildCard = self.cardRule.randomWildPoint()
        gameRound = table.gameRound
        gameRound.wildCard = wildCard
        wildCardBig = self.cardRule.changeCardToWildCard(wildCard, 0)
        gameRound.wildCardBig = wildCardBig
        for seat in gameRound.seats:
            self._changeWildCards(seat.status.cards, wildCardBig)
        self._changeWildCards(gameRound.baseCards, wildCardBig)
        ftlog.info('Table wildCard', 'tableId=', table.tableId, 'roundId=', gameRound.roundId, 'wildCard=', wildCard,
                   'wildCardBig=', wildCardBig, 'seatCards=', [seat.status.cards for seat in gameRound.seats],
                   'baseCards=', gameRound.baseCards, 'firstCallSeat=', gameRound.firstCallSeat.seatId)
        table.fire(WildCardEvent(table, wildCard, wildCardBig))

    def _changeToRealCards(self, table, cards):
        realCards = []
        for c in cards:
            if self.cardRule.isWildCard(c):
                if ftlog.is_debug():
                    ftlog.info('ChangeToRealCards', 'tableId=', table.tableId, 'roundId=', table.gameRound.roundId,
                               'wildCard=', table.gameRound.wildCard, 'card=', c, 'realCard=',
                               table.gameRound.wildCardBig)
                c = table.gameRound.wildCardBig
            realCards.append(c)
        return realCards

    def _changeWildCards(self, cards, wildCard):
        for i, c in enumerate(cards):
            if self.cardRule.isSamePointCard(c, wildCard):
                cards[i] = wildCard

SM_LAIZI = TableStateMachineLaizi()
PLAY_MODE_LAIZI = PlayModeLaizi()
PLAY_MODE_QUICKLAIZI = PlayModeQuickLaizi()

