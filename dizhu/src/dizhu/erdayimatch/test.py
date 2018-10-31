# -*- coding:utf-8 -*-
'''
Created on 2016年7月14日

@author: zhaojiangang
'''
import os
import random
import sys

from dizhu.erdayimatch.interfaceimpl import ErdayiTable, ErdayiMatchFactory
from freetime.core import reactor
import freetime.util.log as ftlog
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.erdayi_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.erdayi_match_ctrl.const import MatchFinishReason
from poker.entity.game.rooms.erdayi_match_ctrl.interface import MatchStage, \
    TableController
from poker.entity.game.rooms.erdayi_match_ctrl.interfacetest import \
    MatchStatusDaoMem, SigninRecordDaoTest, PlayerNotifierTest, MatchRewardsTest, \
    MatchUserIFTest, SignerInfoLoaderTest
from poker.entity.game.rooms.erdayi_match_ctrl.match import MatchMaster, \
    MatchAreaLocal, MatchInst
from poker.entity.game.rooms.erdayi_match_ctrl.models import TableManager
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger, \
    HeartbeatAble


match_conf = {
    "buyinchip" : 0,
    "controlServerCount" : 1,
    "controlTableCount" : 0,
    "dummyUserCount" : 0,
    "gameServerCount" : 20,
    "gameTableCount" : 500,
    "goodCard" : 0,
    "hasrobot" : 0,
    "ismatch" : 1,
    "matchConf" : {
      "matchId":10040838946101,
      "desc" : "开赛时间：21:30 \n报名费用：免费",
      "fees" : [],
      "rank.rewards" : [
        {
          "desc" : "价值1499元的游戏耳机",
          "ranking" : {
            "end" : 1,
            "start" : 1
          },
          "rewards" : [
            {
              "count" : 1,
              "itemId" : "item:4151"
            }
          ]
        },
        {
          "desc" : "10万金币",
          "ranking" : {
            "end" : 4,
            "start" : 2
          },
          "rewards" : [
            {
              "count" : 100000,
              "itemId" : "user:chip"
            }
          ]
        },
        {
          "desc" : "1万金币",
          "ranking" : {
            "end" : 10,
            "start" : 5
          },
          "rewards" : [
            {
              "count" : 10000,
              "itemId" : "user:chip"
            }
          ]
        }
      ],
      "stages" : [
        {
          "animation.type" : 0,
          "card.count" : 1,
          "name" : "海选赛",
          "rise.user.count" : 24,
          "rise.user.refer" : 30,
          "seat.principles" : 1,
          "chip.base":100,
          "grouping.type": 2,
          "grouping.user.count": 30,
          "type" : 1
        },
        {
          "animation.type" : 1,
          "card.count" : 2,
          "name" : "24强赛",
          "rise.user.count" : 12,
          "seat.principles" : 2,
          "chip.base":100,
          "type" : 2
        },
        {
          "animation.type" : 1,
          "card.count" : 2,
          "name" : "12强赛",
          "rise.user.count" : 6,
          "seat.principles" : 2,
          "chip.base":100,
          "type" : 2
        },
        {
          "animation.type" : 3,
          "card.count" : 2,
          "name" : "6强赛",
          "rise.user.count" : 3,
          "seat.principles" : 2,
          "chip.base":100,
          "type" : 2
        },
        {
          "animation.type" : 2,
          "card.count" : 2,
          "name" : "决赛",
          "rise.user.count" : 1,
          "seat.principles" : 2,
          "chip.base":100,
          "type" : 2
        }
      ],
      "start" : {
        "fee.type" : 0,
        "maxplaytime" : 7200,
        "prepare.times" : 0,
        "signin.times" : 2400,
        "table.times":2,
        "start.speed" : 1,
        "times" : {
          "days" : {
            "first":"",
            "interval":"1d",
            "count":100,
          },
          "times_in_day" : {
            "first":"00:00",
            "interval":1,
            "count":2000
          }
        },
        "type" : 2,
        "user.groupsize" : 2000,
        "user.maxsize" : 2000,
        "user.minsize" : 3,
        "user.next.group" : 0
      },
      "table.seat.count" : 1,
      "tips" : {
        "infos" : [
          "积分相同时，按报名先后顺序确定名次。",
          "积分低于淘汰分数线会被淘汰，称打立出局。",
          "打立赛制有局数上限，打满局数会等待他人。",
          "打立阶段，轮空时会记1局游戏。",
          "定局赛制，指打固定局数后按积分排名。",
          "每局会按照开局时的底分结算。",
          "比赛流局时，可能会有积分惩罚。"
        ],
        "interval" : 5
      }
    },
    "maxCoin" : -1,
    "maxCoinQS" : -1,
    "maxLevel" : -1,
    "minCoin" : -1,
    "minCoinQS" : -1,
    "name" : "途游阿里赛",
    "playDesc" : "",
    "playMode" : "happy",
    "robotUserCallUpTime" : 10,
    "robotUserMaxCount" : 0,
    "robotUserOpTime" : [
      5,
      12
    ],
    "roomFee" : 45,
    "roomMutil" : 50,
    "sendCoupon" : 0,
    "showCard" : 0,
    "tableConf" : {
      "autochange" : 1,
      "basebet" : 1,
      "basemulti" : 1,
      "cardNoteChip" : 500,
      "canchat" : 0,
      "coin2chip" : 1,
      "grab" : 1,
      "gslam" : 128,
      "lucky" : 0,
      "maxSeatN" : 3,
      "optime" : 20,
      "passtime" : 5,
      "rangpaiMultiType" : 1,
      "robottimes" : 1,
      "tbbox" : 0,
      "unticheat" : 1
    },
    "typeName" : "erdayi_match",
    "winDesc" : ""
  }

