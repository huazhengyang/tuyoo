# -*- coding=utf-8
'''
Created on 2015年7月31日

@author: zhaojiangang
'''
import unittest

from redis.client import StrictRedis

from biz.mock import patch
from entity.hallbenefits_test import benefits_conf
from entity.hallstore_test import clientIdMap, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
import freetime.util.log as ftlog
from hall.entity import hallitem, hallvip, hallbenefits, hallshare, hall_exmall
from poker.entity.dao import daobase
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


share_conf = {
    "shares": [
        {
            "desc": [
                {
                    "conditions": [],
                    "value": "来玩途游斗地主，输入我的推荐码\\${promoteCode}，一起拿红包，赢话费！"
                }
            ],
            "mail": "恭喜您获得1000金币的分享奖励！",
            "maxRewardCount": 1,
            "rewardTimeCycle":{
                "typeId":"timeCycle.life",
                "timePeriod":{
                    "start":"2017-07-25 00:00:00",
                    "stop":"2017-07-26 00:00:00"
                }
            },
            "rewardContent": {
                "items": [
                    {
                        "count": 1000,
                        "itemId": "user:chip"
                    }
                ],
                "typeId": "FixedContent"
            },
            "shareIcon": [
                {
                    "conditions": [],
                    "value": ""
                }
            ],
            "shareId": 10086,
            "smsDesc": "来玩途游斗地主，输入我的推荐码\\${promoteCode}，一起拿红包，赢话费！下载地址：\\${url}",
            "title": [
                {
                    "conditions": [],
                    "value": "亲爱的小伙伴"
                }
            ],
            "typeId": "hall.share.promote",
            "url": [
                {
                    "conditions": [],
                    "value": "http://001.wx.fx.tuyoo.com/gamesites.html"
                }
            ]
        }
    ]
}

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

