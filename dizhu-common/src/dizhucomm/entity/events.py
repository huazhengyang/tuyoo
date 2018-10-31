# -*- coding:utf-8 -*-
'''
Created on 2017年2月8日

@author: zhaojiangang
'''
from poker.entity.configure import gdata
from poker.entity.events.tyevent import UserEvent


class UserTableEvent(UserEvent):
    '''
    牌桌上发生的事件的基类
    '''
    def __init__(self, gameId, userId, roomId, tableId):
        super(UserTableEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId

class UserTableGameReadyEvent(UserTableEvent):
    '''
    牌局开始, 发完牌后触发的事件
    '''
    def __init__(self, gameId, userId, roomId, tableId):
        super(UserTableGameReadyEvent, self).__init__(gameId, userId, roomId, tableId)

class UserTableCallEvent(UserTableEvent):
    '''
    叫地主阶段, 玩家叫地主
    '''
    def __init__(self, gameId, userId, roomId, tableId, call, isGrab):
        super(UserTableCallEvent, self).__init__(gameId, userId, roomId, tableId)
        self.isGrab = isGrab
        self.call = call

class UserTablePlayEvent(UserTableEvent):
    '''
    已经完成叫地主的过程, 开始出牌事件
    '''
    def __init__(self, gameId, userId, roomId, tableId, baseCardType, dizhuUserId):
        super(UserTablePlayEvent, self).__init__(gameId, userId, roomId, tableId)
        self.baseCardType = baseCardType
        self.dizhuUserId = dizhuUserId

class UserLevelGrowEvent(UserEvent):
    def __init__(self, gameId, userId, oldLevel, newLevel):
        super(UserLevelGrowEvent, self).__init__(userId, gameId)
        self.oldLevel = oldLevel
        self.newLevel = newLevel

class Winlose(object):
    '''
    牌局结束, 当前winUserId的结算信息
    '''
    def __init__(self, winUserId, winCard, isWin,
                 isDizhu, deltaChip, finalChip,
                 windoubles=1, nBomb=0, chunTian=False, slam=False,
                 baseScore=False, rocket=None, punishState=0, outCardSeconds=0, leadWin=0,
                 assist=0, validMaxOutCard=0, **kwargs):
        self.winUserId = winUserId
        self.winCard = winCard
        self.isWin = isWin
        self.isDizhu = isDizhu
        self.deltaChip = deltaChip
        self.finalChip = finalChip
        self.windoubles = windoubles
        self.nBomb = nBomb
        self.chunTian = chunTian
        self.slam = slam
        #
        self.baseScore = baseScore
        self.rocket = rocket
        self.punishState = punishState
        self.outCardSeconds = outCardSeconds
        self.leadWin = leadWin
        self.assist = assist
        self.validMaxOutCard = validMaxOutCard
        self.kwargs = kwargs


class UserTableWinloseEvent(UserTableEvent):
    '''
    牌局结束, 触发当前用户的结算事件
    '''
    def __init__(self, gameId, userId, roomId, tableId, winlose, skillLevelUp=False, **kwargs):
        super(UserTableWinloseEvent, self).__init__(gameId, userId, roomId, tableId)
        self.winlose = winlose
        self.skillLevelUp = skillLevelUp
        self.mixConfRoomId = kwargs.get('mixConfRoomId')

class UserTBoxLotteryEvent(UserEvent):
    def __init__(self, gameId, userId):
        super(UserTBoxLotteryEvent, self).__init__(userId, gameId)

class UseTableEmoticonEvent(UserTableEvent):
    '''
    桌面上, 玩家互动表情的事件
    '''
    def __init__(self, gameId, userId, roomId, tableId, emoticon, price, count=1):
        super(UseTableEmoticonEvent, self).__init__(gameId, userId, roomId, tableId)
        self.emoticon = emoticon
        self.price = price
        self.count = count

class UserMatchSignInEvent(UserEvent):
    '''
    玩家报名比赛事件
    '''
    def __init__(self, gameId, userId, bigRoomId):
        super(UserMatchSignInEvent, self).__init__(userId, gameId)
        self.bigRoomId = bigRoomId


class UserTableOutCardBombEvent(UserTableEvent):
    """
    用户牌桌扔出炸弹的事件
    """
    def __init__(self, gameId, userId, roomId, tableId, userIds, **kwargs):
        super(UserTableOutCardBombEvent, self).__init__(gameId, userId, roomId, tableId)
        self.mixConfRoomId = kwargs.get('mixConfRoomId')
        self.roomName = kwargs.get('roomName', '')
        self.userIds = userIds

    @property
    def bigRoomId(self):
        return int(self.mixConfRoomId) if self.mixConfRoomId else gdata.getBigRoomId(self.roomId)

