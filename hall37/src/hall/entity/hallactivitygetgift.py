# -*- coding: utf-8 -*-
'''
Created on Oct 23, 2015

@author: wuyongsheng
'''
import random,time
import freetime.util.log as ftlog
from poker.entity.dao import userchip, daoconst
from hall.entity import datachangenotify
from poker.entity.biz.item.item import TYAssetUtils

def doGetGift(userId,gameId,clientId):
    conf = {"design": {
                       "1": {
                             "name": "99999金币",
                             "probability": 10,
                             "type":"coin",
                             "count":99999,
                             "limits":1
                             },
                       "2": {
                             "name": "50-100奖劵",
                             "probability": 100,
                             "type":"user:coupon",
                             "count":50,
                             "limits":2
                             },
                       "3": {
                             "name": "10000金币",
                             "probability": 190,
                             "type":"coin",
                             "count":10000,
                             "limits":1
                             },
                       "4": {
                             "name": "1-2参赛劵",
                             "probability": 1000,
                             "type":"item:1007",
                             "count":1,
                             "limits":2
                             },
                       "5": {
                             "name": "1-3左轮手枪",
                             "probability": 1000,
                             "type":"item:4118",
                             "count":1,
                             "limits":3
                             },
                       "6": {
                             "name": "1-2记牌器",
                             "probability": 500,
                             "type":"item:2003",
                             "count":1,
                             "limits":2
                             },
                       "7": {
                             "name": "2500-4000金币",
                             "probability": 1000,
                             "type":"coin",
                             "count":2500,
                             "limits":1.6
                             },
                       "8": {
                             "name": "2000-3500金币",
                             "probability": 1000,
                             "type":"coin",
                             "count":2000,
                             "limits":1.75
                             },
                       "9": {
                             "name": "1500-2500金币",
                             "probability": 2000,
                             "type":"coin",
                             "count":1500,
                             "limits":1.7
                             },
                       "10": {
                              "name": "1200-1800金币",
                              "probability":2200,
                              "type":"coin",
                              "count":1200,
                              "limits":1.5
                              },
                       "11": {
                              "name": "1000-1500金币",
                              "probability": 1000,
                             "type":"coin",
                             "count":1000,
                             "limits":1.5
                              }
                       }
            }
    ftlog.debug("doGetGift key begin:")
    toUser = get_gift(conf,userId,gameId,clientId)
    ftlog.debug("doGetGift key over..toUser",toUser)
    return toUser

def get_gift(conf,userId,gameId,clientId):
    design = conf.get('design', {})
    cardPattern = design.keys()
    probability = [ design[key].get('probability', 0) for key in cardPattern ]
    #根据所有存量进行判断，概率。每一次抽取玩之后，进行储量的减少。
    allNum = 0
    arise_chance = []
    for key in probability :
        allNum += key
    ftlog.debug("get_gift.. allNum..key",allNum)  
    for key in probability :
        num = key/allNum
        arise_chance.append(num)
    ftlog.debug("get_gift.. arise_chance..key",arise_chance)
    ftlog.debug("get_gift.. probability..key",probability)   
    gifttype = random_pick(cardPattern, probability)
    ftlog.debug("doGetGift key begin..Hall_Act_Fanfanle_Gift..Is1:",type(gifttype))
    '''
    count =0
    for key,value in conf:
        count += value.probability
    if count > 1 :
        return
     '''   
    gift = get_gift_for_user(conf,gifttype,userId,gameId,clientId)
    #将数量进行减少,执行-1操作s
    design[gifttype]["probability"] -= 1
    toUser = {}
    toUser["gift"] = gift
    toUser["gifttype"] = gifttype
    ftlog.info("用户的ID，领取的礼物类型,礼物",userId,gifttype,gift)
    return toUser
 
def get_gift_for_user(conf,gifttype,userId,gameId,clientId):
    ftlog.debug("get_gift_for_user begin:")
    design = conf.get('design', {})
    if gifttype in design :
        ftlog.debug("get_gift_for_user begin:1")
        from hall.entity.hallitem import itemSystem
        userAssets = itemSystem.loadUserAssets(userId)
        changed = []
        if design[gifttype]["type"] == "user:coupon":
            x = random.uniform(1, design[gifttype]["limits"])
            coinAdd = int(design[gifttype]["count"] * x)
            asset = userAssets.addAsset(gameId, design[gifttype]["type"], coinAdd,int(time.time()),'HALL_FLIPCARD', 0)
            changed.append(asset)
            changeNames = TYAssetUtils.getChangeDataNames(changed)
            datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
            result = "恭喜你获得了%s" % (asset.buildContent(coinAdd))
            return result
        elif design[gifttype]["type"] == "item:1007":
            x = random.uniform(1, design[gifttype]["limits"])
            coinAdd = int(design[gifttype]["count"] * x)
            asset = userAssets.addAsset(gameId, design[gifttype]["type"], coinAdd,int(time.time()),'HALL_FLIPCARD', 0)
            changed.append(asset)
            changeNames = TYAssetUtils.getChangeDataNames(changed)
            datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
            result = "恭喜你获得了%s" % (asset.buildContent(coinAdd))
            return result
        if design[gifttype]["type"] == "item:4118":
            x = random.uniform(1, design[gifttype]["limits"])
            coinAdd = int(design[gifttype]["count"] * x)
            asset = userAssets.addAsset(gameId, design[gifttype]["type"], coinAdd,int(time.time()),'HALL_FLIPCARD', 0)
            changed.append(asset)
            changeNames = TYAssetUtils.getChangeDataNames(changed)
            datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
            result = "恭喜你获得了%s" % (asset.buildContent(coinAdd))
            return result
        elif design[gifttype]["type"] == "item:2003":
            x = random.uniform(1, design[gifttype]["limits"])
            coinAdd = int(design[gifttype]["count"] * x)
            asset = userAssets.addAsset(gameId, design[gifttype]["type"], coinAdd,int(time.time()),'HALL_FLIPCARD', 0)
            changed.append(asset)
            changeNames = TYAssetUtils.getChangeDataNames(changed)
            datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
            result = "恭喜你获得了%s" % (asset.buildContent(coinAdd))
            return result
        elif design[gifttype]["type"] == "coin" :
            ftlog.debug("get_gift_for_user begin:2")
            x = random.uniform(1, design[gifttype]["limits"])
            coinAdd = int(design[gifttype]["count"] * x)
            userchip.incrChip(userId, gameId, coinAdd, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'HALL_FLIPCARD', 0, clientId)
            datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
            result = "恭喜你获得了%s" % (asset.buildContent(coinAdd))
            return result
        else :
            result = "红包被领完了..."
            return result
    else :
        result = "红包领完了,我很抱歉"
        return result
 
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

