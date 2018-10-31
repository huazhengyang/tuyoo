# -*- coding=utf-8
'''
Created on 2015年7月6日

@author: zhaojiangang
'''
import unittest

from biz.mock import patch
from dizhu.entity import dizhuflipcard
from entity.halldailycheckin_test import dailycheckin_conf
from entity.hallstore_test import clientIdMap, item_conf, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import hallitem, hallvip, halldailycheckin
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


dizhuflipcard_conf = {
    "flipPolicies":[
        {
            "registerDays":{"start":0, "stop":0},
            "randoms":[
                {"weight":1, "item":{"itemId":"user:coupon", "start":100, "stop":200}}
            ]
        },
        {
            "registerDays":{"start":1, "stop":2},
            "randoms":[
                {"weight":30, "item":{"itemId":"user:coupon", "start":5, "stop":15}},
                {"weight":30, "item":{"itemId":"user:chip", "start":1000, "stop":1000}},
                {"weight":30, "item":{"itemId":"item:1007", "start":5, "stop":5}},
                {"weight":10, "item":{"itemId":"item:2003", "start":3, "stop":3}}
            ]
        },
        {
            "registerDays":{"start":1, "stop":2},
            "randoms":[
                {"weight":380, "item":{"itemId":"item:1007", "start":2, "stop":2}},
                {"weight":149, "item":{"itemId":"item:1007", "start":4, "stop":7}},
                {"weight":70, "item":{"itemId":"item:3002", "start":1, "stop":1}},
                {"weight":50, "item":{"itemId":"user:coupon", "start":1, "stop":3}},
                {"weight":200, "item":{"itemId":"item:2003", "start":1, "stop":1}},
                {"weight":150, "item":{"itemId":"user:chip", "start":600, "stop":1500}},
                {"weight":10, "item":{"itemId":"item:3001", "start":1, "stop":1}}
            ]
        }    
    ],
    "paddings":{
        "randoms":[
            {"weight":10, "item":{"itemId":"item:1007", "start":1, "stop":10}},
            {"weight":5, "item":{"itemId":"item:3002", "start":2, "stop":5}},
            {"weight":20, "item":{"itemId":"user:coupon", "start":1, "stop":400}},
            {"weight":10, "item":{"itemId":"item:2003", "start":1, "stop":1}},
            {"weight":10, "item":{"itemId":"item:2003", "start":2, "stop":5}},
            {"weight":5, "item":{"itemId":"user:chip", "start":500, "stop":1000}},
            {"weight":15, "item":{"itemId":"user:coupon", "start":1, "stop":5}},
            {"weight":3, "item":{"itemId":"item:3001", "start":1, "stop":1}},
            {"weight":10, "item":{"itemId":"user:chip", "start":1000, "stop":1500}},
            {"weight":10, "item":{"itemId":"user:chip", "start":300, "stop":1200}}
        ]
    }
}


class TestDailyCheckin(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    
    def getCurrentTimestamp(self):
        return self.timestamp
    
    def setUp(self):
        self.testContext.startMock()
        
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.pktimestampPatcher = patch('poker.util.timestamp.getCurrentTimestamp', self.getCurrentTimestamp)
        self.pktimestampPatcher.start()
        
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        self.testContext.configure.setJson('game:9999:dailycheckin', dailycheckin_conf, 0)
        
        self.testContext.configure.setJson('game:6:flipcard', dizhuflipcard_conf, 0)
        self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', 0)
        
        #def setGameAttr(self, userId, gameId, attrname, value):
        hallitem._initialize()
        hallvip._initialize()
        halldailycheckin._initialize()
        dizhuflipcard._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        self.pktimestampPatcher.stop()
        
    def testLoadStatus(self):
        status = dizhuflipcard.flipCard.loadStatus(self.userId, self.timestamp)
        self.assertEqual(status.getRemFlipCount(), 1)
        
        self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', 1)
        status = dizhuflipcard.flipCard.loadStatus(self.userId, self.timestamp)
        self.assertEqual(status.getRemFlipCount(), 2)
        
        self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', 2)
        status = dizhuflipcard.flipCard.loadStatus(self.userId, self.timestamp)
        self.assertEqual(status.getRemFlipCount(), 3)
        for i in xrange(10):
            self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', i+3)
            status = dizhuflipcard.flipCard.loadStatus(self.userId, self.timestamp)
            self.assertEqual(status.getRemFlipCount(), 3)
        
        self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', 0)
        flipped, status, reward = dizhuflipcard.flipCard.flipCard(self.userId, 0, self.timestamp)
        self.assertEqual(flipped, True)
        
        flipped, status, reward = dizhuflipcard.flipCard.flipCard(self.userId, 1, self.timestamp)
        self.assertEqual(flipped, False)
        
        self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', 1)
        flipped, status, reward = dizhuflipcard.flipCard.flipCard(self.userId, 1, self.timestamp)
        self.assertEqual(flipped, True)
        
        self.timestamp = self.timestamp + 86400
        flipped, status, reward = dizhuflipcard.flipCard.flipCard(self.userId, 0, self.timestamp)
        self.assertEqual(flipped, True)
        flipped, status, reward = dizhuflipcard.flipCard.flipCard(self.userId, 1, self.timestamp)
        self.assertEqual(flipped, True)
        
if __name__ == '__main__':
    unittest.main()
    
