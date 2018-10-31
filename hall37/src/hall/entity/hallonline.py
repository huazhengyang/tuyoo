# -*- coding=utf-8

from hall.entity import hallconf
from hall.entity.hallconf import HALL_GAMEID
from hall.game import TGHall
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.entity.dao import onlinedata, userchip
from poker.entity.events.tyevent import OnLineTcpChangedEvent, \
    OnLineGameChangedEvent, OnLineRoomChangedEvent, OnLineAttrChangedEvent
from poker.util import timestamp

_initialize_ok = 0


def _initialize():
    global _initialize_ok
    if not _initialize_ok:
        TGHall.getEventBus().subscribe(OnLineTcpChangedEvent, processOnLineTcpChangedEvent)
        TGHall.getEventBus().subscribe(OnLineGameChangedEvent, processOnLineGameChangedEvent)
        TGHall.getEventBus().subscribe(OnLineRoomChangedEvent, processOnLineRoomChangedEvent)
        TGHall.getEventBus().subscribe(OnLineAttrChangedEvent, processOnLineAttrChangedEvent)
        _initialize_ok = 1


def processOnLineTcpChangedEvent(evt):
    userId = evt.userId
    isOnline = evt.isOnline
    # 设置在线状态和在线用户集合列表, 离线时,所有通过setGameOnline设置的该用户数据均已经被删除
    onlinedata.setOnlineState(userId, isOnline)
    if not isOnline:
        ctfull = timestamp.formatTimeMs()
        gamedata.setGameAttr(userId, HALL_GAMEID, 'offlineTime', ctfull)
        return
    # 计算其他的数据在线分组
    # 分金币数量级别列表 — 德州等LED引导
    richchip = hallconf.getHallPublic().get('online_rich_limit', 100000)
    if richchip > 0:
        chip = userchip.getUserChipAll(userId)
        if chip > richchip:
            onlinedata.setGameOnline(userId, HALL_GAMEID, 'rich_online_users')
    # 分版本
    # 分等级（可能是大师分，或经验值）
    # 新老用户（是否第一天注册）
    # 有没有玩过某些游戏
    # 是否有道具
    # 是否充值
    # 是否满足比赛报名条件
    pass


def processOnLineGameChangedEvent(evt):
    userId = evt.userId
    gameId = evt.gameId
    isEnter = evt.isEnter
    # 分游戏列表 — 德州等LED引导
    if isEnter:
        onlinedata.setGameOnline(userId, gameId, 'game')
        onlinedata.setGameEnter(userId, gameId)
    else:
        onlinedata.setGameOffline(userId, gameId, 'game')
        onlinedata.setGameLeave(userId, gameId)


def processOnLineRoomChangedEvent(evt):
    userId = evt.userId
    gameId = evt.gameId
    roomId = evt.roomId
    assert (roomId in gdata.bigRoomidsMap)  # 这个地方一定是bigRoomId
    isEnter = evt.isEnter
    # 分房间列表 — 德州等LED引导
    if isEnter:
        onlinedata.setGameOnline(userId, gameId, str(roomId) + ':room')
    else:
        onlinedata.setGameOffline(userId, gameId, str(roomId) + ':room')


def processOnLineAttrChangedEvent(evt):
    userId = evt.userId
    #     gameId = evt.gameId
    attName = evt.attName
    attFinalValue = evt.attFinalValue
    #     attDetalValue = evt.attDetalValue
    if attName == 'chip':
        richchip = hallconf.getHallPublic().get('online_rich_limit', 100000)
        if richchip > 0:
            if attFinalValue > richchip:
                onlinedata.setGameOnline(userId, HALL_GAMEID, 'rich_online_users')
            else:
                onlinedata.setGameOffline(userId, HALL_GAMEID, 'rich_online_users')
