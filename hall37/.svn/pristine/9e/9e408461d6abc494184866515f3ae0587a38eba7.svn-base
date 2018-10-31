# -*- coding=utf-8
'''
Created on 2015年6月3日

@author: zhaojiangang
'''
import unittest

from biz.mock import patch
import freetime.util.log as ftlog
from hall.entity import hallitem, hallexchange
from hall.entity.hallitem import TYBindingItemNotEnoughException, \
    TYItemAlreadyCheckinException, TYItemAlreadyWoreException, \
    TYItemAlreadyExpiresException, TYItemKindAssembleNotEnoughException
from poker.entity.biz.item.exceptions import \
    TYItemActionConditionNotEnoughException, TYAssetNotEnoughException, \
    TYItemActionParamException
from poker.entity.biz.item.item import TYAssetKindItem
import poker.entity.dao.userchip as pkuserchip
import poker.entity.dao.userdata as pkuserdata
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


asset_list = [
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
]

item_cardmatch_id = 1
item_moonkey_id = 2
item_moonbox_id = 3
item_newer_gift_id = 4
item_2day_gift_id = 5
item_3day_gift_id = 6
item_membercard_id = 8
item_gentleman_staff_id = 9
item_revolver_id = 10
item_cardnote_id = 11
item_doublecard_id = 12
item_chip_bag_id = 13
item_chip_bag_part1_id = 14
item_chip_bag_part2_id = 15
item_chip_bag_part3_id = 16
item_chip_bag_part4_id = 17
item_chip_bag_part5_id = 18
item_chip_bag_part6_id = 19
item_chip_bag_part7_id = 20
item_alipay_gift_id = 21
item_packing_paper_id = 22
item_first_charge_gift_id = 23
item_alipay_gift_id = 24
item_phone_card10_id = 25
item_phone_card50_id = 26

item_cardmatch = {
    "kindId":item_cardmatch_id,
    "typeId":"common.simple",
    "displayName":"参赛券",
    "visibleInBag":1,
    "desc":"报名比赛使用",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"sale",
            "displayName":"出售",
            "typeId":"common.sale",
            "saleContent":
                    {"itemId":"user:chip", "count":100}
        }
    ]
}

item_cardnote = {
    "kindId":item_cardnote_id,
    "typeId":"common.switch",
    "displayName":"记牌器",
    "visibleInBag":1,
    "desc":"用于斗地主牌桌记牌，好记性不如烂笔头",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"turnOn",
            "displayName":"打开",
            "typeId":"common.switch.turnOn"
        },
        {
            "name":"turnOff",
            "displayName":"关闭",
            "typeId":"common.switch.turnOff"
        }
    ]
}

item_moonkey = {
    "kindId":item_moonkey_id,
    "typeId":"common.simple",
    "displayName":"月光钥匙",
    "visibleInBag":1,
    "desc":"可开启月光宝盒，获得多种神秘奖励",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0
}

item_moonbox = {
    "kindId":item_moonbox_id,
    "typeId":"common.box",
    "displayName":"月光宝盒",
    "visibleInBag":1,
    "desc":"获得大量金币或奖券，必须使用月光之钥开启",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":0,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "bindings":[
                {"itemId":item_moonkey_id, "count":1}
            ],
            "contents":[
                {
                    "openTimes":{"start":0, "stop":3},
                    "typeId":"FixedContent",
                    "items":[
                        {"itemId":"user:chip", "start":26000, "stop":26000}
                    ]
                },
                {
                    "openTimes":{"start":4, "stop":10},
                    "typeId":"FixedContent",
                    "items":[
                        {"itemId":"user:chip", "start":30000, "stop":30000}
                    ]
                },
                {
                    "openTimes":{"start":11, "stop":-1},
                    "typeId":"FixedContent",
                    "items":[
                        {"itemId":"user:chip", "start":40000, "stop":40000}
                    ]
                }
            ]
        }
    ]
}

item_newer_gift = {
    "kindId":item_newer_gift_id,
    "typeId":"common.box",
    "displayName":"新手次日抽奖礼包",
    "visibleInBag":1,
    "desc":"可以获得奖券或大量金币，来试试手气吧~",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "contents":[
                {
                    "typeId":"FixedContent",
                    "openTimes":{"start":-1, "stop":-1},
                    "items":[
                        {"itemId":"item:%s" % (item_2day_gift_id), "count":1}
                    ]
                }
            ]
        }
    ]
}

