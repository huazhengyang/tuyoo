# -*- coding: utf-8 -*-
"""
Created on 2015年11月21日

@author: zhaojiangang
"""
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from freetime.entity.msg import MsgPack
from hall.entity import sevendayscheckin
from hall.entity.sevendayscheckin import SevenDaysCheckinException
import freetime.util.log as ftlog
from poker.entity.biz import bireport

@markCmdActionHandler
class SevenDaysCheckinHandler(BaseMsgPackChecker):
    def __init__(self):
        super(SevenDaysCheckinHandler, self).__init__()

    @markCmdActionMethod(cmd='sevendays_checkin', action="get", clientIdVer=0)
    def doGetSevenDaysCheckin(self, gameId, userId, clientId):
        try:
            _conf = sevendayscheckin.getConf(gameId) # 配置检查
            mo = MsgPack()
            mo.setCmd('sevendays_checkin')
            status = sevendayscheckin.loadStatus(userId, gameId)
            mo.setResult('todayCheckIn', status.isTodayCheckined())
            mo.setResult('checkInDays',  status.getCheckInDays)
            daysRewards = []
            for _days, rewardContent in enumerate(_conf.get('daysRewards', [])):
                reward = rewardContent.get('reward')
                daysRewards.append({
                    'days': rewardContent.get('days'),
                    'desc': reward.get('desc'),
                    'state': 1 if rewardContent.get('days') <= status.getCheckInDays else 0,
                    'items': reward.get('items')
                })
            mo.setResult('daysRewards', daysRewards)
            mo.setResult('action', 'get')
            router.sendToUser(mo, userId)
            #统计
            bireport.reportGameEvent('SZMJ_SEVEN_DAYS_CHECKIN_GET', userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)
        except SevenDaysCheckinException, e:
            mo = MsgPack()
            mo.setCmd('sevendays_checkin')
            mo.setResult('action', 'get')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.warn('doGetSevenDaysCheckin ' + str(e))

    @markCmdActionMethod(cmd='sevendays_checkin', action="checkin", clientIdVer=0)
    def doSevenDaysCheckin(self, gameId, userId, clientId):
        try:
            _conf = sevendayscheckin.getConf(gameId) # 配置检查
            mo = MsgPack()
            mo.setCmd('sevendays_checkin')
            status = sevendayscheckin.checkin(userId, gameId, clientId)
            if not status:
                mo.setResult('userId', userId)
                ftlog.info('maybe is script userId =', userId)
                mo.setResult('tip', '签到失败')
                router.sendToUser(mo, userId)
                return

            mo.setResult('todayCheckIn', status.isTodayCheckined())
            mo.setResult('checkInDays',  status.getCheckInDays)
            mo.setResult('checkInOk',  1)

            daysRewards = []
            for _days, rewardContent in enumerate(_conf.get('daysRewards', [])):
                reward = rewardContent.get('reward')
                daysRewards.append({
                    'days': rewardContent.get('days'),
                    'desc': reward.get('desc'),
                    'state': 1 if rewardContent.get('days') <= status.getCheckInDays else 0,
                    'items': reward.get('items')
                })
            mo.setResult('daysRewards', daysRewards)
            mo.setResult('action', 'checkin')
            router.sendToUser(mo, userId)
            #统计
            bireport.reportGameEvent('SZMJ_SEVEN_DAYS_CHECKIN_CHECKIN', userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)
        except SevenDaysCheckinException, e:
            mo = MsgPack()
            mo.setCmd('sevendays_checkin')
            mo.setResult('action', 'checkin')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.warn('SevenDaysCheckinException', userId, e.errorCode, e.message)


if __name__ == '__main__':
    pass
