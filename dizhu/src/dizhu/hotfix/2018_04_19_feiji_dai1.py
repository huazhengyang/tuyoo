# -*- coding:utf-8 -*-
'''
Created on 2018年04月19日

@author: zhaoliang
'''
from dizhu.gamecards.dizhu_rule import CardUtils, ValidCards, CardTypeFeiJiDai1

def validate(self, reducedCards):
    if len(reducedCards.cards) < 8 or len(reducedCards.cards) % 4 != 0:
        return None
    
    numberGroup3 = reducedCards.findNumberGroupByNumber(3)
    
    if numberGroup3 is None:
        return None
    
    if -1 == CardUtils.indexOfMaxContinuousN(numberGroup3.groups, len(reducedCards.cards) / 4):
        return None
    
    return ValidCards(self, reducedCards)

CardTypeFeiJiDai1.validate = validate