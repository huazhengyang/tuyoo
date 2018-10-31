# coding=UTF-8
'''
'''
from poker.entity.dao import onlinedata, userdata

__author__ = [
    '"Zhouhao" <zhouhao@tuyoogame.com>', 
]

import unittest
import random
import sys
import os
import signal

from freetime.util import log as ftlog, processtool
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTTimer

from poker.entity.configure import gdata
    
class Test(unittest.TestCase):

    def setUp(self):
        pass

        
    def tearDown(self):
        pass


    def testBigMatchRoom(self):
        serverId = "GR60121"
        
        process =processtool.getOneProcessByKeyword("pypy run.py %s" % serverId)
        print "process of %s : %s" % (serverId, process)
        if process :
            os.kill(process.pid, signal.SIGINT)
        
        config_redis=("172.16.0.204", 6379, 0)
#         config_redis=("192.168.10.73", 6379, 0)
        
        sys.argv = sys.argv[0:1]
        sys.argv.append(serverId)
        sys.argv.append(config_redis[0])
        sys.argv.append(config_redis[1])
        sys.argv.append(config_redis[2])
        print sys.path
        print sys.argv
        
        self.asyncTestSuit()
        
        import run
        run.main()


    def asyncTestSuit(self):
        ftlog.debug("=" * 30)
        testStartTime = 0 # seconds
     
#         testStartTime +=1
#         for _ in xrange(1):
#             FTTimer(testStartTime, self.asyncTest3PlayerMatch)


        testStartTime +=1
        for _ in xrange(1):
            FTTimer(testStartTime, self.asyncTest3PlayerMatchWithRobot)

        ftlog.debug("=" * 30)
   
    def asyncTest3PlayerMatchWithRobot(self):
        ftlog.debug("-" * 30)
        ctrlRoomId = 60121000
#         clientId = "Android_3.501_tuyoo.YDJD.0-hall6.apphui.happy" 
        clientId =  "Android_3.372_momo.momo.0-hall6.momo.momo"
        userId1 = random.randint(10000, 20000)
        onlinedata.setOnlineState(userId1, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId1)
        userdata.setAttr(userId1, "sessionClientId", clientId)
        
        bigMatchRoom = gdata.rooms()[ctrlRoomId]
        
        bigMatchRoom.doEnter(userId1)
        
        bigMatchRoom.doSignin(userId1)
      
    def asyncTest3PlayerMatch(self):
        ftlog.debug("-" * 30)
        ctrlRoomId = 60121000
#         clientId = "Android_3.501_tuyoo.YDJD.0-hall6.apphui.happy" 
        clientId =  "Android_3.372_momo.momo.0-hall6.momo.momo"
        userId1 = random.randint(10000, 20000)
        onlinedata.setOnlineState(userId1, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId1)
        userdata.setAttr(userId1, "sessionClientId", clientId)
        
        userId2 = random.randint(10000, 20000)
        onlinedata.setOnlineState(userId2, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId2)
        userdata.setAttr(userId2, "sessionClientId", clientId)
        
        userId3 = random.randint(10000, 20000)
        onlinedata.setOnlineState(userId3, onlinedata.ONLINE)
        onlinedata.cleanOnlineLoc(userId3)
        userdata.setAttr(userId3, "sessionClientId", clientId)
        
        bigMatchRoom = gdata.rooms()[ctrlRoomId]
        
        bigMatchRoom.doEnter(userId1)
        bigMatchRoom.doEnter(userId2)
        bigMatchRoom.doEnter(userId3)
        
        bigMatchRoom.doSignin(userId1)
        bigMatchRoom.doSignin(userId2)
        bigMatchRoom.doSignin(userId3)
        

if __name__ == "__main__":
#     sys.argv = ['', 'Test.testBigMatchRoom']
    unittest.main()