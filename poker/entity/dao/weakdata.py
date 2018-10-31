# -*- coding: utf-8 -*-
"""
Created on 2013-3-18

@author: Administrator
"""
import calendar
from poker.servers.util.direct import dbuser
from poker.util import timestamp
from datetime import datetime
CYCLE_TYPE_DAY = 1
CYCLE_TYPE_WEEK = 2
CYCLE_TYPE_MONTH = 3
CYCLE_TYPE_MONTH_REMAIN_TIME = 4

def _getCycleInfo(cycleType):
    pass

def getWeakData(userId, gameId, cycleType, datakey):
    """
    取得一个用户的弱存储数据, 例如: 每日登陆的数据,凌晨过后即被清空重新建立
    cycleType 参考: CYCLE_TYPE_DAY, CYCLE_TYPE_WEEK, CYCLE_TYPE_MONTH
    返回必定是一个dict数据集合
    可参考day1st.py的使用方法
    """
    pass

def setWeakData(userId, gameId, cycleType, datakey, datas):
    """
    设置一个用户的弱存储数据, 例如: 每日登陆的数据,凌晨过后即被清空重新建立
    cycleType 参考: CYCLE_TYPE_DAY, CYCLE_TYPE_WEEK, CYCLE_TYPE_MONTH
    datas必须是一个dict数据集合
    可参考day1st.py的使用方法
    """
    pass