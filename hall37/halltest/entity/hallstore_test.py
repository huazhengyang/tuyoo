# -*- coding=utf-8
'''
Created on 2015年6月12日

@author: zhaojiangang
'''
import json
import unittest

from hall.entity import hallstore, hallitem
from hall.entity.todotask import TodoTaskRegister
from poker.entity.biz.store.exceptions import \
    TYDeliveryOrderDiffProductException, TYDeliveryOrderDiffUserException
from poker.entity.biz.store.store import TYOrder, TYChargeInfo
from test_base import HallTestMockContext


product_t50k = {
    "productId":"T50K",  # 商品ID，字符串，全局唯一
    "displayName":"50000金币",  # 商品显示的名字，字符串
    "category":"coin", # 金币商品
    "displayNamePic":"",
    "pic":"goods_t50k.png",  # 商品图片名称，这个需要组合成一个http的URL给客户端
    "price":"5",  # 价格，单位为元
    "priceDiamond":"50",
    "buyType":"direct",
    "diamondExchangeRate":0,
    "desc":"赠：3天记牌器",  # 商品说明
    "mail":"购买${displayName}，获得${content}",  # 商品发货后给用户发的消息
    "content":{  # 目前只支持FixedContent(固定内容), CompositeContent(组合内容), RandomContent(随机内容)
        "typeId":"FixedContent", # 类型
        "desc":"50000金币+3天记牌器",  # 内容说明,type=XXXContent的必须包含desc
        "items":[  # 固定内容必须包含items
            {"itemId":"user:chip", "count":50000}, 
            {"itemId":"item:1", "count":3}
        ]
    },
    "recordLastBuy":1,
    "buyConditions":[
    
    ],
    "buyCountLimit":{
    }
}

product_t60k = {
    "productId":"T60K",  # 商品ID，字符串，全局唯一
    "displayName":"60000金币",  # 商品显示的名字，字符串
    "category":"coin", # 金币商品
    "displayNamePic":"",
    "pic":"goods_t50k.png",  # 商品图片名称，这个需要组合成一个http的URL给客户端
    "price":"6",  # 价格，单位为元
    "priceDiamond":"60",
    "buyType":"direct",
    "diamondExchangeRate":0,
    "desc":"赠：3天记牌器",  # 商品说明
    "mail":"购买${displayName}，获得${content}",  # 商品发货后给用户发的消息
    "content":{  # 目前只支持FixedContent(固定内容), CompositeContent(组合内容), RandomContent(随机内容)
        "typeId":"FixedContent", # 类型
        "desc":"60000金币+3天记牌器",  # 内容说明,type=XXXContent的必须包含desc
        "items":[  # 固定内容必须包含items
            {"itemId":"user:chip", "count":60000}, 
            {"itemId":"item:1", "count":10}
        ]
    },
    "recordLastBuy":1,
}

products_conf = {
    "products":[product_t50k, product_t60k]
}

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
    ]
}

store_template_conf = {
    "templates":{
        "default":[
            {
                "displayName":"道具商城",
                "name":"item",
                "products":[
                    "T60K",
                ],
                "visible":1,
                "iconType":"diamond"
            },
            {
                "displayName":"钻石商城",
                "name":"coin",
                "products":[
                    "T50K",
                ],
                "visible":1,
                "iconType":"diamond"
            },
            {
                "displayName":"钻石商城",
                "name":"zhuanyun",
                "products":[
                    "T50K",
                ],
                "visible":1,
                "iconType":"diamond"
            }
        ]
    },
    "lastBuy":{
        "desc":"您上次购买的商品是\\${displayName}，是否依然购买此商品？",
        "subText":"是",
        "subTextExt":"逛逛商城"
    }
}

store_default_conf = {
    "template":"default"
}

clientIdMap = {
    "IOS_3.6_momo":1,
    "IOS_3.70_360.360.0-hall6.360.day":13232
}

store_conf = store_template_conf['templates']['default']