item_2day_gift = {
    "kindId":item_2day_gift_id,
    "typeId":"common.box",
    "displayName":"新手次日抽奖礼包",
    "visibleInBag":1,
    "desc":"可以获得奖券或大量金币，来试试手气吧~",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "mail":"恭喜您获得了${content}，再赠送您一次抽奖机会，明天还能中奖哦~",
            "nextItemKindId":item_3day_gift_id,
            "conditions":[
                {
                    "typeId":"ITEM.GOT.SECOND_DAYS_LATER",
                    "params":{
                        "failure":"明天才可以打开哦"
                    }
                }
            ],
            "contents":[
                {
                    "openTimes":{"start":-1, "stop":-1},
                    "typeId":"FixedContent",
                    "weight":1,
                    "items":[
                        {"itemId":"user:chip", "start":100, "stop":100}
                    ]
                }
            ]
        }
    ]
}

item_3day_gift = {
    "kindId":item_3day_gift_id,
    "typeId":"common.box",
    "displayName":"新手三日抽奖礼包",
    "visibleInBag":1,
    "desc":"可以获得奖券或大量金币，来试试手气吧~",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "mail":"恭喜您获得了${content}",
            "conditions":[
                {
                    "typeId":"ITEM.GOT.SECOND_DAYS_LATER",
                    "params":{
                        "failure":"明天才可以打开哦"
                    }
                }
            ],
            "contents":[
                {
                    "openTimes":{"start":-1, "stop":-1},
                    "typeId":"FixedContent",
                    "weight":1,
                    "items":[
                        {"itemId":"user:chip", "start":500, "stop":500}
                    ]
                }
            ]
        }
    ]
}

item_membercard = {
    "kindId":item_membercard_id,
    "typeId":"common.memberCard",
    "displayName":"会员卡",
    "visibleInBag":1,
    "desc":"尊贵的会员，每天登陆可多领3万金币，并拥有会员专属标志、，会员互动表情、，双倍积分等会员特权",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.day", "displayName":"天"},
    "removeFromBagWhenRemainingZero":0,
    "removeFromBagWhenExpires":1,
    "actions" : [
        {
            "name" : "checkin",
            "displayName" : "打开",
            "typeId" : "common.checkin",
            "mail" : "会员登录奖励\\${gotContent}",
            "content" : {
                "typeId" : "FixedContent",
                "desc" : "30000金币",
                "items" : [{
                    "itemId" : "user:chip",
                    "count" : 30000
                }]
            }
        }
    ]
}


item_gentleman_staff = {
    "kindId":item_gentleman_staff_id,
    "typeId":"common.decroation",
    "displayName":"绅士手杖",
    "visibleInBag":1,
    "desc":"使用后可在牌桌内激发，“绅士手杖”特效",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.day", "displayName":"天"},
    "removeFromBagWhenRemainingZero":0,
    "removeFromBagWhenExpires":0,
    "localRes":{
        "resName":"item_gentleman_staff"
    },
    "pos":{
        "zOrder":30
    },
    "masks":16,
    "actions":[
        {
            "name":"repair",
            "displayName":"修复",
            "typeId":"common.repair",
            "repairAddUnitsCount":10,
            "repairContent":{"itemId":"user:chip", "count":300}
        },
        {
            "name":"wear",
            "displayName":"佩戴",
            "typeId":"common.decroation.wear"
        },
        {
            "name":"unwear",
            "displayName":"取消佩戴",
            "typeId":"common.decroation.unwear"
        }
    ]
}


item_revolver = {
    "kindId":item_revolver_id,
    "typeId":"common.decroation",
    "displayName":"左轮手枪",
    "visibleInBag":1,
    "desc":"使用后可在牌桌内激发，“左轮手枪”特效",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.day", "displayName":"天"},
    "removeFromBagWhenRemainingZero":0,
    "removeFromBagWhenExpires":0,
    "localRes":{
        "resName":"item_revolver"
    },
    "pos":{
        "zOrder":30
    },
    "masks":16,
    "actions":[
        {
            "name":"wear",
            "displayName":"佩戴",
            "typeId":"common.decroation.wear"
        },
        {
            "name":"unwear",
            "displayName":"取消佩戴",
            "typeId":"common.decroation.unwear"
        }
    ]
}

