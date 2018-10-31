# -*- coding:utf-8 -*-
'''
Created on 2016年9月5日

@author: zhaojiangang
'''
import random
CARD_TYPE_DANPAI = 1
CARD_TYPE_DUIZI = 2
CARD_TYPE_SANZHANG = 3
CARD_TYPE_SANDAI1 = 4
CARD_TYPE_SANDAI2 = 5
CARD_TYPE_DANSHUN = 6
CARD_TYPE_SHUANGSHUN = 7
CARD_TYPE_SANSHUN = 8
CARD_TYPE_FEIJIDAI1 = 9
CARD_TYPE_FEIJIDAI2 = 10
CARD_TYPE_SIDAI2DAN = 11
CARD_TYPE_SIDAI2DUI = 12
CARD_TYPE_ZHADAN = 13
CARD_TYPE_HUOJIAN = 14

CARD_LEVEL_NORMAL = 1
CARD_LEVEL_ZHADAN = 2
CARD_LEVEL_HUOJIAN = 3

class UnknownCardException(Exception):
    '''
    不能识别的牌
    '''
    def __init__(self, card):
        self.card = card

class UnknownPointException(Exception):
    '''
    不能识别的点数
    '''
    def __init__(self, point):
        self.point = point
        
class CardGroup(object):
    '''
    点数相同的牌集 - 【同点牌集】
    '''
    def __init__(self, point, cards=None):
        self.point = point
        self.cards = cards or []
    
    @property
    def cardCount(self):
        return len(self.cards)
    
    def addCard(self, card):
        self.cards.append(card)
        
class SameCountGroup(object):
    '''
    个数相同的牌的集合 【同数牌集】
    例如：AAAKKK8885677 中AK8为个数相同的牌,
    '''
    def __init__(self, count):
        self.count = count
        self.groups = []
        
    def addGroup(self, group):
        assert(isinstance(group, CardGroup))
        assert(group.cardCount == self.count)
        self.groups.append(group)
        
    def findGroupByGTPoint(self, point, exceptPoints=[]):
        '''
        查找一个点数不在exceptPoints中而且点数大于给定点数的【同点牌集】
        '''
        if exceptPoints:
            for group in self.groups:
                if group.point > point and group.point not in exceptPoints:
                    return group
        else:
            for group in self.groups:
                if group.point > point:
                    return group
        return None
    
    def findGroupByExceptPoints(self, exceptPoints=[]):
        '''
        查找一个点数不在exceptPoints中的【同点牌集】
        '''
        if exceptPoints is None:
            return None if len(self.groups) <= 0 else self.groups[0]
            
        for group in self.groups:
            if group.point not in exceptPoints:
                return group
        return None

class ReducedCards(object):
    '''
    整理好牌
    规则：【同数牌集】按照牌数量从小到大排序 
    '''
    def __init__(self, cards, buckets, wildCards, wildBuckets):
        '''
        @param cards: 所有的牌
        @param buckets: cards对应的【同点牌集】的集合
        @param wildCards: 癞子牌
        @param wildBuckets: 癞子牌对应的【同点牌集】的集合
        '''
        self.cards = cards
        self.buckets = buckets
        self.wildCards = wildCards
        self.groups = []
        self.wildGroups = []
        sameCountGroupMap = {}
        for g in buckets:
            if g.cardCount <= 0:
                continue
            self.groups.append(g)
            sameCountGroup = sameCountGroupMap.get(g.cardCount)
            if not sameCountGroup:
                sameCountGroup = SameCountGroup(g.cardCount)
                sameCountGroupMap[g.cardCount] = sameCountGroup
            sameCountGroup.addGroup(g)
            
        for g in wildBuckets:
            if g.cardCount > 0:
                self.wildGroups.append(g)
                
        # 按照张数排序
        self.sameCountGroups = [sameCountGroupMap[cardCount] for cardCount in sorted(sameCountGroupMap.keys())]
        
    @property
    def cardCount(self):
        return len(self.cards)
    
    @property
    def wildCardCount(self):
        return len(self.wildCards)
    
    def findSameCountGroup(self, cardCount):
        for scg in self.sameCountGroups:
            if scg.count == cardCount:
                return scg
        return None
    
    @classmethod
    def reduceHandCards(cls, rule, cards):
        '''
        整理手牌 从手牌中分离癞子牌
        '''
        return cls.reduceCards(rule, cards, True)
    
    @classmethod
    def reduceOutCards(cls, rule, cards):
        '''
        整理出牌 不用从出牌中分离癞子牌
        '''
        return cls.reduceCards(rule, cards, False)
    
    @classmethod
    def reduceCards(cls, rule, cards, separateWild=False):
        '''
        整理一组牌
        @param cards: 一组牌
        @param separateWild: 是否将癞子牌从cards中提取出来
        '''
        buckets = [CardGroup(point) for point in xrange(15)]
        wildCards = []
        wildBuckets = [CardGroup(point) for point in xrange(15)]
        for card in cards:
            point = rule.cardToPoint(card)
            if rule.isWildCard(card):
                wildCards.append(card)
                wildBuckets[point].addCard(card)
                if not separateWild:
                    buckets[point].addCard(card)
            else:
                buckets[point].addCard(card)
                
        # 根据point对wildCards排序
        wildCards.sort(cmp=lambda x, y: cmp(rule.cardToPoint(x), rule.cardToPoint(y)))
                
        return ReducedCards(cards[:], buckets, wildCards, wildBuckets)
        
    
class ValidCards(object):
    '''
    合法的出牌
    '''
    def __init__(self, cardType, reducedCards):
        assert(isinstance(cardType, CardType))
        assert(isinstance(reducedCards, ReducedCards))
        self.cardType = cardType
        self.reducedCards = reducedCards

    @property
    def sortedCards(self):
        retCards = []
        buckets = self.reducedCards.buckets
        cardBuckets = filter(lambda x: x.cardCount > 0, buckets)
        cardBuckets.sort(key=lambda x: (x.cardCount * -1, x.point * -1))
        for bucket in cardBuckets:
            bucketCards = bucket.cards
            bucketCards.sort(key=lambda x: x)
            retCards.extend(bucket.cards)
        return retCards

    @property
    def cards(self):
        return self.reducedCards.cards
    
    def isGreaterThan(self, other):
        assert isinstance(other, ValidCards)
        assert(self.cardType.rule == other.cardType.rule)
        
        # 1. 级别高的牌大
        if self.cardType.level > other.cardType.level:
            return True
        
        if self.cardType.level < other.cardType.level:
            return False
        
        # 2. 相同级别的不同牌型不能比较
        if self.cardType != other.cardType:
            return False
        
        return self.cardType.compareValidCards(self, other) > 0
    
    def isHuoJian(self):
        '''
        判断给定的牌是否是火箭
        '''
        return self.cardType.typeId == CARD_TYPE_HUOJIAN
    
    def isZhaDan(self):
        '''
        判断给定的牌是否是炸弹
        '''
        return self.cardType.typeId == CARD_TYPE_ZHADAN

    def isSanShun(self):
        '''
        判断给定的牌是否是飞机
        '''
        return self.cardType.typeId == CARD_TYPE_SANSHUN

    def isShunZi(self):
        '''
        判断给定的牌是否是顺子
        '''
        return self.cardType.typeId == CARD_TYPE_DANSHUN
    
    def isFeiJiDai1(self):
        '''
        判断给定的牌是否是飞机带单
        '''
        return self.cardType.typeId == CARD_TYPE_FEIJIDAI1
    
    def isFeiJiDai2(self):
        '''
        判断给定的牌是否是飞机带2
        '''
        return self.cardType.typeId == CARD_TYPE_FEIJIDAI2

    def isSanDai1(self):
        '''
        判断给定的牌是否是三带单牌
        '''
        return self.cardType.typeId == CARD_TYPE_SANDAI1

    def isSanDai2(self):
        '''
        判断给定的牌是否是三带对牌
        '''
        return self.cardType.typeId == CARD_TYPE_SANDAI2

    def isDuizi(self):
        '''
        判断给定的牌是否是对子
        '''
        return self.cardType.typeId == CARD_TYPE_DUIZI

    def isDanPai(self):
        '''
        判断给定的牌是否是单牌
        '''
        return self.cardType.typeId == CARD_TYPE_DANPAI

    def isSanzhang(self):
        '''
        判断给定的牌是否是三张
        '''
        return self.cardType.typeId == CARD_TYPE_SANZHANG

    def isLastDizhuAutoOutCard(self):
        '''
        当玩家是地主的时候并且拥有牌权，则系统自动帮助地主出牌。自动出牌包括：单张、对子、三张、三张带单牌/三张带一对、火箭、炸弹。
        '''
        # 癞子打法牌型过滤
        isShunZi = False
        isSanDai2 = False
        if not self.reducedCards.wildCards:
            isSanDai2 = self.isSanDai2()
            isShunZi = self.isShunZi()
        return self.isDanPai() or self.isDuizi() or self.isSanDai1() or self.isSanzhang() or isSanDai2 or self.isHuoJian() or self.isZhaDan() or self.isShunZi() or isShunZi

    def isLastNongminAutoOutCard(self):
        '''
        当玩家是农民的时候，则系统自动帮助地主出牌。自动出牌包括：单张、对子、火箭、炸弹。
        '''
        return self.isDanPai() or self.isDuizi() or self.isHuoJian() or self.isZhaDan()

