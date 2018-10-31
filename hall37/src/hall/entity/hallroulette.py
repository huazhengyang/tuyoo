# -*- coding=utf-8
'''
Created on 2016年4月20日

@author: wuyongsheng
@note: 轮盘功能
'''
import random, time, json
import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem, datachangenotify, hallvip, halluser, hallled
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskGotoShop
from hall.game import TGHall
from poker.entity.events.tyevent import EventConfigure, UserEvent
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from poker.entity.dao import userchip, daoconst, sessiondata
from poker.entity.dao import gamedata as pkgamedata
from poker.entity.dao import daobase
import poker.entity.dao.userchip as pkuserchip
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.item.item import TYAssetUtils
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper

_rouletteMap = {}
# map<templateName,  TYAdsTemplate>           
_rouletteTemplateMap = {}
_condition = None
_inited = False
CURKEY='Roulette.soldiers'
HISKEY='Roulette.history'
HISKEYDETAIL='Roulette.history.detail'

def _reloadConf():
    global _rouletteTemplateMap
    global _rouletteMap
    global _condition

    conf = hallconf.getRouletteConf()
    _rouletteMap = conf.get('items')
    _rouletteTemplateMap = conf.get('template')
    templateConf = _rouletteTemplateMap.get(getTemeplateName(), {})
    from hall.entity.hallusercond import UserConditionRegister
    condition = templateConf.get('conditions')
    if condition:
        _condition = UserConditionRegister.decodeFromDict(condition)


def isSuitableClientID(userId, gameId, clientId):
    if not _condition:
        ftlog('_condition is null!')
        return False
    return _condition.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp())

def _onConfChanged(event):
    if _inited and event.isModuleChanged('roulette'):
        _reloadConf()
        
def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)

def getRouletteTemplateMap():
    global _rouletteTemplateMap
    return _rouletteTemplateMap

def getRouletteMap():
    global _rouletteMap
    return _rouletteMap 

def getTemeplateName():
    '''
    当前只支持一套模板
    大奖及大奖个数也都是全局存储的，没有分模板
    '''
    return 'default'

def getConfForClient(userId, gameId, clientId):
    '''
        获取具体的配置信息
    '''
    clientConf = getTemeplateName()
    rouletteTemplateMap = getRouletteTemplateMap()
    templateConf = rouletteTemplateMap.get(clientConf, {})
    return getConfForTemplate(userId, gameId, clientId, templateConf)

def getConfForTemplate(userId, gameId, clientId, templateConf):
    con = {}
    con['gold_items'] = getConfForList(templateConf.get('gold_items', None))
    con['silver_items'] = getConfForList(templateConf.get('silver_items', []))
    return con

def getWeightConfTemplate(userId, gameId, clientId):
    '''
        获取包含权重的配置信息
    '''
    clientConf = getTemeplateName()
    
    if not clientConf:
        ftlog.warn('doRoulette->', gameId, clientId, userId, 'config is None !')
        return {}
    rouletteTemplateMap = getRouletteTemplateMap()
    templateConf = rouletteTemplateMap.get(clientConf, {})
    return templateConf
    
def getConfForList(listConf):
    itemsConf = getRouletteMap()
    tempConf = []
    for d in listConf:
        tempRouletteId = d.get('rouletteId', '')
        itemConf = itemsConf.get(tempRouletteId, '')
        tempConf.append({'rouletteId':itemConf.get('rouletteId', ''),
                         'picUrl':itemConf.get('picUrl', ''),
                         'itemName':itemConf.get('itemName', ''),
                         'itemDesc':itemConf.get('itemDesc','')
                         })
    return tempConf

def doWeightListForItem(userId, gameId, clientId , itemList):
    if not itemList:
        ftlog.warn('doRoulette->', gameId, clientId, userId, 'itemList is None !')
        return None
    items = []
    probability = []
    allWeight = 0
    for _key, value in enumerate(itemList):
            items.append(value.get('rouletteId'))
            probability.append(value.get('weight'))
            allWeight += value.get('weight')
    ret, _x = random_pick(items, probability, allWeight)
    return ret