memberTry = {
    "typeId":"hall.member.try",
    "desc":"",
    "pic": "${http_download}/hall/popwnd/imgs/member_buy.png",
    "actions":[
        {
            "text":{
                "name":"sub_action_text",
                "value":"获取特权"
            },
            "required":1,
            "action":{
                "name":"sub_action",
                "todotasks":[
                    {
                        "conditions":[],
                        "todotask":{
                            "typeId":"hall.payOrder",
                            "payOrder":{
                                "shelves":["member"],
                                "priceDiamond":{"count":120, "minCount":120, "maxCount":120}
                            }
                        }
                    }
                ]
            }
        },
        {
            "action":{
                "name":"sub_action_close",
                "todotasks":[
                    {
                        "conditions":[],
                        "todotask":{
                            "typeId":"hall.member.try",
                            "desc":"",
                            "pic": "${http_download}/hall/popwnd/imgs/member_try.png",
                            "actions":[
                                {
                                    "text":{
                                        "name":"sub_action_text",
                                        "value":"1元体验"
                                    },
                                    "action":{
                                        "name":"sub_action",
                                        "todotasks":[
                                            {
                                                "conditions":[],
                                                "todotask":{
                                                    "typeId":"hall.payOrder",
                                                    "payOrder":{
                                                        "shelves":["member"],
                                                        "priceDiamond":{"count":10, "minCount":10, "maxCount":10}
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
}

class TestStore(unittest.TestCase):
    gameId = 6
    userId = 10001
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        hallitem._initialize()
        hallstore._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
    
    def testReloadConf(self):
        hallstore._reloadConf()
        
    def _equalShelvesToConf(self, shelves, shelvesConf):
        self.assertEqual(shelves.name, shelvesConf['name'])
        self.assertEqual(shelves.displayName, shelvesConf['displayName'])
        self.assertEqual(shelves.visibleInStore, shelvesConf['visible'])
        self.assertEqual(shelves.iconType, shelvesConf['iconType'])
        productIds = [p.productId for p in shelves.productList]
        self.assertEqual(productIds, shelvesConf['products'])
        
    def testGetShelvesListByClientId(self):
        shelvesList = hallstore.storeSystem.getShelvesListByClientId(self.gameId, self.userId, self.clientId)
        self.assertEqual(len(shelvesList), 3)
        for i, shelves in enumerate(shelvesList):
            self._equalShelvesToConf(shelves, store_conf[i])
    
    def testGetShelvesByClientId(self):
        shelves = hallstore.storeSystem.getShelvesByClientId(self.gameId, self.userId, self.clientId, 'item')
        self._equalShelvesToConf(shelves, store_conf[0])
        shelves = hallstore.storeSystem.getShelvesByClientId(self.gameId, self.userId, self.clientId, 'coin')
        self._equalShelvesToConf(shelves, store_conf[1])
        
    def testBuyProduct(self):
        orderId = 'GO00001'
        order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
        self.assertEqual(order.orderId, orderId)
        self.assertEqual(self.testContext.orderDao.findOrder(orderId), order)
        self.assertEqual(order.state, TYOrder.STATE_CREATE)
        
    def testDeliveryOrder(self):
        orderId = 'GO00001'
        order = hallstore.storeSystem.buyProduct(self.gameId, self.userId, self.clientId, orderId, 'T50K', 1)
        self.assertEqual(order.orderId, orderId)
        self.assertEqual(self.testContext.orderDao.findOrder(orderId), order)
        self.assertEqual(order.state, TYOrder.STATE_CREATE)
        self.assertRaises(TYDeliveryOrderDiffProductException, hallstore.storeSystem.deliveryOrder,
                          self.userId, orderId, 'T50k', TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
        self.assertRaises(TYDeliveryOrderDiffUserException, hallstore.storeSystem.deliveryOrder,
                          1, orderId, 'T50K', TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
        orderDeliveryResult = hallstore.storeSystem.deliveryOrder(self.userId, orderId, 'T50K',
                                                    TYChargeInfo('alipay', {'rmbs':10}, {'coin':100}))
        print 'orderDeliveryResult=', orderDeliveryResult.__dict__
        
    def testGetLastBuyProduct(self):
        pass
    
    def testFindProduct(self):
        todotask = TodoTaskRegister.decodeFromDict(memberTry).newTodoTask(self.gameId, self.userId, self.clientId)
        print json.dumps(todotask.toDict(), ensure_ascii=False, indent=4)
    
if __name__ == '__main__':
    #ftlog.log_level = ftlog.LOG_LEVEL_INFO
    unittest.main()
    
    