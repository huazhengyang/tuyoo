# -*- coding:utf-8 -*-
'''
Created on 2016年3月23日

@author: zhaojiangang
'''
from dizhucomm.entity.events import UserTableWinloseEvent
from poker.entity.configure import gdata
from dizhu.entity import dizhuled
from poker.entity.dao import userdata
import freetime.util.log as ftlog

class XingyaoLed(object):
    ROOM_IDS = [6015]
    WINCHIP_LIMIT = 1600000
    
    @classmethod
    def initialize(cls):
        from dizhu.game import TGDizhu
        eventBus = TGDizhu.getEventBus()
        eventBus.subscribe(UserTableWinloseEvent, cls.onWinlose)
    
    @classmethod
    def needSendLed(cls, event):
        if not event.winlose.isWin or event.winlose.deltaChip <= cls.WINCHIP_LIMIT:
            return False
        bigRoomId = gdata.getBigRoomId(event.roomId)
        return bigRoomId in cls.ROOM_IDS
    
    @classmethod
    def onWinlose(cls, event):
        needSendLed = cls.needSendLed(event)
        if ftlog.is_debug():
            ftlog.debug('XingyaoLed.onWinlose gameId=', event.gameId,
                        'userId=', event.userId,
                        'roomId=', event.roomId,
                        'bigRoomId=', gdata.getBigRoomId(event.roomId),
                        'isWin=', event.winlose.isWin,
                        'deltaChip=', event.winlose.deltaChip,
                        'WINCHIP_LIMIT=', cls.WINCHIP_LIMIT,
                        'ROOM_IDS=', cls.ROOM_IDS,
                        'needSendLed=', needSendLed)
        if needSendLed:
            userName = userdata.getAttr(event.userId, 'name')
            dizhuled.sendLed('恭喜%s在经典星耀大师场赢取金币%s！' % (userName, event.winlose.deltaChip))
        

