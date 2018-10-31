# -*- coding=utf-8 -*-
'''
Created on 16-2-14

@author: luwei
@summary: 积分活动
'''
from dizhu.activities.toolbox import Tool
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.game import TGHall
from poker.entity.dao import sessiondata
from poker.entity.events.tyevent import GameOverEvent, MatchWinloseEvent


class DdzMatchScore(object):
    '''
    积分活动,地主给大厅的积分活动发送事件
    由于大厅积分活动不支持比赛,此处监听比赛结束事件,发送通知给大厅积分活动,来间接实现大厅积分活动对地主比赛的支持
    '''

    @classmethod
    def registerListeners(cls, eventbus):
        eventbus.subscribe(MatchWinloseEvent, cls.onMatchWinlose)
        # eventbus.subscribe(UserTableWinloseEvent, cls.onTableWinlose)
        return True

    @classmethod
    def getDdzActivityConf(cls):
        return dizhuconf.getActivityConf("matchscore")

    @classmethod
    def isOutdate(cls):
        '''
        获得是否过期,使用game/6/activity/0.json中的配置判断
        '''
        dizhuconf = cls.getDdzActivityConf()
        ftlog.debug("DdzMatchScore.onMatchWinlose: dizhuconf=", dizhuconf)
        return not Tool.checkNow(dizhuconf.get('start_date', '2016-01-01 00:00:00'), dizhuconf.get('end_date', '2016-01-01 00:00:00'))

    @classmethod
    def onMatchWinlose(cls, event):
        ftlog.debug("DdzMatchScore.onMatchWinlose: event=", event)
        if cls.isOutdate():
            return ftlog.debug("DdzMatchScore.onMatchWinlose: isOutdate=True")

        userId = event.userId
        roomId = event.matchId
        clientId = sessiondata.getClientId(event.userId)
        # ftlog.debug("DdzMatchScore.onMatchWinlose: event=", event, "event.matchId=", event.matchId, "event.userId=", event.userId, "score=", score)

        gameover = GameOverEvent(userId, DIZHU_GAMEID, clientId, roomId, 0, 0, 0)
        TGHall.getEventBus().publishEvent(gameover)
        ftlog.debug("DdzMatchScore.onMatchWinlose: userId=", event.userId, "gameoverevent=", gameover.__dict__)