class MyRoom(object):
    def __init__(self, roomId):
        self.roomId = roomId
        self.gameId = 6
        
class MyStage(MatchStage):
    def __init__(self, stageConf):
        super(MyStage, self).__init__(stageConf)
        self._count = 0
        self._logger = Logger()
        self._logger.add('stageIndex', self.stageIndex)
        
    def start(self):
        self._logger.info('MatchStage.start')
        
    def kill(self, reason):
        self._logger.info('MatchStage.kill',
                          'reason=', reason)
    
    def finish(self, reason):
        self._logger.info('MatchStage.finish',
                          'reason=', reason)
    
    def processStage(self):
        self._logger.info('MatchStage.processStage',
                          'count=', self._count)
        self._count += 1
        if self._count >= 10:
            self.group.finishGroup(MatchFinishReason.FINISH)
    
class TableControllerTest(TableController):
    def __init__(self, area):
        self.area = area
        self.busyTables = set()
        self._logger = Logger()
        
    def startTable(self, table):
        '''
        让桌子开始
        '''
        self.busyTables.add(table)
        self._logger.info('TableControllerTest.startTable tableId=',
                          table.tableId)
    
    def clearTable(self, table):
        '''
        清理桌子
        '''
        self.busyTables.discard(table)
        self._logger.info('TableControllerTest.clearTable tableId=',
                          table.tableId)
        
    def updateTableInfo(self, table):
        '''
        桌子信息变化
        '''
        self._logger.info('TableControllerTest.updateTableInfo tableId=',
                          table.tableId)
    
    def userReconnect(self, table, seat):
        '''
        用户坐下
        '''
        self._logger.info('TableControllerTest.userReconnect tableId=',
                          table.tableId)

def addTables(tableManager, roomId, baseId, count):
    for i in xrange(count):
        tableManager.addTable(ErdayiTable(6, roomId, baseId + i + 1, 3))
        
def buildMatchMaster(roomId, matchConf):
    room = MyRoom(roomId)
    tableManager = TableManager(room, matchConf.tableSeatCount)
    tableManager.addTables(60571, 0, 100)
    master = MatchMaster(room, matchConf)
    master.matchStatusDao = MatchStatusDaoMem()
    master.matchFactory = ErdayiMatchFactory()
    return master

