# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2015

@author: hanwf
'''
from poker.entity.events.tyevent import MatchWinloseEvent
import freetime.util.log as ftlog
from dizhu.entity import dizhuled, dizhuconf
from poker.entity.dao import userdata
from freetime.core.timer import FTTimer
from poker.entity.configure import gdata

class MatchLed(object):
    
    events = [MatchWinloseEvent]
    endText = []
    afterEndText = []
    scope = 'hall6'
    clientIds = []
    
    @classmethod
    def registerEvent(cls, eventbus):
        for event in cls.events:
            eventbus.subscribe(event, cls.handleEvent)

    @classmethod
    def handleEvent(cls, event):
        ftlog.debug('matchledevent gameId=', event.gameId, 'userId=', event.userId, 'matchId=', event.matchId, 'isWin=', event.isWin, 'rank=', event.rank)
        try:
            matchId = str(event.matchId)
            
            if event.isWin and event.rank == 1:
                matchLed = dizhuconf.getLedNotifyConf()
                for led in matchLed:
                    
                    if matchId == led.get("matchId"):
                        conf = gdata.getRoomConfigure(int(matchId))
                        matchConf = conf.get("matchConf", {})
                        reward = cls.getWinnerReward( matchConf.get("rank.rewards", []) )
                        ftlog.debug('matchledevent matchId=', matchId, 'reward=', reward)
                        if reward:
                            winnername = userdata.getAttr(event.userId, 'name')
                            matchname = conf.get("name")
                            cls.makeLedText(winnername, matchname, reward, led.get("ledtext", {}))
                            cls.clientIds = led.get("clientIds", [])
                            cls.sendEndLed()
        except:
            ftlog.exception()

    @classmethod
    def getWinnerReward(cls, conf):
        result = {}
        for reward in conf:
            rank = reward.get("ranking")
            if rank["start"] == 1 and rank["end"] == 1:
                result[1] = reward["desc"]
            if rank["start"] == 2 and rank["end"] == 2:
                result[2] = reward["desc"]
        return result
    
    @classmethod
    def sendEndLed(cls):
        text = cls.endText.pop()
        dizhuled.sendLed(text, cls.scope, cls.clientIds)
        ftlog.debug('matchledevent sendEndLed text=', text)
        FTTimer(180, cls.sendAfterEndLed)
    
    @classmethod
    def sendAfterEndLed(cls):
        text = cls.afterEndText.pop()
        ftlog.debug('matchledevent sendafterendled text=', text)
        dizhuled.sendLed(text, cls.scope, cls.clientIds)
        
    @classmethod
    def makeLedText(cls, winnername, matchname, reward, ledText):
        for led in ledText:
            stage = led.get("stage", "")
            if stage == "end":
                text = led.get("text").format(WINN1st_NAME=winnername, MATCH_NAME=matchname, WIN1st_REWARD=reward[1])
                ftlog.debug('matchled makeledtext end text=', text)
                cls.endText.append(text)
            if stage == "after_end":
                text = led.get("text").format(MATCH_NAME=matchname, WIN1st_REWARD=reward[1], WIN2nd_REWARD=reward[2])
                ftlog.debug('matchled makeledtext after_end text=', text)
                cls.afterEndText.append(text)
    
