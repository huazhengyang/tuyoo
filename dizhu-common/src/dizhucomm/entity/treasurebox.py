# -*- coding=utf-8 -*-

from datetime import datetime
import time

from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhucomm.entity.events import UserTBoxLotteryEvent
import freetime.util.log as ftlog
from hall.entity import hallitem, hallconf
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure
from poker.entity.dao import weakdata
from poker.entity.game.game import TYGame
from poker.util import timestamp


def _getTbData(gameId, userId):
    data = weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, 'treasurebox')
    if 'tbroomid' not in data:
        data['tbroomid'] = 0
    if 'tbplaytimes' not in data:
        data['tbplaytimes'] = 0
    if 'tblasttime' not in data:
        data['tblasttime'] = 0
    if ftlog.is_debug():
        ftlog.debug('treasurebox._getTbData',
                    'gameId=', gameId,
                    'userId=', userId,
                    'data=', data)
    return data

def _setTbData(gameId, userId, data):
    data = weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, 'treasurebox', data)
    if ftlog.is_debug():
        ftlog.debug('treasurebox._setTbData',
                    'gameId=', gameId,
                    'userId=', userId,
                    'data=', data)
    return data

def getUserTbInfo(gameId, userId, bigRoomId):
    data = _getTbData(gameId, userId)
    tbroomid = data['tbroomid']
    tbplaytimes = data['tbplaytimes']
    tblasttime = data['tblasttime']
    if tbroomid != bigRoomId :
        tbroomid = bigRoomId
        tbplaytimes = 0
        tblasttime = 0
    if ftlog.is_debug():
        ftlog.debug('treasurebox.getUserTbInfo',
                    'gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'tbplaytimes=', tbplaytimes,
                    'tblasttime=', tblasttime,
                    'data=', data)
    return tbplaytimes, tblasttime, data

def getTreasureBoxConf(gameId, bigRoomId):
    infos = configure.getGameJson(gameId, 'table.tbbox', {}, configure.DEFAULT_CLIENT_ID)
    rooms = infos.get('rooms', {})
    return rooms.get(str(bigRoomId), None)

def getTreasureBoxDoubleConf(gameId, bigRoomId):
    infos = configure.getGameJson(gameId, 'table.tbbox', {}, configure.DEFAULT_CLIENT_ID)
    double = infos.get('double', {})
    return double

