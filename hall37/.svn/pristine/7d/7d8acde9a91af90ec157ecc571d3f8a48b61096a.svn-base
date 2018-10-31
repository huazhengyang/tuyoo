# -*- coding: utf-8 -*-
"""
Created on 2015年11月21日

@author: zhaojiangang
"""
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from freetime.entity.msg import MsgPack
from hall.entity import monthcheckin
import freetime.util.log as ftlog
from hall.entity.monthcheckin import MonthCheckinException
from hall.entity import datachangenotify
from poker.util import strutil
import hall.client_ver_judge as client_ver_judge

@markCmdActionHandler
class MonthCheckinHandler(BaseMsgPackChecker):
    def __init__(self):
        super(MonthCheckinHandler, self).__init__()

    @classmethod
    def calcDaysRewardState(cls, status, days):
        if status.isReward(days):
            return 2
        if status.allCheckinCount >= days:
            return 1
        return 0

    @markCmdActionMethod(cmd='month_checkin', action="update", clientIdVer=0)
    def doUpdateMonthCheckin(self, gameId, userId, clientId):
        try:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            status = monthcheckin.loadStatus(userId)
            mo.setResult('curDate', status.curDate.strftime('%Y%m%d'))
            mo.setResult('checkinDates', [d.strftime('%Y%m%d') for d in status.checkinDateList])
            mo.setResult('supCheckinDates', [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
            mo.setResult('rewardDaysList', status.rewardDaysList)
            daysRewards = []
            for _days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards', [])):
                reward = rewardContent.get('reward')
                monthRange = monthcheckin.getMonthRange()
                if rewardContent.get('days') < monthRange:
                    monthRange = rewardContent.get('days')
                daysRewards.append({
                    'days': monthRange,
                    'desc': reward.get('desc'),
                    'picUrl': reward.get('picUrl'),
                    'state': self.calcDaysRewardState(status, monthRange)
                })
                ftlog.debug('doUpdateMonthCheckin daysRewards monthRange =', monthRange)
            mo.setResult('daysRewards', daysRewards)
            checkinRewardMap = monthcheckin.getConf().get('checkDesc', {})
            mo.setResult('specailDate', monthcheckin.getNowSpecailDate(status.curDate.strftime('%Y%m%d')))
            mo.setResult('checkinRewardImg', checkinRewardMap.get('picUrl'))
            _, clientVer, _ = strutil.parseClientId(clientId)
            if clientVer < client_ver_judge.client_ver_397:
                mo.setResult('checkinRewardDesc', '500金币+1幸运卡')
            else:
                mo.setResult('checkinRewardDesc', checkinRewardMap.get('desc', '500金币'))
            activies = []
            for _days, rewardContent in enumerate(monthcheckin.getConf().get('activies', [])):
                activies.append({
                    'date': rewardContent.get('date'),
                    'tip': rewardContent.get('tip')
                })
            mo.setResult('activies', activies)
            mo.setResult('action', 'update')
            mo.setResult('supCheckinCount', monthcheckin.getSupplementCheckinCardCount(userId, gameId))
            ftlog.debug('doUpdateMonthCheckin userId =', userId
                       , 'gameId =', gameId
                       , 'clientId =', clientId
                       , 'curDate =', status.curDate.strftime('%Y%m%d')
                       , 'checkinDates =', [d.strftime('%Y%m%d') for d in status.checkinDateList]
                       , 'supCheckinDates =', [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
            router.sendToUser(mo, userId)
        except MonthCheckinException, e:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            mo.setResult('action', 'update')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.warn('doupdate ' + str(e))

    @markCmdActionMethod(cmd='month_checkin', action="checkin", clientIdVer=0)
    def doCheckinMonth(self, gameId, userId, clientId):
        try:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            status = monthcheckin.checkin(userId, gameId, clientId)
            if not status:
                mo.setResult('userId', userId)
                ftlog.info('maybe is script userId =', userId)
                mo.setResult('tip', 'maybe is script')
                router.sendToUser(mo, userId)
                return
            checkinRewardMap = monthcheckin.getConf().get('checkinReward', {})
            mo.setResult('checkinDateList', [d.strftime('%Y%m%d') for d in status.checkinDateList])
            mo.setResult('supplementCheckinDateList', [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
            mo.setResult('rewardDaysList', status.rewardDaysList)
            _, clientVer, _ = strutil.parseClientId(clientId)
            if clientVer < client_ver_judge.client_ver_397:
                mo.setResult('descSucess', '恭喜你获得500金币+1幸运卡')
            else:
                mo.setResult('descSucess', '恭喜你获得%s'%checkinRewardMap.get('desc', '500金币'))
            mo.setResult('supCheckinCount', monthcheckin.getSupplementCheckinCardCount(userId, gameId))
            daysRewards = []
            for _days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards', [])):
                reward = rewardContent.get('reward')
                monthRange = monthcheckin.getMonthRange()
                if rewardContent.get('days') < monthRange:
                    monthRange = rewardContent.get('days')
                daysRewards.append({
                    'days': monthRange,
                    'desc': reward.get('desc'),
                    'picUrl': reward.get('picUrl'),
                    'state': self.calcDaysRewardState(status, monthRange)
                })
                ftlog.debug('doCheckinMonth daysRewards monthRange =', monthRange)
            mo.setResult('daysRewards', daysRewards)
            mo.setResult('action', 'checkin')
            ftlog.debug('doCheckinMonth userId =', userId
                       , 'gameId =', gameId
                       , 'clientId =', clientId
                       , 'checkinDateList =', [d.strftime('%Y%m%d') for d in status.checkinDateList]
                       , 'supplementCheckinDateList =',
                       [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
            router.sendToUser(mo, userId)
            datachangenotify.sendDataChangeNotify(gameId, userId, ['free', 'promotion_loc'])
        except MonthCheckinException, e:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            mo.setResult('action', 'checkin')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.warn('MonthCheckinException', userId, e.errorCode, e.message)

    @markCmdActionMethod(cmd='month_checkin', action="supCheckin", clientIdVer=0)
    def doSupCheckinMonth(self, gameId, userId, clientId):
        try:
            mo = MsgPack()
            typeData, status = monthcheckin.supplementCheckin(userId, gameId, clientId)

            mo.setCmd('month_checkin')
            if not status:
                mo.setResult('userId', userId)
                mo.setResult('tip', 'maybe is script')
                ftlog.info('maybe is script userId =', userId)
                router.sendToUser(mo, userId)
                return
            if typeData == 1:
                mo.setResult('action', 'supCheckin')
                mo.setResult('lessCard', status['lessCard'])
                router.sendToUser(mo, userId)
            else:
                mo.setResult('action', 'supCheckin')
                mo.setResult('supCheckinCount', monthcheckin.getSupplementCheckinCardCount(userId, gameId))
                mo.setResult('checkinDateList', [d.strftime('%Y%m%d') for d in status.checkinDateList])
                mo.setResult('supplementCheckinDateList',
                             [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
                mo.setResult('rewardDaysList', status.rewardDaysList)
                daysRewards = []
                for _days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards', [])):
                    reward = rewardContent.get('reward')
                    monthRange = monthcheckin.getMonthRange()
                    if rewardContent.get('days') < monthRange:
                        monthRange = rewardContent.get('days')
                    daysRewards.append({
                        'days': monthRange,
                        'desc': reward.get('desc'),
                        'picUrl': reward.get('picUrl'),
                        'state': self.calcDaysRewardState(status, monthRange)
                    })
                    ftlog.debug('doSupCheckinMonth daysRewards monthRange =', monthRange)
                mo.setResult('daysRewards', daysRewards)
                supplementCheckinRewardMap = monthcheckin.getConf().get('supplementCheckinReward', {})
                _, clientVer, _ = strutil.parseClientId(clientId)
                if clientVer < client_ver_judge.client_ver_397:
                    mo.setResult('descSucess', '恭喜你获得500金币+1幸运卡')
                else:
                    mo.setResult('descSucess', '恭喜你获得%s'%supplementCheckinRewardMap.get('desc', '500金币'))
                ftlog.debug('doSupCheckinMonth usereId =', userId
                           , 'gameId =', gameId
                           , 'clientId =', clientId
                           , 'checkinDateList =', [d.strftime('%Y%m%d') for d in status.checkinDateList]
                           , 'supplementCheckinDateList =',
                           [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
                router.sendToUser(mo, userId)
                datachangenotify.sendDataChangeNotify(gameId, userId, ['free', 'promotion_loc'])
        except MonthCheckinException, e:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            mo.setResult('action', 'supCheckin')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.debug('dosupCheckin ' + str(e))

    @markCmdActionMethod(cmd='month_checkin', action="getMessage", clientIdVer=0)
    def doGetMessage(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        state = msg.getParam('state')
        isFirst = msg.getParam('isFirst')
        try:
            mo = MsgPack()
            result = monthcheckin.doMessage(userId, gameId, clientId, state, isFirst)
            mo.setCmd('month_checkin')
            mo.setResult('userId', userId)
            mo.setResult('result', result)
            mo.setResult('gameId', gameId)
            mo.setResult('action', 'getMessage')
            router.sendToUser(mo, userId)
        except MonthCheckinException, e:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            mo.setResult('action', 'getMessage')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.warn('doGetMessage ' + str(e))

    @markCmdActionMethod(cmd='month_checkin', action="getDaysReward", clientIdVer=0)
    def doGetDaysRewardMonth(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        days = msg.getParam('days')
        try:
            mo = MsgPack()
            MonthCheckinStatus = monthcheckin.getDaysReward(userId, days, gameId)
            mo.setCmd('month_checkin')
            if not MonthCheckinStatus:
                mo.setResult('userId', userId)
                mo.setResult('tip', 'maybe is script')
                ftlog.info('maybe is script userId =', userId)
                router.sendToUser(mo, userId)
                return
            mo.setResult('action', 'getDaysReward')
            mo.setResult('checkinDateList', [d.strftime('%Y%m%d') for d in MonthCheckinStatus.checkinDateList])
            daysRewards = []
            for days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards', [])):
                reward = rewardContent.get('reward')
                monthRange = monthcheckin.getMonthRange()
                if rewardContent.get('days') < monthRange:
                    monthRange = rewardContent.get('days')
                daysRewards.append({
                    'days': monthRange,
                    'desc': reward.get('desc'),
                    'picUrl': reward.get('picUrl'),
                    'state': self.calcDaysRewardState(MonthCheckinStatus, monthRange)
                })
                ftlog.debug('doGetDaysRewardMonth daysRewards monthRange =', monthRange)
            mo.setResult('daysRewards', daysRewards)
            mo.setResult('supplementCheckinDateList',
                         [d.strftime('%Y%m%d') for d in MonthCheckinStatus.supplementCheckinDateList])
            mo.setResult('rewardDaysList', MonthCheckinStatus.rewardDaysList)
            ftlog.debug('doGetDaysRewardMonth userId =', userId
                       , 'gameId =', gameId
                       , 'clientId =', clientId
                       , 'daysRewards =', daysRewards)
            router.sendToUser(mo, userId)
            datachangenotify.sendDataChangeNotify(gameId, userId, ['free', 'promotion_loc'])
        except MonthCheckinException, e:
            mo = MsgPack()
            mo.setCmd('month_checkin')
            mo.setResult('action', 'getDaysReward')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
            ftlog.warn('doGetDaysRewardMonth ' + str(e))


if __name__ == '__main__':
    pass