class CardDiZhuRule(object):
    '''
    牌、牌型规则
    '''
    def __init__(self,
                 nDeck=1,
                 nPlayer=3,
                 nHiddenCards=3,
                 nMaxCardsOfZhaDan=4,
                 nWild=0,
                 kingCanBeWild=False):
        '''
        @param nDeck: 几副牌
        @param nPlayer: 几个人玩
        @param nHiddenCards: 几张底牌
        @param nMaxCardsOfZhaDan: 炸弹的最大张数
        @param nWild: 选几个癞子
        @param kingCanBeWild: 王是否能成为癞子 
        '''
        
        self.nDeck = nDeck
        self.nPlayer = nPlayer
        self.nHiddenCards = nHiddenCards
        self.nMaxCardsOfZhaDan = nMaxCardsOfZhaDan
        self.nWild = nWild
        self.kingCanBeWild = kingCanBeWild
        
        # 最多有多少张癞子牌
        self.nMaxWildCards = self.nWild * self.nDeck * 4 
        
        # 最多有多少个王牌
        self.nMaxKings = self.nDeck * 2
        
        # 手中最多能有多少张牌
        self.nMaxCardsInHand = (self.nDeck * 54 - self.nHiddenCards) / self.nPlayer + nHiddenCards
        
        # 所有牌型
        self._cardTypes = []
        # 牌型map, key=typeId, value=CardType
        self._typeId2CardType = {}
        # 牌对应的点数， A=0,13,26,39; 2=1,14,27,40;...
        self._cardToPoint = [11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                             11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                             11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                             11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                             13, 14]
        self._pointToHumanCard = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'w', 'W']
        for _ in xrange(self.nWild):
            self._cardToPoint.extend([11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14])
            
        self._pointToCard = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1, 52, 53]
        
    def toHumanCard(self, card):
        return self._pointToHumanCard[self.cardToPoint(card)]
    
    def toHumanCards(self, cards):
        ret = []
        for c in cards:
            ret.append(self.toHumanCard(c))
        return ret
    
    def cardToPoint(self, card):
        '''
        获取card的点数
        '''
        if (card < 0 or card >= len(self._cardToPoint)):
            raise UnknownCardException(card)
        return self._cardToPoint[card]
    
    def pointToCard(self, point):
        '''
        根据点数获取牌值，不分花色
        '''
        if (point < 0 and point >= len(self._pointToCard)):
            raise UnknownPointException(point)
        return self._pointToCard[point]
    
    def findCardType(self, typeId):
        '''
        查找牌型
        '''
        return self._typeId2CardType.get(typeId)
    
    def findGTLevelCardTypes(self, typeId):
        '''
        查找等级大的牌型
        '''
        curCardType = self._typeId2CardType.get(typeId)
        greaterCardTypes = []
        if curCardType:
            for cardType in self._cardTypes:
                if cardType.level > curCardType.level:
                    greaterCardTypes.append(cardType)
        return greaterCardTypes
    
    def addCardTypes(self, cardTypes):
        '''
        添加牌型
        '''
        for cardType in cardTypes:
            self.addCardType(cardType)
        return self
            
    def addCardType(self, cardType):
        '''
        添加牌型
        '''
        assert(isinstance(cardType, CardType))
        assert(not cardType.rule)
        assert(not self.findCardType(cardType.typeId))
        
        cardType._rule = self
        self._cardTypes.append(cardType)
        self._typeId2CardType[cardType.typeId] = cardType
        return self
    
    def isWildCard(self, card):
        '''
        判断给定的card是否是癞子
        '''
        return card > 53 and card < len(self._cardToPoint)
    
    def isSamePointCard(self, card1, card2):
        '''
        判断给定的两个card的分值一样
        '''
        return self.cardToPoint(card1) == self.cardToPoint(card2)
        
    def changeCardToWildCard(self, card, wildIndex=0):
        '''
        把给定的card变为癞子牌
        '''
        assert(card >= 0 and card <= 53)
        assert(wildIndex >= 0 and wildIndex < self.nWild)
        if (card >= 52):
            return 54 + 15 * wildIndex + 12 + (card - 51)
        return 54 + 15 * wildIndex + (card % 13) 
    
    def changeWildCardToPointCard(self, wildCard, point):
        '''
        改变wildCard为point点数的牌
        '''
        return self.changeWildCardToCard(wildCard, self.pointToCard(point))
    
    def changeWildCardToCard(self, wildCard, target):
        '''
        改变wildCard为target, target不能为王
        '''
        assert(self.isWildCard(wildCard) and (target >= 0 and target < 52))
        
        # (wildCard - 54) / 15 定位到第几个癞子 + target的序号
        return 54 + (wildCard - 54) / 15 * 15 + target % 13
    
    def isKingCard(self, card):
        '''
        判断是否是王牌, 此处不能只判断card == 52 and card == 53
        因为如果王牌是癞子的话card会>53, 算点数是最正确的
        '''
        return self.isKingPoint(self.cardToPoint(card))
    
    def isKingPoint(self, point):
        '''
        根据point判断是否是王牌的点数
        '''
        return point == 13 or point == 14
    
    def isHuoJian(self, cards):
        '''
        判断给定的牌是否是火箭
        '''
        validCards = self.validateCards(cards)
        return validCards.isHuoJian() if validCards else False
    
    def getBombOrKingCount(self):
        '''
        获取王炸或者炸弹张数
        '''
        if self.nDeck == 1:
            return (2, 4)
        return (2, 4)
    
    def validateCardsWithPriorityTypeId(self, cards, priorityCardTypeId):
        '''
        根据牌型id，用一组牌生成合法牌类
        @param cards: 一组非癞子牌或者癞子牌已经变成对应point的癞子牌的一组牌
        @param priorityCardTypeId: 牌型id 
        '''
        priorityCardType = self.findCardType(priorityCardTypeId)
        return self.validateCards(cards, priorityCardType)

    def validateCards(self, cards, priorityCardType=None):
        '''
        生成合法牌类
        @param cards: 一组非癞子牌或者癞子牌已经变成对应point的癞子牌的一组牌
        '''
        if cards and len(cards) > 0:
            reducedCards = ReducedCards.reduceOutCards(self, cards)
            if priorityCardType:
                assert(priorityCardType.rule == self)
                validCards = priorityCardType.validate(reducedCards)
                if validCards is not None:
                    return validCards
            
            for cardType in self._cardTypes:
                if cardType != priorityCardType:
                    validCards = cardType.validate(reducedCards)
                    if validCards is not None:
                        return validCards
        return None
    
    def validateCardsWithReducedCards(self, reducedCards):
        '''
        生成合法牌类
        @param reducedCards: 一组整理的非癞子牌或者癞子牌已经变成对应point的癞子牌的一组整理的牌
        '''
        for cardType in self._cardTypes:
            validCards = cardType.validate(reducedCards)
            if validCards is not None:
                return validCards
        return None 
        
    def checkValidCardsWithHandCards(self, handCards):
        #能一手出就一手出
        handReducedCards = ReducedCards.reduceHandCards(self, handCards)
        return self.checkValidCardsWithHandReducedCards(handReducedCards)
    
    def checkValidCardsWithHandReducedCards(self, handReducedCards):
        #能一手出就一手出
        cardCount = handReducedCards.cardCount
        for cardType in self._cardTypes:
            found = cardType.findMinCards(handReducedCards, True, True)
            if found and found.reducedCards.cardCount == cardCount:
                return found
        return None

    def checkMaxValidCardsWithHandCards(self, handCards):
        handReducedCards = ReducedCards.reduceHandCards(self, handCards)
        # 能一手出就一手出
        cardCount = handReducedCards.cardCount
        self._cardTypes.sort(key=lambda c: c.level, reverse=True)
        for cardType in self._cardTypes:
            found = cardType.findMaxCards(handReducedCards, True, True)
            if found and found.reducedCards.cardCount == cardCount and cardType._isValid(found.reducedCards):
                return found
        return None
    
    def findGreaterValidCards(self, validCards, handCards, useGTLevelCardType=False):
        '''
        找出一个大的牌型
        @param useGTLevelCardType: 是否使用高等级的牌型
        '''
        assert(validCards)
        if not handCards or len(handCards) == 0:
            return None
        
        handReducedCards = ReducedCards.reduceHandCards(self, handCards)
        minValidCards = validCards.cardType.findGreaterMinValidCards(validCards, handReducedCards)
        if minValidCards: return minValidCards
        
        if useGTLevelCardType:
            for cardType in self._cardTypes:
                if cardType.level > validCards.cardType.level:
                    minValidCards = cardType.findMinCards(handReducedCards, True, True)
                    if minValidCards:
                        return minValidCards
        return None
    
    def findGreaterCards(self, cards, handCards, useGTLevelCardType=False):
        '''
        找出一个大的牌型
        @param useGTLevelCardType: 是否使用高等级的牌型
        '''
        if not cards or not handCards:
            return None
        
        validCards = self.validateCards(cards)
        if not validCards:
            return None
        
        return self.findGreaterValidCards(validCards, handCards, useGTLevelCardType)
                
    def findFirstValidCards(self, cards, priorityCardTypeIds = None):
        '''
        找第一个出的牌
        '''
        if not cards or len(cards) <= 0:
            return None
        
        reducedCards = ReducedCards.reduceHandCards(self, cards)
        
        if priorityCardTypeIds:
            if not isinstance(priorityCardTypeIds, list):
                priorityCardTypeIds = [priorityCardTypeIds]
            for priorityCardTypeId in priorityCardTypeIds:
                priorityCardType = self.findCardType(priorityCardTypeId)
                if priorityCardType:
                    priorityMinValidCards = priorityCardType.findMinCards(reducedCards, True, True)
                    if priorityMinValidCards:
                        return priorityMinValidCards
        else:
            priorityCardTypeIds = []

        oneHandValidCards = self.checkValidCardsWithHandReducedCards(reducedCards)
        if oneHandValidCards:
            return oneHandValidCards
        
        for priorityCardTypeId in self._typeId2CardType.keys():
            if priorityCardTypeId not in priorityCardTypeIds:
                cardType = self._typeId2CardType[priorityCardTypeId]
                minValidCards = cardType.findMinCards(reducedCards, True, True)
                if minValidCards:
                    return minValidCards
        return None
    
    def findFirstSmallCard(self, handCards):
        '''
        找第一个出的最小牌
        '''
        return self.findFirstValidCards(handCards, CARD_TYPE_DANPAI)
    
    def findFirstCardNormal(self, handCards):
        if not handCards or len(handCards) <= 0:
            return None
          
        reducedCards = ReducedCards.reduceHandCards(self, handCards)
        
        oneHandValidCards = self.checkValidCardsWithHandReducedCards(reducedCards)
        if oneHandValidCards:
            return oneHandValidCards
        
        normalTypeIds = [CARD_TYPE_FEIJIDAI1, CARD_TYPE_FEIJIDAI2, CARD_TYPE_SANSHUN, CARD_TYPE_SHUANGSHUN,
                         CARD_TYPE_DANSHUN, CARD_TYPE_SANDAI2, CARD_TYPE_SANDAI1, CARD_TYPE_SANZHANG,
                         CARD_TYPE_DANPAI, CARD_TYPE_DUIZI, CARD_TYPE_ZHADAN, CARD_TYPE_HUOJIAN]
        
        for typeId in normalTypeIds:
            cardType = self.findCardType(typeId)
            if cardType:
                found = cardType.findMinCards(reducedCards, False, False)
                if found:
                    return found
        return None
    
    def findFirstGuardCard(self, handCards):
        if not handCards or len(handCards) <= 0:
            return None
        
        reducedCards = ReducedCards.reduceHandCards(self, handCards)
        
        normalTypeIds = [CARD_TYPE_FEIJIDAI1, CARD_TYPE_FEIJIDAI2, CARD_TYPE_SANSHUN, CARD_TYPE_SHUANGSHUN,
                         CARD_TYPE_DANSHUN, CARD_TYPE_SANDAI2, CARD_TYPE_SANDAI1, CARD_TYPE_SANZHANG,
                         CARD_TYPE_DANPAI, CARD_TYPE_DUIZI, CARD_TYPE_ZHADAN, CARD_TYPE_HUOJIAN]
        
        for typeId in normalTypeIds:
            cardType = self.findCardType(typeId)
            if cardType:
                found = cardType.findMinCards(reducedCards, False, False)
                if found:
                    return found
        
        #癞子凑小对
        cardType = self.findCardType(CARD_TYPE_DUIZI)
        if cardType:
            found = cardType.findMinCards(reducedCards, True, True)
            if found:
                return found
        
        #查找最大的单牌
        cardType = self.findCardType(CARD_TYPE_DANPAI)
        if cardType:
            found = cardType.findMaxCards(reducedCards, True, True)
            if found:
                return found
        return None
    
