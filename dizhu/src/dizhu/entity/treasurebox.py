# -*- coding=utf-8 -*-

import time
from dizhu.entity import dizhuconf, dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.usercoupon import user_coupon_details
from hall.entity.usercoupon.events import UserCouponReceiveEvent
from poker.entity.biz.content import TYContentRegister
from hall.entity import hallitem, hallconf
from poker.util import timestamp
from poker.entity.biz.item.item import TYAssetUtils
from dizhucomm.entity.events import UserTBoxLotteryEvent
from datetime import datetime
from poker.entity.dao import weakdata


def _getTbData(userId):
    datas = weakdata.getWeakData(userId, DIZHU_GAMEID, weakdata.CYCLE_TYPE_DAY, 'treasurebox')
    if not 'tbroomid' in datas:
        datas['tbroomid'] = 0
    if not 'tbplaytimes' in datas:
        datas['tbplaytimes'] = 0
    if not 'tblasttime' in datas:
        datas['tblasttime'] = 0
    ftlog.debug('_getTbData->userIds=', userId, datas)
    return datas


def _setTbData(userId, data):
    data = weakdata.setWeakData(userId, DIZHU_GAMEID, weakdata.CYCLE_TYPE_DAY, 'treasurebox', data)
    ftlog.debug('_setTbData->userIds=', userId, data)
    return data


def getUserTbInfo(userId, bigRoomId):
    # 快开进入闯关赛配置
    quickStartConf = dizhuconf.getQuickStart()
    robConf = quickStartConf.get('robotConf', {})
    datas = _getTbData(userId)
    tbroomid = datas['tbroomid']
    tbplaytimes = datas['tbplaytimes']
    tblasttime = datas['tblasttime']
    if tbroomid == robConf.get('robRoomIdForNormal') and bigRoomId == quickStartConf.get('normalRoomId'):
        if ftlog.is_debug():
            ftlog.debug('getUserTbInfo->userIds=', userId, 'tbroomid=', tbroomid,
                        'bigRoomId=', bigRoomId,
                        'robRoomIdForNormal=', robConf.get('robRoomIdForNormal'),
                        'normalRoomId=', quickStartConf.get('normalRoomId'))
    else:
        if tbroomid != bigRoomId:
            tbroomid = bigRoomId
            tbplaytimes = 0
            tblasttime = 0
    ftlog.debug('getUserTbInfo->userIds=', userId, 'bigRoomId=', bigRoomId, tbplaytimes, tblasttime, datas)
    return tbplaytimes, tblasttime, datas


def getTreasureBoxState(userId, bigRoomId):
    tbplaytimes, tblasttime, _ = getUserTbInfo(userId, bigRoomId)
    tbconfigers = dizhuconf.getTreasureBoxInfo(bigRoomId)
    if tbconfigers :
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
    ftlog.debug('getTreasureBoxState->userIds=', userId, 'bigRoomId=', bigRoomId, tbplaytimes, '/', tbplaycount)
    return tbplaytimes, tbplaycount


def getTreasureRewardItem(bigRoomId):
    tbconfigers = dizhuconf.getTreasureBoxInfo(bigRoomId)
    itemId = ''
    itemCount = 0 # 奖励个数 wuyagnwei 20160623 3.773
    if tbconfigers :
        items = tbconfigers.get('reward', {}).get('items', [])
        for item in items:
            if item['count'] > 0:
                itemId = item['itemId']
                itemCount = item['count']
    ftlog.debug('getTreasureRewardItem->bigRoomId=', bigRoomId, 'itemId=', itemId, 'itemCount=', itemCount)
    return itemId, itemCount


def getTreasureTableTip(bigRoomId):
    tbconfigers = dizhuconf.getTreasureBoxInfo(bigRoomId)
    if tbconfigers :
        items = tbconfigers.get('reward', {}).get('items', [])
        for item in items:
            if item['count'] > 0:
                return 1, tbconfigers['desc']
    return 0, ''


def updateTreasureBoxStart(userIds, bigRoomId):
    tbconfigers = dizhuconf.getTreasureBoxInfo(bigRoomId)
    tbcontinuesecodes = -1
    tbplaycount = 1
    if tbconfigers :
        tbplaycount = tbconfigers['playCount']
        tbcontinuesecodes = tbconfigers['continueSeconds']
    tbinfos = {}
    for userId in userIds:
        tbplaytimes, tblasttime, datas = getUserTbInfo(userId, bigRoomId)
        ctime = int(time.time())
        if abs(ctime - tblasttime) > tbcontinuesecodes:
            tbplaytimes = 0
        tbroomid = bigRoomId
        tblasttime = ctime
        tbplaytimes += 1
        datas['tbroomid'] = tbroomid
        datas['tbplaytimes'] = tbplaytimes
        datas['tblasttime'] = tblasttime
        ftlog.debug('updateTreasureBoxStart->userIds=', userId, 'bigRoomId=', bigRoomId, 'datas=', datas)
        _setTbData(userId, datas)
        datas['tbplaycount'] = tbplaycount
        tbinfos[userId] = datas
    return tbinfos