item_doublecard = {
    "kindId":item_doublecard_id,
    "typeId":"common.simple",
    "displayName":"参赛券",
    "visibleInBag":1,
    "desc":"报名比赛使用",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.time", "displayName":"小时", "seconds":3600},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0
}

item_chip_bag_part1 = {
    "kindId":item_chip_bag_part1_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片1",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag_part2 = {
    "kindId":item_chip_bag_part2_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片2",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag_part3 = {
    "kindId":item_chip_bag_part3_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片3",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag_part4 = {
    "kindId":item_chip_bag_part4_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片4",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag_part5 = {
    "kindId":item_chip_bag_part5_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片5",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag_part6 = {
    "kindId":item_chip_bag_part6_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片6",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag_part7 = {
    "kindId":item_chip_bag_part7_id,
    "typeId":"common.simple",
    "displayName":"金币袋碎片7",
    "visibleInBag":1,
    "desc":"可开组装成金币袋",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"assemble",
            "displayName":"合成",
            "typeId":"common.assemble"
        }
    ]
}

item_chip_bag = {
    "kindId":item_chip_bag_id,
    "typeId":"common.simple",
    "displayName":"金币袋",
    "visibleInBag":1,
    "desc":"可开启月光宝盒，获得多种神秘奖励",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "components":[
        {"itemKindId":item_chip_bag_part1_id, "count":1},
        {"itemKindId":item_chip_bag_part2_id, "count":1},
        {"itemKindId":item_chip_bag_part3_id, "count":1},
        {"itemKindId":item_chip_bag_part4_id, "count":1},
        {"itemKindId":item_chip_bag_part5_id, "count":1},
        {"itemKindId":item_chip_bag_part6_id, "count":1},
        {"itemKindId":item_chip_bag_part7_id, "count":1},
    ]
}

item_alipay_gift = {
    "kindId":item_alipay_gift_id,
    "typeId":"common.box",
    "displayName":"支付宝礼包",
    "visibleInBag":1,
    "desc":"使用支付宝充值后，即可使用，内含50000金币哦~",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "mail":"恭喜您获得了${content}",
            "conditions":[
                {
                    "typeId":"ALIPAY.LEAST_ONCE",
                    "params":{
                        "failure":"用支付宝支付后才能使用哦"
                    }
                }
            ],
            "contents":[
                {
                    "openTimes":{"start":-1, "stop":-1},
                    "typeId":"FixedContent",
                    "items":[
                        {"itemId":"user:chip", "count":26000}
                    ]
                }
            ]
        }
    ]
}

item_packing_paper = {
    "kindId":item_packing_paper_id,
    "typeId":"common.simple",
    "displayName":"包装纸",
    "visibleInBag":1,
    "desc":"包装用",
    "singleMode":1,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"张"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0
}

item_first_charge_gift = {
    "kindId":item_first_charge_gift_id,
    "typeId":"common.box",
    "displayName":"首充礼包",
    "visibleInBag":1,
    "desc":"只要充过值即可免费打开，内含30000金币和幸运礼帽，感谢您的支持",
    "singleMode":1,
    "pic":"http://item_1002.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "mail":"您开${displayName}，获得${content}",
            "conditions":[
                {
                    "typeId":"PAY.LEAST_ONCE",
                    "params":{
                        "failure":"您还没充过值，支持一下吧：)"
                    }
                }
            ],
            "contents":[
                {
                    "openTimes":{"start":-1, "stop":-1},
                    "typeId":"FixedContent",
                    "weight":1,
                    "items":[
                        {"itemId":"user:chip", "count":30000},
                        {"itemId":"item:4100", "count":1},
                    ]
                }
            ]
        }
    ]
}

item_alipay_gift = {
    "kindId":item_alipay_gift_id,
    "typeId":"common.box",
    "displayName":"支付宝礼包",
    "visibleInBag":1,
    "desc":"使用支付宝充值后，即可使用，内含50000金币哦~",
    "singleMode":1,
    "pic":"http://item_1002.png",
    "units":{"typeId":"common.count", "displayName":"个"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"open",
            "displayName":"打开",
            "typeId":"common.box.open",
            "mail":"您开启了${displayName}，获得${content}",
            "conditions":[
                {
                    "typeId":"ALIPAY.LEAST_ONCE",
                    "params":{
                        "failure":"用支付宝支付后才能使用哦"
                    }
                }
            ],
            "contents":[
                {
                    "openTimes":{"start":-1, "stop":-1},
                    "typeId":"FixedContent",
                    "weight":1,
                    "items":[
                        {"itemId":"user:chip", "count":30000},
                        {"itemId":"item:4100", "count":1},
                    ]
                }
            ]
        }
    ]
}

