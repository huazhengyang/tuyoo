# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from datetime import datetime, timedelta
import time
from dateutil import relativedelta

def timeStampToStr(ts, formatTime='%Y-%m-%d %H:%M:%S'):
    pass

def getDaysList(tstp, count, formatTime='%Y-%m-%d'):
    pass

def getTimeStampFromStr(strTime, formatTime='%Y-%m-%d %H:%M:%S'):
    pass

def getDeltaMonthStartTimestamp(timestamp=None, deltamonth=0):
    """
    获取timestamp所在时间nmonth前后个月的开始时间，nmonth=0表示当前月, -1表示前一个月, 1表示下一个月
    """
    pass

def getMonthStartTimestamp(timestamp=None):
    """
    获取timestamp所在时间当前月的开始时间
    """
    pass

def getWeekStartTimestamp(timestamp=None):
    """
    获取timestamp这个时间所在周的开始时间
    """
    pass

def getDayLeftSeconds(timestamp=None):
    """
    获取timestamp这个时间到timestamp所在的天结束时的秒数
    """
    pass

def getDayPastSeconds(timestamp=None):
    """
    今日零点到现在过去的秒数
    """
    pass

def getDayStartTimestamp(timestamp=None):
    """
    获取timestamp这个时间戳
    """
    pass

def getHourStartTimestamp(timestamp=None):
    """
    获取timestamp这个时间戳
    """
    pass

def getCurrentWeekStartTimestamp(timestamp=None):
    """
    获取本周开始的时间戳，本周开始的时间点，到当前时间的秒数
    """
    pass

def getCurrentDayLeftSeconds():
    """
    获取当前时间开始，到本天结束时的秒数
    """
    pass

def getCurrentTimestamp():
    """
    获取当前时间戳 int (unit: second)
    """
    pass

def getCurrentTimestampFloat():
    """
    获取当前时间戳 float (unit: second)
    """
    pass

def getCurrentDayStartTimestamp():
    """
    获取今天开始的时间戳
    """
    pass

def getCurrentDayStartTimestampByTimeZone():
    """
    获取服务器当前时区今天开始的时间戳
    """
    pass

def getTimeStrDiff(start, end):
    """
    获取两个时间字符串的时间差，end-start，单位为秒
    时间字符串格式:%Y-%m-%d %H:%M:%S.%f
    """
    pass

def formatTimeMs(ct=None):
    """
    获取当前时间字符串:%Y-%m-%d %H:%M:%S.%f
    """
    pass

def parseTimeMs(timestr):
    """
    解析当前时间字符串:%Y-%m-%d %H:%M:%S.%f
    """
    pass

def formatTimeSecond(ct=None):
    """
    获取当前时间字符串:%Y-%m-%d %H:%M:%S
    """
    pass

def parseTimeSecond(timestr):
    """
    解析当前时间字符串:%Y-%m-%d %H:%M:%S
    """
    pass

def formatTimeMinute(ct=None):
    """
    获取当前时间字符串:%Y-%m-%d %H:%M
    """
    pass

def formatTimeMinuteSort(ct=None):
    """
    获取当前时间字符串:%Y-%m-%d %H:%M
    """
    pass

def parseTimeMinute(timestr):
    """
    解析当前时间字符串:%Y-%m-%d %H:%M
    """
    pass

def formatTimeHour(ct=None):
    """
    获取当前时间字符串:%Y-%m-%d %H
    """
    pass

def parseTimeHour(timestr):
    """
    解析当前时间字符串:%Y-%m-%d %H
    """
    pass

def formatTimeDay(ct=None):
    """
    获取当前时间字符串:%Y-%m-%d
    """
    pass

def parseTimeDay(timestr):
    """
    解析当前时间字符串:%Y-%m-%d
    """
    pass

def formatTimeDayShort(ct=None):
    """
    获取当前时间字符串:%Y%m%d
    """
    pass

def parseTimeDayShort(timestr):
    """
    解析当前时间字符串:%Y%m%d
    """
    pass

def formatTimeMonthShort(ct=None):
    """
    获取当前时间字符串:%Y%m
    """
    pass

def parseTimeMonthShort(timestr):
    """
    解析当前时间字符串:%Y%m
    """
    pass

def formatTimeWeekInt(ct=None):
    """
    取得当前的星期的数值, 例如2015年第二个星期, 返回 int(1502)
    """
    pass

def formatTimeMonthInt(ct=None):
    """
    取得当前的YYMM的int值, int(1507)
    """
    pass

def formatTimeDayInt(ct=None):
    """
    取得当前的YYYYMMDD的int值, int(150721)
    """
    pass

def formatTimeYesterDayInt(ct=None):
    """
    取得当前日期的昨天的的YYMMDD的int值, int(150721)
    """
    pass

def isSameMonth(d1, d2):
    pass

def is_same_week(timestamp1, timestamp2):
    pass

def is_same_day(timestamp1, timestamp2):
    pass

def datetime2Timestamp(dt):
    pass

def datetime2TimestampFloat(dt):
    pass

def timestrToTimestamp(timestr, fmt):
    pass

def timestrToTimestampFloat(timestr, fmt):
    pass

def timestamp2timeStr(value, pattern='%Y-%m-%d %H:%M:%S'):
    """
    把时间戳变成datetime
    """
    pass