def updateTreasureBoxWin(userIds, bigRoomId):
    for userId in userIds:
        tbplaytimes, tblasttime, datas = getUserTbInfo(userId, bigRoomId)
        tblasttime = int(time.time())
        datas['tbroomid'] = bigRoomId
        datas['tbplaytimes'] = tbplaytimes
        datas['tblasttime'] = tblasttime
        ftlog.debug('updateTreasureBoxWin->userIds=', userId, 'bigRoomId=', bigRoomId, 'datas=', datas)
        _setTbData(userId, datas)

# new tbox 获取奖励
def doTreasureBox1(userId):
    datas = _getTbData(userId)
    tbroomid = datas['tbroomid']
    if not tbroomid:
        ftlog.debug('doTreasureBox1 userId=', userId, 'datas=', datas)
        return {'ok' : 0, 'info': '本房间不支持宝箱,请进入高倍房再使用'}
    return doTreasureBox(userId, tbroomid)

# old tbox 获取奖励
def doTreasureBox(userId, bigRoomId):
    ftlog.debug('doTreasureBox userId=', userId, 'bigRoomId=', bigRoomId)
    # 判定房间配置
    tbconfiger = dizhuconf.getTreasureBoxInfo(bigRoomId)
    if not tbconfiger or not tbconfiger.get('reward', None) :
        ftlog.debug('doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, 'not tbox room !')
        return { 'ok' :0, 'info': '本房间不支持宝箱,请进入高倍房再使用'}
    # 判定是否可以领取
    tbplaytimes, tblasttime, datas = getUserTbInfo(userId, bigRoomId)
    tbplaycount = tbconfiger['playCount']
    if tblasttime <= 0 or tbplaytimes < tbplaycount :
        ftlog.debug('doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, 'can not tbox !')
        return {'ok' :0,
                'tbt': min(tbplaytimes, tbplaycount),
                'tbc': tbplaycount,
                'info': tbconfiger['desc']}
    # 更新宝箱状态 
    datas['tblasttime'] = int(time.time())
    datas['tbplaytimes'] = 0
    _setTbData(userId, datas)

    rewards = tbconfiger['reward']
    content = TYContentRegister.decodeFromDict(rewards)
    sitems = content.getItems()
    # 活动加成
    ditems = _getDoubleInfos(bigRoomId)
    if ditems :
        for si in sitems :
            kindId = si.assetKindId
            mutil = ditems.get(kindId, 0)
            if mutil and mutil > 0 :
                si.count = int(si.count * mutil)
    # 发送道具
    # ua = hallitem.itemSystem.loadUserAssets(userId)
    # aslist = ua.sendContentItemList(DIZHU_GAMEID, sitems, 1, True,
    #                                 timestamp.getCurrentTimestamp(), 'TASK_OPEN_TBOX_REWARD', bigRoomId)
    aslist = dizhu_util.sendRewardItems(userId, sitems, '', 'TASK_OPEN_TBOX_REWARD', bigRoomId)
    addmsg = TYAssetUtils.buildContentsString(aslist)
    items = []
    for x in aslist :
        kindId = hallconf.translateAssetKindIdToOld(x[0].kindId)
        items.append({'item':kindId, 'count':x[1], 'total':x[2]})
        if kindId in ['user:coupon', 'COUPON']:
            # 广播事件
            from hall.game import TGHall
            TGHall.getEventBus().publishEvent(
                UserCouponReceiveEvent(HALL_GAMEID, userId, x[1], user_coupon_details.USER_COUPON_TABLE_TBBOX))

    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().publishEvent(UserTBoxLotteryEvent(DIZHU_GAMEID, userId))
    datas = {'ok' : 1,
            'tbt' : 0,
            'tbc' : tbplaycount,
            'info' : '开启宝箱,获得' + addmsg,
            'items' : items
            }
    ftlog.debug('doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, datas)
    return datas


def _getDoubleInfos(bigRoomId, dt=None):
    try:
        act_conf = dizhuconf.getTreasureBoxDoubleInfo(bigRoomId)
        if not act_conf:
            return None
        dt = dt or datetime.now()
        start_date = datetime.strptime(act_conf['act.start.date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(act_conf['act.end.date'], '%Y-%m-%d').date()
        cur_date = dt.date()
        if cur_date < start_date or cur_date >= end_date:
            return None
         
        double_start_time = datetime.strptime(act_conf['double.start.time'], '%H:%M').time()
        double_end_time = datetime.strptime(act_conf['double.end.time'], '%H:%M').time()
         
        cur_time = dt.time()
        if cur_time >= double_start_time and cur_time < double_end_time:
            return act_conf['doubleItems']
    except:
        ftlog.error()
    return None