def doRouletteLottery(userId, gameId, clientId):
    '''
    金盘抽奖
        每次一计算概率，防止连续开出大奖
    '''
    tempRouleteType = bigRewardOrReward(userId, gameId, clientId)
    
    tempResult = getWeightConfTemplate(userId, gameId, clientId)
    item = doWeightListForItem(userId, gameId, clientId, tempResult.get(tempRouleteType, []))
    if not item:
        raise Exception('配置信息出错，没有取到奖品配置')
    
    # 修改大奖个数
    if isBigRewardItem(item):
        daobase.executeMixCmd('hincrby', 'allSoldier', 'bigRewardNumber' , -1)  
        
    return item

def doRouletteSilverLottery(userId, gameId, clientId):
    '''
    金盘抽奖
        每次一计算概率，防止连续开出大奖
    '''
    tempRouleteType = 'silver_items'
    tempResult = getWeightConfTemplate(userId, gameId, clientId)
    item = doWeightListForItem(userId, gameId, clientId, tempResult.get(tempRouleteType, []))
    if not item:
        raise Exception('配置信息出错，没有取到奖品配置')
    
    # 修改大奖个数
    if isBigRewardItem(item):
        daobase.executeMixCmd('hincrby', 'allSoldier', 'bigRewardNumber' , -1)  
        
    return item

def random_pick(items, probability, allWeight):
    x = random.randint(0,allWeight-1)
    cumulative_probability = 0
    ret = 0
    for item, item_probability in zip(items, probability):
        cumulative_probability += item_probability
        ret = item
        if x < cumulative_probability:
            break
    return ret, x

def toShop():
    result = {}
    ret = TodoTaskShowInfo('您的钻石不足，请去商城购买', True)
    ret.setSubCmd(TodoTaskGotoShop('diamond'))
    result['todotask'] = ret.toDict()
    return result

def reach10MaxTimes():
    result = {}
    ret = TodoTaskShowInfo("今日10连转次数已达上限，请明日再来", True)
    result['todotask'] = ret.toDict()
    return result

def reach50MaxTimes():
    result = {}
    ret = TodoTaskShowInfo("今日50连转次数已达上限，请明日再来", True)
    result['todotask'] = ret.toDict()
    return result