class CardType(object):
    def __init__(self, typeId, level):
        # 牌型类型ID
        self._typeId = typeId
        # 牌型级别
        self._level = level
        # 规则
        self._rule = None
    
    @property
    def typeId(self):
        return self._typeId
    
    @property
    def level(self):
        return self._level
    
    @property
    def rule(self):
        return self._rule
    
    def _validateFindCards(self, findCards):
        '''
        用找好的牌生成合法牌型
        '''
        return ValidCards(self, ReducedCards.reduceOutCards(self.rule, findCards))
    
    def validate(self, reducedCards):
        '''
        验证reducedCards是否是合法的牌
        @return: ValidCards or None
        '''
        if self._isValid(reducedCards):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; l == r 返回 0; l < r 返回-1
        '''
        raise NotImplementedError
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        raise NotImplementedError
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 最小的较大牌
        '''
        raise NotImplementedError
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        raise NotImplementedError
    
    def _isValid(self, reducedCards):
        raise NotImplementedError
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        '''
        查找符合本牌型的最小牌
        '''
        raise NotImplemented()
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        '''
        查找符合本牌型的最小牌
        '''
        raise NotImplemented()
    
class CardFinder(object):
    @classmethod
    def findNSamePointCardsByGTPoint(cls, n, point, handReducedCards, excludeGroups=None):
        '''
        从handReducedCards中查找n张点数相同的牌，并且点数比point大的牌
        @return (cards, set)
        '''
        assert(n > 0)
        assert(isinstance(handReducedCards, ReducedCards))
        ret = []
        for scg in handReducedCards.sameCountGroups:
            if scg.count < n:
                continue
            for g in scg.groups:
                if g.point > point and (not excludeGroups or g not in excludeGroups):
                    ret.append((g.cards[0:n], set([g])))
        return ret

    @classmethod
    def calcNShunCount(cls, n, point, handReducedCards):
        count = 0
        for i in range(point, -1, -1):
            if handReducedCards.buckets[i].group.cardCount < n:
                break
        return count

    @classmethod
    def collectNShunGroups(cls, x, n, point, handReducedCards):
        '''
        收集point开始的x的n顺
        '''
        ret = []
        group = handReducedCards.buckets[point]
        if group.cardCount < n:
            return ret
        ret.append(group)
        # 前面的
        for i in range(point - 1, point - x - 1, -1):
            group = handReducedCards.buckets[i]
            if group.cardCount < n:
                break
            ret.insert(0, group)
        for i in range(point + 1, 12):
            group = handReducedCards.buckets[i]
            if group.cardCount < n:
                break
            ret.append(group)
        return ret
        
    @classmethod
    def collectCards(cls, groups, start, end, n):
        cards = []
        groupSet = set()
        for i in range(start, end):
            cards.extend(groups[i].cards[0:n])
            groupSet.add(groups[i])
        return (cards, groupSet)
    
    @classmethod
    def findXNShunByGTPoint(cls, x, n, point, handReducedCards):
        '''
        查找X组N顺的点数比point大的牌
        '''
        ret = []
        while (point + 1 < 12):
            point += 1
            groups = cls.collectNShunGroups(x, n, point, handReducedCards)
            count = len(groups) - x
            if count >= 0:
                point = groups[-1].point + 1
                for i in xrange(count + 1):
                    ret.append(cls.collectCards(groups, i, i + x, n))
        return ret
    
    @classmethod
    def _findNMinCardGroup(cls, n, handReducedCards, excludeGroups=None):
        '''
        查找N张最小的牌（从单张开始）的【同点牌集】
        '''
        groups = []
        cardCount = 0
        for scg in handReducedCards.sameCountGroups:
            for g in scg.groups:
                if excludeGroups and g in excludeGroups:
                    continue
                groups.append(g)
                cardCount += scg.count
                if cardCount >= n:
                    return groups
        return None

    @classmethod
    def findNMinCard(cls, n, handReducedCards, excludeGroups=None):
        groups = cls._findNMinCardGroup(n, handReducedCards, excludeGroups)
        if groups:
            cards = []
            groupSet = set()
            for g in groups:
                count = min(n - len(cards), g.cardCount)
                cards.extend(g.cards[0:count])
                groupSet.add(g)
                if len(cards) >= n:
                    break
            return (cards, groupSet)
        return None
        
    @classmethod
    def find2MinCard(cls, handReducedCards, excludeGroups=None):
        '''
        从handReducedCards中查找2张牌，可以是对
        '''
        # groups = [1][1] or [1][2] or [1][3] or [1][4] or [2]
        groups = cls._findNMinCardGroup(2, handReducedCards, excludeGroups)
        if groups:
            # 找到一组2张及以上的牌
            if len(groups) == 1:
                return (groups[0].cards[0:2], set([groups[0]]))
            
            # 一张单牌，一张对子拆的牌
            if groups[1].cardCount == 2:
                # 拆开对子后剩的单牌比另一张单牌要小，则返回对子牌
                if groups[0].point > groups[1].point:
                    return (groups[1].cards[0:2], set([groups[1]]))

            groups = sorted(groups, key=lambda g:g.point)
            cards = [groups[0].cards[0], groups[1].cards[0]]
            return (cards, set([groups[0], groups[1]]))
        return None
    
    @classmethod
    def findNSamePointCards(cls, rule, n, point, handReducedCards, useWild=False, usePureWild=False, excludeGroups=None, excludeWildCardNum=0):
        '''
        查找n个同点牌
        @param n: 个数
        @param point: 最小点数（不包含）
        @param handReducedCards: 整理好的牌
        @param useWild: 是否使用癞子
        @param userPureWild: 是否使用纯癞子
        @param excludePoint: 排除的牌的点集合 
        @param excludeWildCardNum: 排除的癞子个数
        '''
        # 没癞子情况
        retGroups = cls.findNSamePointCardsByGTPoint(n, point, handReducedCards, excludeGroups)
        # 可用癞子个数
        canUsedWildCardsNum = handReducedCards.wildCardCount - excludeWildCardNum
        if useWild and n > 1 and canUsedWildCardsNum > 0:
            for scg in handReducedCards.sameCountGroups[::-1]:
                if scg.count < n - canUsedWildCardsNum or scg.count >= n:
                    continue
                for g in scg.groups:
                    if g.point > point and g.point <= 12 and (not excludeGroups or g not in excludeGroups):
                        chWildCards = [rule.changeWildCardToPointCard(card, g.point) for card in handReducedCards.wildCards[0:n-g.cardCount]]
                        retGroups.append((g.cards + chWildCards, set([g])))
        if usePureWild and canUsedWildCardsNum >= n:
            for g in handReducedCards.wildGroups:
                if g.point > point and (not excludeGroups or g not in excludeGroups):
                    if g.cardCount >= n:
                        retGroups.append((g.cards[0:n], set([g])))
                    else:
                        chWildCards = [rule.changeWildCardToPointCard(card, g.point) for card in handReducedCards.wildCards if card not in g.cards][0:n-g.cardCount]
                        retGroups.append((g.cards + chWildCards, set([g])))
        return retGroups
    
    @classmethod
    def _findNShunFromContinueGroups(cls, rule, n, groups, wildCards):
        '''
        从连续的groups中以及给定的癞子牌中找n顺
        '''
        usedCards = []
        restWildCards = wildCards[:]
        for group in groups:
            if group.cardCount >= n:
                usedCards.extend(group.cards[0:n])
            elif len(restWildCards) >= n - group.cardCount:
                usedCards.extend(group.cards[:])
                chWildCards = [rule.changeWildCardToPointCard(card, group.point) for card in restWildCards[0:n - group.cardCount]]
                usedCards.extend(chWildCards)
                restWildCards = restWildCards[n - group.cardCount:]
            else:
                return None
        return usedCards
    
    @classmethod
    def findXNShun(cls, rule, x, n, point, handReducedCards, userWild=False):
        '''
        查找长度为x的n顺
        @param x: 顺子长度
        @param n: n顺
        @param point: 顺子的起始牌的点数
        @param handReducedCards: 整理好的牌
        @param useWild: 是否使用癞子
        '''
        assert(point >= 0)
        ret = []
        startPoints = []
        startPoint = point
        endPoint = point + x
        while endPoint <= 12:
            groups = handReducedCards.buckets[startPoint:endPoint]
            nShunCards = cls._findNShunFromContinueGroups(rule, n, groups, [])
            if nShunCards:
                ret.append((nShunCards, groups))
                startPoints.append(startPoint)
            startPoint = startPoint + 1
            endPoint = endPoint + 1
        if userWild and handReducedCards.wildCardCount > 0:
            wildCards = handReducedCards.wildCards
            startPoint = point
            endPoint = point + x
            while endPoint <= 12:
                if startPoint not in startPoints:
                    groups = handReducedCards.buckets[startPoint:endPoint]
                    nShunCards = cls._findNShunFromContinueGroups(rule, n, groups, wildCards)
                    if nShunCards:
                        ret.append((nShunCards, groups))
                startPoint = startPoint + 1
                endPoint = endPoint + 1
        return ret
    
    @classmethod
    def findNMinCardsWithOutZhadanOrHuojian(cls, rule, n, handReducedCards, excludeGroups=None):
        excludeGroups2 = set(excludeGroups) if excludeGroups else set()
        kingGroups = set()
        for group in handReducedCards.groups:
            if group.cardCount == 4 and group not in excludeGroups2:
                excludeGroups2.add(group)
            elif rule.isKingPoint(group.point):
                kingGroups.add(group)
                
        if sum([g.cardCount for g in kingGroups]) == rule.nMaxKings:
            excludeGroups2 = excludeGroups2.union(kingGroups)
        return cls.findNMinCard(n, handReducedCards, excludeGroups2)
    
    @classmethod
    def findDanCardsWithOutZhadanOrHuojian(cls, rule, handReducedCards, excludeGroups=None):
        excludeGroups2 = set(excludeGroups) if excludeGroups else set()
        kingGroups = set()
        for group in handReducedCards.groups:
            if group.cardCount == 4 and group not in excludeGroups2:
                excludeGroups2.add(group)
            elif rule.isKingPoint(group.point):
                kingGroups.add(group)
                
        if sum([g.cardCount for g in kingGroups]) == rule.nMaxKings:
            excludeGroups2 = excludeGroups2.union(kingGroups)
        return cls.findNSamePointCards(rule, 1, -1, handReducedCards, False, False, excludeGroups2)

    @classmethod
    def findHuojian(cls, rule, handReducedCards):
        kingGroups = set()
        for group in handReducedCards.groups:
            if rule.isKingPoint(group.point):
                kingGroups.add(group)
        if sum([g.cardCount for g in kingGroups]) == rule.nMaxKings:
            return True
        return False

    @classmethod
    def findFeijiCount(cls, rule, handReducedCards):
        return len(cls.findXNShun(rule, 2, 3, 0, handReducedCards))

    @classmethod
    def findZhadanCount(cls, rule, handReducedCards):
        zhaDanCount = 0
        for group in handReducedCards.groups:
            if group.cardCount == 4:
                zhaDanCount += 1
        return zhaDanCount

    @classmethod
    def findHuojianAndZhadan2(cls, rule, handReducedCards):
        zhadan2 = False
        for group in handReducedCards.groups:
            if group.cardCount == 4 and group.point == rule.cardToPoint(2):
                zhadan2 = True
                break
        return cls.findHuojian(rule, handReducedCards) or zhadan2

        

