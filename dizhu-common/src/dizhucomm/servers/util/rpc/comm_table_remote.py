# -*- coding:utf-8 -*-
'''
Created on 2017年2月10日

@author: zhaojiangang
'''
from dizhucomm.entity import treasurebox, commconf, gameexp
from dizhucomm.entity.events import UseTableEmoticonEvent, UserTablePlayEvent, \
    UserTableCallEvent, UserLevelGrowEvent
import freetime.util.log as ftlog
from hall.entity import datachangenotify, sdkclient
from hall.servers.util.rpc import user_remote
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import userchip, daoconst, userdata, gamedata, daobase
from poker.entity.game.game import TYGame
from poker.protocol.rpccore import markRpcCall
from poker.servers.rpc import roommgr
from poker.util import strutil
import math


def recoverUserAttr(value, recoverType, defaultValue):
    '''
    校验检查用户的基本信息内容, 返回检查变化后的值
    '''
    try:
        value = recoverType(value)
    except:
        ftlog.warn('ERROR !! recoverUserAttr', value, recoverType, defaultValue)
        value = recoverType(defaultValue)
    return value

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def getUserChips(gameId, userId, tableId):
    tchip = userchip.getTableChip(userId, gameId, tableId)
    chip = userchip.getChip(userId)
    return tchip, chip

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableTreasureBox(gameId, userId, bigRoomId):
    data = treasurebox.doTreasureBox(gameId, userId, bigRoomId)
    if ftlog.is_debug():
        ftlog.debug('table_remote.doTableTreasureBox',
                    'gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'ret=', data)
    return data

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableThrowEmojiFrom(gameId, userId, roomId, bigRoomId, tableId,
                          emojiId, minchip, price, charmDelta, clientId):
    eventId = 'EMOTICON_%s_CONSUME' % (emojiId.upper())
    trueDelta, final = userchip.incrChipLimit(userId,
                                              gameId,
                                              -price, price + minchip, -1,
                                               daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                               eventId, roomId, clientId)
    # 发送通知
    if trueDelta != 0:
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')

    if trueDelta != -price:
        return 0, trueDelta, final
    bireport.gcoin('out.chip.emoticon', gameId, price)
    # 魅力值
    userdata.incrCharm(userId, charmDelta)
    bireport.gcoin('out.smilies.' + emojiId + '.' + str(bigRoomId), gameId, price)
    
    TYGame(gameId).getEventBus().publishEvent(UseTableEmoticonEvent(gameId, userId, roomId, tableId, emojiId, price))
    return 1, trueDelta, final

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableThrowEmojiFrom_3_775(gameId, userId, roomId, bigRoomId, tableId,
                                emojiId, minchip, price, charmDelta, clientId,
                                count, throwWhenChipZero=False):
    assert(count > 0)
    if 0 == price:
        return count, 0, 0
    
    eventId = 'EMOTICON_%s_CONSUME' % (emojiId.upper())
    costChip = price * count
    trueDelta, final = userchip.incrChipLimit(userId,
                                              gameId, 
                                              -costChip,
                                              -1, -1,
                                              daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                              eventId,
                                              roomId,
                                              clientId)
    # 没有金币则返回0
    if trueDelta == 0:
        return 0, trueDelta, final
    
    # 真实的发送个数，金币不足也至少发送一次
    realCostChip = abs(trueDelta)
    realCount = max(1, int(math.ceil(realCostChip/price)))
    if realCostChip > 0:
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
        bireport.gcoin('out.chip.emoticon', gameId, realCostChip)
        bireport.gcoin('out.smilies.' + emojiId + '.' + str(bigRoomId), gameId, realCostChip)
    # 魅力值
    userdata.incrCharm(userId, charmDelta * realCount)
    eventBus = gdata.games()[gameId].getEventBus()
    if eventBus:
        eventBus.publishEvent(UseTableEmoticonEvent(gameId, userId, roomId, tableId, emojiId, price, realCount))
    return realCount, trueDelta, final


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableThrowEmojiFromBursts(gameId, userId, roomId, tableId,
                                emojiId, charmDelta, burstsConf):

    assert (burstsConf.get('cost', {}).get('count', 0) > 0)

    cost = burstsConf.get('cost')
    contentItemList = [cost]
    eventId = 'EMOTICON_%s_CONSUME' % (emojiId.upper())
    assetKindId, count = user_remote.consumeAssets(gameId, userId, contentItemList, eventId, roomId)
    if assetKindId:
        return 0

    # 魅力值
    userdata.incrCharm(userId, charmDelta * burstsConf.get('count', 1))
    eventBus = gdata.games()[gameId].getEventBus()
    if eventBus:
        eventBus.publishEvent(UseTableEmoticonEvent(gameId, userId, roomId, tableId, emojiId, cost.get('count', 0), burstsConf.get('count', 0)))
    return burstsConf.get('count', 0)


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableThrowEmojiTo(gameId, userId, charmDelta, count=1):
    # 魅力值
    userdata.incrCharm(userId, charmDelta * count)
    return count

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableGameCall(gameId, roomId, tableId, roundId, userId, callValue, isGrab):
    eventBus = gdata.games()[gameId].getEventBus()
    if eventBus:
        eventBus.publishEvent(UserTableCallEvent(gameId,
                                                 userId,
                                                 roomId,
                                                 tableId,
                                                 callValue,
                                                 isGrab))
    return 1

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def doTableGameStart(gameId, roomId, tableId, roundId, dizhuUserId, baseCardType, baseScore, userId, **kwargs):
    # 魅力值
    bigRoomId = gdata.roomIdDefineMap()[roomId].bigRoomId
    tbinfo = treasurebox.updateTreasureBoxStart(gameId, userId, kwargs.get('mixConfRoomId') or bigRoomId)
    # 更新每个人的winrate
    checkSetMedal(gameId, userId, baseScore, True, 0)
    # 更新牌桌的winrate
    roomConfigure = gdata.roomIdDefineMap()[roomId].configure
    if ftlog.is_debug():
        ftlog.debug('comm_table_remote.doTableGameStart userId=', userId,
                    'roomId, tableId, roundId=', roomId, tableId, roundId,
                    'typeName=', roomConfigure.get('typeName'))
    if roomConfigure.get('typeName') in ['dizhu_normal', 'dizhu_mix']:
        increaceChipTableWinrate(gameId, userId, True, 0)
    # 触发每个人的游戏开始事件
    eventBus = gdata.games()[gameId].getEventBus()
    if eventBus:
        eventBus.publishEvent(UserTablePlayEvent(gameId,
                                                 userId,
                                                 roomId,
                                                 tableId,
                                                 baseCardType,
                                                 dizhuUserId))
    return tbinfo


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def addUserQuitLoc(gameId, userId, roomId, tableId, seatId, timestamp):
    try:
        bigRoomId = strutil.getBigRoomIdFromInstanceRoomId(roomId)
        d = {
            'timestamp': timestamp,
            'roomId': roomId,
            'tableId': tableId,
            'seatId': seatId
        }
        return daobase.executeUserCmd(userId, 'HSET', 'quitol' + ':' + str(gameId) + ':' + str(userId), str(bigRoomId), strutil.dumps(d))

    except:
        ftlog.error('comm_table_remote.addUserQuitLoc gameId=', gameId,
                    'roomId=', roomId,
                    'tableId=', tableId,
                    'seatId=', seatId,
                    'userId=', userId)
        return None


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def checkUserQuitLoc(gameId, userId, roomId, clientId):
    gid = strutil.getBigRoomIdFromInstanceRoomId(roomId)
    ret = daobase.executeUserCmd(userId, 'HGET', 'quitol' + ':' + str(gameId) + ':' + str(userId), str(gid))
    retDict = strutil.loads(ret) if ret else None
    if retDict:
        rid = retDict.get('roomId')
        tid = retDict.get('tableId')
        sid = retDict.get('seatId')
        gid = strutil.getGameIdFromInstanceRoomId(rid)
        if gid > 0 and rid > 0 and tid > 0:
            # 到具体的房间或桌子的服务上去查询, 是否是真的在桌子上
            if tid == rid * 10000:  # 玩家在队列房间或者比赛房间的等待队列中, 此处不做一致性检查，玩家发起quick_start时检查。
                return 1
            else:
                try:
                    seatId, isObserving = roommgr.doCheckUserLoc(userId, gid, rid, tid, clientId)
                except:
                    ftlog.error()
                    return -1
                ftlog.debug('_checkUserLoc->userId=', userId, 'seatId=', seatId, 'isObserving=', isObserving)
                if seatId > 0 or isObserving == 1:
                    # 还在桌子上游戏
                    return 1
                else:
                    # 已经不再桌子上了, 清理所有的桌子带入金币
                    if sid > 0:
                        from poker.entity.dao import userchip
                        userchip.moveAllTableChipToChip(
                            userId, gid,
                            'TABLE_TCHIP_TO_CHIP',
                            0, clientId, tid)
                    # 清理当前的在线数据
                    _removeUserQuitLoc(gameId, userId, rid)
                    return 0
        else:
            # 到这儿, 数据是错误的, 删除处理
            _removeUserQuitLoc(gameId, userId, rid)
            return 0

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def removeUserQuitLoc(gameId, userId, roomId):
    gid = strutil.getBigRoomIdFromInstanceRoomId(roomId)
    daobase.executeUserCmd(userId, 'HDEL', 'quitol' + ':' + str(gameId) + ':' + str(userId), str(gid))

def _removeUserQuitLoc(gameId, userId, rid):
    gid = strutil.getBigRoomIdFromInstanceRoomId(rid)
    daobase.executeUserCmd(userId, 'HDEL', 'quitol' + ':' + str(gameId) + ':' + str(userId), str(gid))

def _processGamePlayWinTimes(wrd, isGameStart):
    if not wrd:
        return
    if isGameStart :
        if 'pt' not in wrd:
            wrd['pt'] = 0
        wrd['pt'] += 1  # 全局play数加1
    else:
        if 'wt' not in wrd:
            wrd['wt'] = 0
        wrd['wt'] += 1  # 全局play数加1
    return wrd

def _calUserDetalExp(winchip, baseScore):
    if winchip <= 0 :
        return 30  # 只要开玩，那么加30经验
    winexp = winchip * 1.0 / baseScore / 10.0
    return abs(int(winexp))

def increaceChipTableWinrate(gameId, userId, isGameStart, winchip):
    winchip = 0 if isGameStart else winchip
    winrate2 = gamedata.getGameAttrs(userId, gameId, ['winrate2'], False)[0]
    winrate2 = strutil.loads(winrate2, ignoreException=True, execptionValue={})
    if not winrate2:
        winrate2 = {'pt': 0, 'wt': 0}
    if winchip >= 0 or isGameStart:
        _processGamePlayWinTimes(winrate2, isGameStart)
    gamedata.setGameAttrs(userId, gameId, ['winrate2'], [strutil.dumps(winrate2)])
    return winrate2

def checkSetMedal(gameId, userId, baseScore, isGameStart, winchip):
    winchip = 0 if isGameStart else winchip

    winrate, oldLevel = gamedata.getGameAttrs(userId, gameId, ['winrate', 'level'], False)
    winrate = strutil.loads(winrate, ignoreException=True, execptionValue={})
    if winrate is None:
        winrate = {}
    if winchip >= 0 or isGameStart:
        _processGamePlayWinTimes(winrate, isGameStart)
    oldLevel = strutil.parseInts(oldLevel)
    deltaExp = 0
    if winchip > 0 or isGameStart:
        deltaExp = _calUserDetalExp(winchip, baseScore)
    
    exp = userdata.incrExp(userId, deltaExp)
    explevel, _ = gameexp.getLevelInfo(gameId, exp)
    gamedata.setGameAttrs(userId, gameId, ['winrate', 'level'], [strutil.dumps(winrate), explevel])
    if oldLevel != explevel:
        TYGame(gameId).getEventBus().publishEvent(UserLevelGrowEvent(gameId, userId, oldLevel, explevel))
    if isGameStart:
        # 广告商通知
        pcount = commconf.getAdNotifyPlayCount(gameId)
        if pcount > 0 and winrate.get('pt', 0) == pcount :
            sdkclient.adNotifyCallBack(gameId, userId)
    return exp, deltaExp, winrate


