# -*- coding: utf-8 -*-
"""
Created on 2017年11月21日

@author: lyj
"""
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from freetime.entity.msg import MsgPack
from hall.entity import daily_free_give
import freetime.util.log as ftlog
from hall.entity import sevendayscheckin
from hall.entity import hallshare
import poker.util.timestamp as pktimestamp
from poker.entity.biz import bireport

@markCmdActionHandler
class DailyFreeGiveHandler(BaseMsgPackChecker):
    def __init__(self):
        super(DailyFreeGiveHandler, self).__init__()

    def _check_param_shareId(self, msg, key, params):
        try:
            shareId = msg.getParam(key, msg.getParam('shareId'))
            return None, int(shareId)
        except:
            return None, -1

    @markCmdActionMethod(cmd='daily_free_give', action="query", clientIdVer=0)
    def doQueryDailyFreeGive(self, gameId, userId, shareId, clientId):
        try:
            mo = MsgPack()
            mo.setCmd('daily_free_give')
            mo.setResult('action', 'query')
            mo.setResult('dailyFreeGive', daily_free_give.queryDailyFreeGive(userId, gameId))
            mo.setResult('todayCheckIn', sevendayscheckin.loadStatus(userId, gameId).isTodayCheckined())
            share = hallshare.findShare(shareId)
            if share:
                shareInfo = hallshare.getShareStatus(userId, share, pktimestamp.getCurrentTimestamp())
                mo.setResult('shareRewardCount', shareInfo[1])
            else:
                mo.setResult('shareRewardCount', 0)
            router.sendToUser(mo, userId)
            #统计
            bireport.reportGameEvent('SZMJ_DAILY_FREE_GIVE_QUERY', userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)
        except Exception as e:
            mo = MsgPack()
            mo.setCmd('daily_free_give')
            mo.setResult('action', 'query')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='daily_free_give', action="recieve", clientIdVer=0)
    def doRecieveDailyFreeGive(self, gameId, userId, clientId):
        try:
            mo = MsgPack()
            mo.setCmd('daily_free_give')
            mo.setResult('action', 'recieve')
            ret = daily_free_give.receiveDailyFreeGive(userId, gameId)
            if not ret:
                mo.setResult('ok', 0)
                ftlog.info('maybe is script userId =', userId)
                mo.setResult('tip', '领取失败')
                router.sendToUser(mo, userId)
                return

            mo.setResult('deltaChip', ret[1])
            mo.setResult('finalChip', ret[2])
            mo.setResult('freeGiveCountLeft', ret[3])
            mo.setResult('ok',  1)
            router.sendToUser(mo, userId)
            #统计
            bireport.reportGameEvent('SZMJ_DAILY_FREE_GIVE_RECIEVE', userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)
        except Exception as e:
            mo = MsgPack()
            mo.setCmd('daily_free_give')
            mo.setResult('action', 'recieve')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)


if __name__ == '__main__':
    pass