def doGoldLottery(userId, gameId, clientId, number):
    '''
        金盘抽奖
    '''
    if number <= 0 or number > 50:
        ftlog.error('doGoldLottery number best be > 0 or <= 50, the msg is fake')
        return
    
    if ftlog.is_debug():
        ftlog.debug('hallroulette.doGoldLottery userId:', userId,
                    ' gameId:', gameId,
                    ' clientId:', clientId,
                    ' number:', number
                    )

    # 添加关于部分情况下每日抽奖次数限制的功能
    addLottoryNum = 0  # 0:初始值 1:增加数量1或者隔天后重新开始,初值设置为1
    #add50LottoryOrReset = 0  # 0:初始值 1:增加数量1或者隔天后重新开始,初值设置为1
    now_time = pktimestamp.getCurrentTimestamp()

    isSuitableClient = isSuitableClientID(userId, gameId, clientId)
    if isSuitableClient:
        tempResult = getWeightConfTemplate(userId, gameId, clientId)
        lastDoLottoryTime = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'LastDoLottoryTime')

        if not pktimestamp.is_same_day(now_time, lastDoLottoryTime):
            resetDailyRouletteData(userId, now_time)

        if 10 == number:
            dailyDo10LottoryNum = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'Do10LottoryNum')
            do10LottoryMaxTimes = tempResult.get('roulette_10_max_daily_num', 1000)
            if dailyDo10LottoryNum >= do10LottoryMaxTimes:
                ftlog.debug('hallroulette.doGoldLottery dailyDo10LottoryNum >= do10LottoryMaxTimes, beyond max limit',
                            'dailyDo10LottoryNum', dailyDo10LottoryNum,
                            'do10LottoryMaxTimes', do10LottoryMaxTimes
                            )
                return reach10MaxTimes()
            else:
                addLottoryNum = 1


        if 50 == number:
            dailyDo50LottoryNum = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'Do50LottoryNum')
            do50LottoryMaxTimes = tempResult.get('roulette_50_max_daily_num', 1000)
            if dailyDo50LottoryNum >= do50LottoryMaxTimes:
                ftlog.debug('hallroulette.doGoldLottery dailyDo50LottoryNum >= do50LottoryMaxTimes, beyond max limit',
                            'dailyDo50LottoryNum', dailyDo50LottoryNum,
                            'do50LottoryMaxTimes', do50LottoryMaxTimes
                            )
                return reach50MaxTimes()
            else:
                addLottoryNum = 1


    # 减少钻石
    result = {}
    count = -(number * 20)
    trueDelta, _finalCount = userchip.incrDiamond(userId, gameId, count, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, 'HALL_ROULETTE', 0, 0)
    if not trueDelta :
        # 消费失败 
        return toShop()

    #在扣除砖石后做每日抽奖次数限制的功能的数值设定0
    if isSuitableClient:
        tempResult = getWeightConfTemplate(userId, gameId, clientId)
        if 1 == addLottoryNum:
            if 10 == number:
                pkgamedata.incrGameAttr(userId, HALL_GAMEID, 'Do10LottoryNum', 1)
                pkgamedata.setGameAttr(userId, HALL_GAMEID, 'LastDoLottoryTime', now_time)
            if 50 == number:
                pkgamedata.incrGameAttr(userId, HALL_GAMEID, 'Do50LottoryNum', 1)
                pkgamedata.setGameAttr(userId, HALL_GAMEID, 'LastDoLottoryTime', now_time)

        result['10lottoryNum'] = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'Do10LottoryNum')
        result['50lottoryNum'] = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'Do50LottoryNum')
        result['10MaxNum'] = tempResult.get('roulette_10_max_daily_num', 1000)
        result['50MaxNum'] = tempResult.get('roulette_50_max_daily_num', 1000)
        ftlog.debug('after change diamond, roulette limit data, 10lottoryNum', result['10lottoryNum'],
                    '50lottoryNum', result['50lottoryNum'], '10MaxNum', result['10MaxNum'],
                    '50MaxNum', result['50MaxNum'])

    #将抽奖数进行存储，满足bigRewardNumber，使用大奖概率，否则使用小奖概率
    addBigRewardToPool(userId, gameId, clientId, number)
    # 抽奖
    items = []    
    for _num in range(0, number):
        items.append(doRouletteLottery(userId, gameId, clientId))
        
    result['items'] = items
    #对抽奖进行修改，连抽的话进行统一的数据库操作
    sendGiftsToUser(userId, gameId, clientId, items)
    #更新钻石
    datachangenotify.sendDataChangeNotify(gameId, userId, ['udata'])
    #抽奖成功，进行小兵的下发
    for _ in range(0, number):
        daobase.executeMixCmd('RPUSH', CURKEY, userId)
        
    #统计需求
    ftlog.hinfo('doGoldLottery.userId=', userId,
               'gameId=', gameId,
               'clientId=', clientId,
               'number=', number,
               'rouletteType=', 2,
               'rewardItem=', items)
    TGHall.getEventBus().publishEvent(TYEventRouletteDiamond(userId, gameId, number))
    return result

def resetDailyRouletteData(userId, now_time):
    pkgamedata.setGameAttr(userId, HALL_GAMEID, 'LastDoLottoryTime', now_time)
    pkgamedata.setGameAttr(userId, HALL_GAMEID, 'Do10LottoryNum', 0)
    pkgamedata.setGameAttr(userId, HALL_GAMEID, 'Do50LottoryNum', 0)


def bigRewardOrReward(userId, gameId, clientId):
    '''
        判断用户金盘抽奖的概率池
    '''
    nowBigRewardNumber = daobase.executeMixCmd('HGET', 'allSoldier', 'bigRewardNumber') or 0
    if int(nowBigRewardNumber) > 0:
        if ftlog.is_debug():
            ftlog.debug('hallroulette.nowBigRewardNumber: ', nowBigRewardNumber, ' user goldBigRewardConfig...')
        return 'goldBigReward_items'
        
    return 'gold_items'