def buildMatchArea(roomId, matchConf, master):
    room = MyRoom(roomId)
    tableManager = TableManager(room, matchConf.tableSeatCount)
    tableManager.addTables(roomId, 1, 100)
    area = MatchAreaLocal(master, room, matchConf)
    area.signinRecordDao = SigninRecordDaoTest()
    area.tableManager = tableManager
    area.tableController = TableControllerTest(area)
    area.playerNotifier = PlayerNotifierTest()
    area.matchRewards = MatchRewardsTest()
    area.matchUserIF = MatchUserIFTest()
    area.signerInfoLoader = SignerInfoLoaderTest()
    area.matchFactory = ErdayiMatchFactory()
    return area

CLIENT_IDS = [
    'Android_3.372_tuyoo.weakChinaMobile.0-hall7.ydmm.happyxinchun',
    'Winpc_3.70_360.360.0-hall8.360.texas',
    'Android_3.72_tyOneKey,tyAccount,tyGuest.tuyoo.0-hall8.duokunew.day',
    'Android_3.363_pps.pps,weakChinaMobile,woStore,aigame.0-hall6.pps.dj'
]

class MatchChecker(HeartbeatAble):
    def __init__(self, master, areas, signerInfoLoader):
        super(MatchChecker, self).__init__(1)
        self._master = master
        self._areaMap = {area.roomId:area for area in areas}
        self._userId = 1040000001
        self._signerCountPerArea = 30
        self.signerInfoLoader = signerInfoLoader
        self.userIds = [self._userId + i for i in xrange(len(self._areaMap) * self._signerCountPerArea)]
        for userId in self.userIds:
            clientId = CLIENT_IDS[random.randint(0, len(CLIENT_IDS) - 1)]
            self.signerInfoLoader.setUserAttrs(i + 1, {'name':'user%s'%(userId),
                                                     'sessionClientId':clientId,
                                                     'snsId':'sns%s'%(userId),
                                                     'gameClientVer':0})
            
    def _doHeartbeat(self):
        isAllReady = self._isAllReady()
        ftlog.info('MatchChecker._doHeartbeat isAllReady=', isAllReady)
        if isAllReady:
            # 报名到master
            for i, area in enumerate(self._areaMap.values()):
                self._signinToMatch(area, self.userIds[i*self._signerCountPerArea:i*self._signerCountPerArea+self._signerCountPerArea])
            self.stopHeart()
            
    def _isAllReady(self):
        if (not self._master._instCtrl
            or self._master._instCtrl.state < MatchInst.ST_SIGNIN):
            return False
        for area in self._areaMap.values():
            if not area.curInst:
                return False
        return True

    def _signinToMatch(self, area, userIds):
        for userId in userIds:
            area.curInst.signin(userId, 0)
            
def loadRoomInfo(gameId, roomId):
    return None

def saveRoomInfo(gameId, roomInfo):
    pass

def removeRoomInfo(gameId, roomId):
    pass
    
if __name__ == '__main__':
    if sys.getdefaultencoding().lower() != "utf-8" :
        reload(sys)
        sys.setdefaultencoding("utf-8")
    #ftlog.initLog('groupmatch.log', './logs/')
    masterRoomId = 60571
    areaRoomIds = [60571]
    roominfo.saveRoomInfo = saveRoomInfo
    roominfo.removeRoomInfo = removeRoomInfo
    roominfo.loadRoomInfo = loadRoomInfo
    matchConf = MatchConfig.parse(6, 60571, 10040838946101, '满3人开赛', match_conf['matchConf'])
    signerInfoLoader = SignerInfoLoaderTest()
    areas = []
    master = buildMatchMaster(masterRoomId, matchConf)
    for areaRoomId in areaRoomIds:
        area = buildMatchArea(areaRoomId, matchConf, master)
        ftlog.info('main areaRoomId=', areaRoomId,
                   'idleTableCount=', area.tableManager.idleTableCount)
        areas.append(area)
        master.addArea(area)
        
    master.startHeart()
    MatchChecker(master, areas, signerInfoLoader).startHeart()
    reactor.mainloop()

    