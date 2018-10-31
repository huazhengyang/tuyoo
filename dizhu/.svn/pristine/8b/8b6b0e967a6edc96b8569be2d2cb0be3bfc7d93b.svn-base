# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''
from dizhu.gamecards.dizhu_card import CardDizhu
from dizhu.gamecards.dizhu_rule import CardDiZhuNormal3Player, CardDiZhuLaizi3Player, CardDiZhuQuickLaizi3Player
from dizhu.gamecards.dizhu_card_laizi import CardDizhuLaiZi
from dizhu.gamecards.dizhu_card_quicklaizi import CardDizhuQuickLaiZi
from dizhu.gamecards.dizhu_card_erdou import CardRander
from dizhu.entity import dizhuconf
from freetime.util import log as ftlog

class CardHappy(object):


    def __init__(self):
        self.rule = CardDiZhuNormal3Player()
        self.cardmaker = CardDizhu
        self.cardfinder = self.rule
    
    
    def getBaseCardInfo(self, baseCards):
        '''
        取得底牌的基本信息, 底牌的牌型和加倍的倍率
        '''
        bctype = CardDizhu.getBaseCardType(baseCards)
        bcmulti = CardDizhu.getBcMultiByBcType(bctype)
        return bctype, bcmulti
    
    
    def generateLuckCard(self, userids, playCounts, isGoodCard, luck, config):
        '''
        生成一手新的牌
        userids 需要发牌的所有玩家的ID
        playCounts 对应userids中, 每个玩家已经玩的局数
        isGoodCard 是否进行新手保护和好牌座位的处理
        luck 好牌点0~100
        config 扩展的发牌使用的配置内容
        '''
        goodSeatId = 0
        cards = None
        if isGoodCard :
            goodSeatId, cards = self.cardmaker.sendCard2(playCounts, config)
        else:
            cards = self.cardmaker.sendCard(len(userids), luck)
        if ftlog.is_debug():
            ftlog.debug('CardHappy.generateLuckCard',
                        'userIds=', userids,
                        'playCounts=', playCounts,
                        'isGoodCard=', isGoodCard,
                        'luck=', luck,
                        'goodSeatId=', goodSeatId,
                        'cards=', cards)
        return goodSeatId, cards


    def findFirstCards(self, hand_cards):
        return self.cardfinder.findFirstCards(hand_cards)


    def findGreaterCards(self, topcard, handcard):
        return self.cardfinder.findGreaterCards(topcard, handcard)


    def findFirstSmallCard(self, hand_cards):
        return self.cardfinder.findFirstSmallCard(hand_cards)


    def isDoubleKing(self, cards):
        return CardDizhu.isDoubleKing(cards)


    def validateCards(self, cards, priorityCardType=None):
        return self.rule.validateCards(cards, priorityCardType)


    def isWildCard(self, card):
        return self.rule.isWildCard(card)


    def randomWildCard(self):
        return self.rule.randomWildCard()


    def changeCardToWildCard(self, card, wildIndex=0):
        return self.rule.changeCardToWildCard(card, wildIndex)


    def isSamePointCard(self, card1, card2):
        return self.rule.isSamePointCard(card1, card2)


    def pointToCard(self, point):
        return self.rule.pointToCard(point)


    def cardToPoint(self, card):
        return self.rule.cardToPoint(card)


class CardLaiZi(CardHappy):


    def __init__(self):
        super(CardLaiZi, self).__init__()
        self.rule = CardDiZhuLaizi3Player()
        self.cardmaker = CardDizhuLaiZi
        self.cardfinder = self.rule


class CardQuickLaiZi(CardHappy):

    def __init__(self):
        super(CardQuickLaiZi, self).__init__()
        self.rule = CardDiZhuQuickLaizi3Player()
        self.cardmaker = CardDizhuQuickLaiZi
        self.cardfinder = self.rule


class Card123(CardHappy):


    def __init__(self):
        super(Card123, self).__init__()


    def getBaseCardInfo(self, baseCards):
        '''
        取得底牌的基本信息, 底牌的牌型和加倍的倍率
        '''
        bctype = CardDizhu.getBaseCardType(baseCards)
        return bctype, 1


class CardErDou(CardHappy):


    def __init__(self):
        super(CardErDou, self).__init__()


    def generateLuckCard(self, userids, playCounts, isGoodCard, luck, config):
        '''
        生成一手新的牌
        userids 需要发牌的所有玩家的ID
        playCounts 对应userids中, 每个玩家已经玩的局数
        isGoodCard 是否进行新手保护和好牌座位的处理
        luck 好牌点0~100
        config 扩展的发牌使用的配置内容
        '''
        kick_out_card= [2, 3, 15, 16, 28, 29, 41, 42]
        goodSeatId = 0
        rander = CardRander()
        rander.escapeCards(kick_out_card)
        cards = []
        cards.append(rander.randCard(17))
        cards.append(rander.randCard(17))
        cards.append(rander.randCard(3))
        # 废弃牌
        kick_out_card.extend(rander.randCard(9))
        cards.append(kick_out_card)

        return goodSeatId, cards


def getDizhuCard(playMode):
    if playMode == dizhuconf.PLAYMODE_HAPPY :
        return CardHappy()
    if playMode == dizhuconf.PLAYMODE_123 :
        return Card123()
    if playMode == dizhuconf.PLAYMODE_LAIZI :
        return CardLaiZi()
    if playMode == dizhuconf.PLAYMODE_ERDOU :
        return CardErDou()
    if playMode == dizhuconf.PLAYMODE_ERDAYI:
        return Card123()
    if playMode == dizhuconf.PLAYMODE_QUICKLAIZI:
        return CardQuickLaiZi()

