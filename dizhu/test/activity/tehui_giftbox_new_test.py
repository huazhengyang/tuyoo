# -*- coding:utf-8 -*-
'''
Created on 2016年7月5日

@author: zhaojiangang
'''
import time
import unittest

from biz import mock
from dizhu.activitynew import activitysystemnew
from dizhu.activitynew.buy_send_prize import SendPrizeStatus
from entity.hallstore_test import products_conf
from hall.entity import hallitem, hallstore
from hall.game import TGHall
from poker.entity.biz.store.store import TYChargeInfo
from poker.entity.dao import userdata
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.util import strutil
from test_base import HallTestMockContext


item_conf = {
    'assets':[
        {
            "kindId":"user:chip",
            "typeId":"common.chip",
            "displayName":"金币",
            "pic":"http://chip.png",
            "desc":"金币",
            "units":"个",
            "keyForChangeNotify":"chip"
        },
        {
            "kindId":"user:coupon",
            "typeId":"common.coupon",
            "displayName":"奖券",
            "pic":"http://chip.png",
            "desc":"奖券",
            "units":"张",
            "keyForChangeNotify":"coupon"
        },
        {
            "kindId":"game:assistance",
            "typeId":"common.assistance",
            "displayName":"江湖救急",
            "pic":"http://chip.png",
            "desc":"江湖救急",
            "units":"次",
            "keyForChangeNotify":"gdata"
        },
    ],
    'items':[
        {
            "kindId":1,
            "typeId":"common.simple",
            "displayName":"测试道具1",
            "visibleInBag":1,
            "desc":"desc1",
            "singleMode":1,
            "pic":"http://pic.png",
            "units":{"typeId":"common.count", "displayName":"个"},
            "removeFromBagWhenRemainingZero":1,
            "removeFromBagWhenExpires":0,
        },
             {
            "kindId":89,
            "typeId":"common.simple",
            "displayName":"测试道具1",
            "visibleInBag":1,
            "desc":"desc1",
            "singleMode":1,
            "pic":"http://pic.png",
            "units":{"typeId":"common.count", "displayName":"个"},
            "removeFromBagWhenRemainingZero":1,
            "removeFromBagWhenExpires":0,
        },
        {
            "kindId": 1001,
            "typeId": "common.box",
            "displayName": "新手礼包",
            "visibleInBag": 1,
            "desc": "新手上路 微微薄礼，请您笑纳~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1001.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得\\${gotContent}",
                    "message": "您开启了\\${item}，获得\\${gotContent}",
                    "contents": [
                        {
                            "typeId": "FixedContent",
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "count": 100
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 4347,
            "typeId": "common.simple",
            "displayName": "初级特惠礼包",
            "visibleInBag": 1,
            "desc": "单笔充值30元以上，可得20万金币",
            "singleMode": 0,
            "pic": "${http_download}/hall/item/imgs/item_4347.png",
            "units": {
                "typeId": "common.count.nday",
                "displayName": "个",
                "nday":3
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1
        },
        {
            "kindId": 4348,
            "typeId": "common.simple",
            "displayName": "中级特惠礼包",
            "visibleInBag": 1,
            "desc": "单笔充值100元以上，可得50万金币",
            "singleMode": 0,
            "pic": "${http_download}/hall/item/imgs/item_4348.png",
            "units": {
                "typeId": "common.count.nday",
                "displayName": "个",
                "nday":3
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1
        },
        {
            "kindId": 4349,
            "typeId": "common.simple",
            "displayName": "高级特惠礼包",
            "visibleInBag": 1,
            "desc": "单笔充值300元以上，可得100万金币",
            "singleMode": 0,
            "pic": "${http_download}/hall/item/imgs/item_4349.png",
            "units": {
                "typeId": "common.count.nday",
                "displayName": "个",
                "nday":3
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1
        }
    ]
}

activity_new_conf = {
    "activities":[
        {
            "actId":"act2",
            "typeId":"ddz.act.tuihuigift_new",
            "intActId":60003,
            "startTime":"2016-07-12 00:00:00",
            "endTime":"2016-07-25 00:00:00",
            "mail":"恭喜您获得\\${rewardContent}特惠礼包奖励！",
            "gifts": [
                {"itemId":"item:4347", "rmb":30, "reward":{"itemId":"user:chip", "count":200000, "desc":"20万金币"} },
                {"itemId":"item:4348", "rmb":100, "reward":{"itemId":"user:chip", "count":500000, "desc":"50万金币"} },
                {"itemId":"item:4349", "rmb":300, "reward":{"itemId":"user:chip", "count":1000000, "desc":"100万金币"} }
            ]
        }
    ]
}

store_template_conf = {
    "templates":[
        {
            "name"                  : "default",
            "shelves"               : [
                {
                    "displayName"           : "购买金币",
                    "iconType"              : "coin",
                    "name"                  : "coin",
                    "products"              : [
                        "T50K"
                    ],
                    "sort"                  : 0,
                    "visible"               : 1
                }
            ]
        }
    ],
    "lastBuy":{
        "desc":"您上次购买的商品是\\${displayName}，是否依然购买此商品？",
        "subText":"是",
        "subTextExt":"逛逛商城"
    }
}

store_vc_conf = {
    "default":"default",
    "default_ios":"default",
    "default_android":"default"
}

clientIdMap = {
    "IOS_3.6_momo":1,
    "IOS_3.70_360.360.0-hall6.360.day":13232
}

conf = {}

# def loadUserQuizStatus(actId, userId):
#     jstr = userdata.getAttr(userId, 'act:%s' % (actId))
#     if not jstr:
#         return None
#     d = strutil.loads(jstr)
#     return UserQuizStatus(userId).fromDict(d)
#     
# def saveUserQuizStatus(actId, status):
#     d = status.toDict()
#     jstr = strutil.dumps(d)
#     userdata.setAttr(status.userId, 'act:%s' % (actId), jstr)
#     
def loadStatus(userId, actId):
    jstr = userdata.getAttr(userId, 'act:%s' % (actId))
    if jstr:
        d = strutil.loads(jstr)
        return SendPrizeStatus(userId).fromDict(d)
    return None 

def saveStatus(actId, status):
    d = status.toDict()
    jstr = strutil.dumps(d)
    userdata.setAttr(status.userId, 'act:%s' % (actId), jstr)

class TestTehuiGiftboxNew(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.70_360.360.0-hall6.360.day'
    testContext = HallTestMockContext()
    productId = 'T50K'
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('poker:global', {'config.game.ids':[6,9999]}, None)
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('poker:map.clientid', clientIdMap, None)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:6:store:tc', store_template_conf, None)
        self.testContext.configure.setJson('game:6:store:vc', store_vc_conf, None)
        self.testContext.configure.setJson('game:6:activity.new', activity_new_conf, 0)
        
        hallitem._initialize()
        hallstore._initialize()
        activitysystemnew._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testOrderDelivery(self):
        userdata.setAttr(self.userId, 'chip', 100)
        TGHall.getEventBus().publishEvent(ChargeNotifyEvent(self.userId, self.gameId, 10, 100, 'T50K', self.clientId))
        self.assertEqual(userdata.getAttr(self.userId, 'chip'), 100)
        
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userAssets.addAsset(self.gameId, 'item:4347', 1, int(time.time()), 'TEST', 0)
        
        TGHall.getEventBus().publishEvent(ChargeNotifyEvent(self.userId, self.gameId, 10, 100, 'T50K', self.clientId))
        self.assertEqual(userdata.getAttr(self.userId, 'chip'), 100)
        
        TGHall.getEventBus().publishEvent(ChargeNotifyEvent(self.userId, self.gameId, 30, 100, 'T50K', self.clientId))
        self.assertEqual(userdata.getAttr(self.userId, 'chip'), 200000+100)
        print userdata.getAttr(self.userId, 'chip')
#         orderId = 'GO00001'
#         order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
#         orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
#                                                                   TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
#         
#         
#         orderId = 'GO00002'
#         order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
#         orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
#                                                                   TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
#          
#         orderId = 'GO00003'
#         order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
#         orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
#                                                                   TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
#         
if __name__ == '__main__':
    unittest.main()
