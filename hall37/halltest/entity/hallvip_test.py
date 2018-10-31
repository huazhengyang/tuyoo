# -*- coding=utf-8
'''
Created on 2015年6月30日

@author: zhaojiangang
'''
import unittest

from entity.hallstore_test import clientIdMap, item_conf, products_conf, \
    store_template_conf, store_default_conf
from hall.entity import hallvip, hallitem
from test_base import HallTestMockContext
import poker.util.timestamp as pktimestamp

vip_conf = {
    "assistanceChip":3000,
    "assistanceChipUpperLimit":100,
    "level_up_desc":"恭喜您，成为VIP\\${curLevel}级用户，又有好礼可以拿啦！",
    "got_gift_desc":"恭喜您，获得了$\\{rewardContent}！",
    "got_assistance_desc":"恭喜您，领取了\\${rewardContent}的江湖救急金！",
    "levelUpPayOrder":{
       "shelves":["lessbuychip"],
       "buyTypes":["direct"]
   },
    "levels":[
        {
            "level":0,
            "name":"VIP0",
            "exp":0,
            "pic":"${http_download}/hall/vip/vip0.png",
            "desc":[],
            "nextLevel":1,
            "expDesc":"您还不是VIP呢，仅需充值${deltaRmb}元就能成为VIP"
        },
        {
            "level":1,
            "name":"VIP1",
            "exp":60,
            "pic":"${http_download}/hall/vip/vip1.png",
            "desc":[
                "每日可领取5次免费金币",
                "赠送神秘烟斗3天",
                "赠送3次VIP江湖救急",
                "VIP专享地主、农民造型"
            ],
            "rewardContent":{
                "typeId":"FixedContent",
                "desc":"3次江湖救急",
                "items":[
                    {"itemId":"game:assistance", "count":3}
                ]
            },
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"神秘烟斗3天",
                "items":[
                    {"itemId":"item:4117", "count":3}, 
                ]
            },
            "nextLevel":2,
            "expDesc":"您再充${deltaRmb}元就能达到${nextVipLevelName}"
        },
        {
            "level":2,
            "name":"VIP2",
            "exp":350,
            "pic":"${http_download}/hall/vip/vip2.png",
            "desc":[
                "每次免费金币增加1000",
                "赠送神秘礼帽3天",
                "赠送3次VIP江湖救急"
            ],
            "rewardContent":{
                "typeId":"FixedContent",
                "desc":"3次江湖救急",
                "items":[
                    {"itemId":"game:assistance", "count":3}
                ]
            },
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"神秘礼帽3天",
                "items":[
                    {"itemId":"item:4101", "count":3}
                ]
            },
            "nextLevel":3,
            "expDesc":"您再充${deltaRmb}元就能达到${nextVipLevelName}"
        },
        {
            "level":3,
            "name":"VIP3",
            "exp":2000,
            "pic":"${http_download}/hall/vip/vip3.png",
            "desc":[
                "赠送青春派头像各3天",
                "赠送绅士礼帽3天",
                "赠送3次VIP江湖救急",
                "VIP专享地主、农民造型"
            ],
            "rewardContent":{
                "typeId":"FixedContent",
                "desc":"3次江湖救急",
                "items":[
                    {"itemId":"game:assistance", "count":3}
                ]
            },
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"绅士礼帽3天+青春派头像各3天",
                "items":[
                    {"itemId":"item:4102", "count":3},
                    {"itemId":"item:4109", "count":3},
                    {"itemId":"item:4110", "count":3}
                ]
            },
            "nextLevel":4,
            "expDesc":"您再充${deltaRmb}元就能达到${nextVipLevelName}"
        },
        {
            "level":4,
            "name":"VIP4",
            "exp":5000,
            "pic":"${http_download}/hall/vip/vip4.png",
            "desc":[
                "赠送魅力族头像各1天",
                "互动表情魅力值增加50%",
                "赠送牛仔帽3天",
                "赠送幸运项链10天"
            ],
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"牛仔帽3天+幸运项链10天",
                "items":[
                    {"itemId":"item:4111", "count":1},
                    {"itemId":"item:4112", "count":1},
                    {"itemId":"item:4103", "count":3}, 
                    {"itemId":"item:4113", "count":10}
                ]
            },
            "nextLevel":5,
            "expDesc":""
        },
        {
            "level":5,
            "name":"VIP5",
            "exp":20000,
            "pic":"${http_download}/hall/vip/vip5.png",
            "desc":[
                "赠送命运酒杯10天",
                "赠送精灵花冠3天"
            ],
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"命运酒杯10天+精灵花冠3天",
                "items":[
                    {"itemId":"item:4114", "count":10}, 
                    {"itemId":"item:4105", "count":3}
                ]
            },
            "nextLevel":6,
            "expDesc":""
        },
        {
            "level":6,
            "name":"红卡VIP",
            "exp":100000,
            "pic":"${http_download}/hall/vip/vip6.png",
            "desc":[
                "赠送绅士手杖10天",
                "赠送多彩皇冠3天"
            ],
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"1000金币",
                "items":[
                    {"itemId":"item:4115", "count":10}, 
                    {"itemId":"item:4104", "count":3}
                ]
            },
            "nextLevel":7,
            "expDesc":""
        },
        {
            "level":7,
            "name":"金卡VIP",
            "exp":500000,
            "pic":"${http_download}/hall/vip/vip7.png",
            "desc":[
                "赠送恶魔角饰3天",
                "赠送左轮手枪10天"
            ],
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"1000金币",
                "items":[
                    {"itemId":"item:4106", "count":3}, 
                    {"itemId":"item:4118", "count":10}
                ]
            },
            "nextLevel":8,
            "expDesc":""
        },
        {
            "level":8,
            "name":"黑卡VIP",
            "exp":10000000,
            "pic":"${http_download}/hall/vip/vip8.png",
            "desc":[
                "赠送天使之翼7天",
                "赠送地狱之戟10天",
                "赠送天使头环3天",
                "尊贵昵称显示"
            ],
            "giftContent":{
                "typeId":"FixedContent",
                "desc":"1000金币",
                "items":[
                    {"itemId":"item:4121", "count":7}, 
                    {"itemId":"item:4120", "count":10},
                    {"itemId":"item:4107", "count":3}
                ]
            },
            "expDesc":""
        }
    ]
}

