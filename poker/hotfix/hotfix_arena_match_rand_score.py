# -*- coding: utf-8 -*-
"""
Created on 2017年10月30日

@author: wangyonghui
"""
import random

def randomRobotData(self, users):
    """
    随机机器人的轮次和积分
    积分在真人积分的最小值和最大值之间随机。
    
    如果积分等于第一阶段的初始积分，则轮次为第一赛段的轮次
    其他时候随机一个轮次
    """
    pass
from poker.entity.game.rooms.common_arena_match_ctrl.ca_match import CommonArenaMatch
CommonArenaMatch.randomRobotData = randomRobotData