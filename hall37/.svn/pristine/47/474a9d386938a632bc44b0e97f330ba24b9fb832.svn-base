'''
Created on 2015年12月3日

@author: zhaojiangang
'''
from datetime import datetime, date, timedelta
import json,time
from hall.entity import hallconf, monthcheckin
import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import UserEvent
from poker.util import sortedlist  # FIXME:
import poker.util.timestamp as pktimestamp
from hall.entity import datachangenotify,hallitem
from poker.util import strutil
import poker.entity.dao.gamedata as pkgamedata
from poker.entity.dao import userdata as pkuserdata


def supplementCheckin(userId, gameId, clientId, supplementDate=None, nowDate=None):
    '''
    用户补签
    @param userId: 用户ID
    @param supDate: 补签日期，如果为None则表示补签最近一天
    @param nowDate: 当前日期
    @return: MonthCheckinStatus
    '''
    nowDate = nowDate or datetime.now().date()
    status = monthcheckin.loadStatus(userId, nowDate)
    if monthcheckin.isScriptDoGetReward(userId) :
        raise monthcheckin.AlreadyCheckinException('非法签到')
    # 检查最大补签数
    if status.supplementCheckinCount >= monthcheckin._monthCheckinConf.get("maxSupplementCheckinCount"):
        raise monthcheckin.SupplementOverException()
    
    if supplementDate:
        if not pktimestamp.isSameMonth(supplementDate, status.curDate):
            raise monthcheckin.InvalidSupplementDateException()
    else:
        supplementDate = status._getHoleDateList()
        if not supplementDate:
            raise monthcheckin.AlreadyCheckinException()
    
    if not status.addSupplementCheckinDate(supplementDate[0]):
        raise monthcheckin.AlreadyCheckinException()

    # TODO 发放补签奖励
    # TODO publish event
    #减少抽奖卡，消耗成功之后，发放奖励。
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()
    
    _, consumeCount, _final = userAssets.consumeAsset(gameId, 'item:4168', 1,
                                                         timestamp, 'HALL_CHECKIN', 0)
    if consumeCount < 1 :
        result = {}
        result["lessCard"] = "您的补签卡不足"
        return 1,result
    datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
    monthcheckin._saveStatus(status)
    monthcheckin.userToGetGift(userId, gameId,state = 0)
    #领取累计奖励
    _, clientVer, _ = strutil.parseClientId(clientId)
    if clientVer <= 3.76:
        #自动领奖
        days = status.allCheckinCount
        monthcheckin.getDaysReward(userId, days,gameId)
    ftlog.info('supplementCheckin userId =', userId
               ,'gameId =', gameId
               ,'clientId =', clientId
               ,'noeDate =', nowDate)
    return 0,status

monthcheckin.supplementCheckin = supplementCheckin