class TestVIP(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        hallitem._initialize()
        hallvip._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testAddUserVipExp(self):
        hallvip.userVipSystem.addUserVipExp(self.gameId, self.userId, 100, 0, 0)
        userVip = hallvip.userVipSystem.getUserVip(self.userId)
        self.assertEqual(userVip.vipExp, 100)
        self.assertEqual(userVip.vipLevel.level, 1)
        hallvip.userVipSystem.gainUserVipGift(self.gameId, self.userId, 1)
        hallvip.userVipSystem.addUserVipExp(self.gameId, self.userId, 260, 0, 0)
        userVip = hallvip.userVipSystem.getUserVip(self.userId)
        self.assertEqual(userVip.vipExp, 360)
        self.assertEqual(userVip.vipLevel.level, 2)
        
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        
        _assetKind, count, final = userAssets.addAsset(self.gameId, 'game:assistance', 1,
                                                       pktimestamp.getCurrentTimestamp(), 'TEST_ADJUST', 0)
        self.assertEqual(count, 1)
        self.assertEqual(final, 7)
        
        assistanceCount = hallvip.userVipSystem.getAssistanceCount(self.gameId, self.userId)
        self.assertEqual(assistanceCount, 7)
        
        consumeCount, finalCount, sendChip = hallvip.userVipSystem.gainAssistance(self.gameId, self.userId)
        self.assertEqual(consumeCount, 1)
        self.assertEqual(finalCount, 6)
        self.assertEqual(sendChip, hallvip.vipSystem.getAssistanceChip())
        
if __name__ == '__main__':
    unittest.main()