def addBigRewardToPool(userId, gameId, clientId, number):
    nowAllNumber = int(daobase.executeMixCmd('hincrby', 'allSoldier', 'allRewardNumber' , number))
    tempResult = getWeightConfTemplate(userId, gameId, clientId)
    needBigNumber = tempResult.get('bigRewardNumber',1200)
    if nowAllNumber > needBigNumber:
        if ftlog.is_debug():
            ftlog.debug('hallroulette.addBigRewardToPool bigRewardNumber_config:', needBigNumber,
                        ' nowAllNumber:', nowAllNumber,
                        ' need add bigRewardNumber'
                        )
            
        nowAllNumber -= needBigNumber
        daobase.executeMixCmd('hincrby', 'allSoldier', 'bigRewardNumber' , 1)
        if ftlog.is_debug():
            nowBigRewardNum = daobase.executeMixCmd('HGET', 'allSoldier', 'bigRewardNumber')
            ftlog.debug('hallroulette.addBigRewardToPool hincrby bigRewardNumber to : ', nowBigRewardNum)
        daobase.executeMixCmd('hincrby', 'allSoldier', 'allRewardNumber', -needBigNumber)

def sendSoldierRewardToUser(userId, gameId, reward):
    '''
        将本期的奖品进行下发
    '''
    changed = []
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetKind, _addCount, _final = userAssets.addAsset(gameId, reward.get('itemId'), reward.get('count'), int(time.time()), 'ROULETTE_BIGREWARD', 0)
    if assetKind.keyForChangeNotify:
                changed.append(assetKind.keyForChangeNotify)
    datachangenotify.sendDataChangeNotify(gameId, userId, changed)

def sendGiftsToUser(userId, gameId, clientId, items):
    '''
        多个奖品时的发奖,或者一个奖品的发奖，items为数组
    '''
    contentItemList = []  
    rouletteMap = getRouletteMap() 
    
    for item in items:
        itemMap = rouletteMap.get(item, {}) 
        if itemMap:
            #添加判断流程，判断奖励是否需要发送led
            if itemMap.get('isSendLed', False):
                userInfo = halluser.getUserInfo(userId, gameId, clientId)
                msgstr = '恭喜玩家' + userInfo.get('name', '') + '在幸运大转盘中，抽中了' + itemMap.get('itemDesc', '') + '大奖！快来参与，大奖得主就是你！'
                hallled.sendLed(HALL_GAMEID, msgstr, 0, 'hall')

                # 轮播LED仅保留最近10条中奖记录
                doRouletteRecordKey = "roulette:recordLed"
                try:
                    datas = {'name': userInfo.get('name', ''), 'itemDesc': itemMap.get('itemDesc', '')}
                    recordledLen = daobase.executeMixCmd('RPUSH', doRouletteRecordKey, json.dumps(datas))
                    if recordledLen > 10:
                        # 超过10个就截取后10个
                        daobase.executeMixCmd('LTRIM', doRouletteRecordKey, -10, -1)
                except:
                    ftlog.warn("redis rpush|ltrim roulette:recordLed error", gameId, userId, clientId, msgstr)

                ftlog.debug("sendGiftsToUser|1", userId, gameId, clientId, msgstr)
            ftlog.debug("sendGiftsToUser|2", userId, gameId, clientId, itemMap.get('isSendLed'))
            
            # 添加中奖内容    
            contentItemList.append(TYContentItem.decodeFromDict({'itemId':itemMap.get('itemId'), 'count':itemMap.get('count')}))

    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    results = userAssets.sendContentItemList(gameId, contentItemList, 1, True, int(time.time()), 'ROULETTE_GOLD', 0)
    datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(results))
    
def sendMsgToUser(userId, gameId):
    """
    将中奖信息发给用户prize
    """
    snatchConf = getSnatchConf()
    sendToMsg = snatchConf.get('rewardMsg', '')
    from poker.entity.biz.message import message
    message.send(gameId, message.MESSAGE_TYPE_SYSTEM, userId, sendToMsg)
        
