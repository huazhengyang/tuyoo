# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from freetime.util import log as ftlog
from poker.entity.dao import daobase

def openLottery(self):
    """
    开奖
    """
    pass
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_lottery_rewards import MillionLotteryRewardOpenModule
MillionLotteryRewardOpenModule.openLottery = openLottery