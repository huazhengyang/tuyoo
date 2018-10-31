# -*- coding: utf-8 -*-
'''
Created on Oct 29, 2015

@author: hanwf
'''
from datetime import datetime
import json

from dizhu.entity import dizhuconf
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import datachangenotify, hallitem
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import gamedata
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from poker.entity.biz.item.item import TYAssetUtils


class ProtocolBuilder(object):
    
    @classmethod
    def buildHuiYuanInfo(cls, gameId, userId, isopen, gifts, mo):
        mo.setCmd('activity_pc')
        mo.setResult('action', "huiyuan_360_info")
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('open', isopen)
        mo.setResult('gifts', gifts)
    
    @classmethod
    def buildGetGift(cls, gameId, userId, giftId, tip, ecode, status, all_count, get_count, mo):
        mo.setCmd('activity_pc')
        mo.setResult('action', "get_gift")
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('giftId', giftId)
        mo.setResult('tip', tip)
        mo.setResult('ecode', ecode)
        mo.setResult('status', status)
        mo.setResult('all_count', all_count)
        mo.setResult('get_count', get_count)

@markCmdActionHandler
class ActivityPCHandler(BaseMsgPackChecker):
    
    def _check_param_giftId(self, msg, key, params):
        giftId = msg.getParam(key)
        if giftId and isinstance(giftId, (str, unicode)):
            return None, giftId
        return 'ERROR of giftId !' + str(giftId), None
    
    def dateCheck(self, gameId, userId, conf):
        day_now = datetime.now()
        startdate = datetime.strptime(conf.get('start_date', '2015-01-01'), '%Y-%m-%d').date()
        enddate = datetime.strptime(conf.get('end_date', '2015-01-01'), '%Y-%m-%d').date()
        
        ftlog.debug("activity_pc userId=", userId, "day_now=", day_now, "startdate=", startdate, "enddate=", enddate)
        if day_now.date()>=startdate and day_now.date()<=enddate:
            return True
        return False
    
    def getDay30Status(self, gameId, userId):
        from dizhu.activities.login30_360 import Login30
        status = 0
        all_count = 0
        get_count = 0
        data = gamedata.getGameAttrJson(userId, gameId, Login30.attr_act, {})
        if data:
            all_count = data["all_count"]
            get_count = data["get_count"]
            if (data["get_count"] < data["current_count"]) and (data["get_count"] < all_count):
                status = 1
            else:
                status = 0
        
        return status, all_count, get_count
    
    def getChouJiang5Status(self, gameId, userId):
        from dizhu.activities.choujiang_360 import ChouJiang360
        status = 0
        all_count = ChouJiang360.getAllRound()
        get_count = 0
        data = gamedata.getGameAttrJson(userId, gameId, ChouJiang360.attr_act, {})
        if data:
            all_count = data["all_count"]
            get_count = data["get_count"]
            if (data["get_count"] < data["current_count"]) and (data["get_count"] < all_count):
                status = 1
            else:
                status = 0
        
        return status, all_count, get_count
        
    
    def getDay30StatusInfo(self, gameId, userId):
        status, all_count, get_count = self.getDay30Status(gameId, userId)
        
        return {
            "status": status,
            "all_count": all_count,
            "get_count": get_count
        }
        
    def getChouJiang5StatusInfo(self, gameId, userId):
        status, all_count, get_count = self.getChouJiang5Status(gameId, userId)
        
        return {
            "status": status,
            "all_count": all_count,
            "get_count": get_count
        }
    
    @markCmdActionMethod(cmd="activity_pc", action="huiyuan_360_info", clientIdVer=0, scope="game")
    def doHuiYuanInfo(self, gameId, userId, clientId):
        ftlog.debug("activity_pc dohuiyuaninfo gameId=", gameId, "userId=", userId, "clientId=", clientId)
        conf = dizhuconf.getActivityConf("huiyuan_360")
        
        isopen = 1
        if not self.dateCheck(gameId, userId, conf):
            isopen = 0
        
        gifts = {
            "day_30": self.getDay30StatusInfo(gameId, userId),
            "choujiang_5": self.getChouJiang5StatusInfo(gameId, userId)
        }
        
        mo = MsgPack()
        ProtocolBuilder.buildHuiYuanInfo(gameId, userId, isopen, gifts, mo)
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd="activity_pc", action="get_gift", clientIdVer=0, scope="game")
    def doGetGift(self, gameId, userId, clientId, giftId):
        ftlog.debug("activity_pc dogetgift gameId=", gameId, "userId=", userId, "clientId=", clientId)
        
        tip = ''
        ecode = 0
        status = 0
        all_count = 0
        get_count = 0
        
        if giftId == "day_30":
            tip, ecode, status, all_count, get_count = self.getDay30Reward(gameId, userId, clientId)
        elif giftId == "choujiang_5":
            tip, ecode, status, all_count, get_count = self.getChouJiangReward(gameId, userId, clientId)
        else:
            pass
        
        mo = MsgPack()
        ProtocolBuilder.buildGetGift(gameId, userId, giftId, tip, ecode, status, all_count, get_count, mo)
        router.sendToUser(mo, userId)
        
    def getDay30Reward(self, gameId, userId, clientId):
        from dizhu.activities.login30_360 import Login30
        status = 0
        all_count = 0
        get_count = 0
        tip = ''
        ecode = 0
        try:
            conf = dizhuconf.getActivityConf("huiyuan_360")
            data = gamedata.getGameAttrJson(userId, gameId, Login30.attr_act, {})
            if data:
                if data["get_count"] != data["current_count"]:
                    reward = conf.get("login30", [])[data["current_count"]-1]
                    contentItem = TYContentItem.decodeFromDict(reward)
                    tip = self.sendReward(gameId, userId, clientId, contentItem, 'HUI_YUAN_360', 0)
                    data["get_count"] = data["current_count"]
                    
                all_count = data["all_count"]
                get_count = data["get_count"]
                
                status = int(data["get_count"] < data["current_count"])
                
                gamedata.setGameAttr(userId, gameId, Login30.attr_act, json.dumps(data))
        except:
            ftlog.exception()
            tip = "领取失败"
            ecode = 1
        
        return tip, ecode, status, all_count, get_count
    
    def getChouJiangReward(self, gameId, userId, clientId):
        from dizhu.activities.choujiang_360 import ChouJiang360
        status = 0
        all_count = 0
        get_count = 0
        tip = ''
        ecode = 0
        try:
            data = gamedata.getGameAttrJson(userId, gameId, ChouJiang360.attr_act, {})
            if data:
                if data["get_count"] < data["current_count"]:
                    tip = self.sendReward(gameId, userId, clientId,
                                          TYContentItem('item:4147', 1),
                                          'HUI_YUAN_360', 0)
                    tip = ''.join([tip, ' 请去背包查收'])
                    data["get_count"] += 1
                    
                all_count = data["all_count"]
                get_count = data["get_count"]
                
                status = int(data["get_count"] < data["current_count"])
                
                gamedata.setGameAttr(userId, gameId, ChouJiang360.attr_act, json.dumps(data))
        except:
            ftlog.exception()
            tip = "领取失败"
            ecode = 1
        
        return tip, ecode, status, all_count, get_count
    
    def sendReward(self, gameId, userId, clientId, contentItem, eventId, intEventParam):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            assetKind, count, final = userAssets.addAsset(gameId, contentItem.assetKindId,
                                                          contentItem.count, timestamp,
                                                          eventId, intEventParam)
            if assetKind.keyForChangeNotify:
                datachangenotify.sendDataChangeNotify(gameId, userId, [assetKind.keyForChangeNotify])
            contentStr = TYAssetUtils.buildContent((assetKind, count, final))
            ftlog.info('ActivityPCHandler.sendReward gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'reward=', '(%s,%s)' % (contentItem.assetKindId, contentItem.count),
                       'eventId=', eventId,
                       'intEventParam=', intEventParam)
            return '恭喜您获得%s!' % (contentStr)
        except TYBizException, e:
            ftlog.warn('ActivityPCHandler.sendReward gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'reward=', '(%s,%s)' % (contentItem.assetKindId, contentItem.count),
                       'eventId=', eventId,
                       'intEventParam=', intEventParam,
                       'err=', str(e))
            return '领取失败'
        
#     def sendChip(self, gameId, userId, clientId, chip):
#         try:
#             userchip.incrChip(userId, gameId, chip, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, 'HUI_YUAN_360', 0, clientId)
#             datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
#             return 0
#         except:
#             return -1
#     
#     def sendItem(self, gameId, userId, clientId, itemId, itemcount):
#         try:
#             timestamp = pktimestamp.getCurrentTimestamp()
#             itemKind = hallitem.itemSystem.findItemKind(itemId)
#             if not itemKind:
#                 ftlog.warn('activity_pc.sendItem gameId=', gameId, 'userId=', userId, 'itemKindId=', itemId, 'err=', 'UnknownItemKindId')
#                 return None
#             userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
#             userBag.addItemUnitsByKind(gameId, itemKind, itemcount, timestamp, 0, 'HUI_YUAN_360', 0)
#             datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
#             return itemKind
#         except:
#             return None

