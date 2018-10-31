# -*- coding=utf-8 -*-

import time
from dizhu.entity import dizhuconf, treasurebox
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from dizhu.entity.treasurebox import _getTbData, getUserTbInfo, _setTbData, _getDoubleInfos
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.usercoupon import user_coupon_details
from hall.entity.usercoupon.events import UserCouponReceiveEvent
from poker.entity.biz.content import TYContentRegister
from hall.entity import hallitem, hallconf
from poker.util import timestamp
from poker.entity.biz.item.item import TYAssetUtils
from dizhucomm.entity.events import UserTBoxLotteryEvent

# new tbox 获取奖励
def doTreasureBox1(userId):
    datas = _getTbData(userId)
    tbroomid = datas['tbroomid']
    if not tbroomid:
        ftlog.warn('doTreasureBox1 userId=', userId, 'datas=', datas)
        return {'ok' : 0, 'info': '本房间不支持宝箱,请进入高倍房再使用'}
    return doTreasureBox(userId, tbroomid)

# old tbox 获取奖励
def doTreasureBox(userId, bigRoomId):
    ftlog.debug('doTreasureBox userId=', userId, 'bigRoomId=', bigRoomId)
    # 判定房间配置
    tbconfiger = dizhuconf.getTreasureBoxInfo(bigRoomId)
    if not tbconfiger or not tbconfiger.get('reward', None) :
        ftlog.warn('doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, 'not tbox room !')
        return { 'ok' :0, 'info': '本房间不支持宝箱,请进入高倍房再使用'}
    # 判定是否可以领取
    tbplaytimes, tblasttime, datas = getUserTbInfo(userId, bigRoomId)
    tbplaycount = tbconfiger['playCount']
    if tblasttime <= 0 or tbplaytimes < tbplaycount :
        ftlog.warn('doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, 'can not tbox !')
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
    ua = hallitem.itemSystem.loadUserAssets(userId)
    aslist = ua.sendContentItemList(DIZHU_GAMEID, sitems, 1, True,
                                    timestamp.getCurrentTimestamp(), 'TASK_OPEN_TBOX_REWARD', bigRoomId)
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
    ftlog.info('doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, datas)
    return datas


treasurebox.doTreasureBox1 = doTreasureBox1
treasurebox.doTreasureBox = doTreasureBox