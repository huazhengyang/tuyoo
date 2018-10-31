# -*- coding: utf-8 -*-
"""
Created on 2017年09月18日

@author: zqh
请不要删除或随意修改此文件，此py文件作为停服前的关闭房间、检测功能而使用
"""
from freetime.core.timer import FTTimer
from poker.entity.dao import daobase

def addWinners():
    pass
FTTimer(1, addWinners)