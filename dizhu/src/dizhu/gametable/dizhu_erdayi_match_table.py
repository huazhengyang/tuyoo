# -*- coding:utf-8 -*-
'''
Created on 2016年7月19日

@author: zhaojiangang
'''
import time

from dizhu.entity import dizhuconf
from dizhu.gamecards.dizhu_rule import ReducedCards, CardTypeHuoJian,\
    CardTypeDanPai, CardTypeDuiZi, CardTypeSanZhang, CardTypeZhaDan,\
    CardTypeFeiJi, CardTypeFeiJiDai1, CardTypeFeiJiDai2, CardTypeShuangShun,\
    CardTypeDanShun, CardTypeSanDai1, CardTypeSanDai2
from dizhu.gametable.dizhu_erdayi_match_sender import DizhuErdayiMatchSender
from dizhu.gametable.dizhu_player import DizhuPlayer
from dizhu.gametable.dizhu_table import DizhuTable
from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.game.rooms.erdayi_match_ctrl.const import AnimationType
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_seat import TYSeat
from poker.entity.game.tables.table_timer import TYTableTimer
from poker.protocol import router
from freetime.util import log as ftlog

class AIPlayer(object):
    cardCountToCardType = {
        1:CardTypeDanPai,
        2:CardTypeDuiZi,
        3:CardTypeSanZhang,
        4:CardTypeZhaDan
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
    def gamePlay(self):
        return self.table.gamePlay
    
    @property
    def card(self):
        return self.gamePlay.card
    
    @property
    def cardRule(self):
        return self.card.rule
    
    def enureWinCards(self, reducedCards):
        '''
        必胜的牌，只记牌记到A，能记住有没有炸弹
        '''
        pass
    
    def doActiveOutCard(self):
        cards = None
        try:
            reducedCards = ReducedCards.reduceForHandCards(self.cardRule, self.table.seats[self.player.seatIndex].cards)
            cards = self._doActiveOutCard(reducedCards)
        except:
            ftlog.error('AIPlayer.doActiveOutCard seatId=', self.player.seatId,
                        'userId=', self.player.userId,
                        'cards=', cards)
        if not cards:
            handcards = self.table.seats[self.player.seatIndex].cards
            cards = self.card.findFirstCards(handcards)
        return cards
        
    def doPassiveOutCard(self):
        cards = None
        try:
            reducedCards = ReducedCards.reduceForHandCards(self.cardRule, self.table.seats[self.player.seatIndex].cards)
            cards = self._doPassiveOutCard(reducedCards)
        except:
            ftlog.error('AIPlayer.doPassiveOutCard seatId=', self.player.seatId,
                        'userId=', self.player.userId,
                        'cards=', cards)
            cards = []
        return cards
            
    def fillCardNote(self, cardNote, cards):
        for card in cards:
            point = self.cardRule.cardToPoint(card)
            assert(point < 15)
            cardNote[point] += 1
        return cardNote
    
    def buildCardNote(self):
        ret = [0 for _ in xrange(15)]
        for i, seat in enumerate(self.table.seats):
            if i != self.player.seatIndex:
                self.fillCardNote(ret, seat.cards)
        return ret
    
    def isDizhu(self):
        return self.player.seatId == self.table.status.diZhu
    
    def isFriend(self, seatIndex):
        return (self.player.seatId != self.table.status.diZhu
                and seatIndex + 1 != self.table.status.diZhu) 
        
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
            if cardNote[i] >= group.length():
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
        if (reducedCards.groupBuckets[13].length() > 0
            and reducedCards.groupBuckets[14].length() > 0):
            ret.append((CardTypeHuoJian, [52, 53], [reducedCards.groupBuckets[13], reducedCards.groupBuckets[14]]))
        
        # 查找手中最大的group
        for group in reducedCards.groupBuckets:
            if group.length() > 0 and (group.length() == 4 or group.point >= minPoint):
                if self.isBiggestCard(cardNote, group):
                    ret.append((self.cardCountToCardType.get(group.length()), group.cards[:], [group]))
        
        return ret
        
    def removeCards(self, srcCards, toRemoveCards):
        if ftlog.is_debug():
            ftlog.debug('AIPlayer.removeCards srcCards=', self.toHumanCards(srcCards),
                        'toRemoveCards=', self.toHumanCards(toRemoveCards))
        for card in toRemoveCards:
            srcCards.remove(card)
        return srcCards
            
    def checkBombOrHuojianWinCard(self, reducedCards, cardNote):
        if (reducedCards.groupBuckets[13].length() > 0
            and reducedCards.groupBuckets[14].length() > 0):
            remCards = self.removeCards(reducedCards.cards[:], [52, 53])
            if not remCards or self.cardRule.validateCards(remCards):
                return [52, 53]
        for group in reducedCards.groupBuckets[::-1]:
            if group.length() == 4 and not self.hasBiggerBomb(cardNote, group.point):
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
            bombPoint = -1 if cardType != CardTypeZhaDan else groups[0].point
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
            if cardType == CardTypeSanZhang:
                remReducedCards = ReducedCards.reduceForHandCards(self.cardRule, remCards)
                # 从remReducedCards中去掉1张或者一对之后还剩一手牌
                for group in remReducedCards.groupBuckets:
                    for i in xrange(min(2, group.length())):
                        # 去掉i+1张
                        if ftlog.is_debug():
                            ftlog.debug('AIPlayer.checkWinCard srcCards=', self.toHumanCards(reducedCards.cards),
                                        'biggestCards=', self.toHumanCards(cards),
                                        'remCamds=', self.toHumanCards(remCards),
                                        'toRemoveCards=', self.toHumanCards(group.cards[0:i+1]))
                        rem1Cards = self.removeCards(remCards[:], group.cards[0:i+1])
                        if not rem1Cards or self.cardRule.validateCards(rem1Cards):
                            return cards
        return None
                    
    def findFirstCards(self, reducedCards, cardTypeClasses):
        for cardTypeClass in cardTypeClasses:
            cardType = self.cardRule.findCardTypeByClass(cardTypeClass)
            if cardType:
                found = cardType.findMinCards(reducedCards)
                if found:
                    return found[0]
        return None
    
    def findNCards(self, reducedCards, n, canChaipai, reverse=False):
        '''
        查找N张点数相同的牌
        @param reverse: 是否从后往前找
        '''
        groupBuckets = reducedCards.groupBuckets if not reverse else reducedCards.groupBuckets[::-1]
        for group in groupBuckets:
            if (group.length() == n
                or (canChaipai and group.length() >= n)):
                return group.cards[0:n]
        return None
    
    def findNCardsByGTPoint(self, reducedCards, n, point, canChaipai, reverse=False):
        '''
        查找N张点数相同的牌
        @param reverse: 是否从后往前找
        '''
        groupBuckets = reducedCards.groupBuckets if not reverse else reducedCards.groupBuckets[::-1]
        for group in groupBuckets:
            if (group.point > point
                and (group.length() == n
                     or (canChaipai and group.length() >= n))):
                return group.cards[0:n]
        return None
    
    def findNCardsByGTPointWithMinPoint(self, reducedCards, n, point, minPoint, canChaipai, reverse=False):
        '''
        查找N张点数相同的牌
        @param reverse: 是否从后往前找
        '''
        groupBuckets = reducedCards.groupBuckets if not reverse else reducedCards.groupBuckets[::-1]
        for group in groupBuckets:
            if (group.point > point
                and group.point >= minPoint
                and (group.length() == n
                     or (canChaipai and group.length() >= n))):
                return group.cards[0:n]
        return None
    
    def getNextSeatIndex(self, seatIndex):
        return (seatIndex + 1) % len(self.table.seats)
    
    def getPrevSeatIndex(self, seatIndex):
        return (seatIndex - 1) % len(self.table.seats)
    
    def toHumanCards(self, cards):
        ret = []
        if cards:
            for c in cards:
                ret.append(self.HUMAN_CARDS[c])
        return ret
    
    def _doActiveOutCard(self, reducedCards):
        cardNote = self.buildCardNote()
        if ftlog.is_debug():
            ftlog.debug('>>> AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'cardNote=', cardNote)
            
        cards = self.checkWinCard(reducedCards, cardNote, 11)
        
        if ftlog.is_debug():
            ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'checkWinCard',
                        'checkWinCard=', self.toHumanCards(cards))
                
        # 剩余最大一手牌+任意一手牌
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'cardNote=', cardNote,
                            'checkWinCard=', cards,
                            'desc=', 'checkWinCard',
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards
        
        # 剩余一手牌
        cards = self.cardRule.checkValidCardsWithHandReducedCards(reducedCards)
        if ftlog.is_debug():
            ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'checkValidCardsWithHandReducedCards',
                        'cards=', self.toHumanCards(cards))
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'checkValidCardsWithHandReducedCards'
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards
        
        nextSeatIndex = self.getNextSeatIndex(self.player.seatIndex)
        enemySeatIndex = nextSeatIndex if not self.isFriend(nextSeatIndex) else self.getPrevSeatIndex(self.player.seatIndex)
        
        if nextSeatIndex != enemySeatIndex:
            # 队友剩单牌，出最小的牌
            if len(self.table.seats[nextSeatIndex].cards) == 1:
                cards = self.findNCards(reducedCards, 1, True, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'PassFriend1',
                                    'out=', self.toHumanCards(cards))
                    return cards
            elif len(self.table.seats[nextSeatIndex].cards) == 2:
                # 队友剩对子，出最小的对子
                cards = self.findNCards(reducedCards, 2, False, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'PassFriend2',
                                    'out=', self.toHumanCards(cards))
                    return cards
        
        # 查找飞机，三顺，双顺，单顺，三带单，三带对
        cards = self.findFirstCards(reducedCards, [CardTypeFeiJiDai1, CardTypeFeiJiDai2, CardTypeFeiJi, CardTypeShuangShun, CardTypeDanShun, CardTypeSanDai1, CardTypeSanDai2])
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'findFirstCards',
                            'out=', self.toHumanCards(cards))
            return cards
        
        reverse = True if enemySeatIndex == nextSeatIndex else False
        enemyCardCount = len(self.table.seats[enemySeatIndex].cards)
        
        # 敌人报牌了
        if enemyCardCount <= 2:
            if ftlog.is_debug():
                ftlog.debug('AIPlayer._doActiveOutCard EnemyAlarm handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'enemyAlarm%s' % (enemyCardCount),
                            'enemyCardCount=', enemyCardCount)
                
            if enemyCardCount == 2:
                # 敌人剩双数，优先出单牌，捡小牌出
                cards = self.findNCards(reducedCards, 1, True, False)
                if cards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seatIndex,
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
                                    'seatIndex=', self.player.seatIndex,
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
                                    'seatIndex=', self.player.seatIndex,
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
                                    'seatIndex=', self.player.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'enemyAlarm%s Out2' % (enemyCardCount),
                                    'enemyCardCount=', enemyCardCount,
                                    'out=', self.toHumanCards(cards))
                    return cards
        
        if nextSeatIndex == enemySeatIndex:
            if ftlog.is_debug():
                ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
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
                                    'seatIndex=', self.player.seatIndex,
                                    'cardNote=', cardNote,
                                    'desc=', 'NextIsEnemy Ding',
                                    'out=', self.toHumanCards(cards))
                    return cards
            
            if prevCards:
                if ftlog.is_debug():
                    ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seatIndex,
                                'cardNote=', cardNote,
                                'desc=', 'NextIsEnemy Ding PrevCards',
                                'out=', self.toHumanCards(prevCards))
                return prevCards
                    
        if ftlog.is_debug():
            ftlog.debug('AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
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
                            'seatIndex=', self.player.seatIndex,
                            'cardNote=', cardNote,
                            'desc=', 'OutMinCard',
                            'out=', cards)
                return cards
        if prevCards:
            ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'OutMinCard PrevCards',
                        'out=', cards)
            return prevCards
            
        cards = self.findNCards(reducedCards, 1, True, False)
        if ftlog.is_debug():
            ftlog.debug('<<< AIPlayer._doActiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'cardNote=', cardNote,
                        'desc=', 'ChaiDanpai',
                        'out=', self.toHumanCards(cards))
        return cards

    def _findDingNCardsGTPoint(self, reducedCards, n, chaiPai, point, dingPoint):
        hasHuojian = False
        if (reducedCards.groupBuckets[13].length() > 0
            and reducedCards.groupBuckets[14].length() > 0):
            hasHuojian = True
            
        for i in xrange(dingPoint, point, -1):
            group = reducedCards.groupBuckets[i]
            if (group.length() == n
                or (group.length() > n and chaiPai)):
                return group.cards[0:n]

        # 找大的，不能拆双王
        startPoint = max(dingPoint, point + 1)
        maxPoint = 12 if hasHuojian else 14
        for i in xrange(startPoint, maxPoint + 1):
            group = reducedCards.groupBuckets[i]
            if (group.length() == n
                or (group.length() > n and chaiPai)):
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
        topValidCard = self.table.status.topValidCard
        topSeatIndex = self.table.status.topSeatId - 1
        
        if ftlog.is_debug():
            ftlog.debug('>>> AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'topSeatIndex=', self.table.status.topSeatId - 1,
                        'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                        'cardNote=', cardNote)
        
        # 双王或炸弹必胜
        cards = self.checkBombOrHuojianWinCard(reducedCards, cardNote)
        if cards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard checkBombOrHuojianWinCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'topSeatIndex=', self.table.status.topSeatId - 1,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'first checkBombOrHuojianWinCard',
                            'out=', self.toHumanCards(cards))
            return cards
        
        found = self.cardRule.findGreaterCardsByValidCards(topValidCard, reducedCards, True)
        # 管不住
        if not found:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard findGreaterCardsByValidCardsPass handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'topSeatIndex=', self.table.status.topSeatId - 1,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'NoGreaterCards',
                            'out=', [])
            return []
        
        cards = found[0]
        
        # 管牌后就出完了
        remCards = self.removeCards(reducedCards.cards[:], cards)
        if not remCards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'topSeatIndex=', self.table.status.topSeatId - 1,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'NotRemCards',
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards
        
        remReducedCards = ReducedCards.reduceForHandCards(self.cardRule, remCards)
        # 管牌后剩余双王或炸弹必胜
        winCards = self.checkBombOrHuojianWinCard(remReducedCards, cardNote)
        if winCards:
            if ftlog.is_debug():
                ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'topSeatIndex=', self.table.status.topSeatId - 1,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'remCards checkBombOrHuojianWinCard',
                            'remCards=', remCards,
                            'cards=', self.toHumanCards(cards),
                            'out=', self.toHumanCards(cards))
            return cards
        
        dizhuCardCount = len(self.table.seats[self.table.status.diZhu - 1].cards)
        topCardCount = len(topValidCard.reducedCards.cards)
        
        # 队友出的牌
        if self.isFriend(self.table.status.topSeatId - 1):
            if ftlog.is_debug():
                ftlog.debug('AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                            'seatIndex=', self.player.seatIndex,
                            'topSeatIndex=', self.table.status.topSeatId - 1,
                            'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                            'cardNote=', cardNote,
                            'desc=', 'FriendIsTopSeat',
                            'cards=', self.toHumanCards(cards))
            
            if self._isHuojianOrZhadan(cards):
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seatIndex,
                                'topSeatIndex=', self.table.status.topSeatId - 1,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'HuojianOrZhadan cannot kill friend',
                                'cards=', self.toHumanCards(cards),
                                'out=', [])
                return []
            
            # 如果队友是下家则不管
            if self.getNextSeatIndex(self.player.seatIndex) == self.table.status.topSeatId - 1:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seatIndex,
                                'topSeatIndex=', self.table.status.topSeatId - 1,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Friend continue outCards',
                                'out=', [])
                return []
            
            if topCardCount > 2:
                # 只跟队友出单牌和对子
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seatIndex,
                                'topSeatIndex=', self.table.status.topSeatId - 1,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Friend Out > 2',
                                'out=', [])
                return []

            # 如果队友出的对子，地主剩单张则不管
            if topCardCount == 2 and dizhuCardCount == 1:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seatIndex,
                                'topSeatIndex=', self.table.status.topSeatId - 1,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Firend out 2Cards dizhu rem 1Cards',
                                'out=', [])
                return []
            
            # 队友出的单牌或者对牌，地主剩对应张数的牌，需要顶最大的
            if topCardCount == dizhuCardCount:
                chaiPai = True if topCardCount == 1 else False
                dingCards = self.findNCardsByGTPoint(reducedCards, topCardCount, self.table.status.topValidCard.reducedCards.groups[0].point, chaiPai, True)
                if dingCards:
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seatIndex,
                                    'topSeatIndex=', self.table.status.topSeatId - 1,
                                    'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                    'cardNote=', cardNote,
                                    'desc=', 'Firend out %sCards dizhu rem %sCards Ding' % (topCardCount, topCardCount),
                                    'out=', self.toHumanCards(dingCards))
                    return dingCards
            
            # 队友的牌>=跟牌点数则不跟
            if topValidCard.reducedCards.groups[0].point >= self.FOLLOW_FRIEND_MAX_POINT:
                if ftlog.is_debug():
                    ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                'seatIndex=', self.player.seatIndex,
                                'topSeatIndex=', self.table.status.topSeatId - 1,
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
                                'seatIndex=', self.player.seatIndex,
                                'topSeatIndex=', self.table.status.topSeatId - 1,
                                'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                'cardNote=', cardNote,
                                'desc=', 'Firend out %sCards Ding' % (topCardCount),
                                'cards=', self.toHumanCards(cards),
                                'out=', self.toHumanCards(dingCards))
                return dingCards
        else:
            if len(cards) == 1:
                if (cards[0] in (52, 53)
                    and reducedCards.groupBuckets[13].length() > 0
                    and reducedCards.groupBuckets[14].length() > 0):
                    # 出的王牌，并且手里有双王，敌人手牌 > 5不出
                    if len(self.table.seats[topSeatIndex].cards) > 5:
                        # 不出
                        if ftlog.is_debug():
                            ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                        'seatIndex=', self.player.seatIndex,
                                        'topSeatIndex=', self.table.status.topSeatId - 1,
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
                                        'seatIndex=', self.player.seatIndex,
                                        'topSeatIndex=', self.table.status.topSeatId - 1,
                                        'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                        'cardNote=', cardNote,
                                        'desc=', 'HasHuojian enemyCards <= 5',
                                        'cards=', self.toHumanCards(cards),
                                        'out=', [52, 53])
                        return [52, 53]
                    
                # 敌人出牌单牌，大王可以管，小王在外面，并且出牌的敌人手牌>5,则不出
                if (cards[0] == 53
                    and cardNote[13] > 0
                    and len(self.table.seats[topSeatIndex].cards) > 5):
                    if ftlog.is_debug():
                        ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                                    'seatIndex=', self.player.seatIndex,
                                    'topSeatIndex=', self.table.status.topSeatId - 1,
                                    'topCards=', self.toHumanCards(topValidCard.reducedCards.cards),
                                    'cardNote=', cardNote,
                                    'desc=', 'MinKing not Out keep MaxKing',
                                    'cards=', self.toHumanCards(cards),
                                    'out=', [])
                    return []
                
        if ftlog.is_debug():
            ftlog.debug('<<< AIPlayer._doPassiveOutCard handCards=', self.toHumanCards(reducedCards.cards),
                        'seatIndex=', self.player.seatIndex,
                        'topSeatIndex=', self.table.status.topSeatId - 1,
                        'topCards=', self.toHumanCards(self.table.status.topValidCard.reducedCards.cards),
                        'cardNote=', cardNote,
                        'desc=', 'Normal',
                        'cards=', self.toHumanCards(cards),
                        'out=', self.toHumanCards(cards))
        return cards
    
