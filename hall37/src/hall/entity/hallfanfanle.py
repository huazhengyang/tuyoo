# -*- coding: utf-8 -*-
'''
Created on Oct 20, 2015

@author: hanwf
'''
import random,string
import freetime.util.log as ftlog
from poker.entity.dao import daobase
from poker.util import strutil

class CardPatternFactory(object):
    TBaoZiA = "1" # 豹子A
    TBaoZi = "2"  # 豹子
    TTongHuaShun = "3" # 同花顺
    TTongHua = "4" # 同花
    TShunZi = "5" # 顺子
    TDuiZi = "6" # 对子
    TBigK = "7" # K以上单张
    TSingle = "8" # 单张
    
    cardsType = [1, 2, 3, 4]
    cardsNum = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    cardsNumExceptA = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    cardsNumShunZi = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    cardsBigThanK = [1, 13]
    cardsNoA = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    cardsNoK = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    cardsSmallThanK = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    @classmethod
    def getRandomPattern(cls, cardtype):
        if cardtype == cls.TBaoZiA:
            return cls.getBaoZiA()
        elif cardtype == cls.TBaoZi:
            return cls.getBaoZiExceptA()
        elif cardtype == cls.TTongHuaShun:
            return cls.getTongHuaShun()
        elif cardtype == cls.TTongHua:
            return cls.getTongHua()
        elif cardtype == cls.TShunZi:
            return cls.getShunZi()
        elif cardtype == cls.TDuiZi:
            return cls.getDuiZi()
        elif cardtype == cls.TBigK:
            return cls.getBigK()
        elif cardtype == cls.TSingle:
            return cls.getSingle()

    @classmethod
    def getBaoZiA(cls):
        '''
        豹子A
        '''
        random.shuffle(cls.cardsType)
        return [
                {'num': 1, 'type': cls.cardsType[0]},
                {'num': 1, 'type': cls.cardsType[1]},
                {'num': 1, 'type': cls.cardsType[2]}
                ]
    
    @classmethod
    def getBaoZiExceptA(cls):
        '''
        豹子
        '''
        num = random.choice(cls.cardsNumExceptA)
        random.shuffle(cls.cardsType)
        return [
                {'num': num, 'type': cls.cardsType[0]},
                {'num': num, 'type': cls.cardsType[1]},
                {'num': num, 'type': cls.cardsType[2]}
                ]
    
    @classmethod
    def getShunziNum(cls):
        num = random.choice(cls.cardsNumShunZi)
        return num, num+1, num+2
    
    @classmethod
    def getTongHuaShun(cls):
        '''
        同花顺
        '''
        cardType = random.choice(cls.cardsType)
        num1, num2, num3 = cls.getShunziNum()
        return [
                {'num': num1, 'type': cardType},
                {'num': num2, 'type': cardType},
                {'num': num3, 'type': cardType}
                ]
    
    @classmethod
    def sortThree(cls, nums):
        if nums[0] > nums[1]:
            nums[0], nums[1] = nums[1], nums[0]
        if nums[0] > nums[2]:
            nums[0], nums[2] = nums[2], nums[0]
        if nums[1] > nums[2]:
            nums[1], nums[2] = nums[2], nums[1]
    
    @classmethod
    def toNonShunZi(cls, continueThree):
        if continueThree[0] > 1:
            continueThree[0] -= 1
        else:
            continueThree[2] += 1

    @classmethod
    def getNonShunZi(cls, cards):
        '''
        既不是顺子也不是对子，不连续的单张
        '''
        tempCardsNum = strutil.cloneData(cards)
        a1 = random.choice(tempCardsNum)
        tempCardsNum.remove(a1)
        a2 = random.choice(tempCardsNum)
        tempCardsNum.remove(a2)
        a3 = random.choice(tempCardsNum)
        rawList = [a1, a2, a3]
        copyList = [a1, a2, a3]
        cls.sortThree(copyList)
        
        if copyList == [1, 12, 13]:
            return [1, 12, random.choice(cls.cardsNoK)]
        
        if copyList[0]+1 != copyList[1] or copyList[1]+1 != copyList[2]:
            return rawList
        else:
            cls.toNonShunZi(copyList)
            return copyList
        
    @classmethod
    def getTongHua(cls):
        '''
        同花
        '''
        cardType = random.choice(cls.cardsType)
        num1, num2, num3 = cls.getNonShunZi(cls.cardsNum)
        return [
                {'num': num1, 'type': cardType},
                {'num': num2, 'type': cardType},
                {'num': num3, 'type': cardType}
                ]
    
    @classmethod
    def getShunZi(cls):
        '''
        顺子
        '''
        num1, num2, num3 = cls.getShunziNum()
        random.shuffle(cls.cardsType)
        return [
                {'num': num1, 'type': cls.cardsType[0]},
                {'num': num2, 'type': cls.cardsType[1]},
                {'num': num3, 'type': cls.cardsType[2]}
                ]
    
    @classmethod
    def getDuiZi(cls):
        '''
        对子
        '''
        tempCardsType = strutil.cloneData(cls.cardsType)
        tempCardsNum = strutil.cloneData(cls.cardsNum)
        num1 = random.choice(tempCardsNum)
        tempCardsNum.remove(num1)
        num2 = random.choice(tempCardsNum)
        cardType1 = random.choice(tempCardsType)
        tempCardsType.remove(cardType1)
        cardType2 = random.choice(tempCardsType)
        cardType3 = random.choice(cls.cardsType)
        return [
                {'num': num1, 'type': cardType1},
                {'num': num1, 'type': cardType2},
                {'num': num2, 'type': cardType3}
                ]
    
    @classmethod
    def getBigK(cls):
        '''
        K以上单张,不是顺子，不是同花等
        '''
        tempCardsType = strutil.cloneData(cls.cardsType)
        tempCardsNoA = strutil.cloneData(cls.cardsNoA)
        tempCardsNoK = strutil.cloneData(cls.cardsNoK)
        num1 = random.choice(cls.cardsBigThanK)
        if num1 == 13:
            num2 = random.choice(tempCardsNoK)
            tempCardsNoK.remove(num2)
            if num2 == 12:
                tempCardsNoK.remove(11)
                tempCardsNoK.remove(1)
            elif num2 == 11:
                tempCardsNoK.remove(12)
            else:
                pass
            num3 = random.choice(tempCardsNoK)
        else:
            num2 = random.choice(tempCardsNoA)
            tempCardsNoA.remove(num2)
            if num2 == 2:
                tempCardsNoA.remove(3)
            elif num2 == 3:
                tempCardsNoA.remove(2)
            else:
                pass
            num3 = random.choice(tempCardsNoA)
        cardType1 = random.choice(tempCardsType)
        cardType2 = random.choice(tempCardsType)
        tempCardsType.remove(cardType2)
        cardType3 = random.choice(tempCardsType)
        return [
                {'num': num1, 'type': cardType1},
                {'num': num2, 'type': cardType2},
                {'num': num3, 'type': cardType3}
                ]

    @classmethod
    def getSingle(cls):
        '''
        单张,确保不是顺子,也不是同花,也没有对子
        '''
        num1, num2, num3 = cls.getNonShunZi(cls.cardsSmallThanK)
        tempCardsType = strutil.cloneData(cls.cardsType)
        cardType1 = random.choice(tempCardsType)
        cardType2 = random.choice(tempCardsType)
        if cardType1 == cardType2:
            tempCardsType.remove(cardType2)
        cardType3 = random.choice(tempCardsType)
        return [
                {'num': num1, 'type': cardType1},
                {'num': num2, 'type': cardType2},
                {'num': num3, 'type': cardType3}
                ]
 
