# -*- coding:utf-8 -*-
'''
Created on 2018年5月13日

@author: wangyonghui
'''
from poker.entity.events.tyevent import UserEvent


class UserCouponReceiveEvent(UserEvent):
    '''
    用户接收奖券事件
    '''
    def __init__(self, gameId, userId, count, source):
        super(UserCouponReceiveEvent, self).__init__(userId, gameId)
        self.count = count
        self.source = source