class TestHallShare(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
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
        
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        self.testContext.configure.setJson('game:9999:benefits', benefits_conf, 0)
        self.testContext.configure.setJson('game:9999:share', share_conf, 0)
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.pktimestampPatcher = patch('poker.util.timestamp.getCurrentTimestamp', self.getCurrentTimestamp)
        self.pktimestampPatcher.start()
        
        hallitem._initialize()
        hallvip._initialize()
        hallbenefits._initialize()
        hallshare._initialize()
        
        daobase.executeUserCmd(10001, 'del', 'share.status:9999:10001')
        
    def tearDown(self):
        self.pktimestampPatcher.stop()
        self.testContext.stopMock()
        
    def getCurrentTimestamp(self):
        return self.timestamp
    
    def testLoad(self):
        shareList = hallshare.getAllShare()
        for share in shareList:
            timestamp = self.timestamp
            if share.rewardTimeCycle.isTimestampIn(timestamp):
                ok, rewardCount = hallshare.incrRewardCount(10001, share, timestamp)
                self.assertEqual((ok, rewardCount), (True, 1))
                hallshare.sendReward(self.gameId, self.userId, share, 'test')
                self.assertFalse(hallshare.canReward(10001, share, timestamp))
            
            daobase.executeUserCmd(10001, 'del', 'share.status:9999:10001')
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            timestamp += 86400
            self.assertFalse(hallshare.canReward(10001, share, timestamp))
    
    def testPerDay(self):
        share_conf = {
            "shares": [
                {
                    "desc": [
                        {
                            "conditions": [],
                            "value": "来玩途游斗地主，输入我的推荐码\\${promoteCode}，一起拿红包，赢话费！"
                        }
                    ],
                    "mail": "恭喜您获得1000金币的分享奖励！",
                    "maxRewardCount": 1,
                    "rewardTimeCycle":{
                        "typeId":"timeCycle.perDay"
                    },
                    "rewardContent": {
                        "items": [
                            {
                                "count": 1000,
                                "itemId": "user:chip"
                            }
                        ],
                        "typeId": "FixedContent"
                    },
                    "shareIcon": [
                        {
                            "conditions": [],
                            "value": ""
                        }
                    ],
                    "shareId": 10086,
                    "smsDesc": "来玩途游斗地主，输入我的推荐码\\${promoteCode}，一起拿红包，赢话费！下载地址：\\${url}",
                    "title": [
                        {
                            "conditions": [],
                            "value": "亲爱的小伙伴"
                        }
                    ],
                    "typeId": "hall.share.promote",
                    "url": [
                        {
                            "conditions": [],
                            "value": "http://001.wx.fx.tuyoo.com/gamesites.html"
                        }
                    ]
                }
            ]
        }
        self.testContext.configure.setJson('game:9999:share', share_conf, 0)
        hallshare._reloadConf()
        shareList = hallshare.getAllShare()
        for share in shareList:
            timestamp = self.timestamp
            if share.rewardTimeCycle.isTimestampIn(timestamp):
                ok, rewardCount = hallshare.incrRewardCount(10001, share, timestamp)
                self.assertEqual((ok, rewardCount), (True, 1))
                hallshare.sendReward(self.gameId, self.userId, share, 'test')
                self.assertFalse(hallshare.canReward(10001, share, timestamp))
            
            daobase.executeUserCmd(10001, 'del', 'share.status:9999:10001')
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            timestamp += 86400
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            
            ok, rewardCount = hallshare.incrRewardCount(10001, share, timestamp)
            self.assertEqual((ok, rewardCount), (True, 1))
            hallshare.sendReward(self.gameId, self.userId, share, 'test')
            self.assertFalse(hallshare.canReward(10001, share, timestamp))
            
            timestamp += 86400
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            timestamp += 86400
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            timestamp += 86400
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            timestamp += 86400
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
    
    def testRewardCountN(self):
        share_conf = {
            "shares": [
                {
                    "desc": [
                        {
                            "conditions": [],
                            "value": "来玩途游斗地主，输入我的推荐码\\${promoteCode}，一起拿红包，赢话费！"
                        }
                    ],
                    "mail": "恭喜您获得1000金币的分享奖励！",
                    "maxRewardCount": 10,
                    "rewardTimeCycle":{
                        "typeId":"timeCycle.perDay"
                    },
                    "rewardContent": {
                        "items": [
                            {
                                "count": 1000,
                                "itemId": "user:chip"
                            }
                        ],
                        "typeId": "FixedContent"
                    },
                    "shareIcon": [
                        {
                            "conditions": [],
                            "value": ""
                        }
                    ],
                    "shareId": 10086,
                    "smsDesc": "来玩途游斗地主，输入我的推荐码\\${promoteCode}，一起拿红包，赢话费！下载地址：\\${url}",
                    "title": [
                        {
                            "conditions": [],
                            "value": "亲爱的小伙伴"
                        }
                    ],
                    "typeId": "hall.share.promote",
                    "url": [
                        {
                            "conditions": [],
                            "value": "http://001.wx.fx.tuyoo.com/gamesites.html"
                        }
                    ]
                }
            ]
        }
        self.testContext.configure.setJson('game:9999:share', share_conf, 0)
        hallshare._reloadConf()
        shareList = hallshare.getAllShare()
        for share in shareList:
            timestamp = self.timestamp
            for i in xrange(share.maxRewardCount):
                ok, rewardCount = hallshare.incrRewardCount(10001, share, timestamp)
                self.assertEqual((ok, rewardCount), (True, i + 1))
                hallshare.sendReward(self.gameId, self.userId, share, 'test')
            self.assertFalse(hallshare.canReward(10001, share, timestamp))
            
            timestamp += 86400
            self.assertTrue(hallshare.canReward(10001, share, timestamp))
            for i in xrange(share.maxRewardCount):
                ok, rewardCount = hallshare.incrRewardCount(10001, share, timestamp)
                self.assertEqual((ok, rewardCount), (True, i + 1))
                hallshare.sendReward(self.gameId, self.userId, share, 'test')
            self.assertFalse(hallshare.canReward(10001, share, timestamp))
            
if __name__ == '__main__':
    unittest.main()


