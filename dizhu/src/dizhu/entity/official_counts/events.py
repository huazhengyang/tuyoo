# -*- coding: utf-8 -*-
from poker.entity.events.tyevent import UserEvent


class OfficialMessageEvent(UserEvent):
    '''
    公众号推送事件
    '''

    def __init__(self, gameId, userId, eventId, msgParams=None, **kwargs):
        super(OfficialMessageEvent, self).__init__(userId, gameId)
        self.eventId = eventId
        self.msgParams = msgParams or {}
        self.kwargs = kwargs