"""
    4. 牌型定义 花色类型： [ 1 ⇒ 方片♦️, 2 ⇒ 梅花♣️, 3 ⇒ 红桃❤️, 4 ⇒ 黑桃♠️,]

    数值类型：[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    "design": {
        "1": {
            "name": "豹子A",
            "payrate": 666,
            "probability": 0.0001
        },
        "2": {
            "name": "豹子",
            "payrate": 88,
            "probability": 0.0012
        },
        "3": {
            "name": "同花顺",
            "payrate": 66,
            "probability": 0.001
        },
        "4": {
            "name": "同花",
            "payrate": 10,
            "probability": 0.01
        },
        "5": {
            "name": "顺子",
            "payrate": 5,
            "probability": 0.01
        },
        "6": {
            "name": "对子",
            "payrate": 2,
            "probability": 0.1
        },
        "7": {
            "name": "K以上单张",
            "payrate": 1.2,
            "probability": 0.3
        },
        "8": {
            "name": "单张",
            "payrate": 0,
            "probability": 0.5777
        }
    }
"""

def doFlipCard(conf):
    ftlog.debug("_doFlipcard key begin:")
    toUser = flipit(conf)
    ftlog.debug("_doFlipcard key over")
    return toUser

def flipit(conf):
    design = conf.get('design', {})
    cardPattern = design.keys()
    probability = [ design[key].get('probability', 0) for key in cardPattern ]
    cardtype = random_pick(cardPattern, probability)
    ftlog.debug("doGetGift key begin..Hall_Act_Fanfanle_Gift..Is11:",type(cardtype))
    '''
    count =0
    for key,value in conf:
        count += value.probability
    if count > 1 :
        return
     '''   
    cards = CardPatternFactory.getRandomPattern(cardtype)
    toUser = {}
    toUser["cards"] = cards
    toUser["cardtype"] = cardtype
    return toUser
 
def random_pick(items, probability):
    x = random.uniform(0, 1)
    cumulative_probability = 0
    ret = 0
    for item, item_probability in zip(items, probability):
        cumulative_probability += item_probability
        ret = item
        if x <= cumulative_probability:
            break
    ftlog.debug("random_pick over ret:",ret)
    return ret