class DizhuPlayerErdayi(DizhuPlayer):
    def __init__(self, table, seatIndex, copyData=None):
        super(DizhuPlayerErdayi, self).__init__(table, seatIndex, copyData)
        self.isAI = True if table.isVsAI and seatIndex > 0 else False
        self.ai = None
        if self.isAI:
            self.ai = AIPlayer(self)
        
    def initUser(self, isNextBuyin, isUsingScore):
        '''
        从redis里获取并初始化player数据, 远程操作
        '''
        ret = super(DizhuPlayerErdayi, self).initUser(isNextBuyin, isUsingScore)
        if self.isAI and not self.clientId:
            self.clientId = 'robot_3.7_-hall6-robot'
        return ret

    def doActiveOutCard(self):
        assert(self.isAI)
        return self.ai.doActiveOutCard()
        
    def doPassiveOutCard(self):
        assert(self.isAI)
        return self.ai.doPassiveOutCard()
    
class DizhuErdayiMatchTable(DizhuTable):
    MSTART_SLEEP = 3
    AI_USER_IDS = [1, 2]
    def __init__(self, room, tableId):
        self.seatOpTimers = []
        super(DizhuErdayiMatchTable, self).__init__(room, tableId)
        self._match_table_info = None
        self.gamePlay.sender = DizhuErdayiMatchSender(self)
        
        for _ in xrange(self.maxSeatN):
            self.seatOpTimers.append(TYTableTimer(self))
            
        self._doMatchTableClear()
        
        self._logger = Logger()
        self._logger.add('gameId', self.gameId)
        self._logger.add('roomId', room.roomId)
        self._logger.add('tableId', tableId)
        self._logger.add('matchId', room.bigmatchId)

    def clear(self, userids):
        '''
        完全清理桌子数据和状态, 恢复到初始化的状态
        '''
        super(DizhuErdayiMatchTable, self).clear(userids)
        self.cancelAllSeatOpTimers()
            
    @property
    def isVsAI(self):
        return self.config.get('isVsAI', 1)
    
    def _makePlayer(self, seatIndex):
        return DizhuPlayerErdayi(self, seatIndex)

    def canJiabei(self, seat):
        point2score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 3]
        # 按大牌来吧 计算大牌多就加倍王=3 2=2 A=1 8点及以上加倍
        score = 0
        for card in seat.cards:
            point = self.gamePlay.card.rule.cardToPoint(card)
            score += point2score[point]
        return score >= 8
        
    def cancelAllSeatOpTimers(self):
        for timer in self.seatOpTimers:
            timer.cancel()
            
    def _doOtherAction(self, msg, player, seatId, action, clientId):
        if action == 'AI_OUTCARD_TIMEUP':
            self.seatOpTimers[player.seatIndex].cancel()
            ccrc = msg.getParam('ccrc')
            self.gamePlay.doAIOutCard(player, ccrc)
        elif action == 'AI_JIABEI':
            jiabei = msg.getParam('jiabei', 0)
            self.seatOpTimers[player.seatIndex].cancel()
            self.gamePlay.doJiabei(player, jiabei)
        
    def _doTableManage(self, msg, action):
        '''
        处理来自大比赛的table_manage命令
        '''
        if action == 'm_table_start':
            self.doMatchTableStart(msg)
            return
 
        if action == 'm_table_info':
            self.doUpdateMatchTableInfo(msg)
            return
 
        if action == 'm_table_clear':
            self.doMatchTableClear(msg)
            return
     
    def _getUserIdsFromTableInfo(self, tableInfo):
        userIds = []
        for seatInfo in tableInfo['seats']:
            userIds.append(seatInfo['userId'])
        return userIds
         
    def _checkSeatInfo(self, seatInfo):
        if seatInfo['userId'] == 0:
            self._logger.error('DizhuErdayiMatchTable._checkSeatInfo',
                               'err=', 'userId must not 0')
            return False
        return True
 
    def _checkMatchTableInfo(self, tableInfo):
        if not isinstance(tableInfo, dict):
            self._logger.error('DizhuErdayiMatchTable._checkMatchTableInfo',
                               'err=', 'matchTableInfo must be dict')
            return False
        gameId = tableInfo.get('gameId')
        roomId = tableInfo.get('roomId')
        tableId = tableInfo.get('tableId')
        matchId = tableInfo.get('matchId')
        if (self.gameId != gameId
            or self.roomId != roomId
            or self.tableId != tableId
            or self.room.bigmatchId != matchId):
            self._logger.error('DizhuErdayiMatchTable._checkMatchTableInfo',
                               'gameIdParam=', gameId,
                               'roomIdParam=', roomId,
                               'tableIdParam=', tableId,
                               'matchIdParam=', matchId,
                               'err=', 'diff roomId or tableId or bigmatchId')
            return False
         
        ccrc = tableInfo.get('ccrc')
        if not isinstance(ccrc, int):
            self._logger.error('DizhuErdayiMatchTable._checkMatchTableInfo',
                               'err=', 'ccrc must be int')
            return False
         
        seatInfos = tableInfo.get('seats')
        if len(seatInfos) != 1:
            self._logger.error('DizhuErdayiMatchTable._checkMatchTableInfo',
                               'err=', 'len(seatInfos) must == 1')
            return False
        
        for seatInfo in seatInfos:
            if not self._checkSeatInfo(seatInfo):
                return False
            
        return True
    
    def doMatchTableStart(self, msg):
        if self._logger.isDebug():
            self._logger.debug('DizhuErdayiMatchTable.doMatchTableStart',
                               'msg=', msg)
        startTime = int(time.time())
        table_info = msg.getKey('params')
        if self._checkMatchTableInfo(table_info):
            self._doUpdateTableInfo(table_info)
            self._doMatchQuickStart()
        if self._logger.isDebug():
            self._logger.debug('DizhuErdayiMatchTable.doMatchTableStart',
                               'msg=', msg,
                               'used=', int(time.time()) - startTime)
             
    def doMatchTableClear(self, msg):
        if self._logger.isDebug():
            self._logger.debug('DizhuErdayiMatchTable.doMatchTableClear',
                               'msg=', msg)
        params = msg.getKey('params')
        matchId = params.get('matchId', -1)
        ccrc = params.get('ccrc', -1)
        if matchId != self.room.bigmatchId:
            self._logger.error('DizhuErdayiMatchTable.doMatchTableClear',
                               'msg=', msg,
                               'err=', 'DiffMatchId')
            return
          
        if not self._match_table_info:
            self._logger.error('DizhuErdayiMatchTable.doMatchTableClear',
                               'msg=', msg,
                               'err=', 'table match is clear')
            return
          
        if ccrc != self._match_table_info['ccrc']:
            self._logger.error('DizhuErdayiMatchTable.doMatchTableClear',
                               'msg=', msg,
                               'ccrc=', self._match_table_info['ccrc'],
                               'err=', 'diff ccrc')
            return
          
        self._doMatchTableClear()
      
    def _getSeatInfo(self, seatIndex):
        if (self._match_table_info
            and seatIndex >= 0
            and seatIndex < len(self._match_table_info['seats'])):
            return self._match_table_info['seats'][seatIndex]
        return None
     
    def _doMatchTableClear(self):
        for seatIndex in xrange(len(self.seats)):
            seatInfo = self._getSeatInfo(seatIndex)
            if seatInfo:
                #比赛阶段清理牌桌时无需刷新客户端
                self.gamePlay.doStandUp(seatInfo['userId'], seatIndex+1, TYRoom.LEAVE_ROOM_REASON_MATCH_END, seatInfo['clientId'])
        self.clear(None)
        self._time_stamp = 0
        self._match_table_info = None
   
    def _doUpdateTableInfo(self, tableInfo):
        self._time_stamp = time.time()
        self._match_table_info = tableInfo
          
    def _doMatchQuickStart(self):
        tableInfo = self._match_table_info
        seatInfos = tableInfo['seats']
        userIds = []
        userSeatList = []
        for seatInfo in seatInfos:
            userIds.append(seatInfo['userId'])
        if self.isVsAI:
            userIds.extend(self.AI_USER_IDS)

        self._logger.info('DizhuErdayiMatchTable._doMatchQuickStart',
                          'userIds=', userIds,
                          'seatCount=', len(self.seats),
                          'seats=', self.seats)
        
        for i, userId in enumerate(userIds):
            this_seat = self.seats[i]
            this_seat.userId = userId
            this_seat.state = TYSeat.SEAT_STATE_WAIT
            this_seat.call123 = -1
            userSeatList.append((userId, i + 1))
         
        # 初始化用户数据
        for x in xrange(len(self.players)):
            self.players[x].initUser(0, 1)
 
        for player in self.players:
            if not player.isAI:
                try:
                    onlinedata.setBigRoomOnlineLoc(player.userId, self.roomId, self.tableId, player.seatId)
                    if self._logger.isDebug():
                        self._logger.debug('DizhuErdayiMatchTable._doMatchQuickStart setBigRoomOnlineLoc',
                                           'userId=', player.userId,
                                           'tableId=', self.tableId,
                                           'seatId=', player.seatId)
                except:
                    self._logger.error('DizhuErdayiMatchTable._doMatchQuickStart')
 
        # 增加从比赛等待界面到下一局开始时的时间间隔
        inter = self._getWaitToNextMatchInter(tableInfo)
        if self._logger.isDebug():
            self._logger.debug('DizhuErdayiMatchTable._doMatchQuickStart',
                               '_getWaitToNextMatchInter=', inter)
        if inter > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(inter)
        
        for player in self.players:
            if not player.isAI:
                mq = MsgPack()
                mq.setCmd('quick_start')
                mq.setResult('userId', player.userId)
                mq.setResult('gameId', self.gameId)
                mq.setResult('roomId', self.roomId)
                mq.setResult('tableId', self.tableId)
                mq.setResult('seatId', player.seatId)
                # 发送用户的quick_start
                router.sendToUser(mq, player.userId)
                # 发送table_info
                self.gamePlay.sender.sendTableInfoRes(player.userId, player.clientId, 0)
 
        # 延迟1秒进行animation Info相关处理
        FTTasklet.getCurrentFTTasklet().sleepNb(1)
 
        playAnimation, delaySeconds = self._playAnimationIfNeed(tableInfo)
         
        if playAnimation and delaySeconds > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(delaySeconds)

        for x in xrange(len(self.players)):
            self.gamePlay.doReady(self.players[x], False)
          
    def _buildNote(self, userId, tableInfo):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        for seatInfo in tableInfo['seats']:
            if seatInfo['userId'] == userId:
                return u'%s：%s人晋级，第%s副（共%s副）' % (tableInfo['step']['name'],
                                      tableInfo['step']['riseCount'],
                                      seatInfo['cardCount'],
                                      tableInfo['step']['cardCount'])
        return ''
    
    def _buildMatchStepInfo(self, userId, tableInfo):
        res = {'curCount':-1, 'totoal':-1}
        for seatInfo in tableInfo['seats']:
            if seatInfo['userId'] == userId:
                res['curCount'] = seatInfo['cardCount']
                res['totoal'] = tableInfo['step']['cardCount']
        return res
     
    def _playAnimationIfNeed(self, tableInfo):
        playAnimation, delaySeconds = False, 0
        for player in self.players:
            if not player.isAI and player.userId > 0:
                clientVer = sessiondata.getClientIdVer(player.userId)
                animationType = self._getAnimationType(clientVer)
                if animationType != AnimationType.UNKNOWN:
                    msg = MsgPack()
                    msg.setCmd('m_play_animation')
                    msg.setResult('gameId', self.gameId)
                    msg.setResult('roomId', self.roomId)
                    msg.setResult('tableId', self.tableId)
                    msg.setResult('type', animationType)
                    isStartStep = tableInfo['step']['stageIndex'] == 0
                    # 添加是否是第一个阶段的标志，是的话前端播放开始比赛的动画
                    msg.setResult('isStartStep', isStartStep)
                    # 组织当前比赛是第几局、共几局的信息
                    msg.setResult('curMatchStep', self._buildMatchStepInfo(player.userId, tableInfo))
                    router.sendToUser(msg, player.userId)
                         
                    curDelay = self._getAnimationInter(animationType, isStartStep, clientVer)
                    if curDelay > delaySeconds:
                        delaySeconds = curDelay
                    playAnimation = True
        return playAnimation, delaySeconds
     
    def _getAnimationType(self, clientVer):
        try:
            if clientVer < 3.37:
                return AnimationType.UNKNOWN
            if clientVer < 3.77:
                # 小于3.77版本的还是每一个阶段只播一次
                if self._match_table_info['step']['totalCardCount'] == 0:
                    return self._match_table_info['step']['animationType']
                return AnimationType.UNKNOWN
            return self._match_table_info['step']['animationType']
        except:
            return self._match_table_info['step']['animationType']
 
    def _getWaitToNextMatchInter(self, tableInfo):
        isStartStep = tableInfo['step']['stageIndex'] == 0
        if isStartStep:
            # 第一个阶段不做延迟
            return 0
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        return delayConf.get('waitToNextMatch', 3)
     
    def _getAnimationInter(self, AnimationType, isStartStep, clientVer):
        if str(clientVer)<3.77:
            return self.MSTART_SLEEP
         
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        if not delayConf:
            if isStartStep:
                return 5
            return 3
        valKey = 'startStep'
        if not isStartStep:
            valKey = 'type'+str(AnimationType)
        return delayConf.get(valKey, 3)
     
    def _findMatchSeatInfoByUserId(self, userId):
        if self._match_table_info:
            for seatInfo in self._match_table_info['seats']:
                if seatInfo['userId'] == userId:
                    return seatInfo
        return None
      

