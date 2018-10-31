# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from poker.protocol import router

def matchSignInFail(self, userId, code, info, loc=None):
    """
    比赛报名成功
    """
    pass
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_message import AsyncUpgradeHeroMatchMessage
AsyncUpgradeHeroMatchMessage.matchSignInFail = matchSignInFail