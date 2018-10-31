# -*- coding=utf-8
'''
Created on 2015年9月18日
hall.menulist单元测试
@author: zhaol
'''

import unittest
from entity.hallstore_test import clientIdMap
from hall.entity import hallmenulist
from test_base import HallTestMockContext

menulist_conf = {
    "templates":{
        "default":["shop", "activity", "bag", "account", "friends", "rank", "message", "help", "settings"],
        "default_mobile":["shop", "activity", "bag", "account", "rank", "message", "help", "settings"]
    }
}

class TestMenuList(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:menulist', menulist_conf, 0)
        hallmenulist._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testQueryMenuList(self):
        print 'testQueryMenuList'
        menuTemplate = hallmenulist.getClientMenuList(self.clientId)
        print menuTemplate
        
if __name__ == '__main__':
    unittest.main()
    
    
