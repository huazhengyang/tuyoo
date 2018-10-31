# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from hall.game import TGHall
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.dao import onlinedata
from poker.entity.events.tyevent import OnLineTcpChangedEvent
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.entity.game.rooms.room import TYRoom
from poker.entity.biz import integrate
from poker.util import strutil


def _donOnline(userId, clientId):
    # TODO 此方法预留给hall5进行补丁操作
    pass

@markCmdActionHandler
class OnlineTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass


    @markCmdActionMethod(cmd='user', action='online', clientIdVer=0)
    def doUserOnline(self, userId, clientId):
        _donOnline(userId, clientId)
        evt = OnLineTcpChangedEvent(userId, HALL_GAMEID, 1)
        TGHall.getEventBus().publishEvent(evt)
        # 通知push服务
        self._notifyPushUserOnlineStateChanged(userId, 1, clientId)

    @markCmdActionMethod(cmd='user', action='offline', clientIdVer=0)
    def doUserOffline(self, userId, clientId):
        evt = OnLineTcpChangedEvent(userId, HALL_GAMEID, 0)
        TGHall.getEventBus().publishEvent(evt)
        # 补发room_leave消息
        olist = onlinedata.getOnlineLocList(userId)
        ftlog.debug('doUserOffline onlines->', olist)
        for ol in olist :
            roomId, _, _ = ol[0], ol[1], ol[2]
            if roomId > 0 :
                msg = MsgPack()
                msg.setCmdAction('room', 'leave')
                msg.setParam('userId', userId)
                msg.setParam('roomId', roomId)
                msg.setParam('gameId', strutil.getGameIdFromInstanceRoomId(roomId))
                msg.setParam('clientId', clientId)
                msg.setParam('reason', TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION)
                router.sendRoomServer(msg, roomId)
        
        # offline_geoc处理
        onlinedata.setUserGeoOffline(userId, HALL_GAMEID)
        # 通知push服务
        self._notifyPushUserOnlineStateChanged(userId, 0, clientId)
        

    def _notifyPushUserOnlineStateChanged(self, userId, isOnline, clientId):
        if integrate.isEnabled('pushserver') :
            try:
                mo = MsgPack()
                mo.setCmd('push_set_user_tag')
                mo.setParam('appId', HALL_GAMEID)
                mo.setParam('userId', userId)
                mo.setParam('clientId', clientId)
                if isOnline :
                    mo.setParam('tag', 'online')
                else:
                    mo.setParam('tag', 'offline')
                integrate.sendTo('pushserver', mo)
            except:
                ftlog.error()

