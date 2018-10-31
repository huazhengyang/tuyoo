# -*- coding:utf-8 -*-
'''
Created on 2017年2月8日

@author: zhaojiangang
'''
from dizhucomm import playmodes
from dizhucomm.core.playmode import PlayMode
from dizhucomm.playmodes import cardcenter


class PlayModeNormalHappy(PlayMode):
    def __init__(self, name=playmodes.PLAYMODE_HAPPY, cardRule=cardcenter.cardRuleNormal, seatCount=3):
        super(PlayModeNormalHappy, self).__init__(name, cardRule, seatCount)


class PlayModeNormalClassic(PlayMode):
    def __init__(self, name=playmodes.PLAYMODE_123, cardRule=cardcenter.cardRuleNormal, seatCount=3):
        super(PlayModeNormalClassic, self).__init__(name, cardRule, seatCount)


PLAY_MODE_NORMAL_HAPPY = PlayModeNormalHappy()
PLAY_MODE_NORMAL_CLASSIC = PlayModeNormalClassic()