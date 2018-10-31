# -*- coding:utf-8 -*-
'''
Created on 2018年8月11日

@author: wangyonghui
'''
from poker.entity.events.tyevent import UserEvent


class TreasureChestEvent(UserEvent):
    '''
    分享获取奖励事件
    '''
    def __init__(self, gameId, userId, rewardType, rewards, **kwargs):
        super(TreasureChestEvent, self).__init__(userId, gameId)
        self.rewardType = rewardType
        self.rewards = rewards
        self.params = kwargs


def publishTreasureChestEvent(gameId, userId, rewardType, rewards, **kwargs):
    from dizhu.game import TGDizhu
    eventBus = TGDizhu.getEventBus()
    if eventBus:
        eventBus.publishEvent(TreasureChestEvent(gameId, userId, rewardType, rewards, **kwargs))
