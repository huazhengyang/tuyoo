# -*- coding=utf-8
'''
Created on 2015年7月30日

@author: zhaojiangang
'''
from datetime import datetime

import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify, hallled, hallvip, hallaccount
from hall.entity.hallactivity import activity
from hall.entity.hallactivity.activity_share_click import TYActShareClick
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.content import TYContentItemGenerator
from poker.entity.biz.item.exceptions import TYAssetNotEnoughException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata, gamedata, userchip, daoconst, userdata
from poker.protocol import router
from poker.protocol.rpccore import markRpcCall
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.game.game import TYGame
from poker.entity.dao.daoconst import UserDataSchema
from poker.entity.dao import sessiondata

def decodeContentItems(contentItems):
    ret = []
    genList = TYContentItemGenerator.decodeList(contentItems)
    for gen in genList:
        ret.append(gen.generate())
    return ret

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def consumeAsset(gameId, userId, assetKindId, count, eventId, intEventParam):
    try:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _, consumeCount, final = userAssets.consumeAsset(gameId, assetKindId, count, pktimestamp.getCurrentTimestamp(), eventId, intEventParam)
        return consumeCount, final
    except:
        ftlog.error('user_remote.consumeAsset gameId=', gameId,
                    'userId=', userId,
                    'assetKindId=', assetKindId,
                    'count=', count,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam)
        return 0, 0

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def consumeAssets(gameId, userId, contentItems, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    if ftlog.is_debug():
        ftlog.debug('consumeAssets gameId=', gameId,
                    'userId=', userId,
                    'contentItems=', contentItems,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam,
                    'roomId=', roomId,
                    'tableId=', tableId,
                    'roundId=', roundId,
                    'param01=', param01,
                    'param02=', param02
                    )
    try:
        contentItems = decodeContentItems(contentItems)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.consumeContentItemList(gameId, contentItems, True,
                                                      pktimestamp.getCurrentTimestamp(), eventId, intEventParam,
                                                      roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)
        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
        return None, 0
    except TYAssetNotEnoughException, e:
        return e.assetKind.kindId, e.required - e.actually

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addAsset(gameId, userId, assetKindId, count, eventId, intEventParam):
    try:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _, addCount, final = userAssets.addAsset(gameId, assetKindId, count, pktimestamp.getCurrentTimestamp(), eventId, intEventParam)
        return addCount, final
    except:
        ftlog.error('user_remote.addAsset gameId=', gameId,
                    'userId=', userId,
                    'assetKindId=', assetKindId,
                    'count=', count,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam)
        return 0, 0

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addAssets(gameId, userId, contentItems, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    if ftlog.is_debug():
        ftlog.debug('addAssets gameId=', gameId,
                    'userId=', userId,
                    'contentItems=', contentItems,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam,
                    'roomId=', roomId,
                    'tableId=', tableId,
                    'roundId=', roundId,
                    'param01=', param01,
                    'param02=', param02
                    )
    try:
        contentItems = decodeContentItems(contentItems)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContentItemList(gameId, contentItems, 1, True,
                                                   pktimestamp.getCurrentTimestamp(), eventId, intEventParam,
                                                   roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)
        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
        return True
    except:
        ftlog.error()
        return False


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def queryUserWeardItemKindIds(gameId, userId):
    from hall.servers.util.decroation_handler import DecroationHelper
    return DecroationHelper.queryUserWeardItemKindIds(gameId, userId)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def presentItemByUnitsCount(gameId, userId, fromUserId, kindId, count, receiveMail):
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        return False
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    userBag.addItemUnitsByKind(gameId, itemKind, count,
                               pktimestamp.getCurrentTimestamp(), fromUserId,
                               'ACCEPT_PRESENT_ITEM', fromUserId)
    if receiveMail:
        pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, receiveMail)
    datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
    return True


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def presentItem(gameId, userId, fromUserId, itemDataDict, receiveMail):
    kindId = itemDataDict['itemKindId']
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        return False
    itemData = itemKind.newItemData()
    itemData = itemData.fromDict(itemDataDict)
    item = hallitem.itemSystem.newItemFromItemData(itemData)
    if not item:
        return False
    item.fromUserId = fromUserId
    item.giftHandCount += 1
    timestamp = pktimestamp.getCurrentTimestamp()
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    userBag.addItem(gameId, item, timestamp, 'ACCEPT_PRESENT_ITEM', fromUserId)

    if receiveMail:
        pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, receiveMail)
    datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
    return True


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addfriend(userId, friendId, gameId, prize):
    from hall.entity.hallneituiguang import NeiTuiGuang
    return NeiTuiGuang.addfriend(userId, friendId, gameId, prize)


