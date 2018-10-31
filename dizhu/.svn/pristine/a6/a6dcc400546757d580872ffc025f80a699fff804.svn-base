# -*- coding:utf-8 -*-
'''
Created on 2018-09-20

@author: wangyonghui
'''
import random

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games.normalbase.tableroom import DizhuPlayerNormalBase
from dizhucomm.core.cardrule import CardTypeDanPai, CardTypeDuizi, CardTypeSanzhang, CardTypeZhadan, ReducedCards, CardTypeFeijiDai1, CardTypeFeijiDai2, \
    CardTypeSanShun, CardTypeShuangShun, CardTypeDanShun, CardTypeSanDai1, CardTypeSanDai2, CardTypeHuojian
from freetime.util import log as ftlog
from poker.entity.configure import configure


class AIRule(object):
    cardCountToCardType = {
        1: CardTypeDanPai,
        2: CardTypeDuizi,
        3: CardTypeSanzhang,
        4: CardTypeZhadan
    }
    DING_POINT = 8
    # K以上就不跟了
    FOLLOW_FRIEND_MAX_POINT = 10
    # 单牌剩余A及以上就不出单牌了
    ACTIVE_MAX_POINT = 11

    HUMAN_CARDS = [
        'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
        'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
        'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
        'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
        'w', 'W'
    ]

    def __init__(self, player):
        self.player = player

    @property
    def table(self):
        return self.player.table

    @property
    def cardRule(self):
        return self.table.playMode.cardRule

    def enureWinCards(self, reducedCards):
        '''
        必胜的牌，只记牌记到A，能记住有没有炸弹
        '''
        pass

    def doActiveOutCard(self):
        cards = None
        try:
            reducedCards = ReducedCards.reduceHandCards(self.cardRule, self.player.seat.status.cards)
            cards = self._doActiveOutCard(reducedCards)
        except:
            ftlog.error('AIPlayer.doActiveOutCard',
                        'seatId=', self.player.seatId,
                        'userId=', self.player.userId,
                        'cards=', cards)
        if not cards:
            handcards = self.player.seat.status.cards
            cards = self.cardRule.findFirstValidCards(handcards)
            cards = cards.cards if cards else []
        return cards

    def doPassiveOutCard(self):
        cards = None
        try:
            reducedCards = ReducedCards.reduceHandCards(self.cardRule, self.player.seat.status.cards)
            cards = self._doPassiveOutCard(reducedCards)
        except:
            ftlog.error('AIPlayer.doPassiveOutCard',
                        'seatId=', self.player.seatId,
                        'userId=', self.player.userId,
                        'cards=', cards)
            cards = []
        return cards

    def fillCardNote(self, cardNote, cards):
        for card in cards:
            point = self.cardRule.cardToPoint(card)
            assert (point < 15)
            cardNote[point] += 1
        return cardNote

    def buildCardNote(self):
        ret = [0 for _ in xrange(15)]
        for seat in self.table.gameRound.seats:
            if seat != self.player.seat:
                self.fillCardNote(ret, seat.status.cards)
        return ret

    def isDizhu(self):
        return self.player.seat == self.table.gameRound.dizhuSeat

    def isFriend(self, seat):
        # 自己不是地主，对方不是地主，则为朋友
        return (self.player.seat != self.table.gameRound.dizhuSeat
                and seat != self.table.gameRound.dizhuSeat)

    def hasHuojian(self, cardNote):
        return cardNote[12] > 0 and cardNote[13] > 0

    def hasBiggerBomb(self, cardNote, point):
        '''
        查找是否有比point大的炸弹
        '''
        for i in range(point + 1, 13):
            if cardNote[i] >= 4:
                return True
        return False

    def hasBiggerBombOrHuojian(self, cardNote, point):
        return self.hasHuojian(cardNote) or self.hasBiggerBomb(cardNote, point)

    def findBiggerCards(self, cardNote, group):
        for i in range(group.point + 1, 15):
            if cardNote[i] >= group.cardCount:
                return i
        return -1

    def isBiggestCard(self, cardNote, group):
        '''
        检查cards是否是最大的牌
        '''
        return self.findBiggerCards(cardNote, group) != -1

    def findBiggestCards(self, reducedCards, minPoint, cardNote):
        '''
        查找手中各个牌型的最大牌，本次只查找双王，炸，单牌，对子，三张
        '''
        ret = []
        # 先查找火箭
        if (reducedCards.buckets[13].cardCount > 0
                and reducedCards.buckets[14].cardCount > 0):
            ret.append((CardTypeHuojian, [52, 53], [reducedCards.buckets[13], reducedCards.buckets[14]]))

        # 查找手中最大的group
        for group in reducedCards.buckets:
            if group.cardCount > 0 and (group.cardCount == 4 or group.point >= minPoint):
                if self.isBiggestCard(cardNote, group):
                    ret.append((self.cardCountToCardType.get(group.cardCount), group.cards[:], [group]))

        return ret

    def removeCards(self, srcCards, toRemoveCards):
        if ftlog.is_debug():
            ftlog.debug('AIPlayer.removeCards srcCards=', self.toHumanCards(srcCards),
                        'toRemoveCards=', self.toHumanCards(toRemoveCards))
        for card in toRemoveCards:
            srcCards.remove(card)
        return srcCards

    def checkBombOrHuojianWinCard(self, reducedCards, cardNote):
        if (reducedCards.buckets[13].cardCount > 0
                and reducedCards.buckets[14].cardCount > 0):
            remCards = self.removeCards(reducedCards.cards[:], [52, 53])
            if not remCards or self.cardRule.validateCards(remCards):
                return [52, 53]
        for group in reducedCards.buckets[::-1]:
            if group.cardCount == 4 and not self.hasBiggerBomb(cardNote, group.point):
                remCards = self.removeCards(reducedCards.cards[:], group.cards)
                if not remCards or self.cardRule.validateCards(remCards):
                    return group.cards[:]
        return None

    def checkWinCard(self, reducedCards, cardNote, minPoint):
        '''
        查找每个牌型最大的牌，单牌，对牌，炸弹
        '''
        # 外面有火箭，不能必胜
        if self.hasHuojian(cardNote):
            return None

        # 查找手中无敌的牌（此时不考虑炸弹，稍后再考虑）
        ret = self.findBiggestCards(reducedCards, minPoint, cardNote)
        for cardType, cards, groups in ret:
            bombPoint = -1 if cardType != CardTypeZhadan else groups[0].point
            # 有大于bombPoint的炸弹, 不是必胜的牌
            if self.hasBiggerBomb(cardNote, bombPoint):
                continue

            remCards = self.removeCards(reducedCards.cards[:], cards)
            if not remCards:
                return cards
            # 还剩一手牌
            if self.cardRule.validateCards(remCards):
                return cards
            # 三张牌可以带1张和1对
            if cardType == CardTypeSanzhang:
                remReducedCards = ReducedCards.reduceHandCards(self.cardRule, remCards)
                # 从remReducedCards中去掉1张或者一对之后还剩一手牌
                for group in remReducedCards.buckets:
                    for i in xrange(min(2, group.cardCount)):
                        # 去掉i+1张
                        if ftlog.is_debug():
                            ftlog.debug('AIPlayer.checkWinCard srcCards=', self.toHumanCards(reducedCards.cards),
                                        'biggestCards=', self.toHumanCards(cards),
                                        'remCamds=', self.toHumanCards(remCards),
                                        'toRemoveCards=', self.toHumanCards(group.cards[0:i + 1]))
                        rem1Cards = self.removeCards(remCards[:], group.cards[0:i + 1])
                        if not rem1Cards or self.cardRule.validateCards(rem1Cards):
                            return cards
        return None

    def findFirstCards(self, reducedCards, cardTypeClasses):
        for cardTypeClass in cardTypeClasses:
            cardType = self.cardRule.findCardType(cardTypeClass().typeId)
            if cardType:
                found = cardType.findMinCards(reducedCards)
                if found:
                    return found.cards
        return None

    def findNCards(self, reducedCards, n, canChaipai, reverse=False):
        '''
        查找N张点数相同的牌
        @param reverse: 是否从后往前找
        '''
        groupBuckets = reducedCards.buckets if not reverse else reducedCards.buckets[::-1]
        for group in groupBuckets:
            if (group.cardCount == n
                    or (canChaipai and group.cardCount >= n)):
                return group.cards[0:n]
        return None

    def findNCardsByGTPoint(self, reducedCards, n, point, canChaipai, reverse=False):
        '''
        查找N张点数相同的牌
        @param reverse: 是否从后往前找
        '''
        groupBuckets = reducedCards.buckets if not reverse else reducedCards.buckets[::-1]
        for group in groupBuckets:
            if (group.point > point
                    and (group.cardCount == n
                         or (canChaipai and group.cardCount >= n))):
                return group.cards[0:n]
        return None

    def findNCardsByGTPointWithMinPoint(self, reducedCards, n, point, minPoint, canChaipai, reverse=False):
        '''
        查找N张点数相同的牌
        @param reverse: 是否从后往前找
        '''
        groupBuckets = reducedCards.buckets if not reverse else reducedCards.buckets[::-1]
        for group in groupBuckets:
            if (group.point > point
                    and group.point >= minPoint
                    and (group.cardCount == n
                         or (canChaipai and group.cardCount >= n))):
                return group.cards[0:n]
        return None

    def toHumanCards(self, cards):
        ret = []
        if cards:
            for c in cards:
                ret.append(self.HUMAN_CARDS[c])
        return ret

    def checkValidCardsWithHandReducedCards(self, reducedCards):
        cards = self.cardRule.checkValidCardsWithHandReducedCards(reducedCards)
        if cards:
            cards = cards.cards
        return cards

    def _doActiveOutCard(self, reducedCards):
        cardNote = self.buildCardNote()
        if ftlog.is_debug():
            ftlog.debug('>>> AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'cardNote=', cardNote)

        cards = self.checkWinCard(reducedCards, cardNote, 11)

        if ftlog.is_debug():
            ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'checkWinCard',
                        'checkWinCard=', self.toHumanCards(cards))

        # 剩余最大一手牌+任意一手牌
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'cardNote=', cardNote,
                            'checkWinCard=', cards,
                            'desc=', 'checkWinCard',
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards

        # 剩余一手牌
        cards = self.checkValidCardsWithHandReducedCards(reducedCards)
        if ftlog.is_debug():
            ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'checkValidCardsWithHandReducedCards',
                        'cards=', self.toHumanCards(cards))
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'checkValidCardsWithHandReducedCards'
                                     'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards

        nextSeat = self.player.seat.next
        enemySeat = nextSeat if not self.isFriend(nextSeat) else self.player.seat.next.next

        if nextSeat != enemySeat:
            # 队友剩单牌，出最小的牌
            if len(nextSeat.status.cards) == 1:
                cards = self.findNCards(reducedCards, 1, True, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'PassFriend1',
                                    'out=', self.toHumanCards(cards))
                    return cards
            elif len(nextSeat.status.cards) == 2:
                # 队友剩对子，出最小的对子
                cards = self.findNCards(reducedCards, 2, False, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'PassFriend2',
                                    'out=', self.toHumanCards(cards))
                    return cards

        # 查找飞机，三顺，双顺，单顺，三带单，三带对
        cards = self.findFirstCards(reducedCards, [CardTypeFeijiDai1, CardTypeFeijiDai2, CardTypeSanShun, CardTypeShuangShun, CardTypeDanShun, CardTypeSanDai1,
                                                   CardTypeSanDai2])
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'findFirstCards',
                            'out=', self.toHumanCards(cards))
            return cards

        reverse = True if enemySeat == nextSeat else False
        enemyCardCount = len(enemySeat.status.cards)

        # 敌人报牌了
        if enemyCardCount <= 2:
            if ftlog.is_debug():
                ftlog.debug('AIPlayer._doActiveOutCard EnemyAlarm handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'enemyAlarm%s' % (enemyCardCount),
                            'enemyCardCount=', enemyCardCount)

            if enemyCardCount == 2:
                # 敌人剩双数，优先出单牌，捡小牌出
                cards = self.findNCards(reducedCards, 1, True, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'enemyAlarm%s Out1' % (enemyCardCount),
                                    'enemyCardCount=', enemyCardCount,
                                    'out=', self.toHumanCards(cards))
                    return cards
                # 出对子
                cards = self.findNCards(reducedCards, 2, False, reverse)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard EnemyAlarm2 Out2 handCards=', reducedCards.cards,
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'enemyAlarm%s Out2' % (enemyCardCount),
                                    'enemyCardCount=', enemyCardCount,
                                    'out=', self.toHumanCards(cards))
                    return cards
            else:
                # 敌人剩单张，优先出对子，捡小的出
                cards = self.findNCards(reducedCards, 2, False, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard Out2 handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'enemyAlarm%s Out2' % (enemyCardCount),
                                    'enemyCardCount=', enemyCardCount,
                                    'out=', self.toHumanCards(cards))
                    return cards

                # 出单牌
                cards = self.findNCards(reducedCards, 1, True, reverse)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard Out2 handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'enemyAlarm%s Out2' % (enemyCardCount),
                                    'enemyCardCount=', enemyCardCount,
                                    'out=', self.toHumanCards(cards))
                    return cards

        if nextSeat == enemySeat:
            if ftlog.is_debug():
                ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'NextIsEnemy Ding')

            prevCards = None
            # 下家是敌人，顶牌
            for i in xrange(4):
                cards = self._findDingNCardsGTPoint(reducedCards, i + 1, False, -1, self.DING_POINT)
                if cards:
                    if not prevCards:
                        prevCards = cards
                    if i < 2 and self.cardRule.cardToPoint(cards[0]) >= self.ACTIVE_MAX_POINT:
                        continue
                    if i == 3 and prevCards:
                        break
                    if ftlog.is_debug():
                        ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'NextIsEnemy Ding',
                                    'out=', self.toHumanCards(cards))
                    return cards

            if prevCards:
                if ftlog.is_debug():
                    ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'cardNote=', cardNote,
                                'desc=', 'NextIsEnemy Ding PrevCards',
                                'out=', self.toHumanCards(prevCards))
                return prevCards

        if ftlog.is_debug():
            ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'OutMinCard')
        # 下家是队友，或者自己是地主，从小牌开始出
        prevCards = None
        for i in xrange(4):
            cards = self.findNCards(reducedCards, i + 1, False, False)
            if cards:
                if not prevCards:
                    prevCards = cards
                if i < 2 and self.cardRule.cardToPoint(cards[0]) >= self.ACTIVE_MAX_POINT:
                    continue
                if i == 3 and prevCards:
                    break
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'OutMinCard',
                            'out=', cards)
                return cards
        if prevCards:
            ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'OutMinCard PrevCards',
                        'out=', cards)
            return prevCards

        cards = self.findNCards(reducedCards, 1, True, False)
        if ftlog.is_debug():
            ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'ChaiDanpai',
                        'out=', self.toHumanCards(cards))
        return cards

    def _findDingNCardsGTPoint(self, reducedCards, n, chaiPai, point, dingPoint):
        hasHuojian = False
        if (reducedCards.buckets[13].cardCount > 0
                and reducedCards.buckets[14].cardCount > 0):
            hasHuojian = True

        for i in xrange(dingPoint, point, -1):
            group = reducedCards.buckets[i]
            if (group.cardCount == n
                    or (group.cardCount > n and chaiPai)):
                return group.cards[0:n]

        # 找大的，不能拆双王
        startPoint = max(dingPoint, point + 1)
        maxPoint = 12 if hasHuojian else 14
        for i in xrange(startPoint, maxPoint + 1):
            group = reducedCards.buckets[i]
            if (group.cardCount == n
                    or (group.cardCount > n and chaiPai)):
                return group.cards[0:n]
        return None

    def _isHuojianOrZhadan(self, cards):
        if cards:
            if len(cards) == 2 and cards[0] in (52, 53) and cards[1] in (52, 53):
                return True
            elif len(cards) == 4:
                return self.cardRule.cardToPoint(cards[0]) == \
                       self.cardRule.cardToPoint(cards[1]) == \
                       self.cardRule.cardToPoint(cards[2]) == \
                       self.cardRule.cardToPoint(cards[3])

        return False

    def _doPassiveOutCard(self, reducedCards):
        cardNote = self.buildCardNote()
        topValidCard = self.table.gameRound.topValidCards
        topSeat = self.table.gameRound.topSeat

        if ftlog.is_debug():
            ftlog.debug('>>> AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'topSeatIndex=', self.table.gameRound.topSeat.seatIndex,
                        'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                        'cardNote=', cardNote)

        # 双王或炸弹必胜
        cards = self.checkBombOrHuojianWinCard(reducedCards, cardNote)
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard checkBombOrHuojianWinCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'topSeatIndex=', topSeat.seatIndex,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'first checkBombOrHuojianWinCard',
                            'out=', self.toHumanCards(cards))
            return cards

        found = self.cardRule.findGreaterValidCards(topValidCard, reducedCards.cards[:], True)
        # 管不住
        if not found:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard findGreaterCardsByValidCardsPass handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'topSeatIndex=', topSeat.seatIndex,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'NoGreaterCards',
                            'out=', [])
            return []

        cards = found.cards

        # 管牌后就出完了
        remCards = self.removeCards(reducedCards.cards[:], cards)
        if not remCards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'topSeatIndex=', topSeat.seatIndex,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'NotRemCards',
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards

        remReducedCards = ReducedCards.reduceHandCards(self.cardRule, remCards)
        # 管牌后剩余双王或炸弹必胜
        winCards = self.checkBombOrHuojianWinCard(remReducedCards, cardNote)
        if winCards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'topSeatIndex=', topSeat.seatIndex,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'remCards checkBombOrHuojianWinCard',
                            'remCards=', remCards,
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards

        dizhuCardCount = len(self.table.gameRound.dizhuSeat.status.cards)
        topCardCount = len(topValidCard.reducedCards.cards)

        # 队友出的牌
        if self.isFriend(self.table.gameRound.topSeat):
            if ftlog.is_debug():
                ftlog.debug('AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seat.seatIndex,
                            'topSeatIndex=', topSeat.seatIndex,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'FriendIsTopSeat',
                            'cards=', self.toHumanCards(cards))

            if self._isHuojianOrZhadan(cards):
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'topSeatIndex=', topSeat.seatIndex,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'HuojianOrZhadan cannot kill friend',
                                'cards=', self.toHumanCards(cards),
                                'out=', [])
                return []

            # 如果队友是下家则不管
            if self.player.seat.next == self.table.gameRound.topSeat:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'topSeatIndex=', topSeat.seatIndex,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Friend continue outCards',
                                'out=', [])
                return []

            if topCardCount > 2:
                # 只跟队友出单牌和对子
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'topSeatIndex=', topSeat.seatIndex,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Friend Out > 2',
                                'out=', [])
                return []

            # 如果队友出的对子，地主剩单张则不管
            if topCardCount == 2 and dizhuCardCount == 1:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'topSeatIndex=', topSeat.seatIndex,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Firend out 2Cards dizhu rem 1Cards',
                                'out=', [])
                return []

            # 队友出的单牌或者对牌，地主剩对应张数的牌，需要顶最大的
            if topCardCount == dizhuCardCount:
                chaiPai = True if topCardCount == 1 else False
                dingCards = self.findNCardsByGTPoint(reducedCards, topCardCount, topValidCard.reducedCards.groups[0].point, chaiPai, True)
                if dingCards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'topSeatIndex=', topSeat.seatIndex,
                                    'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                    'cardNote=', cardNote,
                                    'desc=', 'Firend out %sCards dizhu rem %sCards Ding' % (topCardCount, topCardCount),
                                    'out=', self.toHumanCards(dingCards))
                    return dingCards

            # 队友的牌>=跟牌点数则不跟
            if topValidCard.reducedCards.groups[0].point >= self.FOLLOW_FRIEND_MAX_POINT:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'topSeatIndex=', topSeat.seatIndex,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'NotFollow Firend out %sCards >= FOLLOW_FRIEND_MAX_POINT %s' % (topCardCount, self.FOLLOW_FRIEND_MAX_POINT),
                                'cards=', self.toHumanCards(cards),
                                'out=', [])
                return []

            # 顶牌
            dingCards = self._findDingNCardsGTPoint(reducedCards, topCardCount, False, topValidCard.reducedCards.groups[0].point, self.DING_POINT)
            if dingCards:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seat.seatIndex,
                                'topSeatIndex=', topSeat.seatIndex,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Firend out %sCards Ding' % (topCardCount),
                                'cards=', self.toHumanCards(cards),
                                'out=', self.toHumanCards(dingCards))
                return dingCards
        else:
            if len(cards) == 1:
                if (cards[0] in (52, 53)
                        and reducedCards.buckets[13].cardCount > 0
                        and reducedCards.buckets[14].cardCount > 0):
                    # 出的王牌，并且手里有双王，敌人手牌 > 5不出
                    if len(self.table.gameRound.topSeat.status.cards) > 5:
                        # 不出
                        if ftlog.is_debug():
                            ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                        'seatIndex=', self.player.seat.seatIndex,
                                        'topSeatIndex=', topSeat.seatIndex,
                                        'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                        'cardNote=', cardNote,
                                        'desc=', 'HasHuojian enemyCards > 5',
                                        'cards=', self.toHumanCards(cards),
                                        'out=', [])
                        return []
                    else:
                        # 出双王
                        if ftlog.is_debug():
                            ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                        'seatIndex=', self.player.seat.seatIndex,
                                        'topSeatIndex=', topSeat.seatIndex,
                                        'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                        'cardNote=', cardNote,
                                        'desc=', 'HasHuojian enemyCards <= 5',
                                        'cards=', self.toHumanCards(cards),
                                        'out=', [52, 53])
                        return [52, 53]

                # 敌人出牌单牌，大王可以管，小王在外面，并且出牌的敌人手牌>5,则不出
                if (cards[0] == 53
                        and cardNote[13] > 0
                        and len(self.table.gameRound.topSeat.status.cards) > 5):
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seat.seatIndex,
                                    'topSeatIndex=', topSeat.seatIndex,
                                    'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                    'cardNote=', cardNote,
                                    'desc=', 'MinKing not Out keep MaxKing',
                                    'cards=', self.toHumanCards(cards),
                                    'out=', [])
                    return []

        if ftlog.is_debug():
            ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seat.seatIndex,
                        'topSeatIndex=', topSeat.seatIndex,
                        'topCards=', self.toHumanCards(self.table.gameRound.topValidCards.reducedCards.cards),
                        'cardNote=', cardNote,
                        'desc=', 'Normal',
                        'cards=', self.toHumanCards(cards),
                        'out=', self.toHumanCards(cards))
        return cards


