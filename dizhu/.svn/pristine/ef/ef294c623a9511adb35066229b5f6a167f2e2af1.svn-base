# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: hanwf

充值引导：用户获得大满贯，春天，连胜的时候，弹窗引导充值

'''
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from hall.entity import hallproductselector, hallpopwnd
from hall.entity.todotask import TodoTaskHelper
from poker.entity.dao import gamedata, sessiondata
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from dizhu.activities.toolbox import UserInfo

def can_ios_tablefinish_fivestar(event):
    if not event.winlose.isWin:
        return False

    # 玩家在高倍场馆单局倍数超过128倍并获胜
    if event.winlose.windoubles >= 128:
        return True

    # 账号注册时间大于五天、游戏局数超过20局的玩家，连续获胜3局时
    timestamp = pktimestamp.getCurrentTimestamp()
    if UserInfo.getRegisterDays(event.userId, timestamp) > 5:
        winrate, winstreak = gamedata.getGameAttrs(event.userId, 6, ['winrate', 'winstreak'])
        winrate = strutil.loads(winrate, ignoreException=True, execptionValue={'pt':0, 'wt':0})
        try:
            winstreak = 0 if winstreak is None else int(winstreak)
        except:
            winstreak = 0
        if winrate.get('pt', 0) > 20 and winstreak == 3:
            return True
    return False


class ChargeLead(object):
    eventset = [UserTableWinloseEvent]
    
    @classmethod
    def registerEvents(cls, eventBus):
        ftlog.debug('chargelead register events')
        for event in cls.eventset:
            eventBus.subscribe(event, cls.handleEvent)
    
    @classmethod
    def handleEvent(cls, event):
        try:
            winlose = event.winlose
            if not winlose.isWin:
                # 失败不弹出
                return
            if event.skillLevelUp:
                # 升段不弹出
                return

            clientGiftVer = SessionDizhuVersion.getVersionNumber(event.userId)
            if clientGiftVer >= 3.824:
                # 新礼包过滤老礼包
                from poker.entity.configure import gdata
                roomConf = gdata.getRoomConfigure(event.roomId)
                newTypeOfGift = roomConf.get('newTypeOfGift', 0) if roomConf else None
                if ftlog.is_debug():
                    ftlog.debug('ChargeLead handleEvent', 'roomId=', event.roomId,
                                'clientVer=', clientGiftVer, 'newTypeOfGift=', newTypeOfGift,
                                'roomConf=', roomConf, 'newTypeOfGift=', newTypeOfGift)
                if newTypeOfGift:
                    return

            winstreak = gamedata.getGameAttr(event.userId, event.gameId, 'winstreak') or 0

            # 纪录连胜日志, 方便以后线上查询
            ftlog.debug('[<ChargeLead>UserTableWinloseEvent|isWin=True]Dizhu',
                       'gameId=', event.gameId,
                       'userId=', event.userId,
                       'roomId=', event.roomId,
                       'slam=', winlose.slam,
                       'chunTian=', winlose.chunTian,
                       'skillLevelUp=', event.skillLevelUp,
                       'mixConfRoomId=', event.mixConfRoomId,
                       'winstreak=', winstreak)
            
            clientId = sessiondata.getClientId(event.userId)
            _, clientVer, _ = strutil.parseClientId(clientId)

            # 当玩家取得3的倍数连胜时或达成春天、大满贯（及以上倍数）取胜时弹出高手礼包
            if winstreak % 3 == 0 or winlose.slam or winlose.chunTian:
                if ftlog.is_debug():
                    ftlog.debug('ChargeLead.handleEvent gameId=', event.gameId,
                                'userId=', event.userId,
                                'roomId=', event.roomId,
                                'winstreak=', winstreak,
                                'mixConfRoomId=', event.mixConfRoomId,
                                'clientId=', clientId)

                if clientVer >= 3.7:
                    todotask = hallpopwnd.makeTodoTaskWinBuy(event.gameId, event.userId, clientId, event.mixConfRoomId or event.roomId)
                    if todotask:
                        todotask.setParam('delay', 3)
                        TodoTaskHelper.sendTodoTask(event.gameId, event.userId, todotask)
                else:
                    product, _ = hallproductselector.selectWinleadProduct(event.gameId, event.userId, clientId, event.mixConfRoomId or event.roomId)
                    if not product:
                        ftlog.warn('ChargeLead.handleEvent NotFoundProduct gameId=', event.gameId,
                                   'userId=', event.userId,
                                   'roomId=', event.roomId,
                                   'winstreak=', winstreak,
                                   'mixConfRoomId=', event.mixConfRoomId,
                                   'clientId=', clientId)
                        return
                    cls.sendChargeLeadToDoTask(event.gameId, event.userId, product)
        except:
            ftlog.exception()
    
    @classmethod
    def sendChargeLeadToDoTask(cls, gameId, userId, product):
        tasks = TodoTaskHelper.makeWinLeadTodoTask(userId, product)
        TodoTaskHelper.sendTodoTask(gameId, userId, [tasks])
    