import random

from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from dizhu.entity.dizhuconf import DIZHU_GAMEID

def sendCards(self, tableId, userIds):
    from poker.entity.configure import gdata
    if gdata.mode() == gdata.RUN_MODE_ONLINE:
        return None

    final_bcards = []
    allCards = set([c for c in xrange(54)])
    if len(userIds) == 2:
        kick_out_card = set([2, 3, 15, 16, 28, 29, 41, 42])
        allCards -= kick_out_card
    ret = [None for _ in xrange(len(userIds) + 1)]
    try:
        for i, userId in enumerate(userIds):
            cards, bcards = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['test.cards', 'test.bcards'])
            if cards:
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
            final_bcards = self.__sendCards(final_bcards, allCards)

        final_bcards = self.__buqiCards(final_bcards, allCards, 3)
        ret[-1] = list(final_bcards)

        # for i in xrange(len(userIds)):
        #     if not ret[i] or len(ret[i]) != 17:
        #         ret[i] = list(self.__buqiCards(ret[i], allCards, 17))

        return ret if ret else None

    except:
        ftlog.error('sendCards.sendCardsToAllUserIds error')
    return None


from dizhu.gamecards.sendcard import SendCardPolicyUserId
SendCardPolicyUserId.sendCards = sendCards

ftlog.info('dizhu/hotfix/h_2017_11_03_sendcard.py hotfix ok')