class CardTypeDanPai(CardType):
    '''
    单牌
    '''
    def __init__(self):
        super(CardTypeDanPai, self).__init__(CARD_TYPE_DANPAI, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.groups[0].point, r.reducedCards.groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        point = validCards.reducedCards.groups[0].point
        ret = CardFinder.findNSamePointCards(self.rule, 1, point, handReducedCards, True, True)
        return [cards for cards, _ in ret]
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return self._validateFindCards(ret[0]) if len(ret) > 0 else None
        
    def _isValid(self, reducedCards):
        return reducedCards.cardCount == 1
    
    def findMinCards(self, handReducedCards, useWild=False, purlWild=False):
        founds = CardFinder.findNSamePointCards(self.rule, 1, -1, handReducedCards, useWild, purlWild)
        return self._validateFindCards(founds[0][0]) if len(founds) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        founds = CardFinder.findNSamePointCards(self.rule, 1, -1, handReducedCards, useWild, purlWild)
        return self._validateFindCards(founds[-1][0]) if len(founds) > 0 else None
    
class CardTypeDuizi(CardType):
    def __init__(self):
        super(CardTypeDuizi, self).__init__(CARD_TYPE_DUIZI, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.groups[0].point, r.reducedCards.groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        point = validCards.reducedCards.groups[0].point
        ret = CardFinder.findNSamePointCards(self.rule, 2, point, handReducedCards, True, True)
        return [cards for cards, _ in ret]
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return self._validateFindCards(ret[0]) if len(ret) > 0 else None

    def _isValid(self, reducedCards):
        return reducedCards.cardCount == 2 and len(reducedCards.groups) == 1
    
    def findMinCards(self, handReducedCards, useWild=False, purlWild=False):
        founds = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild)
        return self._validateFindCards(founds[0][0]) if len(founds) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        founds = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild)
        return self._validateFindCards(founds[-1][0]) if len(founds) > 0 else None

