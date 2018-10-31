# -*- coding: utf-8 -*-
'''
Created on 2015-5-12
@author: zqh
'''

from dizhu.resource import loadResource
from dizhu.robot.robotuser import RobotUser
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.entity.robot.robot import TYRobotManager
from poker.util import strutil


class DizhuRobotManager(TYRobotManager):


    def __init__(self):
        super(DizhuRobotManager, self).__init__()
        res = loadResource('robot_info.json')
        rinfo = strutil.loads(res)
        baseSnsId = rinfo['basesnsid'] + gdata.serverId()
        users = []
        names = rinfo["names"]
        for x in xrange(len(names)) :
            name = names[x]
            snsId = baseSnsId + '_' + str(x)
            users.append(RobotUser(None, snsId, name)) 
        self.freeRobotUsers = users
        ftlog.debug('robot user count ->', len(users))