def doGetGoldUpdate(userId, gameId, clientId):
    '''
        单独获取金盘配置信息
    '''
    result = {}
    # 拿到配置信息
    tempResult = getConfForClient(userId, gameId, clientId)
    if tempResult.get('gold_items', None):
        result['rouletteType'] = 'gold'
        result['isFirstCheck'] = doGetFisrtToGold(userId, gameId)
        result['items'] = tempResult.get('gold_items', [])
        return result

def doSilverLottery(userId, gameId, clientId):
    '''
        银盘抽奖
    '''
    # 减少抽奖卡
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    _, consumeCount, _final = userAssets.consumeAsset(gameId, hallitem.ASSET_ITEM_LOTTERY_CARD_ID, 1,
                                                      timestamp, 'ROULETTE_SILVER', 0)
    if consumeCount < 1:  # 去金盘抽奖
        result = doGetGoldUpdate(userId, gameId, clientId)
        from hall.servers.util.roulette_handler import rouletteHelper
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_goldUpdate', result)
        from poker.protocol import router
        router.sendToUser(mo, userId)
        return
    datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
    # 抽奖
    result = {}
    result['items'] = doRouletteSilverLottery(userId, gameId, clientId)
    # 判断下次的抽奖为金盘还是银盘
    result['rouletteType'] = 'silver'
    result['cardNumber'] =  userAssets.balance(gameId,hallitem.ASSET_ITEM_LOTTERY_CARD_ID,timestamp)
    # 返回信息，判断是否有抽奖卡，没有的话，改为金盘抽奖
    ftlog.hinfo('doSilverLottery.userId=', userId,
               'gameId=', gameId,
               'clientId=', clientId,
               'items=', result.get('items', []),
               'rouletteType=', 1,
               'number=', 1)
    sendGiftsToUser(userId, gameId, clientId, [result['items']])
    return result

def sendToUserALotteryCard(userId, gameId, clientId):
    '''
        用户第一次使用轮盘功能，赠送一张抽奖卡
    '''
    changed = []
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetKind, _addCount, _final = userAssets.addAsset(gameId, hallitem.ASSET_ITEM_LOTTERY_CARD_ID, 1, int(time.time()), 'ROULETTE_SILVER', 0)
    if assetKind.keyForChangeNotify:
        changed.append(assetKind.keyForChangeNotify)
    datachangenotify.sendDataChangeNotify(gameId, userId, changed)
    
def nowUserLotteryCardNumber(userId, gameId, clientId):
    '''
        判断用户的抽奖类型
    '''
    result = None
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()
    consumeCount = userAssets.balance(gameId,hallitem.ASSET_ITEM_LOTTERY_CARD_ID,timestamp)
    if consumeCount > 0:
        result = True
    else:
        result = False
    return result

'''
    更新信息
'''
def doUpdate(userId, gameId, clientId):
    '''
        刷新信息,判断用户进入银盘抽奖还是金盘抽奖
    '''
    result = {}
    # 判断用户是否是第一次进入该功能，如果是，则赠送一张银盘抽奖卡
    isFirstRoulette = pkgamedata.setnxGameAttr(userId, gameId, 'isFirstRoulette', 1)
    if isFirstRoulette:
        sendToUserALotteryCard(userId, gameId, clientId)
    # 拿到配置信息
    tempResult = getConfForClient(userId, gameId, clientId)
    # 判断用户的抽奖卡张数，决定进入金盘抽奖还是银盘抽奖
    if nowUserLotteryCardNumber(userId, gameId, clientId) :
        # 银盘
        result['rouletteType'] = 'silver'
        result['items'] = tempResult.get('silver_items', [])
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        result['cardNumber'] =  userAssets.balance(gameId,hallitem.ASSET_ITEM_LOTTERY_CARD_ID,timestamp)
    else:
        if tempResult.get('gold_items', None):
            # 金盘
            result['rouletteType'] = 'gold'
            result['isFirstCheck'] = doGetFisrtToGold(userId, gameId)
            result['items'] = tempResult.get('gold_items', [])

        # 部分情况需要限制每日抽奖的次数
        isSuitableClient = isSuitableClientID(userId, gameId, clientId)
        if isSuitableClient:
            result['10lottoryNum'] = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'Do10LottoryNum')
            result['50lottoryNum'] = pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'Do50LottoryNum')
            result['10MaxNum'] = tempResult.get('roulette_10_max_daily_num', 0)
            result['50MaxNum'] = tempResult.get('roulette_50_max_daily_num', 0)
        else:
            result['10lottoryNum'] = -1
            result['50lottoryNum'] = -1
            result['10MaxNum'] = -1
            result['50MaxNum'] = -1
            pass
    return result