class CardTypeSanzhang(CardType):
    def __init__(self):
        super(CardTypeSanzhang, self).__init__(CARD_TYPE_SANZHANG, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.groups[0].point, r.reducedCards.groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        point = validCards.reducedCards.groups[0].point
        ret = CardFinder.findNSamePointCards(self.rule, 3, point, handReducedCards, True, True)
        return [cards for cards, _ in ret]
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return self._validateFindCards(ret[0]) if len(ret) > 0 else None

    def _isValid(self, reducedCards):
        return reducedCards.cardCount == 3 and len(reducedCards.groups) == 1
    
    def findMinCards(self, handReducedCards, useWild=False, purlWild=False):
        founds = CardFinder.findNSamePointCards(self.rule, 3, -1, handReducedCards, useWild, purlWild)
        return self._validateFindCards(founds[0][0]) if len(founds) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        founds = CardFinder.findNSamePointCards(self.rule, 3, -1, handReducedCards, useWild, purlWild)
        return self._validateFindCards(founds[-1][0]) if len(founds) > 0 else None

class CardTypeSanDai1(CardType):
    def __init__(self):
        super(CardTypeSanDai1, self).__init__(CARD_TYPE_SANDAI1, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.sameCountGroups[-1].groups[0].point,
                   r.reducedCards.sameCountGroups[-1].groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 4 or len(handReducedCards.groups) < 2: 
            return []
        ret = []
        point = validCards.reducedCards.sameCountGroups[-1].groups[0].point
        sanzhangList = CardFinder.findNSamePointCards(self.rule, 3, point, handReducedCards, True, True)
        for sanzhang, groups in sanzhangList:
            danpaiList = CardFinder.findDanCardsWithOutZhadanOrHuojian(self.rule, handReducedCards, groups)
            if len(sanzhangList) > 1:
                cards = sanzhang[:]
                cards.extend(danpaiList[0][0])
                ret.append(cards)
            else:
                for danpai, _ in danpaiList:
                    cards = sanzhang[:]
                    cards.extend(danpai)
                    ret.append(cards)
        return ret
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 4 or len(handReducedCards.groups) < 2: 
            return []
        
        point = validCards.reducedCards.sameCountGroups[-1].groups[0].point
        sanzhangList = CardFinder.findNSamePointCards(self.rule, 3, point, handReducedCards, True, True)
        for sanzhang, groups in sanzhangList:
            danpaiList = CardFinder.findDanCardsWithOutZhadanOrHuojian(self.rule, handReducedCards, groups)
            if len(sanzhangList) > 1:
                cards = sanzhang[:]
                cards.extend(danpaiList[0][0])
                return self._validateFindCards(cards)
            else:
                for danpai, _ in danpaiList:
                    cards = sanzhang[:]
                    cards.extend(danpai)
                    return self._validateFindCards(cards)
        return None

    def _isValid(self, reducedCards):
        return (reducedCards.cardCount == 4
                and len(reducedCards.groups) == 2
                and reducedCards.sameCountGroups[-1].count == 3)
    
    def findMinCards(self, handReducedCards, useWild=False, purlWild=False):
        if handReducedCards.cardCount < 4 or len(handReducedCards.groups) < 2: 
            return None
        founds = CardFinder.findNSamePointCards(self.rule, 3, -1, handReducedCards, useWild, purlWild)
        if len(founds) == 0:
            return None
        danCards = CardFinder.findNSamePointCards(self.rule, 1, -1, handReducedCards, False, False, founds[0][1])
        if len(danCards) == 0:
            return None
        return self._validateFindCards(founds[0][0] + danCards[0][0])
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 4 or len(handReducedCards.groups) < 2: 
            return None
        founds = CardFinder.findNSamePointCards(self.rule, 3, -1, handReducedCards, useWild, purlWild)
        if len(founds) == 0:
            return None
        danCards = CardFinder.findNSamePointCards(self.rule, 1, -1, handReducedCards, False, False, founds[-1][1])
        if len(danCards) == 0:
            return None
        return self._validateFindCards(founds[-1][0] + danCards[0][0])
        
class CardTypeSanDai2(CardType):
    def __init__(self):
        super(CardTypeSanDai2, self).__init__(CARD_TYPE_SANDAI2, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.sameCountGroups[-1].groups[0].point,
                   r.reducedCards.sameCountGroups[-1].groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 5: 
            return []
        ret = []
        point = validCards.reducedCards.sameCountGroups[-1].groups[0].point
        sanzhangList = CardFinder.findNSamePointCards(self.rule, 3, point, handReducedCards, True, True)
        for sanzhang, groups in sanzhangList:
            founds = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, True, False, groups, 3-list(groups)[0].cardCount)
            if len(founds) > 0:
                cards = sanzhang[:]
                cards.extend(founds[0][0])
                ret.append(cards)
        return ret
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self. findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 5: 
            return []
        
        point = validCards.reducedCards.sameCountGroups[-1].groups[0].point
        sanzhangList = CardFinder.findNSamePointCards(self.rule, 3, point, handReducedCards, True, True)
        for sanzhang, groups in sanzhangList:
            founds = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, True, False, groups, 3-list(groups)[0].cardCount)
            if len(founds) > 0:
                cards = sanzhang[:]
                cards.extend(founds[0][0])
                return self._validateFindCards(cards)
        return None

    def _isValid(self, reducedCards):
        return (reducedCards.cardCount == 5 
                and len(reducedCards.groups) == 2
                and reducedCards.sameCountGroups[-1].count == 3)
    
    def findMinCards(self, handReducedCards, useWild=False, purlWild=False):
        if handReducedCards.cardCount < 5 or len(handReducedCards.groups) < 2: 
            return None
        founds = CardFinder.findNSamePointCards(self.rule, 3, -1, handReducedCards, useWild, purlWild)
        if len(founds) == 0:
            return None
        duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild, founds[0][1])
        if len(duiCards) == 0:
            return None
        return self._validateFindCards(founds[0][0] + duiCards[0][0])
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 5 or len(handReducedCards.groups) < 2: 
            return None
        founds = CardFinder.findNSamePointCards(self.rule, 3, -1, handReducedCards, useWild, purlWild)
        if len(founds) == 0:
            return None
        duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild, founds[-1][1])
        if len(duiCards) == 0:
            return None
        return self._validateFindCards(founds[-1][0] + duiCards[0][0])
        