def getTreasureBoxState(gameId, userId, bigRoomId):
    tbplaytimes, tblasttime, _ = getUserTbInfo(gameId, userId, bigRoomId)
    tbconfigers = getTreasureBoxConf(gameId, bigRoomId)
    if tbconfigers:
        ctime = int(time.time())
        tbplaycount = tbconfigers['playCount']
        tbcontinuesecodes = tbconfigers['continueSeconds']
        if tbplaycount < 2 or abs(ctime - tblasttime) > tbcontinuesecodes:
            if tbplaycount < 2:
                tbplaycount = 1
            tbplaytimes = 0
    else:
        tbplaycount = 1
        tbplaytimes = 0
    if tbplaytimes > tbplaycount:
        tbplaytimes = tbplaycount
    if ftlog.is_debug():
        ftlog.debug('treasurebox.getTreasureBoxState',
                    'gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'state=', '%s/%s' % (tbplaytimes, tbplaycount))
    return tbplaytimes, tbplaycount

def getTreasureRewardItem(gameId, bigRoomId):
    tbconfigers = getTreasureBoxConf(gameId, bigRoomId)
    itemId = None
    itemCount = 0
    if tbconfigers :
        items = tbconfigers.get('reward', {}).get('items', [])
        for item in items:
            if item['count'] > 0:
                itemId = item['itemId']
                itemCount = item['count']
                break
    if ftlog.is_debug():
        ftlog.debug('treasurebox.getTreasureRewardItem',
                    'gameId=', gameId,
                    'bigRoomId=', bigRoomId,
                    'itemId=', itemId,
                    'itemCount=', itemCount)
    return itemId, itemCount

def getTreasureTableTip(gameId, bigRoomId):
    tbconfigers = getTreasureBoxConf(gameId, bigRoomId)
    if tbconfigers:
        items = tbconfigers.get('reward', {}).get('items', [])
        for item in items:
            if item['count'] > 0:
                return 1, tbconfigers['desc']
    return 0, ''

def updateTreasureBoxStart(gameId, userId, bigRoomId):
    tbconfigers = getTreasureBoxConf(gameId, bigRoomId)
    tbcontinuesecodes = -1
    tbplaycount = 1
    if tbconfigers:
        tbplaycount = tbconfigers['playCount']
        tbcontinuesecodes = tbconfigers['continueSeconds']
    tbplaytimes, tblasttime, data = getUserTbInfo(gameId, userId, bigRoomId)
    ctime = int(time.time())
    if abs(ctime - tblasttime) > tbcontinuesecodes:
        tbplaytimes = 0

    dizhuver = SessionDizhuVersion.getVersionNumber(userId)
    if dizhuver >= 5.10 and tbplaytimes >= tbplaycount:
        tbplaytimes = 0

    tbroomid = bigRoomId
    tblasttime = ctime
    tbplaytimes += 1
    data['tbroomid'] = tbroomid
    data['tbplaytimes'] = min(tbplaytimes, tbplaycount)
    data['tblasttime'] = tblasttime
    _setTbData(gameId, userId, data)
    data['tbplaycount'] = tbplaycount
    if ftlog.is_debug():
        ftlog.debug('treasurebox.updateTreasureBoxStart',
                    'gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'data=', data)
    return data

def updateTreasureBoxWin(gameId, userId, bigRoomId):
    tbplaytimes, _tblasttime, data = getUserTbInfo(gameId, userId, bigRoomId)
    data['tbroomid'] = bigRoomId
    data['tbplaytimes'] = tbplaytimes
    data['tblasttime'] = int(time.time())
    if ftlog.is_debug():
        ftlog.debug('treasurebox.updateTreasureBoxWin',
                    'gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'data=', data)
    _setTbData(gameId, userId, data)

# new tbox 获取奖励
def doTreasureBox1(gameId, userId):
    data = _getTbData(gameId, userId)
    tbroomid = data['tbroomid']
    if not tbroomid:
        if ftlog.is_debug():
            ftlog.debug('treasurebox.doTreasureBox1',
                        'gameId=', gameId,
                        'userId=', userId,
                        'err=', 'NotSupported')
        return {'ok' : 0, 'info': '本房间不支持宝箱,请进入高倍房再使用'}
    return doTreasureBox(gameId, userId, tbroomid)

# old tbox 获取奖励
def doTreasureBox(gameId, userId, bigRoomId):
    data = _getTbData(gameId, userId)
    bigRoomId = data['tbroomid']
    if ftlog.is_debug():
        ftlog.debug('treasurebox.doTreasureBox',
                    'gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId)
    # 判定房间配置
    tbconfiger = getTreasureBoxConf(gameId, bigRoomId)
    if not tbconfiger or not tbconfiger.get('reward', None):
        if ftlog.is_debug():
            ftlog.debug('treasurebox.doTreasureBox',
                        'gameId=', gameId,
                        'userId=', userId,
                        'err=', 'NotTBoxRoom')
        return { 'ok' :0, 'info': '本房间不支持宝箱,请进入高倍房再使用'}
    # 判定是否可以领取
    tbplaytimes, tblasttime, datas = getUserTbInfo(gameId, userId, bigRoomId)
    tbplaycount = tbconfiger['playCount']
    if tblasttime <= 0 or tbplaytimes < tbplaycount:
        if ftlog.is_debug():
            ftlog.debug('treasurebox.doTreasureBox',
                        'gameId=', gameId,
                        'userId=', userId,
                        'err=', 'CanNotTBox')
        return {'ok' :0,
                'tbt': min(tbplaytimes, tbplaycount),
                'tbc': tbplaycount,
                'info': tbconfiger['desc']}
    # 更新宝箱状态 
    datas['tblasttime'] = int(time.time())
    datas['tbplaytimes'] = 0
    _setTbData(gameId, userId, datas)

    rewards = tbconfiger['reward']
    content = TYContentRegister.decodeFromDict(rewards)
    sitems = content.getItems()
    # 活动加成
    ditems = _getDoubleInfos(gameId, bigRoomId)
    if ditems :
        for si in sitems :
            kindId = si.assetKindId
            mutil = ditems.get(kindId, 0)
            if mutil and mutil > 0 :
                si.count = int(si.count * mutil)
    # 发送道具
    ua = hallitem.itemSystem.loadUserAssets(userId)
    aslist = ua.sendContentItemList(gameId, sitems, 1, True,
                                    timestamp.getCurrentTimestamp(),
                                    'TASK_OPEN_TBOX_REWARD', bigRoomId)
    addmsg = TYAssetUtils.buildContentsString(aslist)
    items = []
    for x in aslist :
        kindId = hallconf.translateAssetKindIdToOld(x[0].kindId)
        items.append({'item':kindId, 'count':x[1], 'total':x[2]})

    TYGame(gameId).getEventBus().publishEvent(UserTBoxLotteryEvent(gameId, userId))
    data = {
        'ok' : 1,
        'tbt' : 0,
        'tbc' : tbplaycount,
        'info' : '开启宝箱,获得' + addmsg,
        'items' : items
    }
    if ftlog.is_debug():
        ftlog.debug('treasurebox.doTreasureBox',
                    'gameId=', gameId,
                    'userId=', userId,
                    'data=', data)
    return data

def _getDoubleInfos(gameId, bigRoomId, dt=None):
    try:
        actConf = getTreasureBoxDoubleConf(gameId, bigRoomId)
        if not actConf:
            return None
        dt = dt or datetime.now()
        start_date = datetime.strptime(actConf['act.start.date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(actConf['act.end.date'], '%Y-%m-%d').date()
        cur_date = dt.date()
        if cur_date < start_date or cur_date >= end_date:
            return None

        double_start_time = datetime.strptime(actConf['double.start.time'], '%H:%M').time()
        double_end_time = datetime.strptime(actConf['double.end.time'], '%H:%M').time()
         
        cur_time = dt.time()
        if cur_time >= double_start_time and cur_time < double_end_time:
            return actConf['doubleItems']
    except:
        ftlog.error()
    return None

