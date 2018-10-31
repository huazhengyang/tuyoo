# -*- coding:utf-8 -*-
'''
Created on 2017年10月19日

@author: wangyonghui
'''

from dizhu.entity import dizhuhallinfo
from dizhu.games.arenamatch.tableproto import DizhuTableProtoArenaMatch


def getMatchRoomName(self, seat):
    arenaContent = dizhuhallinfo.getArenaMatchProvinceContent(seat.userId, int(seat.player.mixId) if seat.player.mixId else self.bigRoomId, None)
    roomName = seat.player.matchUserInfo.get('roomName')
    if arenaContent:
        roomName = arenaContent.get('showName')
    return roomName or self.table.room.roomConf.get('name', '')

DizhuTableProtoArenaMatch.getMatchRoomName = getMatchRoomName

