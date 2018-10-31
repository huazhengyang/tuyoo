# -*- coding=utf-8 -*-
import time

import datetime

import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hallactivity.activity_type import TYActivityType
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import gdata
from poker.entity.dao import daobase
from poker.entity.events.tyevent import GameOverEvent


class TYActivityPlayGamePresentGift(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_PLAYGAME_GIFT
    hasLoadedScript = False
    EXCHANGE_SCRIPT = "TYActivityPlayGamePresentGift:exchange"
    HANDLE_EVENT_SCRIPT = "TYActivityPlayGamePresentGift:handle_event"

    __exchange_script = '''
    local key = tostring(KEYS[1])
    local needCount = tonumber(KEYS[2])
    local limitTime = tonumber(KEYS[3])
    local exTimesField = tostring(KEYS[4])

    local data = redis.call('hmget', key, 'giftNum', exTimesField)
    local giftNum = tonumber(data[1])
    local exTimes = tonumber(data[2])
    if exTimes and exTimes >= limitTime then
        return 1
    end
    if not giftNum or giftNum < needCount then
        return 2
    end

    if not exTimes then
        exTimes = 1
    else
        exTimes = exTimes + 1
    end

    redis.call('hmset', key, 'giftNum', giftNum - needCount, exTimesField, exTimes)

    return 0
    '''
    '''
    presentNum, accumulateKey, accumulateValue, accumulateType,
                accumulateIdentiferValue,mustContinuous, maxInterval, userActivityKey, rewardNeedNum,
                nowTimeStamp, hasRewardedKey
    '''

    __handle_event_script = '''
    local presentNum = tonumber(KEYS[1])
    local accumulateKey = tostring(KEYS[2])
    local accumulateValue = tonumber(KEYS[3])
    local accumulateType = tonumber(KEYS[4])
    local accumulateIdentiferValue = tostring(KEYS[5])
    local mustContinuous = tonumber(KEYS[6])
    local maxInterval = tonumber(KEYS[7])
    local userActivityKey = tostring(KEYS[8])
    local rewardNeedNum = tonumber(KEYS[9])
    local nowTimeStamp = tonumber(KEYS[10])
    local hasRewardedKey = tostring(KEYS[11])

    local nowValue, hasRewarded, giftNum, nowNewValue
    local oldAccumulateIdentiferValue, oldAccumulateValue, lastAccumulateTimeStamp
    local presentGiftNum

    local ret = 0

    if accumulateType == 1 then
        if  mustContinuous == 0 then
            redis.call('hincrby', userActivityKey, accumulateKey, accumulateValue)
            ret = 5
        else
            local data3 =
                redis.call("hmget", userActivityKey, "accumulateIdentifer",
                    accumulateKey, "lastAccumulateTimeStamp")
            oldAccumulateIdentiferValue = tostring(data3[1])
            oldAccumulateValue = tonumber(data3[2])
            lastAccumulateTimeStamp = tonumber(data3[3])

            if not oldAccumulateIdentiferValue  or not lastAccumulateTimeStamp
                or oldAccumulateIdentiferValue ~= accumulateIdentiferValue
                or (nowTimeStamp - lastAccumulateTimeStamp > maxInterval and maxInterval ~= 0) then
                redis.call('hmset',userActivityKey, "accumulateIdentifer",
                    accumulateIdentiferValue,accumulateKey,accumulateValue,
                    "lastAccumulateTimeStamp", nowTimeStamp)
                ret = 6
            else
                redis.call('hincrby',userActivityKey,accumulateKey,accumulateValue)
                redis.call('hmset',userActivityKey, "accumulateIdentifer", accumulateIdentiferValue,
                    "lastAccumulateTimeStamp", nowTimeStamp)
                ret = 7
            end
        end

        local data4
            = redis.call('hmget', userActivityKey, accumulateKey, hasRewardedKey, "giftNum")
        nowValue = tonumber(data4[1])
        hasRewarded = tonumber(data4[2])
        giftNum = tonumber(data4[3])

        if not nowValue then
            nowValue = 0
        end

        if not hasRewarded then
            hasRewarded = 0
        end
        if not giftNum then
            giftNum = 0
        end

        if nowValue >= rewardNeedNum and ( not hasRewarded or hasRewarded  ==  0) then
            redis.call('hmset', userActivityKey, hasRewardedKey, 1, "giftNum", giftNum + presentNum)
        end
    else
        nowNewValue = 0
        if mustContinuous == 0 then
            nowValue = redis.call('hget', userActivityKey, accumulateKey)
            nowValue = tonumber(nowValue)
            if not nowValue then
                nowValue = 0
            end
            nowNewValue = nowValue + accumulateValue
            ret = 2
        else
            local data2 =
                redis.call("hmget", userActivityKey, "accumulateIdentifer",
                    accumulateKey, "lastAccumulateTimeStamp")
            oldAccumulateIdentiferValue = tostring(data2[1])
            oldAccumulateValue = tonumber(data2[2])
            lastAccumulateTimeStamp = tonumber(data2[3])

            if not oldAccumulateIdentiferValue  or not lastAccumulateTimeStamp
                or oldAccumulateIdentiferValue ~= accumulateIdentiferValue
                or (nowTimeStamp - lastAccumulateTimeStamp > maxInterval and maxInterval ~= 0) then
                redis.call('hmset',userActivityKey, "accumulateIdentifer",
                    accumulateIdentiferValue,accumulateKey,accumulateValue)
                nowNewValue = accumulateValue
                ret = 3
            else
                nowNewValue = redis.call('hincrby',userActivityKey,accumulateKey,accumulateValue)
                nowNewValue = tonumber(nowNewValue)
                ret = 4
            end
        end
        presentGiftNum = math.floor(nowNewValue/rewardNeedNum) * presentNum
        nowNewValue = nowNewValue % rewardNeedNum
        redis.call("hincrby", userActivityKey, "giftNum", presentGiftNum)
        redis.call("hmset", userActivityKey, accumulateKey, nowNewValue, "lastAccumulateTimeStamp", nowTimeStamp)
    end

    return ret
    '''

    @classmethod
    def initialize(cls):
        if not cls.hasLoadedScript:
            daobase.loadLuaScripts(cls.EXCHANGE_SCRIPT, cls.__exchange_script)
            daobase.loadLuaScripts(cls.HANDLE_EVENT_SCRIPT, cls.__handle_event_script)
            cls.hasLoadedScript = True

    def __init__(self, dao, clientConfig, serverConfig):
        super(TYActivityPlayGamePresentGift, self).__init__(dao, clientConfig, serverConfig)
        self.initialize()
        TGHall.getEventBus().subscribe(GameOverEvent, self.handleEvent)

    def finalize(self):
        TGHall.getEventBus().unsubscribe(GameOverEvent, self.handleEvent)

    '''
        "start": "2015-02-28 00:00:00",  # 必须
        "end": "2015-04-01 00:00:00",# 必须
        "reserveDays": 5,# 必须
        "dayTimeLimit":[[12,13],[20,22]],

        "conditions":["roomId","role","roundNum"],# 必须
        "accumulateField":"roundNum",# 必须
        "accumulateType": 0, #1 : 保存1天,一天为单位累计,1天奖励1次；0：不区周期，满足条件就reward，多次循环 # 必须

        "rewardNeedNum":3,  #必须

        #同一房间连续玩
        "accumulateIdentifer":"roomId",
        "accumulateMustContinuous":1,
        "accumulateMaxInterval": 300,#minutes  0：无限制

        #condition
        "roomId":[602,603],
        "role":"landlord",
        "roundNum":3,

        #present config
        "presentConfig":{1:2,2:4,3:10,4:25},
        "presentBased": "roomLevel",

        #another kind of present
        "presentNum": 5,

        #gift also can buy  #奖券  10 个  100 元宵
        "buy":[
                {"id": 1, "consume":"user:coupon", "count":10, "get":100, "unit":"棵树苗"}
            ]
    '''

    def handleEvent(self, event):
        '''
            当收到每局结束发送的event时，在activity.py中调用该方法
            处理前台活动返回的配置包括客户端配置和服务器配置
        '''
        ftlog.debug("TYActivityPlayGamePresentGift handleEvent123:", event.role, event.roomLevel, event.roundNum,
                    event.gameId, event.userId, event.clientId)
        gameId = event.gameId
        userId = event.userId
        activityId = self._clientConf.get("id")
        if not activityId:
            ftlog.debug("TYActivityPlayGamePresentGift handleEvent not find adtivityId")
            return
        if not self.checkOperative():
            ftlog.debug("activity expired:", activityId)
            return
        # 对_config开始解析配置，conditions玩的局数，默认为1
        for cond in self._serverConf["conditions"]:
            if cond == self._serverConf['accumulateField']:
                continue
            condValue = event.get(cond)
            if isinstance(self._serverConf[cond], list):
                if condValue not in self._serverConf[cond]:
                    ftlog.debug("TYActivityPlayGamePresentGift handleEvent, condValue not match,cond:", cond)
                    return
            else:
                if condValue != self._serverConf[cond]:
                    ftlog.debug("TYActivityPlayGamePresentGift handleEvent, condValue not match,cond:", cond)
                    return
        # 有效时间
        if "dayTimeLimit" in self._serverConf:
            if not self._checkDayTime():
                ftlog.debug("TYActivityPlayGamePresentGift handleEvent, dayTimeLimit not match")
                return
        # 所在房间等级
        if "presentBased" in self._serverConf:
            presentBasedValue = event.get(self._serverConf["presentBased"])
            presentBasedValue = gdata.getBigRoomId(presentBasedValue)
            ftlog.debug("TYActivityPlayGamePresentGift handleEvent11:", presentBasedValue)
            if not presentBasedValue:
                ftlog.debug("TYActivityPlayGamePresentGift handleEvent, presentBasedvalue not find, presentBased:",
                            self._serverConf["presentBased"])
                return
            else:
                if (not isinstance(presentBasedValue, int)) or str(presentBasedValue) not in self._serverConf[
                    "presentConfig"]:
                    ftlog.debug("TYActivityPlayGamePresentGift handleEvent, presentBasedValue not match:",
                                presentBasedValue)
                    return
                presentNum = self._serverConf["presentConfig"][str(presentBasedValue)]
        else:
            presentNum = self._serverConf["presentNum"]
        # 是否可连续，1表示1天内连续、0表示可连续
        accumulateType = self._serverConf["accumulateType"]
        # 需要领取奖励的局数
        rewardNeedNum = self._serverConf["rewardNeedNum"]

        accumulateKey = "accumulate"
        hasRewardedKey = "hasRewarded"
        if accumulateType == 1:
            accumulateKey = "%s:%s" % (accumulateKey, time.strftime('%Y-%m-%d', time.localtime(time.time())))
            hasRewardedKey = "%s:%s" % (hasRewardedKey, time.strftime('%Y-%m-%d', time.localtime(time.time())))
        accumulateValue = event.get(self._serverConf["accumulateField"])
        if not accumulateValue:
            ftlog.debug("TYActivityPlayGamePresentGift handleEvent, accumulateValue not find:",
                        self._serverConf["accumulateField"])
            return
        mustContinuous = 0
        maxInterval = 0
        accumulateIdentiferValue = "noidentifer"
        nowTimeStamp = int(time.time())
        if 'accumulateMustContinuous' in self._serverConf:
            if self._serverConf["accumulateMustContinuous"] == 1:
                mustContinuous = 1
                maxInterval = self._serverConf.get("accumulateMaxInterval", 300)
                # 判定是否是同一房间
                if "accumulateIdentifer" in self._serverConf:
                    accumulateIdentifer = self._serverConf["accumulateIdentifer"]
                    accumulateIdentiferValue = event.get(accumulateIdentifer)
                    accumulateIdentiferValue = gdata.getBigRoomId(accumulateIdentiferValue)
                    ftlog.debug("this accumulateIdentiferValue bigRoomId is", accumulateIdentiferValue)
                    if not accumulateIdentiferValue:
                        ftlog.debug("TYActivityPlayGamePresentGift handleEvent, accumulateIdentiferValue not find:",
                                    accumulateIdentifer)
                        return
                else:
                    ftlog.error("TYActivityPlayGamePresentGift handleEvent, accumulateIdentifer not find")
                    return
        userActivityKey = "TYActivity:%d:%d:%s" % (gameId, userId, activityId)
        ftlog.debug("playGamePresentGift handleEvent:", presentNum, accumulateKey, accumulateValue, accumulateType,
                    accumulateIdentiferValue, mustContinuous, maxInterval, userActivityKey, rewardNeedNum,
                    nowTimeStamp, hasRewardedKey)
        ret = daobase.executeUserLua(userId, self.HANDLE_EVENT_SCRIPT,
                                     11, presentNum, accumulateKey, accumulateValue, accumulateType,
                                     accumulateIdentiferValue, mustContinuous, maxInterval, userActivityKey,
                                     rewardNeedNum,
                                     nowTimeStamp, hasRewardedKey)

        ftlog.debug("TYActivityPlayGamePresentGift handleEvent, executeUserLua ret:", ret)

    def addPresentNum(self, gameId, userId, clientId, presentNum):
        activityId = self._clientConf.get("id")

        if not activityId:
            if ftlog.is_debug():
                ftlog.debug("TYActivityPlayGamePresentGift.addPresentNum not find adtivityId")
            return

        if not self.checkOperative():
            if ftlog.is_debug():
                ftlog.info("TYActivityPlayGamePresentGift.addPersentNum activity expired:", activityId)
            return

        # 有效时间
        if "dayTimeLimit" in self._serverConf:
            if not self._checkDayTime():
                ftlog.debug("TYActivityPlayGamePresentGift.addPersentNum, dayTimeLimit not match")
                return

        # 是否可连续，1表示1天内连续、0表示可连续
        accumulateType = self._serverConf["accumulateType"]
        # 需要领取奖励的局数
        rewardNeedNum = self._serverConf["rewardNeedNum"]

        accumulateKey = "accumulate"
        accumulateValue = 1
        hasRewardedKey = "hasRewarded"
        if accumulateType == 1:
            accumulateKey = "%s:%s" % (accumulateKey, time.strftime('%Y-%m-%d', time.localtime(time.time())))
            hasRewardedKey = "%s:%s" % (hasRewardedKey, time.strftime('%Y-%m-%d', time.localtime(time.time())))
        mustContinuous = 0
        maxInterval = 0
        accumulateIdentiferValue = "noidentifer"
        nowTimeStamp = int(time.time())
        if 'accumulateMustContinuous' in self._serverConf:
            if self._serverConf["accumulateMustContinuous"] == 1:
                mustContinuous = 1
                maxInterval = self._serverConf.get("accumulateMaxInterval", 300)

        userActivityKey = "TYActivity:%d:%d:%s" % (gameId, userId, activityId)
        if ftlog.is_debug():
            ftlog.debug("TYActivityPlayGamePresentGift.addPresentNum:",
                        presentNum, accumulateKey, accumulateValue, accumulateType,
                        accumulateIdentiferValue, mustContinuous, maxInterval, userActivityKey, rewardNeedNum,
                        nowTimeStamp, hasRewardedKey)

        ret = daobase.executeUserLua(userId, self.HANDLE_EVENT_SCRIPT,
                                     11, presentNum, accumulateKey, accumulateValue, accumulateType,
                                     accumulateIdentiferValue, mustContinuous, maxInterval, userActivityKey,
                                     rewardNeedNum,
                                     nowTimeStamp, hasRewardedKey)

        if ftlog.is_debug():
            ftlog.debug("TYActivityPlayGamePresentGift.addPresentNum executeUserLua ret:", ret)

    def _checkDayTime(self):
        tt = datetime.datetime.now()
        hour = tt.hour
        ret = False
        for limit in self._serverConf["dayTimeLimit"]:
            if hour >= limit[0] and hour <= limit[1]:
                ret = True
        return ret

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')
        clientId = msg.getParam("clientId")
        activityId = msg.getParam("activityId")
        action = msg.getParam("action")
        if action == "getGifts":
            return self._getGifts(userId, gameId, clientId, activityId)
        elif action == "exchange":
            actionParams = msg.getParam('actionParams')
            if not actionParams or "exchangeId" not in actionParams:
                return {"errorInfo": "exchangeId not found", "errorCode": 3, "list": []}
            else:
                exchangeId = actionParams["exchangeId"]

            return self._exchange(userId, gameId, clientId, activityId, exchangeId)
        elif action == "buy":
            actionParams = msg.getParam('actionParams')
            if not actionParams or "buyId" not in actionParams:
                return {"errorInfo": "buy not found", "errorCode": 4, "list": []}
            else:
                buyId = actionParams["buyId"]
            return self._buy(userId, gameId, clientId, activityId, buyId)
        else:
            return {"errorInfo": "unknown action", "errorCode": 1, "list": []}

    def _getGifts(self, userId, gameId, clientId, activityId):
        key = "TYActivity:%d:%d:%s" % (gameId, userId, activityId)
        ftlog.debug("getGifts key:", key)
        num = daobase.executeUserCmd(userId, 'hget', key, 'giftNum')
        ftlog.debug("getGifts key num1:", num)
        if not num:
            num = 0
        ftlog.debug("getGifts key num:", num)
        return {"giftsNum": num}

    def _exchange(self, userId, gameId, clientId, activityId, exchangeId):
        key = "TYActivity:%d:%d:%s" % (gameId, userId, activityId)
        ftlog.debug("getGifts key:", key)
        ftlog.debug("getGifts key!!!exchangeId:", exchangeId)
        num = daobase.executeUserCmd(userId, 'hget', key, 'giftNum')
        if not num:
            num = 0
        giftsNum = num
        exConfig = self._getExchangeConfig(exchangeId)
        if not exConfig:
            return {"errorInfo": "config not exist", "errorCode": 2}
        needCount = exConfig["consumeCount"]
        limit = exConfig["limitTimes"]
        nowDateStr = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        exTimesField = "exTimes:%d:%s" % (exchangeId, nowDateStr)
        key = "TYActivity:%d:%d:%s" % (gameId, userId, activityId)
        ftlog.debug("_exchange key:", key)
        exchangeResult = daobase.executeUserLua(userId, self.EXCHANGE_SCRIPT,
                                                4, key, needCount, limit, exTimesField)
        if exchangeResult == 1:
            ftlog.info("exceed limit,", "userId", userId, "gameId", gameId, "activityId", activityId,
                       "exchangeId", exchangeId, clientId)
            return {"exchangeResult": [], "reason": u"今日兑换次数已满！", "list": [], "giftsNum": giftsNum}
        if exchangeResult == 2:
            ftlog.info("no enough gifts,", "userId", userId, "gameId", gameId, "activityId", activityId,
                       "exchangeId", exchangeId, clientId)
            ftlog.debug("self._clientConf:", self._clientConf)
            giftName = self._clientConf["config"]["gift"]["name"]
            info = u"您的%s不足！" % giftName
            ftlog.debug("_exchange key123:", key)
            ftlog.debug("_exchange key123:", giftsNum)
            return {"exchangeResult": [], "reason": info, "list": [], "giftsNum": giftsNum}
        result = {}
        result["exchangeResult"] = []
        from hall.entity.hallitem import itemSystem
        userAssets = itemSystem.loadUserAssets(userId)
        assetList = []
        for item in exConfig["items"]:
            asset = userAssets.addAsset(gameId, item['productId'], item['count'], int(time.time()),
                                        'ACTIVITY_GETSCORE', 0)
            assetList.append(asset)
            result["exchangeResult"].append({"name": item["name"], "count": item["count"],
                                             "productId": item["productId"], "unit": item["unit"]})
        info = '兑换成功，您获得%s' % (TYAssetUtils.buildContentsString(assetList, True))
        ftlog.info('exchangeCode userId=', userId,
                   'gameId=', gameId,
                   'clientId=', clientId,
                   'activityId=', activityId,
                   'assetList=', [(atup[0].kindId, atup[1]) for atup in assetList])
        changeNames = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
        result["reason"] = info
        result["list"] = []
        '''
            拿到当前剩余的积分，并返回
        '''
        ftlog.debug("_exchange key123:", key)
        result["giftsNum"] = giftsNum
        ftlog.debug("_exchange key123456:", giftsNum)
        ftlog.info("exchangeResult,", "userId", userId, "gameId", gameId, "activityId", activityId,
                   "exchangeId", exchangeId, clientId, result)
        return result

    def _getExchangeConfig(self, exchangeId):
        conf = None
        ftlog.debug("exchangeId:", exchangeId, self._clientConf,
                    self._clientConf["config"].get("exchange", "not find exchange config"))
        if "exchange" in self._clientConf["config"]:
            exConfigs = self._clientConf["config"]["exchange"]
            for config in exConfigs:
                if exchangeId == config["id"]:
                    conf = config
                    break
        return conf

    def _buy(self, userId, gameId, clientId, activityId, buyId):
        buyConfig = self._getBuyConfig(buyId)
        if not buyConfig:
            return {"errorInfo": "config not exist", "errorCode": 2}
        consumeItemId = buyConfig["consume"]
        consumeName = buyConfig["consumeName"]
        consumeCount = buyConfig["count"]
        getCount = buyConfig["get"]
        unit = buyConfig["unit"]
        from hall.entity.hallitem import itemSystem
        userAssets = itemSystem.loadUserAssets(userId)
        _, count, _ = userAssets.consumeAsset(gameId,
                                              consumeItemId, consumeCount,
                                              int(time.time()), "ACTIVITY_BUY", 0)
        if count != consumeCount:
            info = u"您的%s不足！" % consumeName
            return {"reason": info}
        else:
            key = "TYActivity:%d:%d:%s" % (gameId, userId, activityId)
            daobase.executeUserCmd(userId, "hincrby", key, "giftNum", getCount)
            info = u"您获得了%d%s" % (getCount, unit)
            return {"reason": info}

    def _getBuyConfig(self, buyId):
        conf = None
        ftlog.debug("buyId:", buyId, self._clientConf,
                    self._clientConf["config"].get("buy", "not find buy config"))
        if "buy" in self._clientConf["config"]:
            buyConfigs = self._clientConf["config"]["buy"]
            for config in buyConfigs:
                if buyId == config["id"]:
                    conf = config
                    break
        return conf
