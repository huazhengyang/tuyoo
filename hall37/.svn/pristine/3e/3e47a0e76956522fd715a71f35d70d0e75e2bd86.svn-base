# -*- coding:utf-8 -*-
'''
Created on 2016年5月31日

@author: zhaojiangang
'''
from poker.entity.events.tyevent import UserEvent

class UserBindPhoneEvent(UserEvent):
    def __init__(self, userId, gameId):
        super(UserBindPhoneEvent, self).__init__(userId, gameId)
        

class UserBindWeixinEvent(UserEvent):
    def __init__(self, userId, gameId):
        super(UserBindWeixinEvent, self).__init__(userId, gameId)


class UserGrabRedPacketEvent(UserEvent):
    def __init__(self, userId, gameId, redPacket):
        super(UserGrabRedPacketEvent, self).__init__(userId, gameId)
        self.redPacket = redPacket


class UserRedPacketTaskRewardEvent(UserEvent):
    def __init__(self, userId, gameId, taskKind, assetList):
        super(UserRedPacketTaskRewardEvent, self).__init__(userId, gameId)
        self.taskKind = taskKind
        self.assetList = assetList


class HallShare2Event(UserEvent):
    def __init__(self, gameId, userId, sharePointId):
        super(HallShare2Event, self).__init__(userId, gameId)
        self.sharePointId = sharePointId


class HallShare3Event(UserEvent):
    def __init__(self, gameId, userId, sharePointId, rewards):
        super(HallShare3Event, self).__init__(userId, gameId)
        self.sharePointId = sharePointId
        self.rewards = rewards


class UserReceivedInviteeRewardEvent(UserEvent):
    def __init__(self, gameId, userId, invitee, count):
        super(UserReceivedInviteeRewardEvent, self).__init__(userId, gameId)
        self.invitee = invitee
        self.count = count


class UserReceivedCouponEvent(UserEvent):
    def __init__(self, gameId, userId, count, source):
        super(UserReceivedCouponEvent, self).__init__(userId, gameId)
        self.count = count
        self.source = source
        
class EventAfterUserLogin(UserEvent):
    """
    加入被邀请的好友桌
    """
    def __init__(self, userId, gameId, dayFirst, isCreate, clientId, loc, clipboard):
        super(EventAfterUserLogin, self).__init__(userId, gameId)
        self.dayFirst = dayFirst
        self.isCreate = isCreate
        self.clientId = clientId
        self.loc = loc
        self.clipboard = clipboard 
        
class HallWithdrawCashEvent(UserEvent):
    def __init__(self, userId, gameId, count):
        super(HallWithdrawCashEvent, self).__init__(userId, gameId)
        self.count = count