# coding=UTF-8
'''quickstart测试模块
'''


__author__ = [
    '"Zhouhao" <zhouhao@tuyoogame.com>', 
]

import unittest
import stackless
import random

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.reactor import mainloop
from freetime.core.timer import FTTimer
import freetime.entity.service as ftsvr
import freetime.entity.config as ftcon

import poker.protocol.startup as pstartup
from poker.entity.configure import configure, gdata
from poker.entity.dao import onlinedata, userchip, userdata

from dizhu.gametable.quick_start import DizhuQuickStartDispatcher


class Test(unittest.TestCase):


    def setUp(self):
        config_redis=("172.16.8.111", 6379, 0)
#         config_redis=("192.168.10.73", 6379, 0)
#         serverId = "GR60011"
        serverId = "UT001"
        ftcon.global_config["server_id"] = serverId
        ftcon.initFromRedis(serverId, config_redis)
        ftsvr._init_fun = pstartup.initialize
        stackless.tasklet(mainloop)()
        self.testSuit()
        stackless.run()


    def tearDown(self):
        pass


    def testSuit(self):
        testStartTime = 0 # seconds
        
        testStartTime +=1
        for _ in xrange(1):
            FTTimer(testStartTime, self.testReconnect)
        
        testStartTime +=1
        for _ in xrange(1):
            FTTimer(testStartTime, self.testQuickStart)
            
        testStartTime +=1
        for _ in xrange(1):
            FTTimer(testStartTime, self.testQuickEnterRoom)
            
        testStartTime +=1
        for _ in xrange(1):
            FTTimer(testStartTime, self.testQuickEnterTable)
         
                
    def testReconnect(self):
        '''测试断线重连
        '''
        gameId = 6
        userId = 1234
        roomId = 60110001
        tableId = 1
        seatId = 3
        clientId = "tuyoo_4.0_hall6"
        
        onlinedata.setOnlineState(userId, onlinedata.ONLINE)
        onlinedata.addOnlineLoc(userId, roomId, tableId, seatId)
        
        msg = MsgPack()
        msg.setCmd("quick_start")
        msg.setParam("userId", userId)
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        msg.setParam("clientId", clientId)
        print '='*30
        print msg
        DizhuQuickStartDispatcher.dispatchQuickStart(msg)
        print '='*30

        
    def testQuickStart(self):
        '''测试快速开始'''
        gameId = 6
        userId = 1234
        roomId = 0
        tableId = 0
        chip = 800
        clientId = "Android_3.501_tuyoo.YDJD.0-hall6.apphui.happy"
        
        onlinedata.setOnlineState(userId, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId)
        
        userdata.setAttr(userId, "sessionClientId", clientId)
#         datas = sessiondata._getUserSessionValues(userId)
#         ftlog.debug("|userId, session:", userId, datas)
        
        oldChip = userchip.getChip(userId)
        userchip.incrChip(userId, gameId, chip - oldChip, 0, "GM_ADJUST_COIN", 0, 0)
        
        msg = MsgPack()
        msg.setCmd("quick_start")
        msg.setParam("gameId", gameId)
        msg.setParam("userId", userId)
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        msg.setParam("clientId", clientId)
        print '='*30
        print msg
        DizhuQuickStartDispatcher.dispatchQuickStart(msg)
        print '='*30
        
    def testQuickEnterRoom(self):
        '''测试快速进入房间'''
        gameId = 6
        userId = 1234
        roomId = 60110001
        tableId = 0
        clientId = "tuyoo_4.0_hall6"
        
        onlinedata.setOnlineState(userId, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId)
        
        msg = MsgPack()
        msg.setCmd("quick_start")
        msg.setParam("userId", userId)
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        msg.setParam("clientId", clientId)
        print '='*30
        print msg
        DizhuQuickStartDispatcher.dispatchQuickStart(msg)
        print '='*30


    def testQuickEnterTable(self):
        '''测试快速进入桌子'''
        gameId = 6
        userId = 1234
        roomId = 60110001
        tableId = 1
        clientId = "tuyoo_4.0_hall6"
        
        onlinedata.setOnlineState(userId, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId)
        
        msg = MsgPack()
        msg.setCmd("quick_start")
        msg.setParam("userId", userId)
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        msg.setParam("clientId", clientId)
        print '='*30
        print msg
        DizhuQuickStartDispatcher.dispatchQuickStart(msg)
        print '='*30

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testQuickStart', 'Test.testReconnect']
    unittest.main()