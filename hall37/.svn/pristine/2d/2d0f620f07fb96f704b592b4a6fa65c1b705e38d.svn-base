# -*- coding: utf-8 -*-

from poker.entity.configure import gdata
from poker.protocol import _runenv
from poker.protocol.decorator import markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router,runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from freetime.entity.msg import MsgPack
from hall.entity import monthcheckin, halldailycheckin
from hall.entity.halldailycheckin import TYDailyCheckinImpl
import freetime.util.log as ftlog
from hall.entity.monthcheckin import MonthCheckinException 
from hall.servers.util.monthcheckin_handler import MonthCheckinHandler


@markCmdActionMethod(cmd='month_checkin', action="supCheckin", clientIdVer=0)
def doSupCheckinMonth(gameId,userId,clientId):
    ftlog.debug('doSupCheckinMonth..userId',userId)
    try :
        mo = MsgPack()
        typeData,status = monthcheckin.supplementCheckin(userId, gameId, clientId)
        ftlog.debug('doCheckinMonth..supplementCheckin = ',status)
        mo.setCmd('month_checkin')
        if typeData == 1 :
            mo.setResult('action', 'supCheckin')
            mo.setResult('lessCard',status['lessCard'])
            router.sendToUser(mo, userId)
        else :
            mo.setResult('action', 'supCheckin')
            mo.setResult('checkinDateList', [d.strftime('%Y%m%d') for d in status.checkinDateList])
            mo.setResult('supplementCheckinDateList', [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
            mo.setResult('rewardDaysList', status.rewardDaysList)
            daysRewards = []
            for days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards',[])):
                reward = rewardContent.get('reward')
                daysRewards.append({
                                    'days':rewardContent.get('days'),
                                    'desc':reward.get('desc'),
                                    'picUrl':reward.get('picUrl'),
                                    'state':MonthCheckinHandler.calcDaysRewardState(status, rewardContent.get('days'))
                })
                ftlog.debug('doUpdateMonthCheckin..days',rewardContent.get('days')
                            ,'desc = ',reward.get('desc')
                            ,'state = ',MonthCheckinHandler.calcDaysRewardState(status, rewardContent.get('days')))
            mo.setResult('daysRewards',daysRewards)
            mo.setResult('descSucess', '恭喜你获得500金币+1幸运卡')
            router.sendToUser(mo, userId)
    except MonthCheckinException, e:
        mo = MsgPack()
        mo.setCmd('month_checkin')
        mo.setResult('action','supCheckin')
        mo.setError(e.errorCode, e.message)
        router.sendToUser(mo, userId)
        ftlog.warn('MonthCheckinException', e.errorCode, e.message)


@markCmdActionMethod(cmd='month_checkin', action="checkin", clientIdVer=0)
def doCheckinMonth(gameId,userId,clientId):
    ftlog.debug('doCheckinMonth..userId',userId)
    try :
        mo = MsgPack()
        status = monthcheckin.checkin(userId, gameId, clientId)
        ftlog.debug('doCheckinMonth..status = ',status)
        mo.setCmd('month_checkin')
        
        mo.setResult('checkinDateList', [d.strftime('%Y%m%d') for d in status.checkinDateList])
        mo.setResult('supplementCheckinDateList', [d.strftime('%Y%m%d') for d in status.supplementCheckinDateList])
        mo.setResult('rewardDaysList', status.rewardDaysList)
        mo.setResult('descSucess', '恭喜你获得500金币+1幸运卡')
        daysRewards = []
        for days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards',[])):
            reward = rewardContent.get('reward')
            daysRewards.append({
                            'days':rewardContent.get('days'),
                            'desc':reward.get('desc'),
                            'picUrl':reward.get('picUrl'),
                            'state':MonthCheckinHandler.calcDaysRewardState(status, rewardContent.get('days'))
            })
            ftlog.debug('doUpdateMonthCheckin..days',rewardContent.get('days')
                        ,'desc = ',reward.get('desc')
                        ,'state = ',MonthCheckinHandler.calcDaysRewardState(status, rewardContent.get('days')))
        mo.setResult('daysRewards',daysRewards)
        mo.setResult('action','checkin')
        router.sendToUser(mo, userId)
    except MonthCheckinException, e:
        mo = MsgPack()
        mo.setCmd('month_checkin')
        mo.setResult('action','checkin')
        mo.setError(e.errorCode, e.message)
        router.sendToUser(mo, userId)
        ftlog.warn('MonthCheckinException', userId, e.errorCode, e.message)
    


cmdpath = 'month_checkin#supCheckin'
vcalls = _runenv._cmd_path_methods.get(cmdpath)
if vcalls :
    mp = vcalls[0][1]
    mp['fun_method'] = doSupCheckinMonth
MonthCheckinHandler.doSupCheckinMonth = doSupCheckinMonth

cmdpath = 'month_checkin#checkin'
vcalls = _runenv._cmd_path_methods.get(cmdpath)
if vcalls :
    mp = vcalls[0][1]
    mp['fun_method'] = doCheckinMonth
MonthCheckinHandler.doCheckinMonth = doCheckinMonth
