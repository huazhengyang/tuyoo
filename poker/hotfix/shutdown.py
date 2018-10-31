# -*- coding: utf-8 -*-
"""
Created on 2017年09月18日

@author: zqh
请不要删除或随意修改此文件，此py文件作为停服前的关闭房间、检测功能而使用
"""
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
ftlog.info('ROOM doShutDown check !')
for (rid, room) in gdata.rooms().items():
    if (not hasattr(TYRoom, 'ROOM_STATUS_RUN')):
        results[rid] = 100
        continue
    if (not hasattr(room, 'runStatus')):
        room.runStatus = TYRoom.ROOM_STATUS_RUN
    ftlog.info('ROOM STATUS->', rid, room.runStatus)
    if (room.runStatus == TYRoom.ROOM_STATUS_RUN):
        try:
            room.runStatus = TYRoom.ROOM_STATUS_SHUTDOWN_GO
            room.doShutDown()
        except:
            ftlog.info()
        ftlog.info('ROOM STATUS->', rid, room.runStatus)
    results[rid] = room.runStatus
ftlog.info('ROOM doShutDown status all =', results)