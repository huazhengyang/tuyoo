# -*- coding=utf-8
'''
Created on 2015年3月30日

@author: zhaojiangang
'''
import random

from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from dizhu.entity.dizhuconf import DIZHU_GAMEID


class SendCardPolicy(object):
    def sendCards(self, tableId, userIds):
        pass
    
    @classmethod
    def decodeCards(cls, cardsStr):
        ret = set()
        cards = cardsStr.split(',')
        for c in cards:
            card = int(c.strip())
            if card < 0 or card >= 54:
                raise Exception('card must in [0, 54)')
            ret.add(card)
        return ret
    
class SendCardPolicyUserId(SendCardPolicy):
    __instance = None

    @classmethod
    def getInstance(self):
        if not self.__instance:
            self.__instance = SendCardPolicyUserId()
        return self.__instance

    def sendCards(self, tableId, userIds):
        from poker.entity.configure import gdata
        if gdata.mode() == gdata.RUN_MODE_ONLINE:
            return None

        final_bcards = []
        allCards = set([c for c in xrange(54)])
        if len(userIds) == 2:
            kick_out_card = set([2, 3, 15, 16, 28, 29, 41, 42])
            allCards -= kick_out_card
        ret = [[] for _ in xrange(len(userIds) + 1)]
        changed = False
        try:
            for i, userId in enumerate(userIds):
                cards, bcards = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['test.cards', 'test.bcards'])
                if cards:
                    changed = True
                    cards = self.decodeCards(cards)
                    if len(cards) > 17:
                        cards = cards[0:17]
                    cards = self.__sendCards(cards, allCards)
                    cards = self.__buqiCards(cards, allCards, 17)
                    ret[i] = list(cards)

                if not final_bcards and bcards:
                    final_bcards = self.decodeCards(bcards)
                    if len(final_bcards) > 3:
                        final_bcards = final_bcards[0:3]

            if final_bcards:
                changed = True
                final_bcards = self.__sendCards(final_bcards, allCards)
                final_bcards = self.__buqiCards(final_bcards, allCards, 3)
                ret[-1] = list(final_bcards)

            if changed:
                for i in xrange(len(userIds)):
                    if not ret[i] or len(ret[i]) != 17:
                        ret[i] = list(self.__buqiCards(ret[i], allCards, 17))
                return ret
            return None

        except:
            ftlog.error('sendCards.sendCardsToAllUserIds error')
        return None
    
    @classmethod
    def __buqiCards(cls, cards, allCards, count):
        if not cards:
            cards = set()
        diffCount = count - len(cards)
        if diffCount > 0:
            for _ in xrange(diffCount):
                if len(allCards) > 0:
                    allCardList = list(allCards)
                    index = random.randint(0, len(allCardList) - 1)
                    c = allCardList[index]
                    cards.add(c)
                    allCards.remove(c)
        return cards

    @classmethod
    def __sendCards(cls, needCards, allCards):
        cards = set()
        for c in needCards:
            if c in allCards:
                cards.add(c)
                allCards.remove(c)
        return cards
    