@markRpcCall(groupName="userId", lockName="", syncCall=1)  # 只读接口无需进行lock
def getFriendGameInfo(userId, gameIds, for_level_info, for_winchip, for_online_info=1):
    return _getFriendGameInfo(userId, gameIds, for_level_info, for_winchip, for_online_info)


@markRpcCall(groupName="userId", lockName="", syncCall=1, future=1)
def getFriendGameInfoFuture(userId, gameIds, for_level_info, for_winchip, for_online_info=1):
    '''
    延迟rpc远程方法，同步返回 rpccore.FutureResult 实例，通过 getResult 方法获取远程结果
    '''
    return _getFriendGameInfo(userId, gameIds, for_level_info, for_winchip, for_online_info)


def _getFriendGameInfo(userId, gameIds, for_level_info, for_winchip, for_online_info=1):
    uid = int(userId)
    datas = {}
    gid, rid, tid, sid = 0, 0, 0, 0
    state = daoconst.OFFLINE
    if for_online_info:
        loclist = onlinedata.getOnlineLocList(uid)
        state = onlinedata.getOnlineState(uid)
        if len(loclist) > 0:
            _rid, _tid, _sid = loclist[0]
            # gid表示用户在哪个游戏中
            gid = strutil.getGameIdFromInstanceRoomId(_rid)
            # 检查是否可加入游戏
            if TYGame(gid).canJoinGame(userId, _rid, _tid, _sid):
                # rid/tid/sid表示用户所在的游戏是否可加入游戏
                # 分享出来的都是可以加入游戏的牌桌信息
                rid = _rid
                tid = _tid
                sid = _sid
            if ftlog.is_debug():
                ftlog.debug('getFriendGameInfo userId:', userId, ' gameId:', gid, ' roomId:', _rid, ' tableId:', _tid,
                            ' seatId:', _sid, ' can not join game....')
        if state == daoconst.OFFLINE:
            offline_time = gamedata.getGameAttr(uid, HALL_GAMEID, 'offlineTime')
            if not offline_time:  # 取不到离线时间,取上线时间
                offline_time = userdata.getAttr(uid, 'authorTime')
            if offline_time:
                offline_time = pktimestamp.parseTimeMs(offline_time)
                delta = datetime.now() - offline_time
                delta = delta.days * 24 * 60 + delta.seconds / 60  # 分钟数
            else:  # 异常情况
                delta = 24 * 60
            datas['offline_time'] = delta if delta > 0 else 1
        if rid > 0:
            try:
                room = gdata.roomIdDefineMap().get(rid, None)
                if room:
                    datas['room_name'] = room.configure['name']
            except:
                ftlog.error()
    # 构造回传给SDK的游戏数据
    datas.update({'uid': uid, 'gid': gid, 'rid': rid, 'tid': tid, 'sid': sid, 'state': state})

    if for_level_info:
        datas['level_game_id'] = 0
        datas['level'] = 0
        datas['level_pic'] = ''
        try:
            for gameId in gameIds:
                if gameId not in gdata.games():
                    continue
                dashifen_info = gdata.games()[gameId].getDaShiFen(uid, '')
                if dashifen_info:
                    level = dashifen_info['level']
                    if level > 0 and level > datas['level']:
                        datas['level_game_id'] = gameId
                        datas['level'] = level
                        level_pic = dashifen_info.get('picbig')
                        datas['level_pic'] = level_pic if level_pic else dashifen_info.get('pic')
        except:
            ftlog.error()

    if for_winchip:
        datas['winchip'] = 0
        datas['winchips'] = 0
        try:
            for gameId in gameIds:
                winchips, todaychips = gamedata.getGameAttrs(userId, gameId, ['winchips', 'todaychips'], False)
                winchips = strutil.parseInts(winchips)
                yest_winchip = 0
                todaychips = strutil.loads(todaychips, ignoreException=True)
                if todaychips and 'today' in todaychips and 'chips' in todaychips and 'last' in todaychips:
                    if pktimestamp.formatTimeDayInt() == todaychips['today']:
                        yest_winchip = todaychips['last']
                    elif pktimestamp.formatTimeYesterDayInt() == todaychips['today']:
                        yest_winchip = todaychips['chips']
                datas['winchip'] += yest_winchip
                datas['winchips'] += winchips
        except:
            ftlog.error()
    return datas


