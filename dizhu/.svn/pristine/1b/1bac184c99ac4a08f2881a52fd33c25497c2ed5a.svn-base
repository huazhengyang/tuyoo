# -*- coding: utf-8 -*-
'''
Created on 15-12-2

@author: luwei
'''
from poker.entity.events.tyevent import EventUserLogin
import freetime.util.log as ftlog
from datetime import datetime
from dizhu.entity import dizhuconf, skillscore
from hall.entity import hallitem, datachangenotify
import poker.util.timestamp as pktimestamp
from poker.entity.biz.content import TYContentItem
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import gamedata, sessiondata
from poker.util import strutil

class DashiSend(object):
#     eventset = [EventUserLogin]
    
    @classmethod
    def registerEvents(cls):
        ftlog.debug('dashisend register events')
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(EventUserLogin, cls.handleEvent)
    
    @classmethod
    def dateCheck(cls, gameId, userId, conf):
        day_now = datetime.now()
        start_datetime = datetime.strptime(conf.get('start_date', '2015-01-01 0:0:0'), '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(conf.get('end_date', '2015-01-01 0:0:0'), '%Y-%m-%d %H:%M:%S')
        
        ftlog.debug("DashiSend.dateCheck userId=", userId, "day_now=", day_now, ";start_datetime=", start_datetime, ";end_datetime=", end_datetime)
        if day_now>=start_datetime and day_now<=end_datetime:
            ftlog.debug("DashiSend.dateCheck daynow in range")
            return True
        ftlog.debug("DashiSend.dateCheck daynow not in range")
        return False

    @classmethod
    def gameCheck(cls, userId, gameId):
        userGameId = strutil.getGameIdFromHallClientId(sessiondata.getClientId(userId))
        ftlog.debug('dashisend gameId=', gameId, 'userGameId=', userGameId)
        if userGameId != gameId:
            return False
        else:
            return True
         
    @classmethod
    def getFlagAttr(cls, start_date):
        return "act_dashi_send:" + start_date
    
    @classmethod
    def removeDashiItems(cls, gameId, userId, conf):
        # 道具生成时间
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()
        
        # 大师登陆礼包群
        dashi_items = conf.get('items', [])
        
        # 将所有的大师登陆礼包删除
        for itemId in dashi_items:
            itemKind = hallitem.itemSystem.findItemKind(itemId)
            count = userBag.calcTotalUnitsCount(itemKind)
            userBag.forceConsumeUnitsCountByKind(gameId, itemKind, count, timestamp, 'DIZHU_DASHI_SEND', 0)
    
    @classmethod
    def handleEvent(cls, event):
        try:
            gameId = 6
            userId = event.userId
            conf = dizhuconf.getActivityConf("dashi_send")
            
            # 检查日期在活动日期内
            if not cls.dateCheck(gameId, userId, conf):
                cls.removeDashiItems(gameId, userId, conf)
                return
            
            # 检查用户当前在地主游戏中
            if not cls.gameCheck(userId, gameId):
                return

            # 获得大师分段位
            dashi_score = gamedata.getGameAttr(userId, gameId, 'skillscore') or 1
            dashi_level = skillscore.get_skill_level(dashi_score)
            
            # 获取配置中大师分的段位限制
            dashi_level_limit = conf.get("dashi_level", 1)

            if dashi_level < dashi_level_limit:
                return
            
            # 如果已经发送过大师登陆礼包，则不发送
            attrname = cls.getFlagAttr(conf.get('start_date', '2015-01-01'))
            is_send = gamedata.getGameAttr(userId, gameId, attrname)
            if is_send:
                return
            
            # 道具生成时间
            timestamp = pktimestamp.getCurrentTimestamp()
            
            # 要发送的道具列表
            items = conf.get("item_send", [])
            for item in items:
                contentItem = TYContentItem.decodeFromDict(item)
                userAssets = hallitem.itemSystem.loadUserAssets(userId)
                assetKind, _, _ = userAssets.addAsset(gameId, contentItem.assetKindId,
                                                              contentItem.count, timestamp,
                                                              'DIZHU_DASHI_SEND', 0)

            # 发送邮箱信息
            mail_message = conf.get("mail", "")
            if mail_message:
                pkmessage.sendPrivate(9999, userId, 0, mail_message)

            # 通知用户道具和消息存在改变
            if assetKind.keyForChangeNotify:
                datachangenotify.sendDataChangeNotify(gameId, userId, [assetKind.keyForChangeNotify, 'message'])

            # 成功发送大师登陆礼包，记录下来，避免重复发送
            gamedata.setGameAttr(userId, gameId, attrname, 1)
           
            ftlog.debug('dashisend dashi_level=', dashi_level, 'dashi_level_limit=', dashi_level_limit, 'userId=', userId)
              
        except:
            ftlog.exception()
        