item_jinzhuan = {
    "kindId": 4138,
    "typeId": "common.simple",
    "displayName": "金砖",
    "visibleInBag": 1,
    "desc": "黄金有价，情无价，送给你最珍贵的人",
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
            "name": "sale",
            "displayName": "出售",
            "typeId": "common.sale",
            "mail": "您出售了\\${item}，获得\\${gotContent}",
            "params": {
                "type": "countSale",
                "desc": "出售可获得:",
                "confirm": 1
            },
            "saleContent": {
                "itemId": "user:chip",
                "count": 1000000
            }
        },
        {
            "name": "present",
            "displayName": "赠送",
            "typeId": "common.present",
            "mail": "您赠送\\${presentCount}\\${units}\\${item}，给\\${targetUserId}",
            "params": {
                "type": "countAndUserId",
                "desc": "赠送描述",
                "confirm": 1
            }
        }
    ]
}

item_phone_card10 = {
    "kindId":item_phone_card10_id,
    "typeId":"common.exchange",
    "displayName":"10元电话卡",
    "visibleInBag":1,
    "desc":"10元电话卡",
    "singleMode":0,
    "pic":"http://pic.png",
    "units":{"typeId":"common.count", "displayName":"张"},
    "removeFromBagWhenRemainingZero":1,
    "removeFromBagWhenExpires":0,
    "actions":[
        {
            "name":"exchange",
            "displayName":"兑换",
            "typeId":"common.exchange",
            "params":{
                "count":10,
                "type":0,
                "desc":"10元电话费"
            }
        }
    ]
}

conf = {
    'assets':asset_list,
    'items':[
        item_cardmatch,
        item_moonbox,
        item_moonkey,
        item_newer_gift,
        item_2day_gift,
        item_3day_gift,
        item_membercard,
        item_gentleman_staff,
        item_revolver,
        item_cardnote,
        item_doublecard,
        item_chip_bag,
        item_chip_bag_part1,
        item_chip_bag_part2,
        item_chip_bag_part3,
        item_chip_bag_part4,
        item_chip_bag_part5,
        item_chip_bag_part6,
        item_chip_bag_part7,
        item_alipay_gift,
        item_jinzhuan,
        item_phone_card10
    ]
}

class UserBank(object):
    def __init__(self):
        # key=userId, value=map<name, value>
        self.userMap = {}
        
    def clear(self):
        self.userMap = {}
        
    def get(self, userId, name, defValue=None):
        bankMap = self.userMap.get(userId)
        if not bankMap:
            return defValue
        return bankMap.get(name, defValue)
    
    def set(self, userId, name, value):
        bankMap = self.userMap.get(userId)
        if not bankMap:
            bankMap = {}
            self.userMap[userId] = bankMap
        bankMap[name] = value
        return value
    
    def incr(self, userId, name, count):
        bankMap = self.userMap.get(userId)
        if not bankMap:
            bankMap = {}
            bankMap[userId] = bankMap
        oldValue = bankMap.get(name, 0)
        bankMap[name] = oldValue + count
        return bankMap[name]
         
