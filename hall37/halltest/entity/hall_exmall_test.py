# -*- coding:utf-8 -*-
'''
Created on 2017年7月15日

@author: zhaojiangang
'''

from datetime import datetime
import time
import traceback
import unittest

from redis.client import StrictRedis

from biz import mock
from biz.mock import patch
from entity.hallstore_test import clientIdMap, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import hallitem, hall_exmall, hallvip
from hall.entity.hall_exmall import Exchange, TimeCycleRegister
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.exmall_handler import HallExMallHandler
from poker.entity.configure import gdata
from poker.entity.dao import daobase, userdata
from poker.util import timestamp as pktimestamp
from test_base import HallTestMockContext


item_conf = {
 "assets"                        : [
  {
   "desc"                          : "金币",
   "kindId"                        : "user:chip",
   "pic"                           : "${http_download}/hall/pdt/imgs/goods_t300k_2.png",
   "displayName"                   : "金币",
   "typeId"                        : "common.chip",
   "units"                         : "个",
   "keyForChangeNotify"            : "chip"
  },
  {
   "desc"                          : "奖券",
   "kindId"                        : "user:coupon",
   "pic"                           : "${http_download}/hall/item/imgs/coupon.png",
   "displayName"                   : "奖券",
   "typeId"                        : "common.coupon",
   "units"                         : "张",
   "keyForChangeNotify"            : "coupon"
  },
  {
   "desc"                          : "经验值",
   "kindId"                        : "user:exp",
   "pic"                           : "${http_download}/hall/item/imgs/coupon.png",
   "displayName"                   : "经验值",
   "typeId"                        : "common.exp",
   "units"                         : "分",
   "keyForChangeNotify"            : "exp"
  },
  {
   "desc"                          : "魅力值",
   "kindId"                        : "user:charm",
   "pic"                           : "${http_download}/hall/item/imgs/meilizhi.png",
   "displayName"                   : "魅力值",
   "typeId"                        : "common.charm",
   "units"                         : "分",
   "keyForChangeNotify"            : "charm"
  },
  {
   "desc"                          : "江湖救急",
   "kindId"                        : "game:assistance",
   "pic"                           : "",
   "displayName"                   : "江湖救急",
   "typeId"                        : "common.assistance",
   "units"                         : "次",
   "keyForChangeNotify"            : "gdata"
  },
  {
   "desc"                          : "会员订阅服务",
   "kindId"                        : "game:subMember",
   "pic"                           : "",
   "displayName"                   : "会员订阅服务",
   "typeId"                        : "common.subMember",
   "units"                         : "",
   "keyForChangeNotify"            : "item"
  },
  {
   "desc"                          : "钻石",
   "kindId"                        : "user:diamond",
   "pic"                           : "${http_download}/hall/store/imgs/diamond.png",
   "displayName"                   : "钻石",
   "typeId"                        : "common.diamond",
   "units"                         : "颗",
   "keyForChangeNotify"            : "diamond"
  },
  {
   "desc"                          : "现金",
   "kindId"                        : "user:cash",
   "pic"                           : "${http_download}/hall/item/imgs/xianjin_erdayi_reward.png",
   "displayName"                   : "现金",
   "typeId"                        : "common.cash",
   "units"                         : "元",
   "keyForChangeNotify"            : "diamond"
  }
 ],
 "exchangeGdssUrl"               : "http://gdss.touch4.me/?act=api.propExchange",
}

