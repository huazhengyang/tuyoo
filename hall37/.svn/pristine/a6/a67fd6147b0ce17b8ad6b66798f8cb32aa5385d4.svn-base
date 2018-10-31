# -*- coding=utf-8
'''
Created on 2015年6月12日

@author: zhaojiangang
'''
import json
import time
import unittest

from entity.halldailycheckin_test import dailycheckin_conf
from hall.entity import hallstore, hallitem, hallpopwnd, halldailycheckin
import poker.entity.dao.gamedata as pkgamedata
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
        {
            "kindId": 88,
            "typeId": "common.memberCard",
            "displayName": "会员卡",
            "visibleInBag": 1,
            "desc": "尊贵的会员，每天登陆可多领3万金币，并拥有会员专属标志、，会员互动表情、，双倍积分等会员特权",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_88_new.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "actions": [
                {
                    "name": "checkin",
                    "displayName": "打开",
                    "typeId": "common.checkin",
                    "mail": "会员登录奖励\\${gotContent}",
                    "content": {
                        "typeId": "FixedContent",
                        "desc": "30000金币",
                        "items": [
                            {
                                "itemId": "user:chip",
                                "count": 30000
                            }
                        ]
                    }
                }
            ]
        }
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
            },
            {
                "displayName":"钻石商城",
                "name":"member",
                "products":[
                    "T50K",
                ],
                "visible":1,
                "iconType":"diamond"
            },
            {
                "displayName":"道具商城",
                "name":"lessbuychip",
                "products":[
                    "T60K",
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
    "IOS_3.6_momo":1
}

store_conf = store_template_conf['templates']['default']

popwnd_conf = {
    "templates":{
        "default":{
            "memberPayOrder":{
                "typeId":"todotask.template.payOrder",
                "payOrder":{
                    "shelves":["member"],
                    "priceDiamond":{"count":120, "minCount":120, "maxCount":-1}
                }
            },
            "memberTryPayOrder":{
                "typeId":"todotask.template.payOrder",
                "payOrder":{
                    "shelves":["member"],
                    "priceDiamond":{"count":10, "minCount":10, "maxCount":10}
                }
            },
            "firstRechargeTry":{
                "typeId":"todotask.template.firstRechargeTry",
                "title":"[[{\"text\": \"仅需充值6元，即可\", \"style\": \"labelStyle_first_recharge_normal\", \"type\": \"ttf\"}, {\"text\": \"额外领取\", \"style\": \"labelStyle_first_recharge_bold\", \"type\": \"ttf\"}]]",
                "imgUrl":"",
                "subActionText":"领取礼包",
                "payOrder":{
                    "shelves":["lessbuychip"],
                    "priceDiamond":{"count":60, "minCount":60, "maxCount":-1}
                },
                "confirm": 1,
                "confirmDesc":"对不起，您不满足领取礼包的条件\n现在就购买\\${product.displayName}(\\${product.price}元)即可领取豪华大礼包！" 
            },
            "memberTry":{
                "typeId":"todotask.template.memberTry",
                "desc":"",
                "pic": "${http_download}/hall/popwnd/imgs/member_try.png",
                "actions":[
                    {
                        "text":{
                            "name":"sub_action_text",
                            "value":"1元体验"
                        },
                        "required":1,
                        "action":{
                            "name":"sub_action",
                            "list":[
                                {
                                    "templateName":"memberTryPayOrder"
                                }
                            ]
                        }
                    }
                ]
            },
            "memberTryMin":{
                "typeId":"todotask.template.memberTryMin",
                "desc":"亲，只需1元即可试用1天会员，包括10000金币及七大特权，当天生效，来试试看？",
                "allowClose":1,
                "actions":[
                    {
                        "action":{
                            "name":"sub_action",
                            "list":[
                                {
                                    "templateName":"memberTryPayOrder"
                                }
                            ]
                        }
                    }
                ]
            },
            "memberBuy":{
                "typeId":"todotask.template.memberBuy",
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
                            "list":[
                                {
                                    "templateName":"memberPayOrder"
                                }
                            ]
                        }
                    },
                    {
                        "required":1,
                        "action":{
                            "name":"sub_action_close",
                            "list":[
                                {
                                    "templateName":"memberTryMin"
                                }
                            ]
                        }
                    }
                ]
            },
            "recommendBuy":{
                "typeId":"todotask.template.recommendBuy",
                "desc":"",
                "pic": "${http_download}/hall/popwnd/imgs/pop_recommend_buy.png",
                "subActionText":"领取礼包",
                "payOrder":{
                    "shelves":["member"],
                    "priceDiamond":{"count":10000000, "minCount":10000000, "maxCount":-1}
                   }
            },
            "activity":{
                "typeId":"todotask.template.activity",
                "actId":"activity_general_btn_raffle_37"
            },
            "lessBuyChip":{
                "typeId":"todotask.template.lessBuyChip",
                "desc":"[[{\"text\": \"您的金币不足进入该房间至少需要\", \"style\": \"labelStyle_pop_order_normal\", \"type\": \"ttf\"}, {\"text\": \"\\${room.minCoin}\", \"font\": \"hall_button_text_special_red\", \"type\": \"bmf\"}], [{\"text\": \"推荐您购买\\${product.displayName}\", \"type\": \"ttf\"}]]",
                "note":"[[{\"text\": \"需要花费\\${product.price}元。客服电话4008-098-000\", \"font\": \"labelStyle_pop_order_tip\", \"type\": \"ttf\"}]]",
                "iconPic":"${http_download}/hall/popwnd/imgs/coin_icon.png"
            },
            "luckBuy":{
                "typeId":"todotask.template.luckBuy",
                "desc":"[[{\"text\": \"胜负乃兵家常事，大侠请重新来过。\", \"style\": \"labelStyle_lucky_text_normal\", \"type\": \"ttf\"}], [{\"text\": \"送您一次限量礼包购买机会，\", \"style\": \"labelStyle_lucky_text_normal\", \"type\": \"ttf\"}], [{\"text\": \"助您时来运转，反败为胜！\", \"style\": \"labelStyle_lucky_text_normal\", \"type\": \"ttf\"}]]",
                "selectProductAction":"zhuanyun",
                "subActionText":"领取礼包",
                "tip":"\\${product.desc}"
            },
            "memberTryRoom":{
                "typeId":"todotask.template.memberTry",
                "desc":"",
                "selectProductAction":"memberTry",
                "subActionText":"1元体验",
                "pic": "${http_download}/hall/popwnd/imgs/member_try.png"
            },
            "winBuy":{
                "typeId":"todotask.template.winBuy",
                "desc":"[[{\"text\": \"水平真高！\", \"style\": \"labelStyle_lucky_text_normal\", \"type\": \"ttf\"}], [{\"text\": \"送您一次限量礼包购买机会，\", \"style\": \"labelStyle_lucky_text_normal\", \"type\": \"ttf\"}], [{\"text\": \"（全国只有8%的人能获得）\", \"style\": \"labelStyle_lucky_text_normal\", \"type\": \"ttf\"}]]",
                "tip":"",
                "selectProductAction":"winlead",
                "subActionText":"领取礼包"
            }
        }
    }
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
        self.testContext.configure.setJson('game:9999:popwnd', popwnd_conf, 0)
        self.testContext.configure.setJson('game:9999:dailycheckin', dailycheckin_conf, 0)
        hallitem._initialize()
        hallstore._initialize()
        hallpopwnd._initialize()
        halldailycheckin._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
    
    def testFindProduct(self):
        remainDays, memberBonus = hallitem.getMemberInfo(self.userId, int(time.time()))
        todotask = hallpopwnd.makeTodoTaskNsloginReward(self.gameId, self.userId, self.clientId, remainDays, memberBonus)
        jstr = json.dumps(todotask.toDict(), indent=4, ensure_ascii=False)
        print jstr
        pkgamedata.incrGameAttr(self.userId, self.gameId, 'first_recharge', 1)
        pkgamedata.incrGameAttr(self.userId, self.gameId, 'first_recharge_reward', 1)
        #def addAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam):
        hallitem.itemSystem.loadUserAssets(self.userId).addAsset(self.gameId, hallitem.ASSET_ITEM_MEMBER_KIND_ID, 1, 0, 0, 0)
        todotask = hallpopwnd.makeTodoTaskNsloginReward(self.gameId, self.userId, self.clientId, remainDays, memberBonus)
        jstr = json.dumps(todotask.toDict(), indent=4, ensure_ascii=False)
        print jstr
        
        todotask = hallpopwnd.makeTodoTaskLuckBuy(self.gameId, self.userId, self.clientId, 601)
        jstr = json.dumps(todotask.toDict(), indent=4, ensure_ascii=False)
        print jstr
        
        
        
if __name__ == '__main__':
    #ftlog.log_level = ftlog.LOG_LEVEL_INFO
    unittest.main()
    
    