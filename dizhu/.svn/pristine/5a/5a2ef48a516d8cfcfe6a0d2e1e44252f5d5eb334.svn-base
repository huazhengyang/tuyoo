# -*- coding: utf-8 -*-
'''
Created on Oct 20, 2015

@author: hanwf
'''
from dizhu.entity.common.events import UserShareLoginEvent
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import router
from poker.entity.biz import bireport

@markCmdActionHandler
class CommonHandler(BaseMsgPackChecker):
    
    def _check_param_roomIds(self, msg, key, params):
        roomIds = msg.getParam('roomIds')
        if isinstance(roomIds, list) :
            return None, roomIds
        return 'ERROR of roomIds !' + str(roomIds), None

    def _check_param_shareUserId(self, msg, key, params):
        shareUserId = msg.getParam(key)
        if isinstance(shareUserId, int):
            return None, shareUserId
        return 'ERROR of shareUserId !' + str(shareUserId), None
    
    def buildRoomOnlineProtocol(self, gameId, userId, counts, roomIds):
        mo = MsgPack()
        mo.setCmd("room_online")
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        if not roomIds:
            mo.setResult("counts", counts)
        else:
            countsR = {}
            for rid in roomIds:
                countsR[rid] = counts.get(str(rid), 0)
            mo.setResult("counts", countsR)
        return mo
    
    @markCmdActionMethod(cmd='room_online', action="", clientIdVer=0, scope='game')
    def getRoomOnline(self, userId, gameId, roomIds):
        try:
            _, counts, _ = bireport.getRoomOnLineUserCount(gameId)
            mo = self.buildRoomOnlineProtocol(gameId, userId, counts, roomIds)
            ftlog.debug("room_online mo=", mo, 'counts=', counts)
            router.sendToUser(mo, userId)
        except:
            ftlog.error()

    @markCmdActionMethod(cmd='dizhu', action='share_login', clientIdVer=0, lockParamName='', scope='game')
    def doShareLogin(self, userId, shareUserId):
        self._doShareLogin(userId, shareUserId)

    @classmethod
    def _doShareLogin(cls, userId, shareUserId):
        # 广播事件
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().publishEvent(UserShareLoginEvent(DIZHU_GAMEID, userId, shareUserId))
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'share_login')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        mo.setResult('success', 1)
        router.sendToUser(mo, userId)
