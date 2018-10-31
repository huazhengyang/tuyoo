# -*- coding:utf-8 -*-
'''
Created on 2017年2月7日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhucomm.room.base import DizhuRoom
from poker.entity.game.tables.table_player import ROBOT_USER_ID_MAX
import freetime.util.log as ftlog

class DizhuTableRoom(DizhuRoom):
    def __init__(self, roomDefine):
        super(DizhuTableRoom, self).__init__(roomDefine)
        self.maptable = {}
        
    def findTable(self, tableId):
        return self.maptable.get(tableId)
    
    def newTable(self, tableId):
        raise NotImplementedError

    def getRoomOnlineInfo(self):
        ucount, pcount, ocount = 0, 0, 0
        for t in self.maptable.values():
            players = t.table.getPlayers()
            if players:
                pcount += 1
                ucount += len(players)
        return ucount, pcount, ocount

    def getRoomOnlineInfoDetail(self):
        ucount, pcount = 0, 0
        tables = {}
        for t in self.maptable.values():
            players = t.table.getPlayers()
            if players:
                pcount += 1
                ucount += len(players)
            userIds = [seat.userId for seat in t.seats]
            userIds.append(t.proto.getTableState())
            tables[t.tableId] = userIds
        return ucount, pcount, tables
    
    def isRobot(self, player):
        if not player or player.userId <= 0:
            return False
        
        if player.userId > 0 and player.userId <= ROBOT_USER_ID_MAX:
            return True
        
        if (player.userId > ROBOT_USER_ID_MAX
            and isstring(player.clientId)
            and player.clientId.find('robot') >= 0):
            return True
        return False
    
    def getRobotUserCount(self):
        count = 0
        for t in self.maptable.values():
            for seat in t.table.seats:
                if self.isRobot(seat.player):
                    count += 1
        return count
    
    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        tableCtrl = self.findTable(tableId)
        if tableCtrl:
            seat = tableCtrl.table.getSeatByUserId(userId)
            if seat:
                return seat.seatId, 0
        return -1, 0
    
    def _onConfReload(self):
        ftlog.info('DizhuTableRoom._onConfReload',
                   'roomId=', self.roomId)
        for tableCtrl in self.maptable.values():
            tableCtrl.reloadConf()


