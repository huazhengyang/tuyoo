# -*- coding: utf-8 -*-
'''
Created on Oct 30, 2015

@author: hanwf
'''
from poker.entity.events.tyevent import EventUserLogin
import freetime.util.log as ftlog
from datetime import datetime
from poker.entity.dao import sessiondata, gamedata
from dizhu.entity import dizhuconf
import json

class Login30(object):
    eventset = [EventUserLogin]
    
    attr_act = "act_login30_360"
    
    @classmethod
    def registerEvents(cls):
        ftlog.debug('login30 register events')
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(EventUserLogin, cls.handleEvent)
    
    @classmethod
    def dateCheck(cls, gameId, userId, conf):
        day_now = datetime.now()
        startdate = datetime.strptime(conf.get('start_date', '2015-01-01'), '%Y-%m-%d').date()
        enddate = datetime.strptime(conf.get('end_date', '2015-01-01'), '%Y-%m-%d').date()
        
        ftlog.debug("login30 userId=", userId, "day_now=", day_now, "startdate=", startdate, "enddate=", enddate)
        if day_now.date()>=startdate and day_now.date()<=enddate:
            return True
        return False
    
    @classmethod
    def clientCheck(cls, gameId, userId, conf):
        clientId = sessiondata.getClientId(userId)
        clientIds = conf.get("clientId", [])
        
        ftlog.debug('login30 gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'clientIds=', clientIds)
        
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
            
            if not data:
                data = { "days": now_day, "all_count": 30, "current_count": 1, "get_count": 0 }
            else:
                if now_day == data["days"]:
                    # 这段代码用于fix以前的bug 
                    if data["get_count"] > data["current_count"]:
                        data["get_count"] = 0
                        gamedata.setGameAttr(userId, gameId, cls.attr_act, json.dumps(data))
                    return
                
                lastdate = datetime.strptime(data["days"], '%Y%m%d').date()
                if (now.date() - lastdate).days != 1:
                    data = { "days": now_day, "all_count": 30, "current_count": 1, "get_count": 0 }
                else:
                    data["days"] = now_day
                    data["current_count"] += 1
                    
                    # 这段代码用于fix以前的bug 
                    if data["get_count"] > data["current_count"]:
                        data["get_count"] = 0
                    
                    if data["current_count"] >= data["all_count"]:
                        data = { "days": now_day, "all_count": 30, "current_count": 1, "get_count": 0 }
            
            ftlog.debug("login30 gameId=", gameId, "userId=", userId, "data=", data)
            gamedata.setGameAttr(userId, gameId, cls.attr_act, json.dumps(data))
            
        except:
            ftlog.exception()
    
