# -*- coding:utf-8 -*-
'''
Created on 2016年7月5日

@author: zhaojiangang
'''
import time
import unittest

from biz import mock
from dizhu.activitynew import activitysystemnew
from dizhu.entity import dizhutask
from dizhu.game import TGDizhu
from dizhu.gamecards.dizhu_rule import CardDiZhuLaizi3Player
from dizhu.gameplays.game_events import UserTableWinloseEvent, Winlose
from entity.hallstore_test import products_conf
from hall.entity import hallitem, hallstore, halltask
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.store.store import TYChargeInfo
from poker.entity.dao import userdata
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
            "gameId":9999,
            "catagoryDesc":"道具",
            "catagoryId":1,
            "sortId":1,
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
            "sortId":89,
            "gameId":9999,
            "catagoryId":1,
            "catagoryDesc":"道具",
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
            "sortId":1001,
            "gameId":9999,
            "catagoryId":1,
            "catagoryDesc":"道具",
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
            "typeId":"ddz.act.quweitask",
            "intActId":6018,
            "taskCount":4,
            "refreshFee":{
                "itemId":"user:chip",
                "count":100
            },
            "gameId":6,
            "initPools":[
                {
                    "kindIds":[5001, 5002, 5003, 5004]
                }
            ],
            "tasks":[
                {
                    "kindId":5001,
                    "typeId":"ddz.qwtask.simple",
                    "name":"春天",
                    "desc":"春天或反春取胜",
                    "count":1,
                    "totalLimit":1,
                    "pic":"",
                    "inspector":{
                        "typeId":"ddz.win",
                        "conditions":[
                            {"typeId":"ddz.cond.chuntian"}
                        ]
                    },
                    "rewardContent":{
                        "typeId":"FixedContent",
                        "items":[
                            {"itemId":"item:1001", "count":5}
                        ]
                    },
                    "rewardMail":"趣味任务奖励：\\${rewardContent}"
                },
                {
                    "kindId":5002,
                    "typeId":"ddz.qwtask.simple",
                    "name":"3连胜",
                    "desc":"3连胜",
                    "count":1,
                    "totalLimit":1,
                    "pic":"",
                    "inspector":{
                        "typeId":"ddz.winStreak",
                        "conditions":[
                        ]
                    },
                    "rewardContent":{
                        "typeId":"FixedContent",
                        "items":[
                            {"itemId":"item:1001", "count":5}
                        ]
                    },
                    "rewardMail":"趣味任务奖励：\\${rewardContent}"
                },
                {
                    "kindId":5003,
                    "typeId":"ddz.qwtask.simple",
                    "name":"32倍胜利3局",
                    "desc":"32倍胜利3局",
                    "count":1,
                    "totalLimit":1,
                    "pic":"",
                    "inspector":{
                        "typeId":"ddz.win",
                        "conditions":[
                            {
                                "typeId": "ddz.cond.windoubles",
                                "stop": -1,
                                "start": 32
                            }
                        ]
                    },
                    "rewardContent":{
                        "typeId":"FixedContent",
                        "items":[
                            {"itemId":"item:1001", "count":5}
                        ]
                    },
                    "rewardMail":"趣味任务奖励：\\${rewardContent}"
                },
                {
                    "kindId":5004,
                    "typeId":"ddz.qwtask.simple",
                    "name":"中级场玩3局",
                    "desc":"中级场玩3局",
                    "count":1,
                    "totalLimit":1,
                    "pic":"",
                    "inspector":{
                        "typeId": "ddz.play",
                        "conditions": [
                            {
                                "typeId": "ddz.cond.roomId",
                                "roomIds": [
                                    6001
                                ]
                            }
                        ]
                    },
                    "rewardContent":{
                        "typeId":"FixedContent",
                        "items":[
                            {"itemId":"item:1001", "count":5}
                        ]
                    },
                    "rewardMail":"趣味任务奖励：\\${rewardContent}"
                },
                {
                    "kindId":5005,
                    "typeId":"ddz.qwtask.simple",
                    "name":"累计充值30",
                    "desc":"累计充值30",
                    "count":30,
                    "totalLimit":1,
                    "pic":"",
                    "inspector":{
                        "typeId":"hall.charge.cumulation",
                        "conditions":[
                        ]
                    },
                    "rewardContent":{
                        "typeId":"FixedContent",
                        "items":[
                            {"itemId":"item:1001", "count":5}
                        ]
                    },
                    "rewardMail":"趣味任务奖励：\\${rewardContent}"
                },
                {
                    "kindId":5006,
                    "typeId":"ddz.qwtask.simple",
                    "name":"单笔充值50",
                    "desc":"单笔充值50",
                    "count":50,
                    "totalLimit":1,
                    "pic":"",
                    "inspector":{
                        "typeId":"hall.charge.single",
                        "conditions":[
                        ]
                    },
                    "rewardContent":{
                        "typeId":"FixedContent",
                        "items":[
                            {"itemId":"item:1001", "count":5}
                        ]
                    },
                    "rewardMail":"趣味任务奖励：\\${rewardContent}"
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

def loadStatusData(gameId, userId, actId):
    return userdata.getAttr(userId,'act:%s' % (actId))

def saveStatusData(gameId, userId, actId, data):
    userdata.setAttr(userId, 'act:%s' % (actId), data)

class TestBuySendGift(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.70_360.360.0-hall6.360.day'
    testContext = HallTestMockContext()
    productId = 'T50K'
    
    dizhutask._registerClasses()
    halltask._registerClasses()
    
    def setUp(self):
        self.testContext.startMock()
        self.buy_send_prize_mock = mock._patch_multiple('dizhu.activitynew.quweitask',
                                                    loadStatusData=loadStatusData,
                                                    saveStatusData=saveStatusData)
        self.buy_send_prize_mock.start()
        self.testContext.configure.setJson('poker:global', {'config.game.ids':[6,9999]}, None)
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('poker:map.clientid', clientIdMap, None)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:6:store:tc', store_template_conf, None)
        self.testContext.configure.setJson('game:6:store:vc', store_vc_conf, None)
        self.testContext.configure.setJson('game:6:activity.new', activity_new_conf, 0)

        self.testContext.gdataTest.setGame(TGDizhu)
        
        hallitem._initialize()
        hallstore._initialize()
        activitysystemnew._initialize()
   
    def tearDown(self):
        self.testContext.stopMock()
        self.buy_send_prize_mock.stop()
        
    def testEvent(self):
#         winlose = Winlose(winuserid, topValidCard, isWin, isDizhu, seat_delta, findChips,
#                       windoubles, bomb, chuntian > 1, winslam)
        timestamp = int(time.time())
        cardRule = CardDiZhuLaizi3Player()
        winCard = cardRule.validateCards([0])
        event = UserTableWinloseEvent(self.gameId, self.userId, 6001, 600101, Winlose(self.userId, winCard, 1, 1, 100, 100, 1, 1, 2, 1))
        TGDizhu.getEventBus().publishEvent(event)
        
        act = activitysystemnew.findActivity('act1')
        status = act.loadStatus(self.userId, int(time.time()))
        act.gainReward(status, 5001, timestamp)
        
        self.assertRaises(TYBizException, act.refresh, status, timestamp)
        
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userAssets.addAsset(self.gameId, 'user:chip', 1000, timestamp, 'TEST', 0)
        act.refresh(status, timestamp)
        
if __name__ == '__main__':
    unittest.main()