def doGetSoldierIdForUser(userId, gameId, clientId, issue):
    '''
        处理客户端请求，在某一期内，寻找用户的小兵id
    '''
    result = {}
    rewardResult = {}
    userSoldier = []
    rewardTime = ''

    # 保存本期中奖信息
    issueDetailStr = daobase.executeMixCmd('HGET', HISKEYDETAIL + str(issue), 'info')
    if issueDetailStr:
        if ftlog.is_debug():
            ftlog.debug('hallroulette.doGetSoldierIdForUser issueDetailStr:', issueDetailStr)
            
        issueDetail = json.loads(issueDetailStr)
        rewardResult = issueDetail['result']
        soldiers = issueDetail['soldiers']
        rewardTime = issueDetail['time']
        
        sNum = len(soldiers)
        for index in range(0, sNum):
            if ftlog.is_debug():
                ftlog.debug('hallroulette.doGetSoldierIdForUser soldier id:', soldiers[index]
                            , 'type:', type(soldiers[index])
                            , ' userId:', userId
                            , ' type:', type(userId))
                
            if soldiers[index] == userId:
                userSoldier.append(getSoldierIdByIndex(index))
    
    result[issue] = userSoldier
    if ftlog.is_debug():
        ftlog.debug('hallroulette.doGetSoldierIdForUser result:', result)
        
    return result, rewardResult, rewardTime

def doGetFisrtToGold(userId, gameId):
    '''
        获取是否第一次进入金盘
    '''
    result = 0
    isFirstCheck = pkgamedata.setnxGameAttr(userId, gameId, 'isFirstGoldRoulette', 1)
    if isFirstCheck:
        result = 1
    return result

def doGetBeforeReward(userId, gameId, clientId):
    '''
        获取往期中奖人的信息
        以及即将开奖的信息
    '''
    result = {}
    result['reward'] = '暂时没有开奖'
    rewardlist = []
    
    issues = daobase.executeMixCmd('LRANGE', HISKEY, 0, -1)
        
    if issues:
        for issue in issues:
            issueResult, reward, rewardTime = doGetSoldierIdForUser(userId, gameId, clientId, issue)
            reward['isCheckin'] = len(issueResult[issue])
            obj = {}
            obj['reward'] = reward
            obj['time'] = rewardTime
            rewardlist.append(obj)
            
    result['reward'] = rewardlist    
    if ftlog.is_debug():
        ftlog.debug('hallroulette.doGetBeforeReward result:', result)
        
    return result

def getSnatchConf():
    '''
        获取当前时间段内的小兵配置
    '''
    clientConf = getTemeplateName()
    rouletteTemplateMap = getRouletteTemplateMap()
    templateConf = rouletteTemplateMap.get(clientConf, {})
    tempTemplate = templateConf.get('snatch', [])
    for v in tempTemplate:
        nowHour = int(time.strftime("%H", time.localtime()))
        if int(v.get('startTime', '')) <= nowHour and nowHour <= int(v.get('endTime', '')):
            return v
    return {}

def isBigRewardItem(item):
    '''
        获取大奖的配置
        判断是否是大奖
    '''
    rouletteMap = getRouletteMap() 
    itemMap = rouletteMap.get(item, {}) 
            
    clientConf = getTemeplateName()
    rouletteTemplateMap = getRouletteTemplateMap()
    templateConf = rouletteTemplateMap.get(clientConf, {})
    bigRewardConf = templateConf.get('bigReward', None)
    if ftlog.is_debug():
        ftlog.debug('hallroulette.isBigRewardItem item:', itemMap
                    , ' bigRewardConf:', bigRewardConf)
        
    if bigRewardConf :
        tempItem = bigRewardConf.get('itemId') 
        tempCount = bigRewardConf.get('count') 
        if tempItem and tempCount and (itemMap.get('itemId', None) == tempItem) and (itemMap.get('count', None) == tempCount):
            return True
    return False

