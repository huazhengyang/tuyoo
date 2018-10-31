
'''  
    Create by wuyongsheng
    on 2015-10-12
    for fanfanle activity_fanfanle
'''
from hall.entity.hallactivity.activity_type import TYActivityType
from hall.entity.todotask import TodoTaskPayOrder
'''
    TYActivity 关联活动，根据活动ID判断是否是翻翻乐，处理翻翻乐的具体操作
        
        需要返回三张牌的牌面（花色、大小）
        需要返回领奖的倍数
    思路分析：
        需要在activity_handler.py中注册action=activityflipcard
'''

from datetime import datetime, timedelta
import time
import freetime.util.log as ftlog
from hall.entity import datachangenotify, hallstore
from hall.entity.hallfanfanle import doFlipCard
from hall.entity.hallactivitygetgift import doGetGift
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.dao import userchip, daoconst

class TYActivityFanfanle(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_FANFANLE
    '''
        USERID_MAP = {"10034":"xxxxxxxx",
                      "10035:"xxxxxxxx"}
    '''
    global USERID_MAP
    USERID_MAP = {}
    # 处理客户端发送的  msg，在activity.py中调用
    def handleRequest(self, msg):
        ftlog.debug("TYActivityFanfanleINIT", caller=self)
        ftlog.debug("TYActivityFanfanleINIT", msg)
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')   
        clientId = msg.getParam("clientId")     
        activityId = msg.getParam("activityId")
        action = msg.getParam("action")
        if action == "activityflipcard":
            coin = msg.getParam('coin')   
            return self._doFlipcard(userId, gameId, clientId, activityId, coin)
        elif action == "activityflipcardMoney":
            ftlog.debug("activityflipcardMoney..begin", userId, gameId, clientId, activityId)
            return self._doGift(userId, gameId, clientId, activityId)
        elif action == "activityflipcardIsMoney":
            ftlog.debug("activityflipcardIsMoney..begin", userId, gameId, clientId, activityId)
            return self._doIsGift(userId, gameId, clientId, activityId)
        else:
            return {"errorInfo":"activityflipcard not found", "errorCode":3}
        
    def _doFlipcard(self, userId, gameId, clientId, activityId, coin):
        result = {}
        key = "TYActivity:%d:%d:%s:%s" % (gameId, userId, clientId, activityId)
        ftlog.debug("_doFlipcard key:", key)
        conf = {
                "design": {
                           "1": {
                                 "name": "豹子A",
                                 "payrate": 20,
                                 "probability": 0.0001
                                 },
                           "2": {
                                 "name": "豹子",
                                 "payrate": 20,
                                 "probability": 0.0012
                                 },
                           "3": {
                                 "name": "同花顺",
                                 "payrate": 15,
                                 "probability": 0.001
                                 },
                           "4": {
                                 "name": "同花",
                                 "payrate": 3,
                                 "probability": 0.01
                                 },
                           "5": {
                                 "name": "顺子",
                                 "payrate": 3,
                                 "probability": 0.01
                                 },
                           "6": {
                                 "name": "对子",
                                 "payrate": 1.5,
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
                }
        
        # 判断用户金币是否足够
        chipNow = userchip.getChip(userId)
        if coin == 1000 and chipNow < 5000 :
            payOrder = {
                        "shelves":["coin"],
                        "buyTypes":["direct"],
                        "priceDiamond":{
                                "count":20,
                                "minCount":0,
                                "maxCount":-1
                            }
                        }
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            payOrder = TodoTaskPayOrder(product)
            result["tip"] = payOrder.toDict()
            return result
        elif coin == 5000 and chipNow < 50000:
            
            payOrder = {
                        "shelves":["coin"],
                        "buyTypes":["direct"],
                        "priceDiamond":{
                                "count":80,
                                "minCount":0,
                                "maxCount":-1
                            }
                        }
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            payOrder = TodoTaskPayOrder(product)
            result["tip"] = payOrder.toDict()
            return result
        elif coin == 10000 and chipNow < 50000:
            payOrder = {
                        "shelves":["coin"],
                        "buyTypes":["direct"],
                        "priceDiamond":{
                                "count":80,
                                "minCount":0,
                                "maxCount":-1
                            }
                        }
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            payOrder = TodoTaskPayOrder(product)
            result["tip"] = payOrder.toDict()
            return result
        elif coin == 50000 and chipNow < 300000:
            payOrder = {
                        "shelves":["coin"],
                        "buyTypes":["direct"],
                        "priceDiamond":{
                                "count":300,
                                "minCount":0,
                                "maxCount":-1
                            }
                        }
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            payOrder = TodoTaskPayOrder(product)
            result["tip"] = payOrder.toDict()
            return result
        else :
            result = doFlipCard(conf)
            ftlog.debug("_doFlipcard result..cardtype:", result["cardtype"])
            # 减金币操作
            coinDel = 0 - coin
            userchip.incrChip(userId, gameId, coinDel, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'HALL_FLIPCARD', 0, clientId)
            datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
            ftlog.info("用户名，用户减少了金币,",userId,coinDel)
            if result["cardtype"] != '8' :
                design = conf.get('design', {})
                cardTypeNumber = design[result["cardtype"]].get('payrate', 0)
                
                # 加金币操作
                coinAdd = int(coin * cardTypeNumber)
                cardText = "恭喜你赢得了%d" % coinAdd + "金币"
                ftlog.debug("_doFlipcard get money:", cardText)
                userchip.incrChip(userId, gameId, coinAdd, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'HALL_FLIPCARD', 0, clientId)
                datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
                ftlog.info("用户名，用户增加了金币,",userId,coinAdd)
                result["todoTask"] = {"action": "pop_tip",
                                      "params": {
                                                 "text": cardText,
                                                 "duration": 2
                                                 }
                                  }
                return result
            else :
                cardText = "再接再厉，下次就会赢哦";
                result["todoTask"] = {"action": "pop_tip",
                                      "params": {
                                                 "text": cardText,
                                                 "duration": 2
                                                 }
                                  }
                ftlog.debug("_doFlipcard key over:", key)
                return result
        
        '''
            生成牌的类型，计算返回的倍数、并且返回
        '''  
        
    def _doGift(self, userId, gameId, clientId, activityId):
        '''
            获取上次领取红包的时间，判断时间间隔，是否可以领取红包
            判断是否有剩余红包
            没有红包，提示退出。有红包，发放
        ''' 
        ftlog.debug("activityflipcardMoney..begin..1")
        global USERID_MAP
        if userId in USERID_MAP :
            '''
                如果存在该用户的id，证明该用户领取过红包，进行时间的判断
               然后判断是否存在红包
               进行红包的领取或者消息的返回 
            '''
            ftlog.debug("activityflipcardMoney..begin..2")
            # 对时间进行划分
            if time.localtime().tm_mday == USERID_MAP[userId].tm_mday :
                # 同一天
                ftlog.debug("activityflipcardMoney..begin..2-1")
                timeDel = time.localtime().tm_hour - USERID_MAP[userId].tm_hour
                ftlog.debug("activityflipcardMoney..begin..2-2", USERID_MAP[userId].tm_hour)
                if USERID_MAP[userId].tm_hour > 12 and USERID_MAP[userId].tm_hour < 18:
                    ftlog.debug("activityflipcardMoney..begin..3..timeDel", timeDel)
                    if timeDel > 6 :
                        # 可以领取
                        USERID_MAP[userId] = time.localtime()
                        return self.user_to_get_gift(userId, gameId, clientId)
                    else :
                        # 您已领取过红包，请等待下次开启
                        return self.next_get_gift_time()
                elif USERID_MAP[userId].tm_hour > 18 and USERID_MAP[userId].tm_hour < 21:
                    ftlog.debug("activityflipcardMoney..begin..4")
                    if timeDel > 3 :
                        # 可以领取
                        USERID_MAP[userId] = time.localtime()
                        return self.user_to_get_gift(userId, gameId, clientId)
                    else :
                        # 您已领取过红包，请等待下次开启
                        return self.next_get_gift_time()
                elif USERID_MAP[userId].tm_hour > 21 and USERID_MAP[userId].tm_hour < 24:
                    ftlog.debug("activityflipcardMoney..begin..5")
                    if timeDel > 3 :
                        # 可以领取
                        USERID_MAP[userId] = time.localtime()
                        return self.user_to_get_gift(userId, gameId, clientId)
                    else :
                        # 您已领取过红包，请等待下次开启
                        return self.next_get_gift_time()
                elif USERID_MAP[userId].tm_hour > 0 and USERID_MAP[userId].tm_hour < 12 :
                    # 等待下次开启
                    return self.next_get_gift_time()
                else:
                    return self.next_get_gift_time()
            elif time.localtime().tm_mday == USERID_MAP[userId].tm_mday + 1 :
                ftlog.debug("activityflipcardMoney..begin..6")
                # 第二天
                timeDel = time.localtime().tm_hour - USERID_MAP[userId].tm_hour + 24
                if timeDel > 12 :
                    USERID_MAP[userId] = time.localtime()
                    return self.user_to_get_gift(userId, gameId, clientId)
                else :
                    return self.next_get_gift_time()
            else :
                ftlog.debug("activityflipcardMoney..begin..8")
                # 不是同一天
                USERID_MAP[userId] = time.localtime()
                return self.user_to_get_gift(userId, gameId, clientId)
                
        else:
            '''
                证明该用户尚未领取过红包
                判断是否还有红包
                进行红包的领取或者消息的返回
                领取成功，将用户加入到map中
            '''
            ftlog.debug("activityflipcardMoney..begin..9")
            USERID_MAP[userId] = time.localtime()
            ftlog.debug("activityflipcardMoney..begin..10", USERID_MAP[userId])
            return self.user_to_get_gift(userId, gameId, clientId)   
    def _doIsGift(self,userId, gameId, clientId, activityId):
        global USERID_MAP
        if userId in USERID_MAP :
            return self.next_get_gift_time()
        else:
            result = {}
            result["isOk"] = 1
            return result
    def user_to_get_gift(self, userId, gameId, clientId):
        
        '''
            领红包
        '''
        ftlog.debug("user_to_get_gift..begin")
        return doGetGift(userId, gameId, clientId)   
    def next_get_gift_time(self):
        '''
            处理红包的逻辑、返回下次开奖时间
        '''
        ftlog.debug("next_get_gift_time..begin")
        result = {}
        # 当前时间获取、返回距离开奖还有多长时间
        now_hour = time.localtime().tm_hour
        start_ts = [12, 18, 21, 24]
        totalFloat = 0
        for key in start_ts :
            if key > now_hour :
                if key == 24 :
                    totalFloat = key - now_hour
                    now_hour = 00
                    break
                else :
                    totalFloat = key - now_hour
                    now_hour = key
                    break
        ftlog.debug("activityflipcardMoneyTime", totalFloat)
        now_min = time.localtime().tm_min
        tempTime = datetime.now() + timedelta(hours=totalFloat) - timedelta(minutes=now_min)
        result["nextGiftTime"] = time.mktime(tempTime.timetuple())
        if totalFloat <= 0 :
            # 不足一小时
            tipText = "距离红包发放不足1小时，等待一下吧"
        else :
            # 超过一小时
            tipText = "距离红包发放还有%d" % totalFloat + "小时，赶紧玩翻翻乐吧"   
        result["tip"] = {
                             "action": "pop_tip",
                                "params": {
                                    "text": tipText,
                                    "duration": 2
                                }
                             }
        return result
