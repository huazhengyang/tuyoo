# -*- coding:utf-8 -*-
'''
Created on 2016年6月13日

@author: zhaojiangang
'''
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.util import strutil


def getOnlineLocListByGameId(userId, gameId, clientId):
    ret = []
    locList = onlinedata.getOnlineLocList(userId)
    for roomId, tableId, seatId in locList:
        try:
            roomGameId = strutil.getGameIdFromInstanceRoomId(roomId)
            if (roomGameId == gameId and tableId != 0 and seatId != 0):
                ret.append((roomGameId, roomId, tableId, seatId))
        except:
            ftlog.error('dizhuonlinedata.getOnlineLocListByGameId userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'roomId=', roomId)
    return ret

def _leaveFromMatchs(userId):
    from dizhu.servers.util.rpc import match_remote
    from dizhu.servers.util.rpc.match_remote import UserMatchInfo
    userMatchInfoMap = match_remote.loadAllUserMatchInfo(DIZHU_GAMEID, userId)
    if ftlog.is_debug():
        ftlog.debug('dizhuonlinedata._leaveFromMatchs userId=', userId,
                    'infos=', [(rid, umi.state) for rid, umi in userMatchInfoMap.iteritems()])
    for _, userMatchInfo in userMatchInfoMap.iteritems():
        if userMatchInfo.state == UserMatchInfo.ST_SIGNIN:
            msg = MsgPack()
            msg.setCmdAction('room', 'leave')
            msg.setParam('userId', userId)
            msg.setParam('roomId', userMatchInfo.ctrlRoomId)
            msg.setParam('gameId', strutil.getGameIdFromInstanceRoomId(userMatchInfo.ctrlRoomId))
            msg.setParam('reason', TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION)
            router.sendRoomServer(msg, userMatchInfo.ctrlRoomId)
    
def onUserOffline(userId):
    _leaveFromMatchs(userId)