def sendHallLed(gameId, msgstr, ismgr=0, scope='hall', clientIds=[], **kwargs):
    count = 0
    colen = router._utilServer.sidlen
    for x in xrange(colen):
        #         count += _sendHallLed(x + 1, gameId, msgstr, ismgr, scope, clientIds)
        _sendHallLed(x + 1, gameId, msgstr, ismgr, scope, clientIds, **kwargs)
    return count


@markRpcCall(groupName="intServerId", lockName="", syncCall=0)
def _sendHallLed(intServerId, gameId, msgstr, ismgr, scope, clientIds, **kwargs):
    hallled.sendLed(gameId, msgstr, ismgr, scope, clientIds, **kwargs)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def incrUserChip(userId, gameId, chip, eventId, intEventParam, clientId):
    trueDelta, final = userchip.incrChip(userId, gameId, chip, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, eventId,
                                         intEventParam, clientId)
    if trueDelta != 0:
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
    return trueDelta, final


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def sendMessage(gameId, userId, fromUid, msg):
    pkmessage.sendPrivate(HALL_GAMEID, userId, fromUid, msg)
    datachangenotify.sendDataChangeNotify(gameId, userId, 'message')


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addVipExp(gameId, userId, toAdd, eventId, intEventParam):
    userVip = hallvip.userVipSystem.addUserVipExp(gameId, userId, toAdd, eventId, intEventParam)
    return 0, userVip.vipExp


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getThirdPartyUserInfo(userId):
    return _getThirdPartyUserInfo(userId)


def _getThirdPartyUserInfo(userId):
    '''
    取得用户的基本账户的信息
    玩家昵称
    玩家id
    钻石数量
    金币数量
    奖券数量
    魅力值
    vip等级
    '''
    userdata.checkUserData(userId)
    ukeys = [UserDataSchema.NAME, UserDataSchema.SEX, UserDataSchema.DIAMOND,
             UserDataSchema.CHIP, UserDataSchema.COUPON, UserDataSchema.CHARM,
             UserDataSchema.PURL, UserDataSchema.CREATETIME]
    udataDb = userdata.getAttrs(userId, ukeys)
    udata = dict(zip(ukeys, udataDb))
    # vip信息
    udata['vipInfo'] = hallvip.userVipSystem.getVipInfo(userId)
    
    # 游戏信息
    clientId = sessiondata.getClientId(userId)
    gameInfo = hallaccount.getGameInfo(userId, clientId)
    udata['gameInfo'] = gameInfo.get('dashifen', {})
    return udata


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def free_set_task_progress(userId, taskid, progress, clientid):
    from hall.entity.halltask import HallNewUserSubTaskSystem, HallChargeSubTaskSystem, _taskSystem
    curtime = pktimestamp.getCurrentTimestamp()
    task_kind = _taskSystem.findTaskKind(taskid)
    if not task_kind:
        return False, 0
    subsys = task_kind.taskUnit.subTaskSystem
    if not isinstance(subsys, (HallNewUserSubTaskSystem, HallChargeSubTaskSystem)):  # 目前只有这俩走这里
        return False, 0

    taskmodel = subsys.loadTaskModel(userId, curtime, clientid)
    if not taskmodel:
        return False, 0
    task = taskmodel.userTaskUnit.findTask(taskid)
    if not task:
        return False, 0
    _changed, finish = task.setProgress(progress, curtime)
    if _changed:
        task.userTaskUnit.updateTask(task)  # 记得存盘。。。
    return _changed, finish


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def activity_share_click(userId, actname):
    config = activity.activitySystem._dao.getActivityConfig(actname)
    if not config:
        return 'act:{} config not exist!'.format(actname)

    actobj = activity.activitySystem.generateOrGetActivityObject(config)
    if not isinstance(actobj, TYActShareClick):
        return 'act:{} type is not TYActShareClick!'.format(actname)
    return actobj.get_award(userId)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def registerAlarm(userId, pluginId, deadline, notice, extparam=None):
    """
    :param userId: 玩家id
    :param pluginId: 插件id
    :param deadline: 到期时间,距1970.1.1零点的秒数
    :param notice: 通知文本
    :param extparam: 可json化的字典,传入自定义参数,诸如roomId
    :return: 闹钟id，0为异常
    """
    from hall.entity import hallalarm
    return hallalarm.registerAlarm(userId, pluginId, deadline, notice, extparam)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def queryAlarm(userId):
    from hall.entity import hallalarm
    msg = hallalarm.queryAlarm(userId)
    if msg:
        return msg._ht