class CardTypeDanShun(CardType):
    def __init__(self):
        super(CardTypeDanShun, self).__init__(CARD_TYPE_DANSHUN, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        if l.reducedCards.cardCount != r.reducedCards.cardCount:
            return -1
        return cmp(l.reducedCards.groups[-1].point, r.reducedCards.groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        x = validCards.reducedCards.cardCount
        if len(handReducedCards.groups) + handReducedCards.wildCardCount < x: 
            return []
        ret = CardFinder.findXNShun(self.rule, 
                                    x,
                                    1,
                                    validCards.reducedCards.groups[1].point,
                                    handReducedCards,
                                    True)
        return [cards for cards, _ in ret]
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return self._validateFindCards(ret[0]) if len(ret) > 0 else None

    def _isValid(self, reducedCards):
        if len(reducedCards.sameCountGroups) != 1 or reducedCards.sameCountGroups[0].count != 1 or len(reducedCards.groups) < 5:
            return False
        # 2以上不能连
        if reducedCards.groups[-1].point >= 12:
            return False
        return (reducedCards.groups[-1].point + 1 - reducedCards.groups[0].point) == len(reducedCards.groups)
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 5: 
            return None
        founds = CardFinder.findXNShun(self.rule, 5, 1, 0, handReducedCards, useWild)
        return self._validateFindCards(founds[0][0]) if len(founds) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 5: 
            return None
        founds = []
        for iCount in xrange(5, 13):
            ret = CardFinder.findXNShun(self.rule, iCount, 1, 0, handReducedCards, useWild)
            founds.extend(ret)
        return self._validateFindCards(founds[-1][0]) if len(founds) > 0 else None


class CardTypeQuickLaiziDanShun(CardTypeDanShun):
    def __init__(self):
        super(CardTypeQuickLaiziDanShun, self).__init__()

    def _isValid(self, reducedCards):
        if len(reducedCards.sameCountGroups) != 1 or reducedCards.sameCountGroups[0].count != 1 or len(
                reducedCards.groups) < 5:
            return False
        # 2以上不能连
        if reducedCards.groups[-1].point >= 12:
            return False
        # 6以下不能连
        if reducedCards.groups[0].point <= 2:
            return False
        return (reducedCards.groups[-1].point + 1 - reducedCards.groups[0].point) == len(reducedCards.groups)


class CardTypeShuangShun(CardType):
    def __init__(self):
        super(CardTypeShuangShun, self).__init__(CARD_TYPE_SHUANGSHUN, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        if l.reducedCards.cardCount != r.reducedCards.cardCount:
            return -1
        return cmp(l.reducedCards.groups[-1].point, r.reducedCards.groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        x = len(validCards.reducedCards.groups)
        if handReducedCards.cardCount < x * 2: 
            return []
        ret = CardFinder.findXNShun(self.rule, x,
                                    2,
                                    validCards.reducedCards.groups[1].point,
                                    handReducedCards,
                                    True)
        return [cards for cards, _ in ret]
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return self._validateFindCards(ret[0]) if len(ret) > 0 else None

    def _isValid(self, reducedCards):
        if len(reducedCards.sameCountGroups) != 1 or reducedCards.sameCountGroups[0].count != 2 or len(reducedCards.groups) < 3:
            return False
        # 2以上不能连
        if reducedCards.groups[-1].point >= 12:
            return False
        return (reducedCards.groups[-1].point + 1 - reducedCards.groups[0].point) == len(reducedCards.groups)
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 6: 
            return None
        founds = CardFinder.findXNShun(self.rule, 3, 2, 0, handReducedCards, useWild)
        return self._validateFindCards(founds[0][0]) if len(founds) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 6: 
            return None
        founds = []
        for iCount in xrange(3, 13):
            ret = CardFinder.findXNShun(self.rule, iCount, 2, 0, handReducedCards, useWild)
            founds.extend(ret)
        return self._validateFindCards(founds[-1][0]) if len(founds) > 0 else None
        
class CardTypeSanShun(CardType):
    def __init__(self):
        super(CardTypeSanShun, self).__init__(CARD_TYPE_SANSHUN, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        if l.reducedCards.cardCount != r.reducedCards.cardCount:
            return -1
        return cmp(l.reducedCards.groups[-1].point, r.reducedCards.groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < len(validCards.reducedCards.groups) * 3: 
            return []
        ret = CardFinder.findXNShun(self.rule, 
                                    len(validCards.reducedCards.groups),
                                    3,
                                    validCards.reducedCards.groups[1].point,
                                    handReducedCards,
                                    True)
        return [cards for cards, _ in ret]
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards, _ in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        ret = self.findGreaterCards(validCards, handReducedCards)
        return self._validateFindCards(ret[0]) if len(ret) > 0 else None
    
    def _isValid(self, reducedCards):
        if len(reducedCards.sameCountGroups) != 1 or reducedCards.sameCountGroups[0].count != 3 or len(reducedCards.groups) < 2:
            return False
        # 2以上不能连
        if reducedCards.groups[-1].point >= 12:
            return False
        return (reducedCards.groups[-1].point + 1 - reducedCards.groups[0].point) == len(reducedCards.groups)
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 6: 
            return None
        founds = CardFinder.findXNShun(self.rule, 2, 3, 0, handReducedCards, useWild)
        return self._validateFindCards(founds[0][0]) if len(founds) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 6: 
            return None
        founds = []
        for iCount in xrange(2, 13):
            ret = CardFinder.findXNShun(self.rule, iCount, 3, 0, handReducedCards, useWild)
            founds.extend(ret)
        return self._validateFindCards(founds[-1][0]) if len(founds) > 0 else None
        
class CardTypeFeijiDai1(CardType):
    def __init__(self):
        super(CardTypeFeijiDai1, self).__init__(CARD_TYPE_FEIJIDAI1, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        if l.reducedCards.cardCount != r.reducedCards.cardCount:
            return -1
        return cmp(l.reducedCards.findSameCountGroup(3).groups[-1].point,
                   r.reducedCards.findSameCountGroup(3).groups[-1].point)
        
    def _feijiInfo(self, validCards):
        '''
        获取飞机的长度以及最小牌点数
        '''
        assert(validCards.cardType == self)
        scg3 = validCards.reducedCards.findSameCountGroup(3)
        scg4 = validCards.reducedCards.findSameCountGroup(4)
        feijiLength = 0 
        minPoint = 0
        if scg3 and not scg4:
            feijiLength = len(scg3.groups)
            minPoint = scg3.groups[0].point
        elif scg4 and not scg3:
            feijiLength = len(scg4.groups)
            minPoint = scg4.groups[0].point
        elif scg4 and scg3:
            feijiLength = len(scg3.groups) + len(scg4.groups)
            minPoint = min(scg3.groups[0].point, scg4.groups[0].point)
        return (feijiLength, minPoint)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        feijiLength, minPoint = self._feijiInfo(validCards)
        if handReducedCards.cardCount < feijiLength * 4: 
            return []
        feijiRet = CardFinder.findXNShun(self.rule, 
                                         feijiLength,
                                         3,
                                         minPoint + 1,
                                         handReducedCards,
                                         True)
        ret = []
        for feiji, groups in feijiRet:
            found = CardFinder.findNMinCardsWithOutZhadanOrHuojian(self.rule, feijiLength, handReducedCards, groups)
            if found:
                cards = feiji[:]
                cards.extend(found[0])
                ret.append(cards)
        return ret
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        feijiLength, minPoint = self._feijiInfo(validCards)
        if handReducedCards.cardCount < feijiLength * 4: 
            return None
        feijiRet = CardFinder.findXNShun(self.rule, 
                                         feijiLength,
                                         3,
                                         minPoint + 1,
                                         handReducedCards,
                                         True)
        
        for feiji, groups in feijiRet:
            found = CardFinder.findNMinCardsWithOutZhadanOrHuojian(self.rule, feijiLength, handReducedCards, groups)
            if found:
                cards = feiji[:]
                cards.extend(found[0])
                return self._validateFindCards(cards)
        return None
    
    def _isValid(self, reducedCards):
        if reducedCards.cardCount % 4 != 0: 
            return False
        # 三顺长度
        sunCount = reducedCards.cardCount / 4
        # 是否能找到
        founds = CardFinder.findXNShun(self.rule, sunCount, 3, 0, reducedCards)
        return len(founds) > 0
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 8: 
            return None
        founds = CardFinder.findXNShun(self.rule, 2, 3, 0, handReducedCards, useWild)
        if len(founds) == 0:
            return None
        danCards = CardFinder.findNMinCardsWithOutZhadanOrHuojian(self.rule, 2, handReducedCards, founds[0][1])
        if danCards:
            cards = founds[0][0][:]
            cards.extend(danCards[0])
            return self._validateFindCards(cards)
        return None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 8: 
            return None
        founds = []
        for iCount in xrange(2, 13):
            ret = CardFinder.findXNShun(self.rule, iCount, 3, 0, handReducedCards, useWild)
            founds.extend(ret)
        if len(founds) == 0:
            return None
        for found in founds[::-1]:
            danCards = CardFinder.findNMinCardsWithOutZhadanOrHuojian(self.rule, len(found[1]), handReducedCards, found[1])
            if danCards:
                cards = found[0][:]
                cards.extend(danCards[0])
                return self._validateFindCards(cards)
        return None
        
class CardTypeFeijiDai2(CardType):
    def __init__(self):
        super(CardTypeFeijiDai2, self).__init__(CARD_TYPE_FEIJIDAI2, CARD_LEVEL_NORMAL)
    
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        if l.reducedCards.cardCount != r.reducedCards.cardCount:
            return -1
        return cmp(l.reducedCards.findSameCountGroup(3).groups[-1].point,
                   r.reducedCards.findSameCountGroup(3).groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        scg = validCards.reducedCards.findSameCountGroup(3)
        if handReducedCards.cardCount < len(scg.groups) * 5: 
            return []
        feijiRet = CardFinder.findXNShun(self.rule, 
                                         len(scg.groups),
                                         3,
                                         scg.groups[1].point,
                                         handReducedCards,
                                         True)
        ret = []
        for feiji, groups in feijiRet:
            usedWildCardNum = len(scg.groups) * 3 - sum([g.cardCount for g in groups])
            duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, True, True, groups, usedWildCardNum)
            if len(duiCards) >= len(scg.groups):
                cards = feiji[:]
                for i in xrange(len(scg.groups)):
                    cards.extend(duiCards[i][0])
                ret.append(cards)
        return ret
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        scg = validCards.reducedCards.findSameCountGroup(3)
        if handReducedCards.cardCount < len(scg.groups) * 5: 
            return None
        feijiRet = CardFinder.findXNShun(self.rule, 
										 len(scg.groups),
                                         3,
                                         scg.groups[1].point,
                                         handReducedCards,
                                         True)
        
        for feiji, groups in feijiRet:
            usedWildCardNum = len(scg.groups) * 3 - sum([g.cardCount for g in groups])
            duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, True, True, groups, usedWildCardNum)
            if len(duiCards) >= len(scg.groups):
                cards = feiji[:]
                for i in xrange(len(scg.groups)):
                    cards.extend(duiCards[i][0])
                return self._validateFindCards(cards)
        return None
    
    def _isValid(self, reducedCards):
        if reducedCards.cardCount < 10 or reducedCards.cardCount % 5 != 0: return False
        
        sc2 = reducedCards.findSameCountGroup(2)
        sc3 = reducedCards.findSameCountGroup(3)
        sc4 = reducedCards.findSameCountGroup(4)
        sc5 = reducedCards.findSameCountGroup(5)
        
        g2count = len(sc2.groups) if sc2 else 0
        g3count = len(sc3.groups) if sc3 else 0
        g4count = len(sc4.groups) if sc4 else 0
        g5count = len(sc5.groups) if sc5 else 0
        
        # 所有对子的个数
        all_g2count = g2count + g5count + 2 * g4count
        # 所有三个的个数
        all_g3count  = g3count + g5count
        
        # 连顺的最大最小值
        sunMin = 0
        sunMax = 0
        if sc3 and sc5:
            sunMin = min(sc3.groups[0].point, sc5.groups[0].point)
            sunMax = max(sc3.groups[-1].point, sc5.groups[-1].point)
        elif sc3:
            sunMin = sc3.groups[0].point
            sunMax = sc3.groups[-1].point
        elif sc5:
            sunMin = sc5.groups[0].point
            sunMax = sc5.groups[-1].point
        
        return all_g2count == all_g3count\
               and all_g3count * 5 == reducedCards.cardCount \
               and all_g2count * 5 == reducedCards.cardCount \
               and sunMax - sunMin + 1 == all_g3count
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 10: 
            return None
        founds = CardFinder.findXNShun(self.rule, 2, 3, 0, handReducedCards, useWild)
        if len(founds) == 0:
            return None
        usedWildCardNum = 6 - sum([g.cardCount for g in founds[0][1]])
        duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild, founds[0][1], usedWildCardNum)
        if len(duiCards) >= 2:
            cards = founds[0][0][:]
            cards.extend(duiCards[0][0])
            cards.extend(duiCards[1][0])
            return self._validateFindCards(cards)
        return None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 10: 
            return None
        founds = []
        for iCount in xrange(2, 13):
            ret = CardFinder.findXNShun(self.rule, iCount, 3, 0, handReducedCards, useWild)
            founds.extend(ret)
        if len(founds) == 0:
            return None
        for cards, groups in founds[::-1]:
            usedWildCardNum = len(cards) - sum([g.cardCount for g in groups])
            duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild, groups, usedWildCardNum)
            if len(duiCards) >= len(groups):
                cardsTmp = cards[:]
                for i in xrange(len(groups)):
                    cardsTmp.extend(duiCards[i][0])
                return self._validateFindCards(cardsTmp)
        return None
    
class CardTypeSiDai2Dan(CardType):
    '''
    四带二张单牌
    '''
    def __init__(self):
        super(CardTypeSiDai2Dan, self).__init__(CARD_TYPE_SIDAI2DAN, CARD_LEVEL_NORMAL)
        
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.sameCountGroups[-1].groups[0].point,
                   r.reducedCards.sameCountGroups[-1].groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 6:
            return []
        ret = CardFinder.findNSamePointCards(self.rule, 4, validCards.reducedCards.findSameCountGroup(4).groups[0].point, handReducedCards, True, True)
        founds = []
        for cards, groups in ret:
            twoCards = CardFinder.find2MinCard(handReducedCards, groups)
            if twoCards:
                founds.append(cards + twoCards[0])
        return founds
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 6:
            return None
        ret = CardFinder.findNSamePointCards(self.rule, 4, validCards.reducedCards.findSameCountGroup(4).groups[0].point, handReducedCards, True, True)
        
        for cards, groups in ret:
            twoCards = CardFinder.find2MinCard(handReducedCards, groups)
            if twoCards:
                return self._validateFindCards(cards + twoCards[0])
        return None

    def _isValid(self, reducedCards):
        return reducedCards.cardCount == 6 \
            and reducedCards.findSameCountGroup(4)
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 6:
            return None
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, useWild, purlWild)
        if len(ret) == 0:
            return None
        twoCards = CardFinder.find2MinCard(handReducedCards, ret[0][1])
        if twoCards:
            return self._validateFindCards(ret[0][0] + twoCards[0])
        return None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 6:
            return None
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, useWild, purlWild)
        if len(ret) == 0:
            return None
        twoCards = CardFinder.find2MinCard(handReducedCards, ret[-1][1])
        if twoCards:
            return self._validateFindCards(ret[-1][0] + twoCards[0])
        return None
    
class CardTypeSiDai2Dui(CardType):
    '''
    四带二对牌
    '''
    def __init__(self):
        super(CardTypeSiDai2Dui, self).__init__(CARD_TYPE_SIDAI2DUI, CARD_LEVEL_NORMAL)
        
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.sameCountGroups[-1].groups[0].point,
                   r.reducedCards.sameCountGroups[-1].groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 8:
            return []
        ret = CardFinder.findNSamePointCards(self.rule, 4, validCards.reducedCards.findSameCountGroup(4).groups[0].point, handReducedCards, True, True)
        founds = []
        for cards, groups in ret:
            duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, True, True, groups, 4 - list(groups)[0].cardCount)
            if len(duiCards) >= 2:
                founds.append(cards + duiCards[0][0] + duiCards[1][0])
        return founds
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        ret = self.findGreaterCards(validCards, handReducedCards)
        return [self._validateFindCards(cards) for cards in ret]
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        if handReducedCards.cardCount < 8:
            return None
        ret = CardFinder.findNSamePointCards(self.rule, 4, validCards.reducedCards.findSameCountGroup(4).groups[0].point, handReducedCards, True, True)
        
        for cards, groups in ret:
            duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, True, True, groups, 4 - list(groups)[0].cardCount)
            if len(duiCards) >= 2:
                return self._validateFindCards(cards + duiCards[0][0] + duiCards[1][0])
        return None

    def _isValid(self, reducedCards):
        if reducedCards.cardCount != 8:
            return False
        
        sc4 = reducedCards.findSameCountGroup(4)
        sc2 = reducedCards.findSameCountGroup(2)
        if not sc4:
            return False
        elif len(sc4.groups) == 2:
            return True
        elif sc2 and len(sc4.groups) == 1 and len(sc2.groups) == 2:
            return True
        
        return False
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 8:
            return None
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, useWild, purlWild)
        if len(ret) == 0:
            return None
        duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild, ret[0][1], 4 - list(ret[0][1])[0].cardCount)
        if len(duiCards) >= 2:
            return self._validateFindCards(ret[0][0] + duiCards[0][0] + duiCards[1][0])
        return None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 8:
            return None
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, useWild, purlWild)
        if len(ret) == 0:
            return None
        duiCards = CardFinder.findNSamePointCards(self.rule, 2, -1, handReducedCards, useWild, purlWild, ret[0][1], 4 - list(ret[-1][1])[0].cardCount)
        if len(duiCards) >= 2:
            return self._validateFindCards(ret[-1][0] + duiCards[0][0] + duiCards[1][0])
        return None
        
        