class TestUserBag(unittest.TestCase):
    userId = 10001
    gameId = 6
    testContext = HallTestMockContext()
    
    def getCurrentTimestamp(self):
        return self.timestamp
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('game:9999:item', conf, 0)
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.pktimestampPatcher = patch('poker.util.timestamp.getCurrentTimestamp', self.getCurrentTimestamp)
        self.pktimestampPatcher.start()
        hallitem._initialize()
        
    def tearDown(self):
        self.pktimestampPatcher.stop()
        self.testContext.stopMock()
    
    def testCardMatch(self):
        # 测试参赛券
        cardMatchKind = hallitem.itemSystem.findItemKind(item_cardmatch_id)
        # 获取用户背包
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(cardMatchKind), [])
        
        # 添加测试
        item = userBag.addItemUnitsByKind(self.gameId, cardMatchKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assert_(item.remaining == 1)
        self.assert_(item.expiresTime == -1)
        
        # 参赛券是非互斥的，每个背包里只存在一个实例
        item1 = userBag.addItemUnitsByKind(self.gameId, cardMatchKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assert_(item.remaining == 2)
        self.assert_(item.expiresTime == -1)
        
        self.assert_(item == item1)
        
        # 测试消耗
        self.assertEqual(userBag.consumeUnitsCountByKind(self.gameId, cardMatchKind, 1, self.timestamp, 0, 0), 1)
        self.assertEqual(item.remaining, 1)
        
        # 测试消耗完从背包删除
        self.assertEqual(userBag.consumeUnitsCountByKind(self.gameId, cardMatchKind, 1, self.timestamp, 0, 0), 1)
        self.assertEqual(item.remaining, 0)
        self.assertIsNone(userBag.findItem(item.itemId))
        self.assertEqual(userBag.getAllKindItem(cardMatchKind), [])
        
        # 测试出售
        item = userBag.addItemUnitsByKind(self.gameId, cardMatchKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assertRaises(TYItemActionParamException, userBag.doAction, self.gameId, item, 'sale',
                          self.timestamp, params={})
        self.assertRaises(TYItemActionParamException, userBag.doAction, self.gameId, item, 'sale',
                          self.timestamp, params={'count':'1'})
        result = userBag.doAction(self.gameId, item, 'sale', self.timestamp, params={'count':1}).gotAssetList
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 100)
        self.assertEqual(result[0][2], 100)
#         self.assertEqual(result[1][0].kindId, 'user:coupon')
#         self.assertEqual(result[1][1], 200)
#         self.assertEqual(result[1][2], 200)
#         self.assertEqual(result[2][0].kindId, 'game:assistance')
#         self.assertEqual(result[2][1], 300)
#         self.assertEqual(result[2][2], 300)
        
        # 测试出售
        item = userBag.addItemUnitsByKind(self.gameId, cardMatchKind, 10, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        result = userBag.doAction(self.gameId, item, 'sale', self.timestamp, params={'count':10}).gotAssetList
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 1000)
        self.assertEqual(result[0][2], 1000+100)
#         self.assertEqual(result[1][0].kindId, 'user:coupon')
#         self.assertEqual(result[1][1], 2000)
#         self.assertEqual(result[1][2], 2000+200)
#         self.assertEqual(result[2][0].kindId, 'game:assistance')
#         self.assertEqual(result[2][1], 3000)
#         self.assertEqual(result[2][2], 3000+300)
#         
    def testCardNote(self):
        # 测试记牌器
        itemKind = hallitem.itemSystem.findItemKind(item_cardnote_id)
        # 获取用户背包
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        # 添加测试
        item = userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assert_(item.remaining == 1)
        self.assert_(item.expiresTime == -1)
        
        # 参赛券是非互斥的，每个背包里只存在一个实例
        item1 = userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assertEqual(item.remaining, 2)
        self.assertEqual(item.expiresTime, -1)
        
        self.assertEqual(item, item1)
        
        # 测试消耗
        self.assertEqual(userBag.consumeUnitsCountByKind(self.gameId, itemKind, 1, self.timestamp, 0, 0), 1)
        self.assertEqual(item.remaining, 1)
        
        # 测试消耗完从背包删除
        self.assertEqual(userBag.consumeUnitsCountByKind(self.gameId, itemKind, 1, self.timestamp, 0, 0), 1)
        self.assertEqual(item.remaining, 0)
        self.assertIsNone(userBag.findItem(item.itemId))
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        item = userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        # 测试turnOn turnOff
        userBag.doAction(self.gameId, item, 'turnOn')
        self.assertEqual(item.isOn, 1)
        userBag.doAction(self.gameId, item, 'turnOff')
        self.assertEqual(item.isOn, 0)
        
    def testMoonbox(self):
        moonboxKind = hallitem.itemSystem.findItemKind(item_moonbox_id)
        # 获取用户背包
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(moonboxKind), [])
        
        # 添加测试
        item = userBag.addItemUnitsByKind(self.gameId, moonboxKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assert_(item.remaining == 1)
        self.assert_(item.expiresTime == -1)
        
        # 非互斥的，每个背包里只存在一个实例
        item1 = userBag.addItemUnitsByKind(self.gameId, moonboxKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assert_(item.remaining == 2)
        self.assert_(item.expiresTime == -1)
        
        self.assert_(item == item1)
        
        self.assertRaises(TYBindingItemNotEnoughException, userBag.doAction, self.gameId, item, 'open')
        
        userBag.consumeUnitsCountByKind(self.gameId, moonboxKind, 2, self.timestamp, 0, 0)
        self.assertEqual(item.remaining, 0)
        
        moonkeyKind = hallitem.itemSystem.findItemKind(item_moonkey_id)
        
        openTimesLevel = [(4, 26000), (7, 30000), (100, 40000)]
        totalChip = 0
        totalOpenTimes = 0 
        for _, (openTimes, chipCount) in enumerate(openTimesLevel):
            moonkeyItem = userBag.addItemUnitsByKind(self.gameId, moonkeyKind, openTimes, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
            self.assertEqual(moonkeyItem.remaining, openTimes)
            userBag.addItemUnitsByKind(self.gameId, moonboxKind, openTimes, self.timestamp, 0, 'TEST_ADJUST', 0)
            for i in xrange(openTimes):
                totalChip += chipCount
                totalOpenTimes += 1
                result = userBag.doAction(self.gameId, item, 'open').gotAssetList
                self.assertEqual(item.openTimes, totalOpenTimes)
                self.assertEqual(result[0][0].kindId, 'user:chip')
                self.assertEqual(result[0][1], chipCount)
                self.assertEqual(result[0][2], totalChip)
                
                self.assertEqual(item.remaining, openTimes - i - 1)
                self.assertEqual(moonkeyItem.remaining, openTimes - i - 1)
                self.assertEqual(pkuserchip.getChip(self.userId), totalChip)
        
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        moonboxItem = userBag.findItem(item.itemId)
        self.assertEqual(moonboxItem.itemId, item.itemId)
        self.assertEqual(moonboxItem.remaining, 0)
        self.assertEqual(moonboxItem.openTimes, totalOpenTimes)
        
    def testNewer(self):
        newerGiftKind = hallitem.itemSystem.findItemKind(item_newer_gift_id)
        # 获取用户背包
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(newerGiftKind), [])
        
        newerGiftItem = userBag.addItemUnitsByKind(self.gameId, newerGiftKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assertEqual(newerGiftItem.remaining, 1)
        
        day2Kind = hallitem.itemSystem.findItemKind(item_2day_gift_id)
        
        # 测试打开
        result = userBag.doAction(self.gameId, newerGiftItem, 'open').gotAssetList
        self.assertEqual(newerGiftItem.remaining, 0)
        self.assertEqual(userBag.getAllKindItem(newerGiftKind), [])
        
        self.assertEqual(result[0][0].kindId,
                         TYAssetKindItem.buildKindIdByItemKind(day2Kind))
        
        day2Item = userBag.getItemByKind(day2Kind)
        self.assertEqual(day2Item.remaining, 1)
        
    def testDay2Gift(self):
        day2Kind = hallitem.itemSystem.findItemKind(item_2day_gift_id)
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(day2Kind), [])
        
        userBag.addItemUnitsByKind(self.gameId, day2Kind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)
        day2Item = userBag.getItemByKind(day2Kind)
        self.assertEqual(day2Item.remaining, 1)
        
        # 测试打开
        day3Kind = hallitem.itemSystem.findItemKind(item_3day_gift_id)
        self.assertRaises(TYItemActionConditionNotEnoughException, userBag.doAction, self.gameId, day2Item, 'open')
        self.timestamp += 86400
        result = userBag.doAction(self.gameId, day2Item, 'open').gotAssetList
        self.assertEqual(day2Item.remaining, 0)
        self.assertEqual(userBag.getAllKindItem(day2Item), [])
        
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 100)
        self.assertEqual(result[0][2], 100)
        
        day3Item = userBag.getItemByKind(day3Kind)
        self.assertEqual(day3Item.remaining, 1)
        # 测试打开
        self.assertRaises(TYItemActionConditionNotEnoughException, userBag.doAction, self.gameId, day3Item, 'open')
        self.timestamp += 86400
        result = userBag.doAction(self.gameId, day3Item, 'open').gotAssetList
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 500)
        self.assertEqual(result[0][2], 500+100)
        
    def testDay3Gift(self):
        day3Kind = hallitem.itemSystem.findItemKind(item_3day_gift_id)
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(day3Kind), [])
        
        userBag.addItemUnitsByKind(self.gameId, day3Kind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)
        day3Item = userBag.getItemByKind(day3Kind)
        self.assertEqual(day3Item.remaining, 1)
        
        # 测试打开
        self.assertRaises(TYItemActionConditionNotEnoughException, userBag.doAction, self.gameId, day3Item, 'open')
        self.timestamp += 86400
        
        result = userBag.doAction(self.gameId, day3Item, 'open').gotAssetList
        self.assertEqual(day3Item.remaining, 0)
        self.assertEqual(userBag.getAllKindItem(day3Item), [])
        
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 500)
        self.assertEqual(result[0][2], 500)
    
        self.assertEqual(userBag.getAllItem(), [])
        
    def testMemberCard(self):
        memberCardKind = hallitem.itemSystem.findItemKind(item_membercard_id)
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userBag = userAssets.getUserBag()
        self.assertEqual(userBag.getAllKindItem(memberCardKind), [])
        
        userBag.addItemUnitsByKind(self.gameId, memberCardKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)
        memberCardItem = userBag.getItemByKind(memberCardKind)
        self.assertEqual(memberCardItem.remaining, 0)
        self.assertEqual(memberCardItem.expiresTime, pktimestamp.getDayStartTimestamp(self.timestamp + 86400*2))
        