def doGetSoldierInfo(userId, gameId, clientId):
    '''
        将小兵的配置信息进行解析，并且将需要下发的信息进行下发
        获取当前的时间，判断是否在时间区间内部，只返回当前的时间区间
    '''
    tempTemplate = getSnatchConf()
    soldierInfo = {}
    soldierInfo['desc'] = tempTemplate.get('desc', '')
    soldierInfo['picUrl'] = tempTemplate.get('picUrl', '')
    soldierInfo['endTime'] = tempTemplate.get('endTime', '')
    soldierInfo['startTime'] = tempTemplate.get('startTime', '')
    soldierInfo['needNumber'] = tempTemplate.get('needNumber', 0)
    nowPeople = []
        
    soldierInfo['issue'] = time.strftime("%Y%m%d", time.localtime()) + getIssue(False)
    
    tempNumber = getSoldierNumber()
    needNumber = tempTemplate.get('needNumber', 0)
    if tempNumber - needNumber > 0:
        tempNumber = needNumber
        
    soldierInfo['nowNumber'] = tempNumber
    
    mySoldier = []
    allSoldier = daobase.executeMixCmd('LRANGE', CURKEY, 0, needNumber - 1)
    if allSoldier:
        sLen = len(allSoldier)
        if ftlog.is_debug():
            ftlog.debug('hallroulette.doGetSoldierInfo allSoldier len:', sLen)
        for index in range(0, sLen):
            if ftlog.is_debug():
                ftlog.debug('hallroulette.doGetSoldierInfo now soldier index:', index
                            , ' soldier id:', allSoldier[index]
                            , ' userId:', userId)
                
            if allSoldier[index] == userId:
                sId = getSoldierIdByIndex(index)
                mySoldier.append(sId)
                
            if allSoldier[index] not in nowPeople:
                nowPeople.append(allSoldier[index])
    
    if ftlog.is_debug():
        ftlog.debug('hallroulette.doGetSoldierInfo mySoldiers:', mySoldier
                    , ' nowPeople:', nowPeople)
                    
    soldierInfo['mySoldiers'] = mySoldier
    soldierInfo['nowPeople'] = len(nowPeople)
    
    result = {}
    result['soldierInfo'] = soldierInfo
    if ftlog.is_debug():
        ftlog.debug('hallroulette.doGetSoldierInfo result:', result)
            
    return result

def getIssue(issueType):
    '''
    期号的统一管理
    '''
    result = ''
    issue = int(daobase.executeMixCmd('HGET', 'allSoldier', 'rouletteIssue') or 0)
    if not issue or issueType:
            count = daobase.executeMixCmd('hincrby', 'allSoldier', 'rouletteIssue', 1)
            result = '%04d' % (count)
    elif not issueType:
        result = '%04d' % (issue)
    return result

def getSoldierIdByIndex(index):
    '''
    获取小兵ID
    '''
    sId = '%07d'%(index + 1)
    return sId
    
