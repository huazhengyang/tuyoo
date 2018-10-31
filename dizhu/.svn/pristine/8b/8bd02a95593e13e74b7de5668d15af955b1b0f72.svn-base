# -*- coding:utf-8 -*-
'''
Created on 2016年7月5日

@author: zhaojiangang
'''
import unittest

from biz import mock
from dizhu.activitynew import activitysystemnew
from dizhu.activitynew.buy_send_prize import SendPrizeStatus
from entity.hallstore_test import products_conf
from hall.entity import hallitem, hallstore
from poker.entity.biz.store.store import TYChargeInfo
from poker.entity.dao import userdata
from test_base import HallTestMockContext
from poker.util import strutil


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
        }
    ]
}

activity_new_conf = {
    "activities":[
        {
            "actId":"act1",
            "typeId":"ddz.act.buy_send_prize",
            "intActId":6010,
            "limitCount":1,
            "limitTimeCycle":{
                "typeId":"life",
            },
            "prizes":[
                {
                    "payOrder":{
                        "productId":"T50K"
                    },
                    "content":{
                        "typeId": "FixedContent",
                        "items": [
                            {
                                "itemId": "user:chip",
                                "count": 50000
                            }
                        ]
                    }
                },
                {
                    "payOrder":{
                        "productId":"T60K"
                    },
                    "content":{
                        "typeId": "FixedContent",
                        "items": [
                            {
                                "itemId": "user:chip",
                                "count": 50000
                            }
                        ]
                    }
                }
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

class TestBuySendGift(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.70_360.360.0-hall6.360.day'
    testContext = HallTestMockContext()
    productId = 'T50K'
    
    def setUp(self):
        self.testContext.startMock()
        self.buy_send_prize_mock = mock._patch_multiple('dizhu.activitynew.buy_send_prize',
                                                    loadStatus=loadStatus,
                                                    saveStatus=saveStatus)
        self.buy_send_prize_mock.start()
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
        self.buy_send_prize_mock.stop()
        
    def testOrderDelivery(self):
        orderId = 'GO00001'
        order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
        orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
                                                                  TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
        
        
        orderId = 'GO00002'
        order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
        orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
                                                                  TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
         
        orderId = 'GO00003'
        order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
        orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
                                                                  TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
        
if __name__ == '__main__':
    unittest.main()
