# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛报名费s
报名时，任选一个即可

@author: zhaol

"""
from poker.entity.game.rooms.common_arena_match_ctrl.ca_match_fee import CommonArenaFee

class CommonArenaFees(object, ):

    def __init__(self):
        pass

    @property
    def fees(self):
        """
        报名费集合
        """
        pass

    def setFees(self, fees):
        pass

    def needFee(self):
        pass

    def getFeeByIndex(self, feeIndex):
        pass

    def initConfig(self, config):
        pass

    def getDesc(self):
        """
        获取报名费描述
        """
        pass
if (__name__ == '__main__'):
    pass