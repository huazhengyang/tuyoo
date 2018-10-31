# -*- coding:utf-8 -*-
'''
Created on 2018年7月23日

@author: wangyonghui
'''

from poker.entity.events.tyevent import UserEvent
import poker.util.timestamp as pktimestamp


class UserRewardAsyncEvent(UserEvent):
    '''
    分享获取奖励事件
    '''
    def __init__(self, gameId, userId, rewardType, rewardId, rewards, **kwargs):
        super(UserRewardAsyncEvent, self).__init__(userId, gameId)
        self.rewardType = rewardType
        self.rewardId = rewardId
        self.rewards = rewards
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.params = kwargs

