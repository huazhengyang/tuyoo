# -*- coding=utf-8
'''
Created on 2015年10月10日

@author: zhaojiangang
'''
import unittest

from biz import mock
from entity.gamelist_test import gamelist_conf
from entity.hallads_test import ads_conf
from entity.hallstore_test import item_conf, products_conf, store_template_conf, \
    store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import fivestarrate
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


fivestar_conf ={
    "channels":{
        "0-hall6.tuyoo.huanle":{
            "rateUrl":"url",
            "rateCountPerDay":500
        }
    }
}

clientIdMap = {
    "IOS_3.6_momo":1,
    "IOS_3.71_tyGuest,weixin.appStore.0-hall6.tuyoo.huanle":2
}

totalCount = 0
def getRateCount(fsRate, timestamp):
    global totalCount
    return totalCount

def incrRateCount(fsRate, timestamp):
    global totalCount
    totalCount += 1
    return totalCount

class TestFiveStar(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.71_tyGuest,weixin.appStore.0-hall6.tuyoo.huanle'
    testContext = HallTestMockContext()
    
    def setUp(self):
        self.testContext.startMock()
        self.rateCountPatch = mock._patch_multiple('hall.entity.fivestarrate',
                                                    _getRateCount=getRateCount,
                                                    _incrRateCount=incrRateCount)
        self.rateCountPatch.start()
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        self.testContext.configure.setJson('game:9999:gamelist', gamelist_conf, 0)
        self.testContext.configure.setJson('game:9999:ads', ads_conf, 0)
        self.testContext.configure.setJson('game:9999:fivestar', fivestar_conf, 0)
        
        
        fivestarrate._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        self.rateCountPatch.stop()
        
    def testFiveStar(self):
        fivestarrate.triggleFiveStarRateIfNeed(self.userId, self.clientId, pktimestamp.getCurrentTimestamp(), 'hello')
        fivestarrate.triggleFiveStarRateIfNeed(self.userId, self.clientId, pktimestamp.getCurrentTimestamp() + 86400*2, 'hello')
        fivestarrate.onFiveStarRated(self.userId, self.clientId, pktimestamp.getCurrentTimestamp())
        fivestarrate.triggleFiveStarRateIfNeed(self.userId, self.clientId, pktimestamp.getCurrentTimestamp() + 86400*10, 'hello1')
        
if __name__ == '__main__':
    unittest.main()
    
    