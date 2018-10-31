# -*- coding: utf-8 -*-
"""
    一个计划任务必须配置两个参数:
        times_in_day表示一天之内的触发时间点,
        days表示计划任务在哪一天触发；
   
    times_in_day有两种配置方式：
        一种是硬配list，把所有时间点列出:
        "times_in_day":
        {
            "list":["10:00", "11:20", "11:30", "22:30"] 
        }
        还有一种按周期配置：
        "times_in_day":
        {
            "first":"10:00",      #开始时间点
            "interval":5,         #按分钟的周期
            "count":200           #重复次数
        }

   
    days也有类似的两种配置方式:
        硬配list:
        "days":
        {
            "list":["20130101", "20130201", "20130301"] 
        }
        还有一种按周期配置，周期支持d（天）w（周）m（月）y（年）
        "days":
        {
            "first":"20130107",
            "interval":"1d",
            "count":2000         #重复次数最多配置MAX_DAY_COUNT
        }

    按照上述配置初始化后，将会得到时间和日期两个列表

    注意：需要安装第三方模块dateutil.relativedelta:
          http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz
"""
import datetime
import json
from dateutil.relativedelta import relativedelta
import freetime.util.log as ftlog

class FTCron:
    MAX_DAY_COUNT = 1000

    def __init__(self, config_json):
        pass

    def getTimeList(self):
        pass

    def getDaysList(self):
        pass

    def getTodayNextLater(self):
        """
        如果今天有match的时间点，返回最近一个点还要等多少秒
        """
        pass

    def getNextTime(self, ntime=None):
        pass