def findRewardUsers(gameId, issue, reward):
    '''
    开奖：
        从本期小兵中获取一个中奖的小兵，并且返回
        修改
            首先，判断是否有多余的小兵，对多余的小兵进行管理
    '''
    needNumber = getSnatchConf().get('needNumber', 0)
    nowNumber = getSoldierNumber()
    if needNumber > nowNumber:
        return 0, 0, {}

    # 本期小兵list
    soldiers = daobase.executeMixCmd('LRANGE', CURKEY, 0, needNumber - 1)
    if not soldiers:
        return 0, 0
    
    # 移除本期小兵，留下下一期小兵
    daobase.executeMixCmd('LTRIM', CURKEY, needNumber, -1)
    
    # 开奖的时候，对每一个参与人的夺宝次数加1
    for soldier in set(soldiers):
        pkgamedata.incrGameAttr(soldier, HALL_GAMEID, 'checkinSoldiers', 1)

    # 中奖序号
    x = random.randint(0, len(soldiers) - 1)
    # 生成中奖结果
    nowUserId = soldiers[x]
    chip = pkuserchip.getUserChipAll(nowUserId)
    vip = hallvip.userVipSystem.getUserVip(nowUserId).vipLevel.level
    userInfo = halluser.getUserInfo(nowUserId, gameId, sessiondata.getClientId(nowUserId))
    result = {}
    result['chip'] = chip
    result['vip'] = vip
    result['sex'] = userInfo.get('sex', 0)
    result['purl'] = userInfo.get('purl', '')
    result['sId'] = getSoldierIdByIndex(x)
    result['uId'] = nowUserId
    result['issue'] = issue
    result['name'] = userInfo.get('name', '')
    result['nowReward'] = reward
    
    # 添加夺宝次数
    # 夺宝人的夺宝次数
    nowRewardNumber = pkgamedata.incrGameAttr(nowUserId, HALL_GAMEID, 'getRewardNumber', 1)
    result['getRewardNumber'] = nowRewardNumber
    result['isCheckin'] = 0
    
    # 添加夺宝人的夺宝次数
    result['checkinSoldiers'] = pkgamedata.getGameAttrInt(nowUserId, HALL_GAMEID, 'checkinSoldiers')        
    
    #下发奖励的时候，全服广播，发led
    strLed = '恭喜' + userInfo.get('name', '') + '玩家在转盘夺宝活动中，斩获'+ issue + '期' + reward + '大奖，不要再等了，你就是下一位夺宝王！'
    from hall.servers.util.rpc import user_remote as SendLed
    SendLed.sendHallLed(gameId, strLed, 1, 'hall')
    
    # 打印开奖日志
    ftlog.hinfo('findRewardUsers.gameId=', gameId,
               'issue=', issue,
               'userId=', nowUserId,
               'reward=', reward,
               'soldiers=', soldiers,
               'result=', result,
               'x=', x,
               'snatchConf=', getSnatchConf())

    # 保存历史中奖信息
    issueObj = {}
    issueObj['issue'] = issue
    issueObj['soldiers'] = soldiers
    issueObj['result'] = result
    issueObj['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # 保存本期中奖信息
    daobase.executeMixCmd('HSET', HISKEYDETAIL + str(issue), 'info', json.dumps(issueObj))
    daobase.executeMixCmd('LPUSH', HISKEY, issue)
    if daobase.executeMixCmd('LLEN', HISKEY) > 10:
        delIssue = daobase.executeMixCmd('RPOP', HISKEY)
        if ftlog.is_debug():
            ftlog.debug('hallroulette.findRewardUsers delIssue:', delIssue)
            
        # 删除过期记录
        if delIssue:
            daobase.executeMixCmd('DEL', HISKEYDETAIL + str(delIssue))

    return nowUserId, result

def getSoldierNumber():
    '''
    获取待开奖的小兵队列
    '''
    soldierNumber = daobase.executeMixCmd('LLEN', CURKEY)
    if soldierNumber:
        if ftlog.is_debug():
            ftlog.debug('hallroulette.getSoldierNumber number:', soldierNumber)
        return int(soldierNumber)
    return 0
        
class Soldier(object):

    def __init__(self, userId):
        self.userId = userId
        self.sId = None
    
    def getUserId(self):
        return self.userId
    
    def setUserId(self, userId):
        self.userId = userId
    
    def getsId(self):
        return self.sId
    
    def setsId(self, sId):
        self.sId = sId
        
    def objToJson(self):
        result = {}
        result['userId'] = self.userId
        result['sId'] = self.sId
        return result


class TYEventRouletteDiamond(UserEvent):
    """
    钻石抽奖事件
    """
    def __init__(self, userid, gameid, number):
        super(TYEventRouletteDiamond, self).__init__(userid, gameid)
        self.number = number