class CardTypeZhadan(CardType):
    def __init__(self):
        super(CardTypeZhadan, self).__init__(CARD_TYPE_ZHADAN, CARD_LEVEL_ZHADAN)
        
    def score(self, nCards, nWildCards, point):
        '''
        炸弹类型分数
        '''
        zhaDanTypeScore = 0
        if nCards == nWildCards:
            zhaDanTypeScore = 1000
        elif nWildCards == 0:
            zhaDanTypeScore = 100
        return nCards * 10000 + zhaDanTypeScore + point
    
    def calcScore(self, validCards):
        assert(validCards.cardType == self)
        nc = validCards.reducedCards.cardCount
        nw = validCards.reducedCards.wildCardCount
        card = validCards.reducedCards.cards[0]
        p = self.rule.cardToPoint(card)
        return self.score(nc, nw, p)
        
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        return cmp(self.calcScore(l), self.calcScore(r))
    
    def _findAllZhadanCards(self, handReducedCards):
        '''
        找出所有的炸弹
        '''
        if handReducedCards.cardCount < 4:
            return []
        # 硬炸
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, False, False)
        
        # 癞子炸弹
        excludeGroups = set()
        for _, groupSet in ret:
            excludeGroups = excludeGroups.union(groupSet)
        ret2 = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, True, False, excludeGroups)
        ret = ret2 + ret
        
        # 纯癞子炸弹         
        excludeGroups = set()
        for _, groupSet in ret:
            excludeGroups = excludeGroups.union(groupSet)
        ret3 = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, False, True, excludeGroups)
        ret = ret + ret3
        return ret
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        score = self.calcScore(validCards)
        ret = self._findAllZhadanCards(handReducedCards)
        founds = []
        for cards, _ in ret:
            validZD = self._validateFindCards(cards)
            if self.calcScore(validZD) > score:
                founds.append(cards)
        return founds
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        score = self.calcScore(validCards)
        ret = self._findAllZhadanCards(handReducedCards)
        founds = []
        for cards, _ in ret:
            validZD = self._validateFindCards(cards)
            if self.calcScore(validZD) > score:
                founds.append(validZD)
        return founds
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        score = self.calcScore(validCards)
        ret = self._findAllZhadanCards(handReducedCards)
        
        for cards, _ in ret:
            validZD = self._validateFindCards(cards)
            if self.calcScore(validZD) > score:
                return validZD
        return None

    def _isValid(self, reducedCards):
        return reducedCards.cardCount >= 4 \
            and len(reducedCards.groups) == 1 \
            and reducedCards.cardCount <= self.rule.nMaxCardsOfZhaDan
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 4:
            return None
        
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, False, False)
        if useWild:
            excludeGroups = set()
            for _, groupSet in ret:
                excludeGroups = excludeGroups.union(groupSet)
            ret2 = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, True, False, excludeGroups)
            ret = ret2 + ret
        if purlWild:
            excludeGroups = set()
            for _, groupSet in ret:
                excludeGroups = excludeGroups.union(groupSet)
            ret3 = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, False, True, excludeGroups)
            ret = ret + ret3
        return self._validateFindCards(ret[0][0]) if len(ret) > 0 else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < 4:
            return None
        
        ret = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, False, False)
        if useWild:
            excludeGroups = set()
            for _, groupSet in ret:
                excludeGroups = excludeGroups.union(groupSet)
            ret2 = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, True, False, excludeGroups)
            ret = ret2 + ret
        if purlWild:
            excludeGroups = set()
            for _, groupSet in ret:
                excludeGroups = excludeGroups.union(groupSet)
            ret3 = CardFinder.findNSamePointCards(self.rule, 4, -1, handReducedCards, False, True, excludeGroups)
            ret = ret + ret3
        return self._validateFindCards(ret[-1][0]) if len(ret) > 0 else None
    
class CardTypeHuojian(CardType):
    def __init__(self):
        super(CardTypeHuojian, self).__init__(CARD_TYPE_HUOJIAN, CARD_LEVEL_HUOJIAN)
        
    def compareValidCards(self, l, r):
        '''
        比较l, r牌的大小，l, r都必须是本牌型的牌
        @return: l > r 返回 1; r == r 返回 0; r < r 返回-1
        '''
        assert(l.cardType == self and r.cardType == self)
        return -1
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        return []
    
    def findGreaterValidCards(self, validCards, handReducedCards):
        '''
        从handReducedCards中找到比validCards大的牌
        @return: 所有比validCards大的本牌型的牌
        '''
        assert(validCards.cardType == self)
        return []
    
    def findGreaterMinValidCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        return None

    def _isValid(self, reducedCards):
        return reducedCards.cardCount == self.rule.nMaxKings \
               and len(reducedCards.groups) == 2 \
               and self.rule.isKingPoint(reducedCards.groups[0].point)
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if handReducedCards.cardCount < self.rule.nMaxKings:
            return None
        kingCards = []
        for group in set(handReducedCards.groups + handReducedCards.wildGroups):
            if self.rule.isKingPoint(group.point):
                kingCards.extend(group.cards)
        return self._validateFindCards(kingCards) if len(kingCards) == self.rule.nMaxKings else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        return self.findMinCards(handReducedCards, useWild, purlWild)