class DizhuAIPlayer(DizhuPlayerNormalBase):
    def __init__(self, room, userId):
        super(DizhuAIPlayer, self).__init__(room, userId)
        self.ai = AIRule(self)
        self.clientId = 'robot_3.7_-hall6-robot'
        self.name = ''
        self.purl = ''
        self.gameClientVer = 5.21
        self.chip = 0
        self.score = 0
        self.sex = random.randint(0, 1)
        self.segment = 1
        self.currentStar = 1
        self.gameAbortCount = 0
        self.isAI = True

    def initPlayer(self):
        '''
        填充player信息
        '''
        roomBuyInChip = self.room.roomConf.get('buyinchip', 0)
        roomMinCoin = self.room.roomConf.get('minCoin', 0)
        self.score = random.randint(roomMinCoin, roomBuyInChip)
        self.chip = self.score
        self._datas.update({
            'segment': self.segment,
            'currentStar': self.currentStar,
            'chip': self.score,
            'buyinChip': self.score,
            'name': self.name,
            'purl': self.purl,
            'sex': self.sex
        })

    @classmethod
    def addRobot(cls, table):
        if ftlog.is_debug():
            ftlog.debug('DizhuAIPlayer.addRobot start')

        robConf = configure.getGameJson(DIZHU_GAMEID, 'ai.player', {})
        aiUserInfoList = robConf.get('aiUserInfoList', [])
        choices = []
        if aiUserInfoList:
            choices = random.sample(aiUserInfoList, table.runConf.maxSeatN - 1)
        for i in range(table.runConf.maxSeatN - 1):
            if ftlog.is_debug():
                ftlog.debug('DizhuAIPlayer.addRobot init userId=', i + 1000)
            rob = DizhuAIPlayer(table.room, i + 1000)
            robInfo = choices[i]
            name, purl = robInfo.get('nickname', ''), robInfo.get('avatar', '')
            rob.name = name
            rob.purl = purl
            rob.initPlayer()
            table.sitdown(rob, False)

    def doActiveOutCard(self):
        return self.ai.doActiveOutCard()

    def doPassiveOutCard(self):
        return self.ai.doPassiveOutCard()
