# -*- coding=utf-8 -*-
'''
Created on 2013年11月15日

@author: zjgzzz@126.com
'''
import random
import copy
from freetime.util import log as ftlog

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
    def __init__(self, point, cards=None):
        self.point = point
        self.cards = cards or []
    
    def length(self):
        return len(self.cards)
    
    def addCard(self, card):
        self.cards.append(card)
        
class SameNumberGroup(object):
    def __init__(self, number, groups=None):
        self.number = number
        self.groups = groups or []
        
    def addGroup(self, group):
        assert(len(group.cards) == self.number)
        self.groups.append(group)
        
    def findGroupByGTPoint(self, point, exceptPoints=[]):
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
        查找点数不在exceptPoints中的group
        '''
        if exceptPoints is None:
            return None if len(self.groups) <= 0 else self.groups[0]
            
        for group in self.groups:
            if group.point not in exceptPoints:
                return group
        return None
    
class CardDiZhuRule(object):
    # 点数==>牌值的映射
    __POINT_TO_CARD = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1, 52, 53]
    
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
        assert((nDeck * 54 - nHiddenCards) % nPlayer == 0)
        
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
        
        # 牌值==>点数的映射
        self.__cardToPoint = [11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            13, 14]
        
        for _ in xrange(self.nWild):
            self.__cardToPoint.extend([11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14])

        self.__cardTypes = []
        self.__numberToCardTypes = {}
        self.__levelCardTypes = [[], [], []]
        self.__classToCardTypes = {}

    def addCardType(self, cardType):
        '''
        添加牌型
        '''
        self.__cardTypes.append(cardType)
        cardType.setRule(self)
        
        validCardCounts = cardType.getValidCardCounts()
        
        for validCardCount in validCardCounts:
            if validCardCount not in self.__numberToCardTypes:
                self.__numberToCardTypes[validCardCount] = [cardType]
            else:
                self.__numberToCardTypes[validCardCount].append(cardType)
            
        self.__levelCardTypes[cardType.level()].append(cardType)
        self.__classToCardTypes[type(cardType)] = cardType
        
    def addCardTypes(self, cardTypes):
        '''
        添加牌型
        '''
        for cardType in cardTypes:
            self.addCardType(cardType)
            
    def findCardTypeByClass(self, cardTypeClass):
        '''
        根据牌型类查找牌型实例
        '''
        return None if cardTypeClass not in self.__classToCardTypes else self.__classToCardTypes[cardTypeClass]
    
    def cardToPoint(self, card):
        '''
        获取card的点数
        '''
        if (card < 0 or card >= len(self.__cardToPoint)):
            raise UnknownCardException(card)
        return self.__cardToPoint[card]
    
    def pointToCard(self, point):
        '''
        根据点数获取牌值
        '''
        if (point >= 0 and point <= 14):
            return CardDiZhuRule.__POINT_TO_CARD[point]
        raise UnknownPointException(point)
    
    def isWildCard(self, card):
        '''
        判断给定的card是否是癞子
        '''
        return card > 53 and card < len(self.__cardToPoint)
    
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
        assert(self.isWildCard(wildCard) and (target >= 0 and target < 13))
        
        # (wildCard - 54) / 15 定位到第几个癞子 + target的序号
        return 54 + (wildCard - 54) / 15 + target % 13
    
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
    
    def validateCardsWithPriorityClass(self, cards, priorityCardTypeClass):
        priorityCardType = None if priorityCardTypeClass is None else self.findCardTypeByClass(priorityCardTypeClass)
        return self.validateCards(cards, priorityCardType)
    
    def validateCards(self, cards, priorityCardType=None):
        if len(cards) <= 0:
            return None
        
        reducedCards = ReducedCards.reduceForOutCards(self, cards)
        
        if priorityCardType is not None:
            assert(priorityCardType.rule() == self)
            validCards = priorityCardType.validate(reducedCards)
            if validCards is not None:
                return validCards
             
        if len(cards) in self.__numberToCardTypes:
            for cardType in self.__numberToCardTypes[len(cards)]:
                if cardType != priorityCardType:
                    validCards = cardType.validate(reducedCards)
                    if validCards is not None:
                        return validCards
        return None
        
    def checkValidCardsWithHandReducedCards(self, handReducedCards):
        #能一手出就一手出
        cardCount = len(handReducedCards.cards)
        if cardCount in self.__numberToCardTypes:
            for cardType in self.__numberToCardTypes[cardCount]:
                found = cardType.findMinCards(handReducedCards, True, True)
                if found and len(found[0]) == cardCount:
                    return found[0]
        return None
    
    def checkValidCardsWithHandCards(self, handCards):
        if len(handCards) <= 0:
            return None
          
        reducedCards = ReducedCards.reduceForHandCards(self, handCards)
        
        return self.checkValidCardsWithHandReducedCards(reducedCards)
    
    def findGreaterCardsByValidCards(self, validCards, handReducedCards, useZhadan = False):
        
        #炸弹一手能出就出炸弹 无视 useZhadan配置
        if len(handReducedCards.cards) in self.getBombOrKingCount():
            for i in range(validCards.cardType.level() + 1, len(self.__levelCardTypes)):
                for cardType in self.__levelCardTypes[i]:
                    found = cardType.findMinCards(handReducedCards, True, True)
                    if found and len(handReducedCards.cards) == len(found[0]):
                        return found            
        
        found = validCards.cardType.findGreaterCards(validCards, handReducedCards)
        if found:
            if isinstance(validCards.cardType, (CardTypeZhaDan)) and not useZhadan:
                return None        
            return found
        
        if useZhadan :
            for i in range(validCards.cardType.level() + 1, len(self.__levelCardTypes)):
                for cardType in self.__levelCardTypes[i]:
                    found = cardType.findMinCards(handReducedCards)
                    if found:
                        return found
        return None
    
    def findGreaterCards(self, cards, handCards, useZhadan = False):
        if len(cards) <= 0 or len(handCards) <= 0:
            return []
        
        validCards = self.validateCards(cards)
        if not validCards:
            return []
    
        handReducedCards = ReducedCards.reduceForHandCards(self, handCards)
        found = self.findGreaterCardsByValidCards(validCards, handReducedCards, useZhadan)
        if found:
            return found[0]
        return []
    
    def findFirstCards(self, cards, priorityCardTypeClasses = None):
        if len(cards) <= 0:
            return []
        
        if not priorityCardTypeClasses:
            priorityCardTypeClasses = [CardTypeShuangShun, CardTypeDanShun, CardTypeSanDai1, CardTypeSanDai2, CardTypeDuiZi, CardTypeDanPai]
            
        reducedCards = ReducedCards.reduceForHandCards(self, cards)
        
        for priorityCardTypeClass in priorityCardTypeClasses:
            cardType = self.findCardTypeByClass(priorityCardTypeClass)
            if cardType:
                found = cardType.findMinCards(reducedCards)
                if found:
                    return found[0]
        return []
    
    def findFirstSmallCard(self, hand_cards):
        return self.findFirstCards(hand_cards, [CardTypeDanPai])
    
    def findFirstCardNormal(self, hand_cards):
        if len(hand_cards) <= 0:
            return []
          
        reducedCards = ReducedCards.reduceForHandCards(self, hand_cards)
        
        #能一手出就一手出
        if len(hand_cards) in self.__numberToCardTypes:
            for cardType in self.__numberToCardTypes[len(hand_cards)]:
                found = cardType.findMinCards(reducedCards, True, True)
                if found and len(found[0]) == len(hand_cards):
                    return found[0]
        
        #查找非癞子牌
        priorityCardTypeClasses = [CardTypeFeiJiDai1, CardTypeFeiJiDai2, CardTypeFeiJi, CardTypeShuangShun,
                                   CardTypeDanShun, CardTypeSanDai2, CardTypeSanDai1, CardTypeSanZhang,
                                   CardTypeDanPai, CardTypeDuiZi, CardTypeZhaDan, CardTypeHuoJian]
        for priorityCardTypeClass in priorityCardTypeClasses:
            cardType = self.findCardTypeByClass(priorityCardTypeClass)
            if cardType:
                found = cardType.findMinCards(reducedCards, False, False)
                if found:
                    return found[0]
        
        #正常数值不会执行此处
        return []
    
    def findFirstGuardCard(self, hand_cards):
        if len(hand_cards) <= 0:
            return []
          
        reducedCards = ReducedCards.reduceForHandCards(self, hand_cards)
        
        #能一手出就一手出
        if len(hand_cards) in self.__numberToCardTypes:
            for cardType in self.__numberToCardTypes[len(hand_cards)]:
                found = cardType.findMinCards(reducedCards, True, True)
                if found and len(found[0]) == len(hand_cards):
                    return found[0]
                
        #查找非癞子牌
        priorityCardTypeClasses = [CardTypeFeiJiDai1, CardTypeFeiJiDai2, CardTypeFeiJi, CardTypeShuangShun,
                                   CardTypeDanShun, CardTypeSanDai2, CardTypeSanDai1, CardTypeSanZhang,
                                   CardTypeDuiZi, CardTypeSiDai1, CardTypeZhaDan, CardTypeHuoJian]
        for priorityCardTypeClass in priorityCardTypeClasses:
            cardType = self.findCardTypeByClass(priorityCardTypeClass)
            if cardType:
                found = cardType.findMinCards(reducedCards, False, False)
                if found:
                    return found[0]
        #癞子凑小对
        cardType = self.findCardTypeByClass(CardTypeDuiZi)
        if cardType:
            found = cardType.findMinCards(reducedCards, True, True)
            if found:
                return found[0]
        
        #查找最大的单牌
        cardType = self.findCardTypeByClass(CardTypeDanPai)
        if cardType:
            found = cardType.findMaxCards(reducedCards, True, True)
            if found:
                return found[0]
        
        return []
    
class CardUtils(object):
    @staticmethod
    def isContinuous(groups):
        '''
        检查groups是否是连续的
        '''
#         string = '['
#          
#         for group in groups:
#             string += str(group.point) + ','
#         string += ']'
#         print 'isContinuous: ' + string
#          
        # 空数组是不连续的
        if len(groups) < 1:
            return False
        
        # 有2或者王牌不可能连续, 因为groups是排序的, 所以点数大的牌肯定在最后
        if groups[-1].point > 11:
            return False
        
        # 数量和差值相等表示连续
        if (groups[-1].point + 1 - groups[0].point) == len(groups):
            return True
        return False
    
    @staticmethod
    def indexOfMaxContinuousN(groups, N):
        assert(N > 0)
        jiange = N - 1
        for i in range(len(groups) - 1, jiange - 1, -1):
            if groups[i].point > 11:
                continue
            if groups[i].point - groups[i - jiange].point == jiange:
                return i - jiange
        return -1
    
    @staticmethod
    def getContinuousN(groups):
        '''
        如果groups是连续的返回连续的数量, 否则返回0
        '''
        return len(groups) if CardUtils.isContinuous(groups) else 0
    
    @staticmethod
    def makeZhaDanScore(nCards, nWildCards, point):
        # 炸弹类型分数
        zhaDanTypeScore = 0
        if nCards == nWildCards:
            zhaDanTypeScore = 1000
        elif nWildCards == 0:
            zhaDanTypeScore = 100
        return nCards * 10000 + zhaDanTypeScore + point
    
    @staticmethod
    def subList(l, r):
        ret = l[:]
        for item in r:
            ret.remove(item)
        return ret
    
class ReducedCards(object):
    def __init__(self, cards, groupBuckets, wildCards):
        '''
        整理
        '''
        self.wildCards = wildCards
        self.groupBuckets = groupBuckets
        self.groups = []
        self.cards = cards
        
        numberGroupDict = {}
                
        for group in groupBuckets:
            if group.length() <= 0:
                continue
            
            self.groups.append(group)
            
            if group.length() not in numberGroupDict:
                numberGroupDict[group.length()] = SameNumberGroup(group.length(), [group])
            else:
                numberGroupDict[group.length()].addGroup(group)
        
        self.numberGroupDict = numberGroupDict
        self.numberGroups = [numberGroupDict[k] for k in sorted(numberGroupDict.keys())]
        self.numberGroupsDesc = self.numberGroups[::-1]
 
    def findNumberGroupByNumber(self, number):
        if number in self.numberGroupDict:
            return self.numberGroupDict[number]
        return None
    
    def findGroupsByNumbers(self, numbers):
        groups = []
        for number in numbers:
            ng = self.findNumberGroupByNumber(number)
            if not ng:
                continue
            
            ftlog.debug('number:', number
                        , ' groups:', ng.groups)
            
            if not groups:
                groups = copy.deepcopy(ng.groups)
            else:
                groups.extend(ng.groups)
        
        groups.sort(lambda x,y: cmp(x.point, y.point))
        ftlog.debug('At last, numbers:', numbers
                    , ' groups:', groups)
        return groups
    
    @classmethod
    def reduceForOutCards(cls, rule, cards):
        assert(len(cards) > 0)
        groupBuckets = [CardGroup(point) for point in xrange(15)];
        wildCards = []
        
        # 对所有牌进行分组, 癞子牌添加到wildCards
        for card in cards:
            point = rule.cardToPoint(card)
            groupBuckets[point].addCard(card)
            if (rule.isWildCard(card)):
                wildCards.append(card)
                
        return ReducedCards(cards[:], groupBuckets, wildCards)
    
    @classmethod
    def reduceForHandCards(cls, rule, cards):
        assert(len(cards) > 0)
        groupBuckets = [CardGroup(point) for point in xrange(15)];
        wildCards = []
        
        # 对所有牌进行分组, 癞子牌添加到wildCards
        for card in cards:
            if not rule.isWildCard(card):
                point = rule.cardToPoint(card)
                groupBuckets[point].addCard(card)
            else:
                wildCards.append(card)
                
        # 根据point对wildCards排序
        wildCards.sort(cmp=lambda x, y: cmp(rule.cardToPoint(x), rule.cardToPoint(y)))
        
        return ReducedCards(cards[:], groupBuckets, wildCards)
 
class ValidCards(object):
    def __init__(self, cardType, reducedCards):
        self.cardType = cardType
        self.reducedCards = reducedCards
    
    def isCreaterThan(self, other):
        '''
        判断是否大于other
        '''
        assert isinstance(other, ValidCards)
        assert(self.cardType.rule() == other.cardType.rule())
        
        # 1. 比较牌型级别
        if self.cardType.level() > other.cardType.level():
            return True
        
        if self.cardType.level() < other.cardType.level():
            return False
        
        # 2. 不是同一类型无法比较
        if self.cardType != other.cardType:
            return False
        
        # 3. 比较同一类型的牌
        return self.cardType.compareValidCards(self, other) > 0
    
    def isHuoJian(self):
        '''
        判断给定的牌是否是火箭
        '''
        return isinstance(self.cardType, CardTypeHuoJian)
    
    def isZhaDan(self):
        '''
        判断给定的牌是否是炸弹
        '''
        return isinstance(self.cardType, CardTypeZhaDan)
    
    def isFeiJiDai1(self):
        '''
        判断给定的牌是否是三带单牌
        '''
        return isinstance(self.cardType, CardTypeFeiJiDai1)
    
    def isFeiJiDai2(self):
        '''
        判断给定的牌是否是三带对牌
        '''
        return isinstance(self.cardType, CardTypeFeiJiDai2)
    
class FinderUtils(object):
    @staticmethod
    def findGroupByGENumberAndGTPoint(numberGroups, number, point, exceptPoints=None):
        '''
        在numberGroups中查找张数大于等于number的, 并且point大于point的group, 
        并且排除点数在exceptPoints中的组.
        '''
        for numberGroup in numberGroups:
            if numberGroup.number >= number:
                group = numberGroup.findGroupByGTPoint(point, exceptPoints)
                if group is not None:
                    return group
        return None
    
    @staticmethod
    def findGroupByLTNumberAndGTPoint(numberGroups, number, point, exceptPoints=None):
        '''
        在numberGroups中查找张数小于number的
        '''
        for numberGroup in numberGroups:
            if numberGroup.number < number:
                group = numberGroup.findGroupByGTPoint(point, exceptPoints)
                if group is not None:
                    return group
        return None

    @staticmethod
    def findNSameWildsByGTPoint(rule, n, point, wildCards):
        # 天地癞子时需要改变
        # TODO
        assert(n > 0)
        return wildCards[0:n] if len(wildCards) >= n and rule.cardToPoint(wildCards[0]) > point else []
    
    @staticmethod
    def findNShunWildsByGTPoint(rule, n, point, wildCards):
        # 天地癞子时需要改变
        # TODO
        return None

    @staticmethod
    def findMinNSameCardsByGTPoint(rule, n, point, handReducedCards, useWild=True, usePureWild=True):
        '''
        查找n个相同的牌，并且牌的point要大于point
        返回结果(outCards, pickCards, [groups], [wildCards])
        '''
        # 先查找硬N张, 升序查找
        group = FinderUtils.findGroupByGENumberAndGTPoint(handReducedCards.numberGroups, n, point)
        
        if group:
            return (group.cards[0:n], group.cards[0:n], [group], [])
    
        if useWild:
            # 查找比N张牌少的并且点数比point大的牌, 并且不能是王牌(因为癞子不能变王牌)
            group = FinderUtils.findGroupByLTNumberAndGTPoint(handReducedCards.numberGroupsDesc, n, point, [13, 14])
        
            if group:
                diff = n - len(group.cards)
                if len(handReducedCards.wildCards) < diff:
                    return None
            
                wildCards = handReducedCards.wildCards[0:diff]
                changedWilds = [rule.changeWildCardToPointCard(wildCard, group.point) for wildCard in wildCards]
                return (changedWilds + group.cards, group.cards + wildCards, [group], wildCards) 
        
        # 查找纯癞子是否可以组合
        if len(handReducedCards.wildCards) < n:
            return None
        
        if usePureWild:
            wildCards = FinderUtils.findNSameWildsByGTPoint(rule, n, point, handReducedCards.wildCards)
            if wildCards:
                return (wildCards, wildCards, [], wildCards) 
        return None
    
    @staticmethod
    def firstNShunByGTPoint(rule, n, point, handReducedCards):
        '''
        查找x个的n顺, 并且最小的point要大于point
        '''
        assert(n > 0 and n < 4)
        
        continuous = 1
        if n == 1:
            continuous = 5
        elif n == 2:
            continuous = 3
        elif n == 3:
            continuous = 2
        else:
            continuous = 2
            
        start = point + 1
        end = point + 1
        
        while end < 12:
            if len(handReducedCards.groupBuckets[end].cards) < n:
                if end - start >= continuous:
                    return (start, end)
                start = end + 1
            end = end + 1
        
        if end - start >= continuous:
            return (start, end)
        return None
    
    @staticmethod
    def indexOfMinNShunByGTPoint(rule, n, nContinuous, point, handReducedCards, useWild=True):
        '''
        查找nContinuous个的n顺, 并且最小的point要大于point
        '''
        assert(n > 0 and n < 4)
        assert(nContinuous > 1)
        
        minScore = 0;
        minIndex = -1
        
        for i in range(point + 1, 12 - nContinuous + 1):
            nNeedWild = 0
            nEffectZhaDan = 0
            nEmptyGroup = 0 
            
            # 查找可以组合的顺子
            for j in range(i, i + nContinuous):
                if len(handReducedCards.groupBuckets[j].cards) >= 4:
                    nEffectZhaDan += 1
                else:
                    if len(handReducedCards.groupBuckets[j].cards) == 0:
                        nEmptyGroup += 1
                    if n > len(handReducedCards.groupBuckets[j].cards):
                        nNeedWild += n - len(handReducedCards.groupBuckets[j].cards)
            
            if (nNeedWild > 0 and not useWild) or nEmptyGroup >= nContinuous or len(handReducedCards.wildCards) < nNeedWild:
                continue
            
            score = nNeedWild * 100000 + nEffectZhaDan * 1000 + i
            
            if minIndex == -1 or score < minScore:
                minScore = score
                minIndex = i
                
        return minIndex
    
    @staticmethod
    def findNShunByNContinuousAndGTPoint(rule, n, nContinuous, point, handReducedCards, useWild=True):
        '''
        查找nContinuous个的n顺, 并且最小的point要大于point
        '''
        assert(n > 0 and n < 4)
        assert(nContinuous > 1)
        
        minIndex = FinderUtils.indexOfMinNShunByGTPoint(rule, n, nContinuous, point, handReducedCards, useWild)
        
        if minIndex < 0:
            return FinderUtils.findNShunWildsByGTPoint(rule, n, point, handReducedCards.wildCards)
            
        outCards = []
        pickCards = []
        wildIndex = 0
        groups = []
        
        for i in range(minIndex, minIndex + nContinuous):
            if len(handReducedCards.groupBuckets[i].cards) >= n:
                groups.append(handReducedCards.groupBuckets[i])
                outCards += handReducedCards.groupBuckets[i].cards[0:n]
                pickCards += handReducedCards.groupBuckets[i].cards[0:n]
            else:
                diff = n - len(handReducedCards.groupBuckets[i].cards)
                wildCards = handReducedCards.wildCards[wildIndex:wildIndex + diff]
                wildIndex += diff
                outCards += [rule.changeWildCardToPointCard(wildCard, i) for wildCard in wildCards]
                pickCards += wildCards
                if len(handReducedCards.groupBuckets[i].cards) > 0:
                    outCards += handReducedCards.groupBuckets[i].cards
                    pickCards += handReducedCards.groupBuckets[i].cards
                    
        return (outCards, pickCards, groups, handReducedCards.wildCards[0:wildIndex])
    
    @staticmethod
    def findNShunByGTPoint(rule, n, point, handReducedCards):
        found = FinderUtils.firstNShunByGTPoint(rule, n, point, handReducedCards)
        if found:
            outCards = []
            groups = []
            for i in range(found[0], found[1]):
                outCards += handReducedCards.groupBuckets[i].cards[0:n]
                groups.append(handReducedCards.groupBuckets[i])
            return (outCards, outCards, groups, [])
        return None
    
    @staticmethod
    def indexByGENumber(numberGroups, number):
        for i in xrange(len(numberGroups)):
            if numberGroups[i].number >= number:
                return i
        return -1
    
    @staticmethod
    def findMaxDanPai(handReducedCards, useWild = True):
        gamenumgroup = handReducedCards.findNumberGroupByNumber(1)
        if gamenumgroup and len(gamenumgroup.groups) > 0:
            group = gamenumgroup.groups[0]
            for i in xrange(len(gamenumgroup.groups)):
                if group.point < gamenumgroup.groups[i].point:
                    group = gamenumgroup.groups[i]
            if group:
                return ([group.cards[0]], [group.cards[0]], [group], [])
        if useWild and len(handReducedCards.wildCards) > 0:
            return ([handReducedCards.wildCards[0]], [handReducedCards.wildCards[0]], [], [handReducedCards.wildCards[0]])
        return None
    
    @staticmethod
    def findGENZhaByGTPoint(rule, nCards, nWildCards, point, handReducedCards, useWild = True):
        '''
        查找>=N张的炸弹, 并且炸弹的point要大于point
        '''
        if len(handReducedCards.cards) < nCards:
            return None
                    
        inputScore = CardUtils.makeZhaDanScore(nCards, nWildCards, point)
        
        # 查找最接近>=nCards的numberGroup
        index = FinderUtils.indexByGENumber(handReducedCards.numberGroups, nCards)
        
        # 查找>=nCards的硬炸弹
        if index != -1:
            for i in range(index, len(handReducedCards.numberGroups)):
                for group in handReducedCards.numberGroups[i].groups:
                    score = CardUtils.makeZhaDanScore(handReducedCards.numberGroups[i].number, 0, group.point)
                    if score > inputScore:
                        return (group.cards[:], group.cards[:], [group], [])
        else:
            index = len(handReducedCards.numberGroups) - 1
        
        # 不用癞子牌    
        if not useWild: return None
            
        if index >= 0:
            leastWilds = nCards - handReducedCards.numberGroups[index].number
            
            if len(handReducedCards.wildCards) < leastWilds:
                return None
            
            for nWild in range(leastWilds, len(handReducedCards.wildCards) + 1):
                for i in xrange(index + 1):
                    if nWild + handReducedCards.numberGroups[i].number > rule.nMaxCardsOfZhaDan:
                        break
                
                    diff = nCards - handReducedCards.numberGroups[i].number
                    if nWild < diff:
                        continue
                    for group in handReducedCards.numberGroups[i].groups:
                        # 癞子不能当王
                        if rule.isKingPoint(group.point):
                            continue 
                        score = CardUtils.makeZhaDanScore(handReducedCards.numberGroups[i].number + nWild, nWild, group.point)
                        if score > inputScore:
                            wildCards = handReducedCards.wildCards[0:nWild]
                            return ([rule.changeWildCardToPointCard(wildCard, group.point) for wildCard in wildCards] + group.cards[:], group.cards[:] + wildCards, [group], wildCards)

        # 查找癞子牌中是否有合适的,如果是癞子炸弹, 则需要找比癞子炸弹点数大的癞子炸弹(天地癞子才会有)
        cmpPoint = point
        if nCards != nWildCards:
            cmpPoint = -1
        wildCards = FinderUtils.findNSameWildsByGTPoint(rule, nCards, cmpPoint, handReducedCards.wildCards)
        if wildCards:
            changedWilds = [wildCard for wildCard in wildCards]
            return (changedWilds, wildCards, [], wildCards)
        return None
    
    @staticmethod
    def findNZhaByGTPoint(rule, nCards, nWildCards, point, handReducedCards, useWild=True, usePureWild=True):
        '''
        查找N张的炸弹, 并且炸弹的point要大于point
        '''
        if len(handReducedCards.cards) < nCards:
            return None
                    
        inputScore = CardUtils.makeZhaDanScore(nCards, nWildCards, point)
        
        # 查找最接近>=nCards的numberGroup
        index = FinderUtils.indexByGENumber(handReducedCards.numberGroups, nCards)
        
        # 查找==nCards的硬炸弹
        if index != -1:
            for i in range(index, len(handReducedCards.numberGroups)):
                for group in handReducedCards.numberGroups[i].groups:
                    score = CardUtils.makeZhaDanScore(nCards, 0, group.point)
                    if score > inputScore:
                        return (group.cards[0:nCards], group.cards[0:nCards], [group], [])
        else:
            index = len(handReducedCards.numberGroups) - 1
            
        if useWild:
            # 从<=nCards的group中组合软炸弹
            for i in range(index, -1, -1):
                diff = nCards - handReducedCards.numberGroups[i].number
                if len(handReducedCards.wildCards) < diff:
                    break
                for group in handReducedCards.numberGroups[i].groups:
                    # 癞子不能当王
                    if rule.isKingPoint(group.point):
                        continue 
                    score = CardUtils.makeZhaDanScore(nCards, nCards - handReducedCards.numberGroups[i].number, group.point)
                    if score > inputScore:
                        wildCards = handReducedCards.wildCards[0:diff]
                        return ([rule.changeWildCardToPointCard(wildCard, i) for wildCard in wildCards] + group.cards, wildCards + group.cards, [group], wildCards)

        if usePureWild:
            # 查找癞子牌中是否有合适的
            cmpPoint = point
            if nCards != nWildCards:
                cmpPoint = -1
            wildCards = FinderUtils.findNSameWildsByGTPoint(rule, nCards, cmpPoint, handReducedCards.wildCards)
            if wildCards:
                changedWilds = [wildCard for wildCard in wildCards]
                return (changedWilds, wildCards, [], wildCards)
        return None
    
    @staticmethod
    def findNDanPai(rule, n, exceptGroups, wildCards, handReducedCards):
        '''
        在numberGrouops中找出n张单牌, exceptGroups是要排除的group
        '''
        outCards = []
        groups = []
        hasHuoJian = (handReducedCards.groupBuckets[13] not in exceptGroups) \
            and (handReducedCards.groupBuckets[14] not in exceptGroups) \
            and (len(handReducedCards.groupBuckets[13].cards) + len(handReducedCards.groupBuckets[14].cards) == rule.nMaxKings)
        
        for numberGroup in handReducedCards.numberGroups:
            for group in numberGroup.groups:
                if group in exceptGroups or (rule.isKingPoint(group.point) and hasHuoJian):
                    continue
                outCards.append(group.cards[0])
                groups.append(group)
                if len(outCards) == n:
                    return (outCards, outCards, groups, [])
        
        diff = n - len(outCards)
        if len(wildCards) < diff:
            return None
        
        outWildCards = wildCards[0:diff]
        outCards += outWildCards
        return (outCards, outCards, groups, outWildCards)
            
    @staticmethod
    def findNDuiZi(rule, n, exceptGroups, wildCards, handReducedCards):
        '''
        在numberGrouops中找出n张单牌, exceptGroups是要排除的group
        '''
        outCards = []
        groups = []
        hasHuoJian = (handReducedCards.groupBuckets[13] not in exceptGroups) \
            and (handReducedCards.groupBuckets[14] not in exceptGroups) \
            and (len(handReducedCards.groupBuckets[13].cards) + len(handReducedCards.groupBuckets[14].cards) == rule.nMaxKings)
        
        for numberGroup in handReducedCards.numberGroups:
            if numberGroup.number < 2:
                continue
            
            for group in numberGroup.groups:
                if group in exceptGroups or (rule.isKingPoint(group.point) and hasHuoJian):
                    continue
                outCards += group.cards[0:2]
                groups.append(group)
                if len(outCards) == n * 2:
                    return (outCards, outCards, groups, [])
        
        danPaiNumberGroup = handReducedCards.findNumberGroupByNumber(1)
        danPaiGroupsLen = 0
        
        if danPaiNumberGroup:
            danPaiGroupsLen = len(danPaiNumberGroup.groups)
            # 排除王牌
            if rule.isKingPoint(danPaiNumberGroup.groups[-1].point):
                danPaiGroupsLen -= 1
            if len(danPaiNumberGroup.groups) > 1 and rule.isKingPoint(danPaiNumberGroup.groups[-2].point):
                danPaiGroupsLen -= 1
        
        # 还需要多少个对子
        diff = n - len(outCards) / 2
        
        nNeedWild = diff if danPaiGroupsLen >= diff else diff + (diff - danPaiGroupsLen)
        
        if len(wildCards) < nNeedWild:
            return None
        
        nUseWild = 0
        pickCards = []
        
        if danPaiNumberGroup and danPaiGroupsLen > 0:
            for i in xrange(nNeedWild):
                groups.append(danPaiNumberGroup.groups[i])
                outCards.append(rule.changeWildCardToPointCard(wildCards[nUseWild], danPaiNumberGroup.groups[i].point))
                outCards += danPaiNumberGroup.groups[i].cards
                pickCards.append(wildCards[nUseWild])
                pickCards += danPaiNumberGroup.groups[i].cards
                nUseWild += 1
            
        if nUseWild < nNeedWild:
            outCards += wildCards[nUseWild:nNeedWild]
            
        return (outCards, pickCards, groups, wildCards[0:nNeedWild])
    
class CardType(object):
    LEVEL_NORMAL = 0
    LEVEL_ZHADAN = 1
    LEVEL_HUOJIAN = 2
    
    '''
    牌型类
    '''
    def __init__(self, name, level):
        self.__rule = None
        self.__name = name
        self.__level = level
    
    def rule(self):
        '''
        获取规则
        '''
        return self.__rule
    
    def setRule(self, rule):
        '''
        设置规则
        '''
        assert(self.__rule is None and rule is not None)
        self.__rule = rule

    def name(self):
        '''
        获取牌型的名称
        '''
        return self.__name
    
    def level(self):
        '''
        获取牌型的级别
        '''
        return self.__level
    
    def getValidCardCounts(self):
        '''
        获取所有合法的牌的数量
        @return: 合法的拍的数量列表
        '''
        raise NotImplemented()
    
    def validate(self, reducedCards):
        '''
        验证给定的牌是否是有效的一手牌
        @param reducedCards: 整理后的一组牌 
        @return: 合法的牌
        '''
        raise NotImplemented()
    
    def compareValidCards(self, l, r):
        '''
        '''
        raise NotImplemented()
    
    def findGreaterCards(self, validCards, handReducedCards):
        '''
        在handReducedCards中找出最小的比validCards中大的牌（能不用癞子就不用癞子）
        '''
        raise NotImplemented()
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        '''
        查找符合本牌型的最小牌
        '''
        raise NotImplemented()
    
class CardTypeHuoJian(CardType):
    '''
    火箭：所有的王牌加在一起为火箭
    '''
    def __init__(self):
        super(CardTypeHuoJian, self).__init__('火箭', CardType.LEVEL_HUOJIAN)
        
    def getValidCardCounts(self):
        return [self.rule().nMaxKings]
    
    def validate(self, reducedCards):
        if (len(reducedCards.groups) == 2
            and len(reducedCards.cards) == self.rule().nMaxKings
            and self.rule().isKingPoint(reducedCards.groups[0].point)):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        # 此处不应该被调用, 因为火箭类型的牌只能有一手
        assert(l.cardType == self and r.cardType == self)
        return 1
 
    def findGreaterCards(self, validCards, handReducedCards):
        assert(validCards.cardType == self)
        return None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        nKings = len(handReducedCards.groupBuckets[13].cards) + len(handReducedCards.groupBuckets[14].cards)
        if nKings >= self.rule().nMaxKings:
            outCards = handReducedCards.groupBuckets[13].cards + handReducedCards.groupBuckets[14].cards
            return (outCards, outCards, [])
            
        outCards = []
        for wildCard in handReducedCards.wildCards:
            if self.rule().isKingCard(wildCard):
                outCards.append(wildCard)
        if nKings + len(outCards) >= self.rule().nMaxKings:
            outCards += handReducedCards.groupBuckets[13]
            outCards += handReducedCards.groupBuckets[14]
            return (outCards, outCards, [])
        return None
    
class CardTypeZhaDan(CardType):
    '''
    炸弹：四张或以上大小相同的牌
    '''
    def __init__(self):
        super(CardTypeZhaDan, self).__init__('炸弹', CardType.LEVEL_ZHADAN)
        self.__validCardCount = None
        
    def getValidCardCounts(self):
        if self.__validCardCount is None:
            maxN = self.rule().nDeck * 4 + self.rule().nMaxWildCards
            maxN = maxN if maxN <= self.rule().nMaxCardsOfZhaDan else self.rule().nMaxCardsOfZhaDan
            self.__validCardCount = [i for i in range(4, maxN + 1)]
        return self.__validCardCount
    
    def validate(self, reducedCards):
        if (len(reducedCards.numberGroups) == 1
            and reducedCards.numberGroups[0].number >= 4
            and reducedCards.numberGroups[0].number <= self.rule().nMaxCardsOfZhaDan):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)

        return cmp(CardUtils.makeZhaDanScore(len(l.reducedCards.cards), len(l.reducedCards.wildCards), l.reducedCards.groups[0].point)
                   , CardUtils.makeZhaDanScore(len(r.reducedCards.cards), len(r.reducedCards.wildCards), r.reducedCards.groups[0].point))
                
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        
        # 检查牌的数量, 如果数量不够则返回None
        if len(handReducedCards.cards) < len(validCards.reducedCards.cards):
            return None
        point = self.rule().cardToPoint(validCards.reducedCards.cards[0])
        found = FinderUtils.findGENZhaByGTPoint(self.rule(), len(validCards.reducedCards.cards), len(validCards.reducedCards.wildCards), point, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        found = FinderUtils.findGENZhaByGTPoint(self.rule(), 4, 1, -1, handReducedCards, useWild)
        return (found[0], found[1], found[3]) if found else None
    
class CardTypeDanPai(CardType):
    '''
    单牌（一手牌）：单个牌
    '''
    VALID_CARD_COUNT = [1]
    
    def __init__(self):
        super(CardTypeDanPai, self).__init__('单牌', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeDanPai.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if len(reducedCards.cards) == 1:
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.groups[0].point, r.reducedCards.groups[0].point)
  
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        found = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 1, validCards.reducedCards.groups[0].point, handReducedCards, False)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        found = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 1, -1, handReducedCards, False)
        return (found[0], found[1], found[3]) if found else None
    
    def findMaxCards(self, handReducedCards, useWild = False, purlWild = False):
        found = FinderUtils.findMaxDanPai(handReducedCards, useWild)
        return (found[0], found[1], found[3]) if found else None
    
class CardTypeDuiZi(CardType):
    '''
    对牌（一手牌）：两张大小相同的牌
    '''
    VALID_CARD_COUNT = [2]
    
    def __init__(self):
        super(CardTypeDuiZi, self).__init__('对子', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeDuiZi.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if (len(reducedCards.groups) == 1
            and len(reducedCards.cards) == 2):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.groups[0].point, r.reducedCards.groups[0].point)
      
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        found = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 2, validCards.reducedCards.groups[0].point, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        found = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 2, -1, handReducedCards, useWild)
        if found and not useWild and len(found[2]) > 0 and len(found[2][0].cards) > 2: return None
        return (found[0], found[1], found[3]) if found else None
    
class CardTypeSanZhang(CardType):
    '''
    三张牌：三张大小相同的牌
    '''
    VALID_CARD_COUNT = [3]
    
    def __init__(self):
        super(CardTypeSanZhang, self).__init__('三张', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeSanZhang.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if (len(reducedCards.groups) == 1
            and len(reducedCards.cards) == 3):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.groups[0].point, r.reducedCards.groups[0].point)
      
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        found = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 3, validCards.reducedCards.groups[0].point, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        found = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 3, -1, handReducedCards, useWild, purlWild)
        if found and not useWild and len(found[2]) > 0 and len(found[2][0].cards) > 3: return None
        return (found[0], found[1], found[3]) if found else None
    
class CardTypeSanDai1(CardType):
    '''
    三带一：三张大小相同的牌＋一张单牌
    '''
    VALID_CARD_COUNT = [4]
    
    def __init__(self):
        super(CardTypeSanDai1, self).__init__('三带一', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeSanDai1.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if (len(reducedCards.cards) == 4
            and len(reducedCards.groups) == 2
            and reducedCards.numberGroupsDesc[0].number == 3):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.numberGroupsDesc[0].groups[0].point, r.reducedCards.numberGroupsDesc[0].groups[0].point)
      
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        sanzhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 3, validCards.reducedCards.numberGroupsDesc[0].groups[0].point, handReducedCards)
        if sanzhang:
            canUseWildCards = [] if len(sanzhang[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, sanzhang[3])
            danpai = FinderUtils.findNDanPai(self.rule(), 1, sanzhang[2], canUseWildCards, handReducedCards)
            if danpai:
                return (sanzhang[0] + danpai[0], sanzhang[1] + danpai[1], sanzhang[3] + danpai[3])
        return None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        sanzhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 3, -1, handReducedCards, useWild, purlWild)
        if sanzhang:
            if not useWild and len(sanzhang[2]) > 0 and len(sanzhang[2][0].cards) > 3: return None
            canUseWildCards = [] if len(sanzhang[2]) <= 0 or not useWild else CardUtils.subList(handReducedCards.wildCards, sanzhang[3])
            danpai = FinderUtils.findNDanPai(self.rule(), 1, sanzhang[2], canUseWildCards, handReducedCards)
            if danpai:
                return (sanzhang[0] + danpai[0], sanzhang[1] + danpai[1], sanzhang[3] + danpai[3])
        return None
    
class CardTypeSanDai2(CardType):
    '''
    三带对：三张大小相同的牌＋一对
    '''
    VALID_CARD_COUNT = [5]
    
    def __init__(self):
        super(CardTypeSanDai2, self).__init__('三带对', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeSanDai2.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if (len(reducedCards.cards) == 5
            and reducedCards.numberGroupsDesc[0].number == 3
            and reducedCards.numberGroupsDesc[1].number == 2):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.numberGroupsDesc[0].groups[0].point, r.reducedCards.numberGroupsDesc[0].groups[0].point)
      
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        sanzhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 3, validCards.reducedCards.numberGroupsDesc[0].groups[0].point, handReducedCards)
        if sanzhang:
            canUseWildCards = [] if len(sanzhang[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, sanzhang[3])
            duizi = FinderUtils.findNDuiZi(self.rule(), 1, sanzhang[2], canUseWildCards, handReducedCards)
            if duizi:
                return (sanzhang[0] + duizi[0], sanzhang[1] + duizi[1], sanzhang[3] + duizi[3])
        return None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        sanzhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 3, -1, handReducedCards, useWild, purlWild)
        if sanzhang:
            if not useWild and len(sanzhang[2]) > 0 and len(sanzhang[2][0].cards) > 3: return None
            canUseWildCards = [] if len(sanzhang[2]) <= 0 or not useWild else CardUtils.subList(handReducedCards.wildCards, sanzhang[3])
            duizi = FinderUtils.findNDuiZi(self.rule(), 1, sanzhang[2], canUseWildCards, handReducedCards)
            if duizi:
                return (sanzhang[0] + duizi[0], sanzhang[1] + duizi[1], sanzhang[3] + duizi[3])
        return None
    
class CardTypeDanShun(CardType):
    '''
    单顺：五张或更多的连续单牌（不包括 2 点和双王，不分花色）
    '''
    VALID_CARD_COUNT = [i for i in range(5, 12 + 1)]
    
    def __init__(self):
        super(CardTypeDanShun, self).__init__('顺子', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeDanShun.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if (len(reducedCards.numberGroups) == 1
            and reducedCards.numberGroups[0].number == 1
            and CardUtils.getContinuousN(reducedCards.numberGroups[0].groups) >= 5):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.numberGroups[0].groups[-1].point, r.reducedCards.numberGroups[0].groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        found = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 1, len(validCards.reducedCards.groups), validCards.reducedCards.groups[0].point, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if len(handReducedCards.cards) < 5: return None
        found = None
        if useWild:
            found = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 1, len(handReducedCards.cards), -1, handReducedCards)
        else: 
            found = FinderUtils.findNShunByGTPoint(self.rule(), 1, -1, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
        
class CardTypeShuangShun(CardType):
    '''
    双顺：三对或更多的连续对牌（不包括 2 点和双王）
    '''
    def __init__(self):
        super(CardTypeShuangShun, self).__init__('双顺', CardType.LEVEL_NORMAL)
        self.__validCardCount = None
        
    def getValidCardCounts(self):
        if self.__validCardCount is None:
            self.__validCardCount = [i for i in range(6, 12 * 2 + 1) if i % 2 == 0]
        return self.__validCardCount
    
    def validate(self, reducedCards):
        if (len(reducedCards.numberGroups) == 1
            and reducedCards.numberGroups[0].number == 2
            and CardUtils.getContinuousN(reducedCards.numberGroups[0].groups) >= 3):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        if len(l.reducedCards.cards) != len(r.reducedCards.cards):
            return -1
        return cmp(l.reducedCards.numberGroups[0].groups[-1].point, r.reducedCards.numberGroups[0].groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        found = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 2, len(validCards.reducedCards.groups), validCards.reducedCards.groups[0].point, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if len(handReducedCards.cards) / 2 < 3 : return None
        found = None
        if useWild:
            found = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 2, len(handReducedCards.cards) / 2, -1, handReducedCards)
        else:
            found = FinderUtils.findNShunByGTPoint(self.rule(), 2, -1, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
class CardTypeFeiJi(CardType):
    '''
    三顺：二个或更多的连续“三张牌”（不包括 2 点和双王）
    '''
    def __init__(self):
        super(CardTypeFeiJi, self).__init__('飞机', CardType.LEVEL_NORMAL)
        self.__validCardCount = None
        
    def getValidCardCounts(self):
        if self.__validCardCount is None:
            maxN = 12 * 3
            maxN = maxN if maxN <= self.rule().nMaxCardsInHand else self.rule().nMaxCardsInHand
            self.__validCardCount = [i for i in range(6, maxN + 1)]
        return self.__validCardCount
    
    def validate(self, reducedCards):
        if (len(reducedCards.numberGroups) == 1
            and reducedCards.numberGroups[0].number == 3
            and CardUtils.getContinuousN(reducedCards.numberGroups[0].groups) >= 2):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        if len(l.reducedCards.cards) != len(r.reducedCards.cards):
            return -1
        return cmp(l.reducedCards.numberGroups[0].groups[-1].point, r.reducedCards.numberGroups[0].groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        found = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 3, len(validCards.reducedCards.groups), validCards.reducedCards.groups[0].point, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if len(handReducedCards.cards) / 3 < 2: return None
        
        found = None
        if useWild:
            found = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 3, len(handReducedCards.cards) / 3, -1, handReducedCards)
        else:
            found = FinderUtils.findNShunByGTPoint(self.rule(), 3, -1, handReducedCards)
        return (found[0], found[1], found[3]) if found else None
    
class CardTypeFeiJiDai1(CardType):
    '''
    飞机带翅膀单：三顺＋同数量的单牌
    '''
    def __init__(self):
        super(CardTypeFeiJiDai1, self).__init__('飞机带翅膀单', CardType.LEVEL_NORMAL)
        self.__validCardCount = None
        
    def getValidCardCounts(self):
        if self.__validCardCount is None:
            self.__validCardCount = [i for i in range(8, self.rule().nMaxCardsInHand + 1) if i % 4 == 0]
            
        ftlog.debug('CardTypeFeiJiDai1.validCardCount:', self.__validCardCount)
        return self.__validCardCount
    
    def validate(self, reducedCards):
        if len(reducedCards.cards) < 8 or len(reducedCards.cards) % 4 != 0:
            return None
        
        numberGroup3 = reducedCards.findGroupsByNumbers([3,4])
        
        if numberGroup3 is None:
            return None
        
        if -1 == CardUtils.indexOfMaxContinuousN(numberGroup3, len(reducedCards.cards) / 4):
            return None
        
        return ValidCards(self, reducedCards)
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        if len(l.reducedCards.cards) != len(r.reducedCards.cards):
            return -1
        
        lGroups = l.reducedCards.findGroupsByNumbers([3,4])
        rGroups = r.reducedCards.findGroupsByNumbers([3,4])
        
        if (not lGroups) or (not rGroups):
            return -1
        
        return cmp(lGroups[-1].point, rGroups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        numberGroup3 = validCards.reducedCards.findNumberGroupByNumber(3)
        feiji = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 3, len(numberGroup3.groups), numberGroup3.groups[0].point, handReducedCards)
        
        if feiji:
            canUseWildCards = [] if len(feiji[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, feiji[3])
            danpai = FinderUtils.findNDanPai(self.rule(), len(validCards.reducedCards.findNumberGroupByNumber(3).groups), feiji[2], canUseWildCards, handReducedCards)
            if danpai:
                return (feiji[0] + danpai[0], feiji[1] + danpai[1], feiji[3] + danpai[3])
        return None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if len(handReducedCards.cards) / 4 < 2: return None
        
        if useWild:
            feiji = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 3, len(handReducedCards.cards)/4, -1, handReducedCards)
            if feiji:
                canUseWildCards = [] if len(feiji[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, feiji[3])
                danpai = FinderUtils.findNDanPai(self.rule(), len(feiji[0]) / 3, feiji[2], canUseWildCards, handReducedCards)
                if danpai:
                    return (feiji[0] + danpai[0], feiji[1] + danpai[1], feiji[3] + danpai[3])
        else:            
            feiji = FinderUtils.findNShunByGTPoint(self.rule(), 3, -1, handReducedCards)
            if feiji:
                danpai = FinderUtils.findNDanPai(self.rule(), len(feiji[0]) / 3, feiji[2], [], handReducedCards)
                if danpai:
                    return (feiji[0] + danpai[0], feiji[1] + danpai[1], feiji[3] + danpai[3])
        return None
    
class CardTypeFeiJiDai2(CardType):
    '''
    飞机带翅膀对：三顺＋同数量的对牌
    '''
    def __init__(self):
        super(CardTypeFeiJiDai2, self).__init__('飞机带翅膀对', CardType.LEVEL_NORMAL)
        self.__validCardCount = None
        
    def getValidCardCounts(self):
        if self.__validCardCount is None:
            self.__validCardCount = [i for i in range(8, self.rule().nMaxCardsInHand + 1) if i % 5 == 0]
        return self.__validCardCount
    
    def validate(self, reducedCards):
        if len(reducedCards.cards) < 10 or len(reducedCards.cards) % 5 != 0:
            return None
        
        numberGroup3 = reducedCards.findNumberGroupByNumber(3)
        
        if numberGroup3 is None:
            return None
        
        N = len(reducedCards.cards) / 5
        
        if CardUtils.getContinuousN(numberGroup3.groups) != N:
            return None
        
        # 获取所有能提取出对的组能提取的对子数
        counts = [len(x.groups) * (x.number / 2) for x in reducedCards.numberGroups if x.number % 2 == 0]
        
        for count in counts:
            N = N - count
            
        if (N == 0):
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        if len(l.reducedCards.cards) != len(r.reducedCards.cards):
            return -1
        return cmp(l.reducedCards.findNumberGroupByNumber(3).groups[-1].point, r.reducedCards.findNumberGroupByNumber(3).groups[-1].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        numberGroup3 = validCards.reducedCards.findNumberGroupByNumber(3)
        feiji = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 3, len(numberGroup3.groups), numberGroup3.groups[0].point, handReducedCards)
        
        if feiji:
            canUseWildCards = [] if len(feiji[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, feiji[3])
            duizi = FinderUtils.findNDuiZi(self.rule(), len(validCards.reducedCards.findNumberGroupByNumber(3).groups), feiji[2], canUseWildCards, handReducedCards)
            if duizi:
                return (feiji[0] + duizi[0], feiji[1] + duizi[1], feiji[3] + duizi[3])
        return None
       
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        if len(handReducedCards.cards) / 5 < 2: return None
        
        if useWild:
            feiji = FinderUtils.findNShunByNContinuousAndGTPoint(self.rule(), 3, len(handReducedCards.cards)/5, -1, handReducedCards)
            if feiji:
                canUseWildCards = [] if len(feiji[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, feiji[3])
                duizi = FinderUtils.findNDuiZi(self.rule(), len(feiji[0]) / 3, feiji[2], canUseWildCards, handReducedCards)
                if duizi:
                    return (feiji[0] + duizi[0], feiji[1] + duizi[1], feiji[3] + duizi[3])
        else:
            feiji = FinderUtils.findNShunByGTPoint(self.rule(), 3, -1, handReducedCards)
            if feiji:
                duizi = FinderUtils.findNDuiZi(self.rule(), len(feiji[0]) / 3, feiji[2], [], handReducedCards)
                if duizi:
                    return (feiji[0] + duizi[0], feiji[1] + duizi[1], feiji[3] + duizi[3])
        return None
    
class CardTypeSiDai1(CardType):
    '''
    四带二单：四张牌＋两单牌
    '''
    VALID_CARD_COUNT = [6]
    
    def __init__(self):
        super(CardTypeSiDai1, self).__init__('四带二单', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeSiDai1.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if len(reducedCards.cards) != 6:
            return None
        
        numberGroup4 = reducedCards.findNumberGroupByNumber(4)
        
        if not numberGroup4:
            return None
        return ValidCards(self, reducedCards)
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.numberGroupsDesc[0].groups[0].point, r.reducedCards.numberGroupsDesc[0].groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        sizhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 4, validCards.reducedCards.findNumberGroupByNumber(4).groups[0].point, handReducedCards)
        if sizhang:
            canUseWildCards = [] if len(sizhang[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, sizhang[3])
            danpai = FinderUtils.findNDanPai(self.rule(), 2, sizhang[2], canUseWildCards, handReducedCards)
            if danpai:
                return (sizhang[0] + danpai[0], sizhang[1] + danpai[1], sizhang[3] + danpai[3])
        return None
    
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        sizhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 4, -1, handReducedCards, useWild, purlWild)
        if sizhang:
            canUseWildCards = [] if len(sizhang[2]) <= 0 or not useWild else CardUtils.subList(handReducedCards.wildCards, sizhang[3])
            danpai = FinderUtils.findNDanPai(self.rule(), 2, sizhang[2], canUseWildCards, handReducedCards)
            if danpai:
                return (sizhang[0] + danpai[0], sizhang[1] + danpai[1], sizhang[3] + danpai[3])
        return None
    
class CardTypeSiDai2(CardType):
    '''
    四带二对子：四张牌＋两对牌
    '''
    VALID_CARD_COUNT = [8]
    
    def __init__(self):
        super(CardTypeSiDai2, self).__init__('四带二对', CardType.LEVEL_NORMAL)
        
    def getValidCardCounts(self):
        return CardTypeSiDai2.VALID_CARD_COUNT
    
    def validate(self, reducedCards):
        if len(reducedCards.cards) != 8:
            return None
        
        numberGroup4 = reducedCards.findNumberGroupByNumber(4)
        
        if not numberGroup4:
            return None
        
        numberGroup2 = reducedCards.findNumberGroupByNumber(2)
        
        if not numberGroup2:
            return None
        
        if len(numberGroup4.groups) == 2 or len(numberGroup2.groups) == 2:
            return ValidCards(self, reducedCards)
        return None
    
    def compareValidCards(self, l, r):
        assert(l.cardType == self and r.cardType == self)
        return cmp(l.reducedCards.numberGroupsDesc[0].groups[0].point, r.reducedCards.numberGroupsDesc[0].groups[0].point)
    
    def findGreaterCards(self, validCards, handReducedCards):
        assert (validCards.cardType == self)
        sizhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 4, validCards.reducedCards.findNumberGroupByNumber(4).groups[0].point, handReducedCards)
        if sizhang:
            canUseWildCards = [] if len(sizhang[2]) <= 0 else CardUtils.subList(handReducedCards.wildCards, sizhang[3])
            duizi = FinderUtils.findNDuiZi(self.rule(), 2, sizhang[2], canUseWildCards, handReducedCards)
            if duizi:
                return (sizhang[0] + duizi[0], sizhang[1] + duizi[1], sizhang[3] + duizi[3])
        return None
        
    def findMinCards(self, handReducedCards, useWild = False, purlWild = False):
        sizhang = FinderUtils.findMinNSameCardsByGTPoint(self.rule(), 4, -1, handReducedCards, useWild, purlWild)
        if sizhang:
            canUseWildCards = [] if len(sizhang[2]) <= 0 or not useWild else CardUtils.subList(handReducedCards.wildCards, sizhang[3])
            duizi = FinderUtils.findNDuiZi(self.rule(), 2, sizhang[2], canUseWildCards, handReducedCards)
            if duizi:
                return (sizhang[0] + duizi[0], sizhang[1] + duizi[1], sizhang[3] + duizi[3])
        return None

class CardDiZhuLaizi3Player(CardDiZhuRule):
    RANDOM_WILD_LIST = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    
    def __init__(self):
        super(CardDiZhuLaizi3Player, self).__init__(1, 3, 3, 4, 1, False)
        CardDiZhuRule.addCardTypes(self, [CardTypeHuoJian(),
                              CardTypeZhaDan(),
                              CardTypeDanPai(),
                              CardTypeDuiZi(),
                              CardTypeSanZhang(),
                              CardTypeSanDai1(),
                              CardTypeSanDai2(),
                              CardTypeDanShun(),
                              CardTypeShuangShun(),
                              CardTypeFeiJi(),
                              CardTypeFeiJiDai1(),
                              CardTypeFeiJiDai2(),
                              CardTypeSiDai1(),
                              CardTypeSiDai2(),
                              ])
    #---------------------------------------------------------------------------------
    # 随机癞子牌
    #---------------------------------------------------------------------------------
    def randomWildCard(self):
        mod = 12 if not self.kingCanBeWild else 14
        return self.RANDOM_WILD_LIST[random.randint(0, mod)]


class CardDiZhuQuickLaizi3Player(CardDiZhuRule):
    RANDOM_WILD_LIST = [0, 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    def __init__(self):
        super(CardDiZhuQuickLaizi3Player, self).__init__(1, 3, 3, 4, 1, False)
        CardDiZhuRule.addCardTypes(self, [CardTypeHuoJian(), CardTypeZhaDan(), CardTypeDanPai(), CardTypeDuiZi(),
                                          CardTypeSanZhang(), CardTypeSanDai1(), CardTypeSanDai2(), CardTypeDanShun(),
                                          CardTypeShuangShun(), CardTypeFeiJi(), CardTypeFeiJiDai1(),
                                          CardTypeFeiJiDai2(), CardTypeSiDai1(), CardTypeSiDai2(), ])

    # ---------------------------------------------------------------------------------
    # 去3、4、5 随机癞子牌
    # ---------------------------------------------------------------------------------
    def randomWildCard(self):
        mod = 9 if not self.kingCanBeWild else 11
        return self.RANDOM_WILD_LIST[random.randint(0, mod)]
    
class CardDiZhuNormal3Player(CardDiZhuRule):
    def __init__(self):
        super(CardDiZhuNormal3Player, self).__init__(1, 3, 3, 4, 0, False)
        CardDiZhuRule.addCardTypes(self, [CardTypeHuoJian(),
                              CardTypeZhaDan(),
                              CardTypeDanPai(),
                              CardTypeDuiZi(),
                              CardTypeSanZhang(),
                              CardTypeSanDai1(),
                              CardTypeSanDai2(),
                              CardTypeDanShun(),
                              CardTypeShuangShun(),
                              CardTypeFeiJi(),
                              CardTypeFeiJiDai1(),
                              CardTypeFeiJiDai2(),
                              CardTypeSiDai1(),
                              CardTypeSiDai2(),
                              ])
        
if __name__ == '__main__':
    rule = CardDiZhuLaizi3Player()
    validCards0 = rule.validateCards([5, 18, 31, 4, 43, 58, 23, 36, 9, 22])
    if validCards0:
        print validCards0.cardType
        
    validCards1 = rule.validateCards([38, 51, 66, 24, 37, 50, 10, 49, 28, 41])
    if validCards1:
        print validCards1.cardType
        
    print validCards0.isCreaterThan(validCards1)
    print validCards1.isCreaterThan(validCards0)
        
    
    
    