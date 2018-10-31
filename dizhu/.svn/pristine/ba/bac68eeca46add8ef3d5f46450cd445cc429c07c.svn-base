# -*- coding:utf-8 -*-
'''
Created on 2017年9月14日

@author: wangyonghui
'''

from dizhu.activities.ddzfund import UserPlayDataDatabase, ActivityDdzFund
import freetime.util.log as ftlog
from poker.entity.configure import gdata

from dizhu.game import TGDizhu
from poker.entity.events.tyevent import MatchWinloseEvent


@classmethod
def onMatchWinlose(cls, event):
    '''
    监听比赛结局胜负
    '''
    ok = cls.checkActivityDate()
    if not ok:
        if ftlog.is_debug():
            ftlog.debug('ActivityDdzFund.onMatchWinlose OutDate userId=', event.userId,
                        'matchId=', event.matchId)
        return

    userId = event.userId

    status = cls.loadFundStatus(userId, event.timestamp)

    if not status.isActivated:
        ftlog.debug('ActivityDdzFund.onMatchWinlose userId=', userId,
                    'status=', status.__dict__)
        return

    roomId = event.matchId
    try:
        roomId = int(roomId)
    except:
        ftlog.warn('ActivityDdzFund.onMatchWinlose BadMatchId userId=', userId,
                   'status=', status.__dict__)
        return

    bigRoomId = gdata.getBigRoomId(roomId)
    data_wrapper = UserPlayDataDatabase(userId)
    data_wrapper.increase(event.isWin, True, 0, bigRoomId)

    ftlog.info('ActivityDdzFund.onMatchWinlose userId=', userId,
               'matchId=', event.matchId,
               'isWin=', event.isWin,
               'isMatch=', True,
               'roomLevel=', 0,
               'bigRoomId=', bigRoomId,
               'roomId=', roomId)


eventBus = TGDizhu.getEventBus()
handlers = eventBus._handlersMap.get(MatchWinloseEvent)
for h in handlers:

    ftlog.info('dizhu.activities.ddzfund __module__=', h.__module__)

    if h.__module__ == 'dizhu.activities.ddzfund':
        #dizhu.activities.ddzfund
        handlers.remove(h)
        ftlog.info('dizhu.activities.ddzfund removed. 20170914')
        break

ActivityDdzFund.onMatchWinlose = onMatchWinlose
eventBus.subscribe(MatchWinloseEvent, ActivityDdzFund.onMatchWinlose)

ftlog.info('dizhu.activities.ddzfund over. 20170914')