hall_exmall_conf = {
    "exchanges":[
        {
            "exchangeId":"10001",
            "displayName":"100万金币",
            "pic":"${http_download}/hall/roulette/hall_roulette_coin.png",
            "desc":"商品描述",
            "cost":{
                "itemId":"user:chip",
                "count":1123456,
                "original":852278212,
                "name":"金币"
            },
            "delivery":{
                "typeId":"ty.delivery:ty",
                "items":[
                    {
                        "itemId":"user:chip",
                        "count":1000000
                    }
                ]
            },
            "displayTimePeriod":{
                "start":"2017-07-20 07:00:00",
                "stop":"2017-07-21 16:00:00"
            },
            "exchangeTimePeriod":{
                "start":"2017-07-21 22:00:00",
                "stop":"2017-07-24 21:00:00"
            },
            "stock":{
                "cycle":{
                    "typeId":"timeCycle.minutes",
                    "minutes":10,
                    "timePeriod":{
                        "start":"2017-07-19 07:00:00",
                        "stop":"2017-07-21 08:00:00"
                    }
                },
                "count":6
            },
            "tagMark":"new"
        },
        {
            "exchangeId":"10002",
            "displayName":"1元话费",
            "pic":"${http_download}/hall/item/imgs/item_phoneCard_39.png",
            "desc":"商品描述",
            "cost":{
                "itemId":"user:coupon",
                "count":2000,
                "original":3000,
                "name":"奖券"
            },
            "delivery":{
                "typeId":"ty.delivery:gdss",
                "auditParams":{
                    "type":0,
                    "desc":"1元话费",
                    "count":1
                },
                "clientParams":{
                    "bindPhone":1,
                    "desc":"请填写您的有效电话号码",
                    "needAddress":0,
                    "type":"phoneNumber",
                    "confirm":1
                }
            },
            "displayTimePeriod":{
                "start":"2017-07-20 07:00:00",
                "stop":"2017-07-21 23:00:00"
            },
            "exchangeTimePeriod":{
                "start":"2017-07-20 07:00:00",
                "stop":"2017-07-25 21:00:00"
            },
            "stock":{
                "cycle":{
                    "typeId":"timeCycle.minutes",
                    "minutes":10,
                    "timePeriod":{
                        "start":"2017-07-19 07:00:00",
                        "stop":"2017-07-21 08:00:00"
                    }
                },
                "count":3,
                "displayStockLimit":2
            },
            "exchangeCountLimit":{
                "cycle":{
                    "typeId":"timeCycle.minutes",
                    "minutes":5,
                    "timePeriod":{
                        "start":"2017-07-19 07:00:00",
                        "stop":"2017-07-21 08:00:00"
                    }
                },
                "failure":"抱歉，您的兑换次数不足！",
                "count":1,
                "visibleInStore":1
            },
            "vipLimit":1,
            "exchangeConditions":[
                {
                    "failure":"vip1以上可兑换！",
                    "visibleInStore":1,
                    "condition":{
                        "startLevel":1,
                        "stopLevel":-1,
                        "typeId":"user.cond.vipLevel"
                    }
                }
            ],
            "tagMark":"new"
        },
        {
            "exchangeId":"10003",
            "displayName":"10元京东卡",
            "pic":"${http_download}/hall/item/imgs/item_4230_39_1.png",
            "desc":"10元京东卡",
            "cost":{
                "itemId":"user:coupon",
                "count":3000,
                "original":4000,
                "name":"奖券"
            },
            "delivery":{
                "typeId":"ty.delivery:gdss",
                "auditParams":{
                    "type":3,
                    "desc":"10元京东卡",
                    "count":10
                },
                "clientParams":{
                    "bindPhone":1,
                    "desc":"请填写您的有效电话号码",
                    "needAddress":0,
                    "type":"phoneNumber",
                    "confirm":1
                }
            },
            "displayTimePeriod":{
                "start":"2017-07-20 07:00:00",
                "stop":"2017-07-21 16:00:00"
            },
            "exchangeTimePeriod":{
                "start":"2017-07-21 14:00:00",
                "stop":"2017-07-21 21:00:00"
            },
            "stock":{
                "cycle":{
                    "typeId":"timeCycle.minutes",
                    "minutes":5,
                    "timePeriod":{
                        "start":"2017-07-19 07:00:00",
                        "stop":"2017-07-21 08:00:00"
                    }
                },
                "count":4,
                "displayStockLimit":3
                
            },
            "exchangeCountLimit":{
                "cycle":{
                    "typeId":"timeCycle.life"
                },
                "failure":"抱歉，您的兑换次数不足！",
                "count":1,
                "visibleInStore":0
            },
            "vipLimit":1,
            "exchangeConditions":[
                {
                    "failure":"vip1以上可兑换",
                    "visibleInStore":0,
                    "condition":{
                        "startLevel":1,
                        "stopLevel":-1,
                        "typeId":"user.cond.vipLevel"
                    }
                }
            ],
            "tagMark":"new"
        },
        {
            "exchangeId":"10004",
            "displayName":"TUPT西安站线下决赛邀请函",
            "pic":"${http_download}/hall/item/imgs/item_2135.png",
            "desc":"TUPT西安站线下决赛邀请函",
            "cost":{
                "itemId":"user:coupon",
                "count":45678901,
                "name":"奖券"
            },
            "delivery":{
                "typeId":"ty.delivery:ty",
                "items":[
                    {
                        "itemId":"item:2137",
                        "count":1
                    }
                ]
            },
            "displayTimePeriod":{
                "start":"2017-07-20 07:00:00",
                "stop":"2017-07-21 16:00:00"
            }
        },
        {
            "exchangeId":"10005",
            "displayName":"10元微信红包",
            "pic":"${http_download}/hall/item/imgs/item_weChat_packet_39.png",
            "desc":"10元微信红包",
            "cost":{
                "itemId":"user:coupon",
                "count":5000,
                "original":3000,
                "name":"奖券"
            },
            "delivery":{
                "typeId":"ty.delivery:gdss",
                "auditParams":{
                    "type":5,
                    "desc":"10元微信红包",
                    "count":10
                },
                "clientParams":{
                    "bindPhone":1,
                    "desc":"请填写您的有效电话号码",
                    "needAddress":0,
                    "type":"phoneNumber",
                    "confirm":1
                }
            },
            "tagMark":"hot"
        },
        {
            "exchangeId":"10006",
            "displayName":"益达无糖口香糖",
            "pic":"http://img13.360buyimg.com/n2/jfs/t2689/10/4226899160/314552/e94acdda/57b27230N22c42f00.jpg",
            "desc":"【京东超市】益达（Extra）木糖醇无糖口香糖混合味70粒98g单瓶装（新旧包装随机发）",
            "cost":{
                "itemId":"user:coupon",
                "count":6000
            },
            "delivery":{
                "typeId":"ty.delivery:gdss",
                "auditParams":{
                    "type":6,
                    "desc":"益达无糖口香糖",
                    "count":1,
                    "jdProductId":"1798191"
                },
                "clientParams":{
                    "bindPhone":0,
                    "desc":"请填写您的有效电话号码",
                    "needAddress":1,
                    "type":"address",
                    "confirm":1
                }
            },
            "tagMark":"hot"
        }
    ]
}

