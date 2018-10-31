# coding=UTF-8
'''
'''
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
from freetime.util import log as ftlog
from dizhu.entity import dizhuconf


class DizhuLaiZiGamePlay(DizhuBaseGamePlay):
    

    def __init__(self, table):
        super(DizhuLaiZiGamePlay, self).__init__(table)


    def getPlayMode(self):
        return dizhuconf.PLAYMODE_LAIZI


    def _gameStartAfter(self):
        self._doWildCard()


    def _changeToRealCard(self, card):
        if self.card.isWildCard(card):
            return self.table.status.wildCardBig
        return card


    def _outCard(self, player, seat, cards):
        # 将玩家的手牌减去出的牌
        sseat = seat.cards[:]
        ftlog.debug('_outCard before->', sseat, cards)
        wildCardBig = self.table.status.wildCardBig
        for i in xrange(len(cards)):
            toRemoveCard = cards[i]
            if self.card.isWildCard(toRemoveCard):
                toRemoveCard = wildCardBig
            if toRemoveCard in sseat:
                sseat.remove(toRemoveCard)
            else:
                ftlog.warn('outCard error: cards=', cards, ' seatCards=',
                           seat.cards, ' wildCardBig=', wildCardBig,
                           ' card[', i, ']=', cards[i], ' toRemoveCard=', toRemoveCard, ' not found ')
                if cards[i] in sseat:
                    sseat.remove(cards[i])
        seat.cards = sseat
        ftlog.debug('_outCard after->', sseat)


    def _doWildCard(self):
        card = self.card.randomWildCard()
        wildCardBig = self.card.changeCardToWildCard(card, 0)
        self.table.status.wildCardBig = wildCardBig
        self.table.status.wildCard = self.card.pointToCard(self.card.cardToPoint(wildCardBig))
        
        for seat in self.table.seats:
            cards = seat.cards
            for j in xrange(len(cards)):
                if self.card.isSamePointCard(cards[j], wildCardBig):
                    cards[j] = wildCardBig
        basecards = self.table.status.baseCardList
        for i in xrange(len(basecards)):
            if self.card.isSamePointCard(basecards[i], wildCardBig):
                basecards[i] = wildCardBig

        self.sender.sendWildCardRes(self.table.status.wildCard, wildCardBig)
        seatCards = []
        for seat in self.table.seats:
            seatCards.append(seat.cards)
        self.table.gameRound.wildCard(wildCardBig, seatCards, basecards[:])

