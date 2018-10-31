# -*- coding: utf-8 -*-
"""
Created on 2016年1月17日

@author: zhaojiangang
"""
import random
import stackless
from freetime.core.reactor import mainloop
import freetime.util.log as ftlog
from poker.entity.game.rooms.group_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.group_match_ctrl.interfacetest import MatchStatusDaoMem, SignIFMem, TableControllerTest, PlayerNotifierTest, MatchRewardsTest, UserInfoLoaderTest
from poker.entity.game.rooms.group_match_ctrl.match import MatchMaster, MatchArea, MatchMasterStubLocal, MatchAreaStubLocal
from poker.entity.game.rooms.group_match_ctrl.models import TableManager
from poker.entity.game.rooms.group_match_ctrl.testbase import MyRoom, match_conf
from poker.entity.game.rooms.group_match_ctrl.utils import HeartbeatAble, Heartbeat

def buildMatchMaster(roomId, matchId, matchConf):
    pass

def buildMatchArea(roomId, matchId, matchConf, master):
    pass
CLIENT_IDS = ['Android_3.372_tuyoo.weakChinaMobile.0-hall7.ydmm.happyxinchun', 'Winpc_3.70_360.360.0-hall8.360.texas', 'Android_3.72_tyOneKey,tyAccount,tyGuest.tuyoo.0-hall8.duokunew.day', 'Android_3.363_pps.pps,weakChinaMobile,woStore,aigame.0-hall6.pps.dj']

class MatchChecker(HeartbeatAble, ):

    def __init__(self, master, areas, userInfoLoader):
        pass

    def start(self):
        pass

    def _doHeartbeat(self):
        pass

    def _isAllReady(self):
        pass

    def _signinToMatch(self, area, userIds):
        pass
if (__name__ == '__main__'):
    ftlog.initLog('groupmatch.log', './logs/')
    matchId = 6057
    masterRoomId = 60571
    areaRoomIds = [60571, 60572, 60573]
    matchConf = MatchConfig.parse(6, 60571, 6057, '\xe6\xbb\xa13\xe4\xba\xba\xe5\xbc\x80\xe8\xb5\x9b', match_conf['matchConf'])
    areas = []
    userInfoLoader = UserInfoLoaderTest()
    master = buildMatchMaster(masterRoomId, matchId, matchConf)
    for areaRoomId in areaRoomIds:
        area = buildMatchArea(areaRoomId, matchId, matchConf, master)
        areas.append(area)
        area.userInfoLoader = userInfoLoader
        master.addAreaStub(MatchAreaStubLocal(master, area))
    master.start()
    for area in areas:
        area.start()
    MatchChecker(master, areas, userInfoLoader).start()
    stackless.tasklet(mainloop)()
    stackless.run()