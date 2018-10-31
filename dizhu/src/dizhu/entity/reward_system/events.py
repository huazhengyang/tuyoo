# -*- coding:utf-8 -*-
'''
Created on 2018年7月23日

@author: wangyonghui
'''

from poker.entity.events.tyevent import UserEvent


class UserRewardSystemEvent(UserEvent):
    '''
    获取奖励事件
    '''
    def __init__(self, gameId, userId, rewards, rewardsControl):
        super(UserRewardSystemEvent, self).__init__(userId, gameId)
        self.rewards = rewards
        self.rewardsControl = rewardsControl
