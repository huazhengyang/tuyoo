# -*- coding: utf-8 -*-
'''
Created on Oct 29, 2015

@author: hanwf
'''
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from dizhu.entity import dizhuconf
from datetime import datetime
from poker.entity.dao import gamedata, sessiondata
import json
from poker.entity.events.tyevent import EventUserLogin

class ChouJiang360(object):
    eventset = [UserTableWinloseEvent, EventUserLogin]
    
    attr_act = "act_choujiang_360"
    
    @classmethod
    def registerEvents(cls, eventBus):
        ftlog.debug("choujiang360 register events")
        for event in cls.eventset:
            eventBus.subscribe(event, cls.handleEvent)
        
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(EventUserLogin, cls.handleEvent)
        
    @classmethod
    def dateCheck(cls, gameId, userId, conf):
        day_now = datetime.now()
        startdate = datetime.strptime(conf.get('start_date', '2015-01-01'), '%Y-%m-%d').date()
        enddate = datetime.strptime(conf.get('end_date', '2015-01-01'), '%Y-%m-%d').date()
        
        ftlog.debug("choujiang360 userId=", userId, "day_now=", day_now, "startdate=", startdate, "enddate=", enddate)
        if day_now.date()>=startdate and day_now.date()<=enddate:
            return True
        return False
    
    @classmethod
    def clientCheck(cls, gameId, userId, conf):
        clientId = sessiondata.getClientId(userId)
        clientIds = conf.get("clientId", [])
        
        ftlog.debug('choujiang360 gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'clientIds=', clientIds)
        if clientId in clientIds:
            return True
        else:
            return False
        
    @classmethod
    def handleEvent(cls, event):
        try:
            gameId = 6
            userId = event.userId
            conf = dizhuconf.getActivityConf("huiyuan_360")
            
            if not cls.clientCheck(gameId, userId, conf):
                return
            
            if not cls.dateCheck(gameId, userId, conf):
                return
            
            
            data = gamedata.getGameAttrJson(userId, gameId, cls.attr_act, {})
            now = datetime.now()
            now_day = '%d%02d%02d'%(now.year, now.month, now.day)
            
            choujiang_round = conf.get("choujiang_round", [])
            
            if isinstance(event, EventUserLogin):
                if (not data) or (now_day != data["date"]):
                    data = { "round": 0, "date": now_day, "all_count": len(choujiang_round), "current_count": 0, "get_count": 0 }
            else:
                if not data:
                    data = { "round": 1, "date": now_day, "all_count": len(choujiang_round), "current_count": 0, "get_count": 0 }
                else:
                    if now_day == data["date"]:
                        data["round"] += 1
                        if data["round"] in choujiang_round:
                            data["current_count"] += 1
                    else:
                        data = { "round": 1, "date": now_day, "all_count": len(choujiang_round), "current_count": 0, "get_count": 0 }
                        if data["round"] in choujiang_round:
                            data["current_count"] += 1
                        
            ftlog.debug("choujiang360 gameId=", gameId, "userId=", userId, "data=", data)
            gamedata.setGameAttr(userId, gameId, cls.attr_act, json.dumps(data))
            
        except:
            ftlog.exception()

    @classmethod
    def getAllRound(cls):
        conf = dizhuconf.getActivityConf("huiyuan_360")
        return len(conf.get("choujiang_round", []))


