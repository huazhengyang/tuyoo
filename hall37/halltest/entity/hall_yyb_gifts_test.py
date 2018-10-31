# -*- coding:utf-8 -*-
'''
Created on 2017年11月27日

@author: zhaojiangang
'''
import unittest

from redis.client import StrictRedis

from biz.mock import patch
from hall.entity import hallitem, hall_yyb_gifts
from poker.entity.dao import daobase, userdata
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext
from poker.entity.events.tyevent import EventUserLogin, GameOverEvent
from hall.game import TGHall


item_conf = item_conf = {
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

clientIdMap = {
    "IOS_3.6_momo":1,
    "IOS_3.70_360.360.0-hall6.360.day":13232,
    "IOS_3.97_weixin,tuyoo.appStore,wxwap,alipaywap.0-hall6.appStore.xinhuanle6":13233,
    "IOS_3.97_weixin,tuyoo.appStore,wxwap,alipaywap.0-hall7.appStore.xinhuanle6":13234,
    "IOS_3.780_tuyoo.appStore,weixinPay,alipay.0-hall6.appStore.baohuang":13235
}

conf = {
    "gifts":[
        {
            "typeId":"yyb.gift:newUser",
            "kindId":99990001,
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":100
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:dailyLogin",
            "kindId":99990002,
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":200
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:exclusive",
            "kindId":99990003,
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":300
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:ddzRound",
            "kindId":99990004,
            "round":10,
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":400
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:back30Day",
            "kindId":99990005,
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990006,
            "desc":"等级豪礼>=30RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":10000
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990007,
            "desc":"等级豪礼>=5000RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990008,
            "desc":"等级豪礼>=30000RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990009,
            "desc":"等级豪礼>=80000RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990010,
            "desc":"每日福利>=30RMB每日领一次",
            "cycle":{
                   "typeId":"day"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990011,
            "desc":"每日福利>=5000RMB每日领一次",
            "cycle":{
                   "typeId":"day"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990012,
            "desc":"每日福利>=30000RMB每日领一次",
            "cycle":{
                   "typeId":"day"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990013,
            "desc":"每日福利>=80000RMB每日领一次",
            "cycle":{
                   "typeId":"day"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990014,
            "desc":"途游斗地主累计付费>=300RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990015,
            "desc":"途游斗地主累计付费>=2000RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        },
        {
            "typeId":"yyb.gift:vplus",
            "kindId":99990016,
            "desc":"途游斗地主累计付费>=8000RMB终身领一次",
            "cycle":{
                   "typeId":"life"
               },
            "reward":{
                   "typeId":"FixedContent",
                   "items":[
                       {
                           "itemId":"user:chip",
                           "count":500
                       }
                   ]
               }
        }
    ]
}

class TestYYBGifts(unittest.TestCase):
    userId = 10001
    gameId = 9999
    clientId = 'IOS_3.70_360.360.0-hall6.360.day'
    testContext = HallTestMockContext()
    
    def runRedisCmd(self, *cmds):
        return self.redisClient.execute_command(*cmds)
    
    def runUserRedisCmd(self, userId, *cmds):
        return self.redisClient.execute_command(*cmds)
    
    def setUp(self):
        self.testContext.startMock()
        self.redisClient = StrictRedis('127.0.0.1', 6379, 0)
        daobase.executeMixCmd = self.runRedisCmd
        daobase._executePayDataCmd = self.runRedisCmd
        daobase.executeUserCmd = self.runUserRedisCmd
        daobase.sendUserCmd = self.runUserRedisCmd
        
        daobase.executeUserCmd(self.userId, 'del', 'yyb.gifts:%s' % (self.userId))
        self.testContext.configure.setJson('poker:global', {'config.game.ids':[6,9999]}, None)
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('poker:map.clientid', clientIdMap, None)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:yyb.gifts', conf, 0)
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.pktimestampPatcher = patch('poker.util.timestamp.getCurrentTimestamp', self.getCurrentTimestamp)
        self.pktimestampPatcher.start()
        
        userdata.setAttr(self.userId, 'lastAuthorTime', '2017-10-27 00:00:00.000')
        userdata.setAttr(self.userId, 'authorTime', '2017-11-28 00:00:00.000')
        
        hallitem._initialize()
        hall_yyb_gifts._initialize()
        
    def tearDown(self):
        self.pktimestampPatcher.stop()
        self.testContext.stopMock()
        
    def getCurrentTimestamp(self):
        return self.timestamp
    
    def testEvents(self):
        events = [
                  [EventUserLogin(self.userId, self.gameId, True, True, self.clientId), 1],
                  #[GameOverEvent(self.userId, 6, self.clientId, 60011001, 600110010001, 0, 0, 0, 0), 10]
                ]
        for event, count in events:
            for _ in xrange(count):
                TGHall.getEventBus().publishEvent(event)
        
        self.assertEqual(hall_yyb_gifts.gainUserGift(self.userId, 99990006, self.timestamp)[0], hall_yyb_gifts.STATE_GAIN)
        self.assertEqual(hall_yyb_gifts.gainUserGift(self.userId, 99990006, self.timestamp)[0], hall_yyb_gifts.STATE_ALREADY_GAIN)
        
        self.assertEqual(hall_yyb_gifts.gainUserGift(self.userId, 99990010, self.timestamp)[0], hall_yyb_gifts.STATE_GAIN)
        self.assertEqual(hall_yyb_gifts.gainUserGift(self.userId, 99990010, self.timestamp)[0], hall_yyb_gifts.STATE_ALREADY_GAIN)


#         self.timestamp += 86400
#         for event, count in events:
#             for _ in xrange(count):
#                 TGHall.getEventBus().publishEvent(event)
#         
#         hall_yyb_gifts.gainUserGift(self.userId, 99990004, self.timestamp)


if __name__ == '__main__':
    unittest.main()


