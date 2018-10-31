# -*- coding=utf-8
'''
Created on 2015年7月6日

@author: zhaojiangang
'''
import unittest

from biz.mock import patch
from entity.hallstore_test import clientIdMap, item_conf, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import hallitem, hallvip, halldailycheckin
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


dailycheckin_conf = {
    "rewards":[
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":300}
            ]
        },
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":600}
            ]
        },
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":1000}
            ]
        },
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":1000}
            ]
        },
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":1000}
            ]
        },
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":1000}
            ]
        },
        {
            "typeId":"FixedContent",
            "items":[
                {"itemId":"user:chip", "count":10000}
            ]
        }
    ]
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
        
        hallitem._initialize()
        hallvip._initialize()
        halldailycheckin._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        self.pktimestampPatcher.stop()
        
    def testGetStates(self):
        states = halldailycheckin.dailyCheckin.getStates(self.gameId, self.userId, self.timestamp)
        self.assertEqual(len(states), len(dailycheckin_conf['rewards']))
        self.assertEqual(states[0]['st'], 1)
        self.assertEqual(states[0]['rewards'], halldailycheckin.dailyCheckin.getRewardContent(0))
        for i in range(1, 7):
            self.assertEqual(states[i]['st'], 0)
            self.assertEqual(states[i]['rewards'], halldailycheckin.dailyCheckin.getRewardContent(i))
        
if __name__ == '__main__':
    unittest.main()
    
    