hall_exmall_tc = {
    "templates": {
        "default":{
            "shelves": [
                {
                    "displayName": "热门兑换",
                    "name": "hot",
                    "products": [
                        "10001",
                        "10002"
                    ],
                    "sort": 12,
                    "visible": 1,
                    "visibleCondition": {
                        "startLevel": 0,
                        "stopLevel":-1,
                        "typeId": "user.cond.vipLevel"
                    }
                },
                {
                    "displayName": "米面粮油",
                    "name": "mimian",
                    "products": [
                        "10001",
                        "10002"
                    ],
                    "sort": 12,
                    "visible": 0,
                    "visibleCondition": {
                        "startLevel": 0,
                        "stopLevel":-1,
                        "typeId": "user.cond.vipLevel"
                    }
                }
            ]
        }
    }
}

hall_exmall_vc = {
    "actual" : {
    },
    "default": "default"
}

class TestHallExMall(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.70_360.360.0-hall6.360.day'
    testContext = HallTestMockContext()
    
    def getCurrentTimestamp(self):
        return self.timestamp
    
    def runRedisCmd(self, *cmds):
        return self.redisClient.execute_command(*cmds)
    
    def runUserRedisCmd(self, userId, *cmds):
        return self.redisClient.execute_command(*cmds)
    
    def getStock(self, exchangeId):
        '''
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        return hall_exmall.getStock(exchangeId, timestamp).stock
    
    def lockStock(self, exchangeId, count):
        timestamp = pktimestamp.getCurrentTimestamp()
        count, balance = hall_exmall.lockStock(exchangeId, count, timestamp)
        return True, balance, timestamp
    
    def backStock(self, exchangeId, count, stockTimestamp):
        '''
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        hall_exmall.backStock(exchangeId, count, stockTimestamp, timestamp)
            
    def setUp(self):
        self.testContext.startMock()
        self.redisClient = StrictRedis('127.0.0.1', 6379, 0)
        
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.pktimestampPatcher = patch('poker.util.timestamp.getCurrentTimestamp', self.getCurrentTimestamp)
        self.pktimestampPatcher.start()
        
        self.stockRemotePatcher = mock._patch_multiple('hall.servers.center.rpc.stock_remote',
                                                       getStock=self.getStock,
                                                       lockStock=self.lockStock,
                                                       backStock=self.backStock)
        self.stockRemotePatcher.start()
        
        daobase.executeMixCmd = self.runRedisCmd
        daobase._executePayDataCmd = self.runRedisCmd
        daobase.executeUserCmd = self.runUserRedisCmd
        
        self.runRedisCmd('flushdb')
        
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('poker:map.clientid', clientIdMap, None)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:exmall', hall_exmall_conf, 0)
        self.testContext.configure.setJson('game:6:exmall:tc', hall_exmall_tc, None)
        self.testContext.configure.setJson('game:6:exmall:vc', hall_exmall_vc, None)
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        
        self.timestamp = pktimestamp.getCurrentTimestamp()
        
        gdata._datas['server_type'] = gdata.SRV_TYPE_CENTER
        
        hallitem._initialize()
        hallvip._initialize()
        hall_exmall._initialize()

        userdata.setAttrs(10001, {'name':'user10001', 'purl':'purl10001', 'coupon':100000})

    def tearDown(self):
        self.testContext.stopMock()
        self.stockRemotePatcher.stop()
        self.pktimestampPatcher.stop()
    
    def _matchTimePeriod(self, timePeriodObj, timePeriodD):
        if not timePeriodD:
            self.assertIsNone(timePeriodObj)
        else:
            self.assertIsNotNone(timePeriodObj)
            start = timePeriodD.get('start')
            if start:
                self.assertEqual(timePeriodObj.startDT.strftime('%Y-%m-%d %H:%M:%S'), start)
            else:
                self.assertIsNone(timePeriodObj.startDT)
            
            stop = timePeriodD.get('stop')
            if stop:
                self.assertEqual(timePeriodObj.stopDT.strftime('%Y-%m-%d %H:%M:%S'), stop)
            else:
                self.assertIsNone(timePeriodObj.stopDT)
    
    def _matchTimeCycle(self, timeCycleObj, timeCycleD):
        self.assertEqual(timeCycleObj.TYPE_ID, timeCycleD.get('typeId'))
            
    def _matchStock(self, stockObj, stockD):
        if not stockD:
            self.assertIsNone(stockObj)
        else:
            self.assertIsNotNone(stockObj)
            self.assertEqual(stockObj.count, stockD.get('count'))
            self.assertEqual(stockObj.displayStockLimit, stockD.get('displayStockLimit', -1))
            self._matchTimeCycle(stockObj.timeCycle, stockD.get('cycle'))
    
    def _matchExchangeCountLimit(self, exchangeCountLimitObj, exchangeCountLimitD):
        if not exchangeCountLimitD:
            self.assertIsNone(exchangeCountLimitObj)
        else:
            self.assertIsNotNone(exchangeCountLimitObj)
            self.assertEqual(exchangeCountLimitObj.count, exchangeCountLimitD.get('count'))
            self.assertEqual(exchangeCountLimitObj.visibleInStore, exchangeCountLimitD.get('visibleInStore', 1))
            self.assertEqual(exchangeCountLimitObj.failure, exchangeCountLimitD.get('failure', ''))
            self._matchTimeCycle(exchangeCountLimitObj.timeCycle, exchangeCountLimitD.get('cycle'))
    
    def _matchDelivery(self, deliveryObj, deliveryD):
        if not deliveryD:
            self.assertIsNone(deliveryObj)
        else:
            self.assertIsNotNone(deliveryObj)
#     
#     def testDecode(self):
#         for exchangeD in hall_exmall_conf['exchanges']:
#             exchange = Exchange().decodeFromDict(exchangeD)
#             self.assertEqual(exchange.exchangeId, exchangeD.get('exchangeId'))
#             self.assertEqual(exchange.displayName, exchangeD.get('displayName'))
#             self.assertEqual(exchange.desc, exchangeD.get('desc', ''))
#             self.assertEqual(exchange.shippingMethod, exchangeD.get('shippingMethod'))
#             # cost
#             self.assertEqual(exchange.cost.itemId, exchangeD.get('cost').get('itemId'))
#             self.assertEqual(exchange.cost.count, exchangeD.get('cost').get('count'))
#             self.assertEqual(exchange.cost.original, exchangeD.get('cost').get('original'))
#             self.assertEqual(exchange.cost.name, exchangeD.get('cost').get('name'))
#             
#             # delivery
#             self._matchDelivery(exchange.delivery, exchangeD.get('delivery'))
#             
#             # displayTimePeriod
#             self._matchTimePeriod(exchange.displayTimePeriod, exchangeD.get('displayTimePeriod'))
#             self._matchTimePeriod(exchange.exchangeTimePeriod, exchangeD.get('exchangeTimePeriod'))
#             
#             self._matchStock(exchange.stock, exchangeD.get('stock'))
#             self._matchExchangeCountLimit(exchange.exchangeCountLimit, exchangeD.get('exchangeCountLimit'))
#     
#     def testGetShelves(self):
#         shelves = hall_exmall.getShelvesList(10001, self.clientId, self.timestamp)
#         print shelves
#     
#     def testHandler(self):
#         mo = HallExMallHandler._doGetShelves(HALL_GAMEID, self.userId, self.clientId)
#         shelvesList = mo.getResult('list', [])
#         print 'shelvesList=', shelvesList
#         for shelves in shelvesList:
#             mo = HallExMallHandler._doGetProduct(HALL_GAMEID, self.userId, self.clientId, shelves['name'], self.timestamp)
#             print '******', mo.pack()
#             for p in mo.getResult('list'):
#                 print p['exchangeId']
# #         HallExMallHandler._doExchange(HALL_GAMEID, self.userId, self.clientId, '10001', 1, {})
# #         HallExMallHandler._doExchange(HALL_GAMEID, self.userId, self.clientId, '10001', 1, {})
# #     
#     def testStockTime(self):
#         c = {
#              "exchanges":[
#         {
#             "exchangeId":"10001",
#             "displayName":"100万金币",
#             "pic":"${http_download}/hall/roulette/hall_roulette_coin.png",
#             "desc":"商品描述",
#             "cost":{
#                 "itemId":"user:chip",
#                 "count":1123456,
#                 "original":852278212,
#                 "name":"金币"
#             },
#             "delivery":{
#                 "typeId":"ty.delivery:ty",
#                 "items":[
#                     {
#                         "itemId":"user:chip",
#                         "count":1000000
#                     }
#                 ]
#             },
#             "displayTimePeriod":{
#                 "start":"2017-07-20 07:00:00",
#                 "stop":"2017-07-21 16:00:00"
#             },
#             "exchangeTimePeriod":{
#                 "start":"2017-07-21 22:00:00",
#                 "stop":"2017-07-24 21:00:00"
#             },
#             "stock":{
#                 "cycle":{
#                     "typeId":"timeCycle.minutes",
#                     "minutes":10,
#                     "timePeriod":{
#                         "start":"2017-07-19 07:00:00",
#                         "stop":"2017-07-21 08:00:00"
#                     }
#                 },
#                 "count":6
#             },
#             "tagMark":"new"
#         }
#         ]
#              }
#         self.testContext.configure.setJson('game:9999:exmall', c, 0)
#         hall_exmall._reloadConf()
#         ex = hall_exmall.findExchange('10001')
#         t = datetime.strptime('2017-07-19 07:00:00', '%Y-%m-%d %H:%M:%S')
#         stockObj = hall_exmall.loadStockObj('10001')
#         ex.stock.adjustStock(stockObj, pktimestamp.datetime2Timestamp(t))
#         print stockObj.__dict__
#         
# #         hall_exmall.saveStockObj(ex.exchangeId, stockObj)
#         t = datetime.strptime('2017-07-21 10:00:00', '%Y-%m-%d %H:%M:%S')
#         stockObj = hall_exmall.loadStockObj('10001')
#         ex.stock.adjustStock(stockObj, pktimestamp.datetime2Timestamp(t))
#         print stockObj.__dict__
#         
#     def testStockTime1(self):
#         c = {
#              "exchanges":[
#         {
#             "exchangeId":"11",
#             "displayName":"美的双开门冰箱",
#             "pic":"http://img13.360buyimg.com/n2/jfs/t4024/119/1045572671/113927/7b81d2e4/58661e08N5ef0af7c.jpg",
#             "desc":"美的(Midea) BCD-169CM(E) 169升 家用双门冰箱 日耗电0.58度 HIPS环保内胆 时尚外观",
#             "cost":{
#                 "itemId":"user:coupon",
#                 "count":98000,
#                 "original":119800,
#                 "name":"美的双开门冰箱"
#             },
#             "delivery":{
#                 "typeId":"ty.delivery:gdss",
#                 "auditParams":{
#                     "type":6,
#                     "desc":"美的双开门冰箱",
#                     "count":1,
#                     "jdProductId":"4280294"
#                 },
#                 "clientParams":{
#                     "bindPhone":0,
#                     "desc":"请填写您的有效电话号码",
#                     "needAddress":1,
#                     "type":"address",
#                     "confirm":1
#                 }
#             },
#             "displayTimePeriod":{
#                 "start":"2017-07-28 11:30:00",
#                 "stop":"2017-07-28 23:00:00"
#             },
#             "exchangeTimePeriod":{
#                 "start":"2017-07-28 12:30:00",
#                 "stop":"2017-07-28 23:00:00"
#             },
#             "stock":{
#                 "cycle":{
#                     "typeId":"timeCycle.life",
#                     "timePeriod":{
#                         "start":"2017-07-27 13:00:00"
#                     }
#                 },
#                 "count":5,
#                 "displayStockLimit":1
#             },    
#             "exchangeCountLimit":{
#                 "cycle":{
#                     "typeId":"timeCycle.life"
#                 },
#                 "failure":"抱歉，该商品每人限购1次哦！",
#                 "count":1,
#                 "visible":1
#             }
#         }
#         ]
#              }
#         self.testContext.configure.setJson('game:9999:exmall', c, 0)
#         hall_exmall._reloadConf()
#         ex = hall_exmall.findExchange('11')
#         t = datetime.strptime('2017-07-28 07:00:00', '%Y-%m-%d %H:%M:%S')
#         stockObj = hall_exmall.loadStockObj('11')
#         ex.stock.adjustStock(stockObj, pktimestamp.datetime2Timestamp(t))
#         print stockObj.__dict__
#         
# #         hall_exmall.saveStockObj(ex.exchangeId, stockObj)
#         t = datetime.strptime('2017-07-28 10:00:00', '%Y-%m-%d %H:%M:%S')
#         stockObj = hall_exmall.loadStockObj('11')
#         ex.stock.adjustStock(stockObj, pktimestamp.datetime2Timestamp(t))
#         print stockObj.__dict__

    def testCountLimit(self):
        c = {
             "exchanges":[
        {
            "exchangeId":"11",
            "displayName":"美的双开门冰箱",
            "pic":"http://img13.360buyimg.com/n2/jfs/t4024/119/1045572671/113927/7b81d2e4/58661e08N5ef0af7c.jpg",
            "desc":"美的(Midea) BCD-169CM(E) 169升 家用双门冰箱 日耗电0.58度 HIPS环保内胆 时尚外观",
            "cost":{
                "itemId":"user:coupon",
                "count":98000,
                "original":119800,
                "name":"美的双开门冰箱"
            },
            "delivery":{
                "typeId":"ty.delivery:gdss",
                "auditParams":{
                    "type":6,
                    "desc":"美的双开门冰箱",
                    "count":1,
                    "jdProductId":"4280294"
                },
                "clientParams":{
                    "bindPhone":0,
                    "desc":"请填写您的有效电话号码",
                    "needAddress":1,
                    "type":"address",
                    "confirm":1
                }
            },
            "displayTimePeriod":{
                "start":"2017-07-20 07:00:00",
                "stop":"2017-07-21 16:00:00"
            },
            "exchangeTimePeriod":{
                "start":"2017-07-28 12:30:00",
                "stop":"2017-07-28 23:00:00"
            },
            "stock":{
                "cycle":{
                    "typeId":"timeCycle.life",
                    "timePeriod":{
                        "start":"2017-07-27 13:00:00"
                    }
                },
                "count":5,
                "displayStockLimit":1
            },    
            "exchangeCountLimit":{
                "cycle":{
                    "typeId":"timeCycle.life"
                },
                "failure":"抱歉，该商品每人限购1次哦！",
                "count":1,
                "visible":1
            }
        }
        ]
             }
        self.testContext.configure.setJson('game:9999:exmall', c, 0)
        hall_exmall._reloadConf()
        ex = hall_exmall.findExchange('11')
        rd = hall_exmall.loadExchangeCountLimitRecord(self.userId, '11')
        ex.exchangeCountLimit.adjustRecord(rd, self.timestamp)
        
        print rd.__dict__
        
if __name__ == '__main__':
    unittest.main()