class CardDiZhuLaizi3Player(CardDiZhuRule):
    '''
    3人普通癞子场
    '''
    def __init__(self):
        super(CardDiZhuLaizi3Player, self).__init__(nDeck=1,
                                                     nPlayer=3,
                                                     nHiddenCards=3,
                                                     nMaxCardsOfZhaDan=4,
                                                     nWild=1,
                                                     kingCanBeWild=False)
        self.randomWildPoints = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        self.addCardTypes([CardTypeDanPai(), CardTypeDuizi(), CardTypeSanzhang(), CardTypeSanDai1(), CardTypeSanDai2(), 
                           CardTypeFeijiDai1(), CardTypeFeijiDai2(), CardTypeDanShun(), CardTypeShuangShun(), CardTypeSanShun(),
                           CardTypeZhadan(), CardTypeHuojian(), CardTypeSiDai2Dan(), CardTypeSiDai2Dui()])
    #---------------------------------------------------------------------------------
    # 随机癞子牌point
    #---------------------------------------------------------------------------------
    def randomWildPoint(self):
        return random.choice(self.randomWildPoints)
    
    #---------------------------------------------------------------------------------
    # 随机癞子牌card
    #---------------------------------------------------------------------------------
    def randomWildCard(self):
        return random.choice(self.randomWildPoints) + 54

class CardDizhuQuickLaizi3Player(CardDiZhuRule):
    '''
        3人快速、去345癞子场
    '''

    def __init__(self):
        super(CardDizhuQuickLaizi3Player, self).__init__(nDeck=1, nPlayer=3, nHiddenCards=3, nMaxCardsOfZhaDan=4, nWild=1,
                                                    kingCanBeWild=False)
        self.randomWildPoints = [0, 1, 5, 6, 7, 8, 9, 10, 11, 12]

        self.addCardTypes([CardTypeDanPai(),
                           CardTypeDuizi(),
                           CardTypeSanzhang(),
                           CardTypeSanDai1(),
                           CardTypeSanDai2(),
                           CardTypeFeijiDai1(),
                           CardTypeFeijiDai2(),
                           CardTypeQuickLaiziDanShun(),
                           CardTypeShuangShun(),
                           CardTypeSanShun(),
                           CardTypeZhadan(),
                           CardTypeHuojian(),
                           CardTypeSiDai2Dan(),
                           CardTypeSiDai2Dui()])

    # ---------------------------------------------------------------------------------
    # 随机癞子牌point
    # ---------------------------------------------------------------------------------
    def randomWildPoint(self):
        return random.choice(self.randomWildPoints)

    # ---------------------------------------------------------------------------------
    # 随机癞子牌card
    # ---------------------------------------------------------------------------------
    def randomWildCard(self):
        return random.choice(self.randomWildPoints) + 54 - 12

class CardDiZhuNormal3Player(CardDiZhuRule):
    '''
    3人普通场
    '''
    def __init__(self):
        super(CardDiZhuNormal3Player, self).__init__(nDeck=1,
                                                     nPlayer=3,
                                                     nHiddenCards=3,
                                                     nMaxCardsOfZhaDan=4,
                                                     nWild=0,
                                                     kingCanBeWild=False)
        
        self.addCardTypes([CardTypeDanPai(), CardTypeDuizi(), CardTypeSanzhang(), CardTypeSanDai1(), CardTypeSanDai2(), 
                           CardTypeFeijiDai1(), CardTypeFeijiDai2(), CardTypeDanShun(), CardTypeShuangShun(), CardTypeSanShun(),
                           CardTypeZhadan(), CardTypeHuojian(), CardTypeSiDai2Dan(), CardTypeSiDai2Dui()])
        


if __name__ == '__main__':
#    print '******************** 3人普通场测试 **********************'
#
    cardRule = CardDiZhuNormal3Player()
#
#    print cardRule.toHumanCards([28, 15, 16, 29, 43, 4, 44, 31, 6, 45, 46, 7, 8, 47, 48, 35])
#     print '-------------------- 单牌测试 ---------------------------'
#     cards = [16]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 对子测试 ---------------------------'
#     cards = [4, 6, 5, 30, 18, 19]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 三张测试 ---------------------------'
#     cards = [4, 17, 30]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 三带1测试 ---------------------------'
#     cards = [5, 4, 18, 44]
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     cards = [5, 0, 18, 44]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 三带2测试 ---------------------------'
#     cards = [5, 0, 18, 44, 0]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 单顺测试 ---------------------------'
#     cards = [6, 8, 7, 9, 10, 11, 38]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 双顺测试 ---------------------------'
#     cards = [8, 21, 9, 22, 10, 23]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 三顺测试 ---------------------------'
#     cards = [8, 21, 34, 9, 22, 35, 10, 23, 36]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 飞机带1 ---------------------------'
#     cards = [8, 21, 34, 9, 22, 35, 10, 23, 36, 11,24,37]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 飞机带2 ---------------------------'
#     cards = [8, 21, 34, 9, 22, 35, 10, 23, 36, 11,24,37,50,12,25]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     cards = [3, 16, 29, 42, 4, 17, 30, 43]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 4带2单 ---------------------------'
#     cards = [7, 20, 33, 46, 1, 11]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 4带2双测试 ---------------------------'
#     cards = [7, 20, 33, 46, 9, 22, 1, 14]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 炸弹测试 ---------------------------'
#     cards = [1, 14, 27, 40]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
#     print '-------------------- 火箭测试 ---------------------------'
#     cards = [52, 53]
#     random.shuffle(cards)
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))
# 
# 
#     print
#     print
#     print '******************** 3人癞子场测试 **********************'
#     cardRule = CardDiZhuLaizi3Player()
#     laizi = cardRule.randomWildCard()
#     print '癞子: %s' % cardRule.toHumanCard(laizi)
# 
#     print '-------------------- 三张 ---------------------------'
#     cards = [15, 28, 56]
#     validateCards = cardRule.validateCards(cards)
#     print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
#     print '输出: %s' % ''.join(cardRule.toHumanCards(validateCards.sortedCards))

    # cardRule = CardDiZhuLaizi3Player()
    # cards = [0, 13, 26, 39, 11, 24, 51, 64]
    # print cardRule.checkMaxValidCardsWithHandCards(cards)

    # cardRule = CardDiZhuLaizi3Player()
    # cards = [52,53, 2, 15, 28, 3, 16, 29, 42, 4, 17, 30]
    # reducedCards = ReducedCards.reduceHandCards(cardRule, cards)
    # print '输入: %s' % ''.join(cardRule.toHumanCards(cards))
    # print CardFinder.findHuojian(cardRule, reducedCards)
    # print CardFinder.findFeijiCount(cardRule, reducedCards)
    # print CardFinder.findZhadanCount(cardRule, reducedCards)

    seatCount = 3
    lucky = 90
    bomb_cards = []  # 预先发的炸弹扑克列表
    bomb_count = 0
    luck_seat = random.randint(0, 2)

    cards = []
    for i in xrange(seatCount):
        cards.append([])

    # 判断制造炸弹
    x = random.randint(1, 100)
    if x <= lucky:
        bomb_count = random.randint(1, 3)
        ls = [luck_seat, (luck_seat + 1) % 3, (luck_seat + 2) % 3]
        #sbc = random.randint(1, 11)#随机出炸弹的点数2345678910JQ
        sbc = random.choice([5, 6, 7, 8, 9, 10, 11, 1]) #no 3 & 4 & 5 & K & A
        #sbc = random.choice([5, 6, 7, 8, 9, 10, 11, 12, 0, 1]) #6-K-A-2
        for bn in xrange(bomb_count):#0 #0 1 #0 1 2#好牌玩家的牌桌索引
            for cn in xrange(4):#0 1 2 3
                cards[ls[bn]].append(sbc + bn + cn * 13)
                bomb_cards.append(sbc + bn + cn * 13)

    cardindex = 0

    pool = []
    polist = [5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
    for i in polist:
        pool.append([i, i + 13, i + 26, i + 39])
    pool.append([52])
    pool.append([53])
    assert (len(pool), 12)
    pools = []
    for index in range(len(pool)):
        pools += pool[index]

    card_list = list(set(pools) - set(bomb_cards))
    random.shuffle(card_list)

    cl = card_list
    for i in xrange(13):
        for j in xrange(seatCount):
            if i < 4:
                if bomb_count == 0 or \
                    (bomb_count == 1 and j != luck_seat) or \
                    (bomb_count == 2 and j == (luck_seat + 2) % 3) or \
                    (bomb_count == 3 and j < 0):
                    cards[j].append(cl[cardindex])
                    cardindex += 1
            else:
                cards[j].append(cl[cardindex])
                cardindex += 1

    # 发送底牌
    # for index in xrange(seatCount):
    #     cards[index].append(cl[cardindex])
    #     cardindex += 1
    baseCard = []
    for index in xrange(seatCount):
        baseCard.append(cl[cardindex])
        #cards[index].append(cl[cardindex])
        cardindex += 1
    cards.append(baseCard)

    print cards