#         self, item, userAssets,
#                              gameId, isDayFirst, timestamp
        #memberCardKind.processWhenUserLogin(memberCardItem, userAssets, self.gameId, False, self.timestamp)
        
        self.assertRaises(TYItemAlreadyCheckinException, userBag.doAction, self.gameId, memberCardItem, 'checkin')
        
        self.timestamp += 86400
        result = userBag.doAction(self.gameId, memberCardItem, 'checkin').gotAssetList
        #memberCardKind.processWhenUserLogin(memberCardItem, userAssets, self.gameId, False, self.timestamp)
        #memberCardKind.processWhenUserLogin(memberCardItem, userAssets, self.gameId, True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 30000)
        self.assertEqual(result[0][2], 30000)
        
        self.assertRaises(TYItemAlreadyCheckinException, userBag.doAction, self.gameId, memberCardItem, 'checkin')
        
    def testGentlemanStaff(self):
        itemKind = hallitem.itemSystem.findItemKind(item_gentleman_staff_id)
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userBag = userAssets.getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        item = userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assertEqual(item, userBag.getItemByKind(itemKind))
        self.assertEqual(item.remaining, 0)
        self.assertEqual(item.expiresTime, pktimestamp.getDayStartTimestamp(self.timestamp + 86400*2))
        
        # 测试佩戴
        unwearItemList = userBag.doAction(self.gameId, item, 'wear').unweardItemList
        self.assertEqual(unwearItemList, [])
        
        # 测试佩戴异常
        self.assertRaises(TYItemAlreadyWoreException, userBag.doAction, self.gameId, item, 'wear')
        # 
        self.assertEqual(userBag.consumeItemUnits(self.gameId, item, 1, self.timestamp, 0, 0), 1)
        self.assertEqual(item.isWore, 0)
        self.assertTrue(item.isExpires(self.timestamp))
        # 过期时佩戴抛异常
        self.assertRaises(TYItemAlreadyExpiresException, userBag.doAction, self.gameId, item, 'wear')
        
        # 测试取消佩戴
        item = userBag.addItemUnits(self.gameId, item, 1, self.timestamp, 0, 0)
        ftlog.info('*************** item.expiresTime=', item.expiresTime)
        userBag.doAction(self.gameId, item, 'wear')
        
        # 测试佩戴互斥
        itemRevolverKind = hallitem.itemSystem.findItemKind(item_revolver_id)
        revolverItem = userBag.addItemUnitsByKind(self.gameId, itemRevolverKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        # 佩戴revolverItem
        unwearItemList = userBag.doAction(self.gameId, revolverItem, 'wear').unweardItemList
        self.assertEqual(len(unwearItemList), 1)
        self.assertEqual(unwearItemList[0], item)
        
        self.assertEqual(item.isWore, 0)
        self.assertEqual(revolverItem.isWore, 1)

        # 测试修复
        userAssets.addAsset(self.gameId, 'user:chip', 200, self.timestamp, 'TEST_ADJUST', 0)
        self.assertEqual(userBag.consumeItemUnits(self.gameId, item, 1, self.timestamp, 'TEST_ADJUST', 0), 1)
        self.assertRaises(TYAssetNotEnoughException, userBag.doAction, self.gameId, item, 'repair', self.timestamp)
        # 增加修复费
        userAssets.addAsset(self.gameId, 'user:chip', 100, self.timestamp, 'TEST_ADJUST', 0)
        consumeAssetsList = userBag.doAction(self.gameId, item, 'repair').consumeAssetList
        self.assertEqual(item.balance(self.timestamp), 10)
        self.assertEqual(len(consumeAssetsList), 1)
        self.assertEqual(consumeAssetsList[0][0].kindId, 'user:chip')
        self.assertEqual(consumeAssetsList[0][1], 300)
        self.assertEqual(consumeAssetsList[0][2], 0)
        
    def testDoubleCard(self):
        # 测试参赛券
        itemKind = hallitem.itemSystem.findItemKind(item_doublecard_id)
        # 获取用户背包
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        # 添加测试
        item = userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
        self.assert_(item.remaining == 0)
        self.assert_(item.expiresTime == self.timestamp + 3600)
        
        self.timestamp += 1
        self.assertEqual(item.balance(self.timestamp), 0)
        self.assertTrue(not item.isExpires(self.timestamp))
        
        self.timestamp += 3600
        self.assertTrue(item.isDied(self.timestamp))
        self.assertTrue(item.isExpires(self.timestamp))
       
    def testChipBag(self):
        # 测试参赛券
        itemKind = hallitem.itemSystem.findItemKind(item_chip_bag_id)
        componentKindIdList = [item_chip_bag_part1_id, item_chip_bag_part2_id,
                            item_chip_bag_part3_id, item_chip_bag_part4_id,
                            item_chip_bag_part5_id, item_chip_bag_part6_id,
                            item_chip_bag_part7_id]
        
        # 获取用户背包
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        
        for i, componentKindId in enumerate(componentKindIdList):
            componentKind = hallitem.itemSystem.findItemKind(componentKindId)
            ftlog.info('componentKindId=', componentKindId, 'componentKind=', componentKind)
            self.assertIsNotNone(componentKind)
            item = userBag.addItemUnitsByKind(self.gameId, componentKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)[0]
            if i + 1 < len(componentKindIdList):
                #gameId, item, actionName, timestamp=None, params={}
                self.assertRaises(TYItemKindAssembleNotEnoughException, userBag.doAction,
                                  self.gameId, item, 'assemble', self.timestamp, {})
        
        newItem = userBag.doAction(self.gameId, item, 'assemble', self.timestamp, {}).assembledItem
        self.assertEqual(newItem.kindId, item_chip_bag_id)

    def testAlipayGift(self):
        itemKind = hallitem.itemSystem.findItemKind(item_alipay_gift_id)
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userBag = userAssets.getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)
        item = userBag.getItemByKind(itemKind)
        self.assertEqual(item.remaining, 1)
        self.assertEqual(item.expiresTime, -1)
        
        self.assertRaises(TYItemActionConditionNotEnoughException, userBag.doAction, self.gameId, item, 'open')
        pkuserdata.incrAttr(userAssets.userId, 'used_alipay', 1)
        result = userBag.doAction(self.gameId, item, 'open').gotAssetList
        
        self.assertEqual(result[0][0].kindId, 'user:chip')
        self.assertEqual(result[0][1], 30000)
        self.assertEqual(result[0][2], 30000)
        
    def testPresent(self):
        itemKind = hallitem.itemSystem.findItemKind(4138)
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userBag = userAssets.getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)
        item = userBag.getItemByKind(itemKind)
        userBag.doAction(self.gameId, item, 'present', self.timestamp, {'userId':10002, 'count':1})
        
    def testExchange(self):
        itemKind = hallitem.itemSystem.findItemKind(item_phone_card10_id)
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        userBag = userAssets.getUserBag()
        self.assertEqual(userBag.getAllKindItem(itemKind), [])
        
        userBag.addItemUnitsByKind(self.gameId, itemKind, 1, self.timestamp, 0, 'TEST_ADJUST', 0)
        item = userBag.getItemByKind(itemKind)
        result = userBag.doAction(self.gameId, item, 'exchange', self.timestamp, {'phoneNumber':'18618378234'})
        hallexchange.handleExchangeAuditResult(self.userId, result.exchangeId, 0)
    
if __name__ == "__main__":
    #ftlog.log_level = ftlog.LOG_LEVEL_INFO
    unittest.main()
    
