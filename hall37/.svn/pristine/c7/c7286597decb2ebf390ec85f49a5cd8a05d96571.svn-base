# -*- coding=utf-8
'''
Created on 2015年12月16日

@author: wuyongsheng
@note: 用来对loterry进行处理
'''
import random,time
import freetime.util.log as ftlog
from hall.entity import hallconf,hallitem,datachangenotify
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskGotoShop
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from poker.entity.dao import userchip, daoconst
        
_lotteryMap = {}
#map<templateName,  TYAdsTemplate>           
_lotteryTemplateMap = {}

_inited = False

def _reloadConf():
    global _lotteryTemplateMap
    global _lotteryMap
    conf = hallconf.getLotteryConf()
    _lotteryTemplateMap = conf.get('templates',{})
    _lotteryMap = conf.get('items',{})
    
    
def _onConfChanged(event):
    if _inited:
        _reloadConf()
        
def _initialize():
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    
def getLotteryTemplateMap():
    return _lotteryTemplateMap

def getLotteryMap():
    return _lotteryMap

def queryLottery(gameId, userId, clientId):
    '''
    @return: TYLotteryTemplate
    '''
    _reloadConf()
    clientLotteryConf = hallconf.getClientLotteryConf(clientId)
    templateName = clientLotteryConf.get('template', 'default')
    result = {}
    result["items"] = getItemsForUser(_lotteryTemplateMap.get(templateName),_lotteryMap)
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()
    cardNum = userAssets.balance(gameId,hallitem.ASSET_ITEM_LOTTERY_CARD_ID,timestamp)
    ftlog.debug('halllottery.queryLottery gameId=', gameId,
                'userId=', userId,
                'clientId=', clientId,
                'templateName=', templateName,
                'cardNum=', cardNum)
    if cardNum > 0 :
        #抽奖卡抽奖
        result["lotteryType"] = "card"
        result["desc"] = "恭喜你使用幸运卡抽奖"
        result["cardNum"] = cardNum
    else:
        #金币抽奖
        result["lotteryType"] = "chip"
        result["desc"] = "恭喜你使用金币抽奖"
        result["cardNum"] = 1000
        
    return result

def getItemsForUser(tempDict,itemDict):
        tempItemList = tempDict.get('items',[])
        tempList = []
        for _key,vaule in enumerate(tempItemList) :
            tempItem = vaule
            lotteryIdTemp = tempItem.get('lotteryId')
            if lotteryIdTemp in itemDict:
                objItem = itemDict.get(lotteryIdTemp)
                res = {}
                res["picUrl"] = objItem.get('picUrl')
                res["lotteryId"] = lotteryIdTemp
                tempList.append(res)
            else :
                pass
        if len(tempList) > 0 :
            return tempList
        else:
            return []
    
def handleLotteryRequest(userId, gameId, clientId, msg):
    action =  msg.getParam('action')
    ftlog.debug('handleLotteryRequest action=', action,
               'userId=', userId,
               'gameId=', gameId,
               'clientId=', clientId)
    if action == 'lottery_card' :
        #减少抽奖卡，抽奖
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _, consumeCount, _final = userAssets.consumeAsset(gameId, hallitem.ASSET_ITEM_LOTTERY_CARD_ID, 1,
                                                         timestamp, 'HALL_LOTTERY', 0)
        if consumeCount < 1:
            #金币抽奖
            result = {}
            result["type"] = "chip"
            result["coinNum"] = 1000
            return result
        datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
        result = {}
        result = doLottery(gameId,clientId,userId)
        if result :
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            timestamp = pktimestamp.getCurrentTimestamp()
            result["card"] = userAssets.balance(gameId,hallitem.ASSET_ITEM_LOTTERY_CARD_ID,timestamp)
        return result
    elif action == 'lottery_chip':
        #减少金币，抽奖
        chipNow = userchip.getChip(userId)
        if chipNow < 20000 :
            #去商城
            ret = TodoTaskShowInfo('您的金币不足两万，请去商城购买',True)
            ret.setSubCmd(TodoTaskGotoShop('coin'))
            result = {}
            result["todotask"] = ret.toDict()
            return result
        else :
            #金币抽
            coinDel = -1000
            userchip.incrChip(userId, gameId, coinDel, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'HALL_LOTTERY', 0, clientId)
            datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
            return doLottery(gameId,clientId,userId)
        
def doLottery(gameId,clientId,userId):
    #抽奖
    clientLotteryConf = hallconf.getClientLotteryConf(clientId)
    templateName = clientLotteryConf.get('template', 'default')
    lotteryConfig = _lotteryTemplateMap.get(templateName)
    if not lotteryConfig :
        ftlog.warn('doLottery->', gameId,clientId,userId, 'config is None !', lotteryConfig)
        return {}
    specialState = lotteryConfig.get('specialState',[])    
    weightList = lotteryConfig.get('items',[])
    result = {}
    for _key,value in enumerate(specialState) :
        rate = value.get('rate')
        conditions = value.get('conditions')
        minNum = value.get('min')
        maxNum = value.get('max')
        tempMap = _lotteryMap.get(conditions.get('lotteryId'))
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        cardNum = userAssets.balance(gameId,tempMap.get('itemId'),timestamp)
        x = random.uniform(0,1)
        #判断是否在该特殊状态内
        if cardNum < minNum or cardNum > maxNum :
            continue
        if x <= rate :
            result["item"] = conditions.get('lotteryId')
            continue
    if 'item' not in result.keys():
        items = []
        probability = []
        sumNum = 0
        for _key,value in enumerate(weightList):
            item = value.get('lotteryId')
            items.append(item)
            tempP = value.get('weight')
            sumNum += tempP
        for _key,value in enumerate(weightList):
            tempP = value.get('weight')
            ftlog.debug('doLottery..tempP  = ',tempP) 
            probability.append(tempP/(sumNum*1.0))
        result["item"] = random_pick(items,probability)
    
    #给用户添加道具
    itemMap = _lotteryMap.get(result["item"])
    changed = []
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetKind, _addCount, _final = userAssets.addAsset(gameId, itemMap.get('itemId'), itemMap.get('count'), int(time.time()), 'HALL_LOTTERY', 0)
    if assetKind.keyForChangeNotify:
            changed.append(assetKind.keyForChangeNotify)
    datachangenotify.sendDataChangeNotify(gameId, userId, changed)
    #判断是否有抽奖卡，然后返回下次抽奖使用的数据
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()
    result["cardNum"] = userAssets.balance(gameId,hallitem.ASSET_ITEM_LOTTERY_CARD_ID,timestamp)
    if result["cardNum"] == 0 :
        #抽奖卡为0，直接跳转到金币抽奖
        result["lotteryType"] = "chip"
        result["cardNum"] = 1000
    else:
        result["lotteryType"] = "card"
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
    return ret
    
    
    
    

