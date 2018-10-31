# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaojiangang
'''
import unittest

from entity.gamelist_test import gamelist_conf
from entity.hallstore_test import clientIdMap, item_conf, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import hallitem, hallvip, hallgamelist, hallads
from test_base import HallTestMockContext


ads_conf = {
    "ads":[
        {
            "id":1,
            "pic": "${http_download}/hall/ads/imgs/ads_11.png",
            "clickable":0,
            "startTime":"2015-07-16 00:00:00",
            "endTime":"2015-08-31 23:59:00"
        },
        {
            "id":2,
            "pic": "${http_download}/hall/ads/imgs/ads_12.png",
            "clickable":0,
            "startTime":"2015-07-16 00:00:00",
            "endTime":"2015-12-31 23:59:00"
        },
        {
            "id":3,
            "pic": "${http_download}/hall/ads/imgs/ads_13.png",
            "clickable":0,
            "startTime":"2015-07-16 00:00:00",
            "endTime":"2015-12-31 23:59:00"
        },
        {
            "id":4,
            "pic": "${http_download}/hall/ads/imgs/ads_10.png",
            "clickable":0,
            "startTime":"2015-08-01 00:00:00",
            "endTime":"2015-08-06 00:00:00"
        }
    ],
    "templates":{
        "default":{
            "name":"default",
            "interval":5,
            "ads":[
                1, 3, 4
            ]
        }
    }
}


class TestGameList(unittest.TestCase):
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
        self.testContext.configure.setJson('game:9999:gamelist', gamelist_conf, 0)
        self.testContext.configure.setJson('game:9999:ads', ads_conf, 0)
        
        hallitem._initialize()
        hallvip._initialize()
        hallgamelist._initialize()
        hallads._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testQueryAds(self):
        adsTemplate = hallads.queryAds(self.gameId, self.userId, self.clientId)
        print adsTemplate.name, adsTemplate.adsList
        
if __name__ == '__main__':
    unittest.main()
    
    
