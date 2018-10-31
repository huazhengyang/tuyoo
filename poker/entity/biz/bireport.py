# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import struct
import time
import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao.daoconst import CHIP_TYPE_ALL, CHIP_TYPE_ITEM
from poker.util import timestamp, strutil
from poker.entity.dao import bidata, sessiondata
from poker.entity.biz import integrate
from datetime import datetime
_BILOGER = None
_CHIP_RECORD_TYPE = 1
_GAME_RECORD_TYPE = 4
_BI_LOG_SEQ_NUM = 0
_BI_LOG_SEQ_DATE = datetime.now().strftime('%Y_%m_%d')

def _generateRecordId():
    """
    生成日志记录的唯一id
    """
    pass

def _getFBRecordField(field):
    """
    获取Filebeat日志记录字段值
    """
    pass

def _fbReport(logType, *argList):
    """
    Filebeat日志记录
    """
    pass

def _report(arglist, argdict, isHinfo=0):
    """
    本地日志记录
    """
    pass

def report(moduleName, *arglist, **argdict):
    pass

def _getCurrentDay():
    pass

def itemUpdate(gameId, userId, kindId, detalCount, finalCount, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0, *arglist, **argdict):
    """
    道具变化的标准本地日志文件汇报
    """
    pass

def tableStart(gameId, roomId, tableId, cardId, userIdList, *arglist, **argdict):
    """
    桌子游戏开始的标准本地日志文件汇报
    """
    pass

def tableWinLose(gameId, roomId, tableId, cardId, userIdList, *arglist, **argdict):
    """
    桌子游戏结束的标准本地日志文件汇报
    """
    pass

def tcpUserOnline(userCount, *arglist, **argdict):
    """
    用户TCP连接在线数量的标准本地日志文件汇报和REDIS实时数据汇报
    """
    pass

def getConnOnlineUserCount():
    """
    重BI数据库取得当前所有CONN进程的在线人数合计
    """
    pass

def roomUserOnline(gameId, roomId, userCount, playTableCount, observerCount, *arglist, **argdict):
    """
    房间内在线用户数量的标准本地日志文件汇报和REDIS实时数据汇报
    """
    pass

def getRoomOnLineUserCount(gameId, withShadowRoomInfo=0):
    """
    重BI数据库中取得当前的游戏的所有的在线人数信息
    return allcount, counts, details
    allcount int，游戏内所有房间的人数的总和
    counts 字典dict，key为大房间ID（bigRoomId)，value为该大房间内的人数总和
    details 字典dict，key为房间实例ID（roomId），value为该放假内的人数
    此数据由每个GR，GT进程每10秒钟向BI数据库进行汇报一次
    """
    pass

def getRoomOnLineUserCount2(gameId, withShadowRoomInfo=0):
    """
    重BI数据库中取得当前的游戏的所有的在线人数信息, 与getRoomOnLineUserCount功能一致，仅多出一个返回值ocount
    return allcount, counts, details, allobcount, obcounts, obdetails
    allobcount, obcounts, obdetails 观察者数量，需要table类实现observersNum属性
    """
    pass

def gcoin(coinKey, gameId, detalCount, *arglist, **argdict):
    """
    一类货币数量变化的标准本地日志文件汇报和REDIS实时数据汇报
    """
    pass

def creatGameData(gameId, userId, clientId, dataKeys, dataValues, *arglist, **argdict):
    """
    创建用户游戏数据的标准本地日志文件汇报
    """
    pass

def tableRoomFee(gameId, fees, *arglist, **argdict):
    """
    房间费用的标准本地日志文件汇报
    """
    pass

def userGameEnter(gameId, userId, clientId, *arglist, **argdict):
    """
    用户进入游戏的标准本地日志文件汇报
    """
    pass

def userGameLeave(gameId, userId, clientId, *arglist, **argdict):
    """
    用户离开游戏的标准本地日志文件汇报
    """
    pass

def userBindUser(gameId, userId, clientId, *arglist, **argdict):
    """
    用户进入大厅的标准本地日志文件汇报
    """
    pass

def tableEvent(gameId, roomId, tableId, event, *arglist, **argdict):
    """
    桌子事件的标准本地日志文件汇报
    """
    pass

def playerEvent(gameId, userId, roomId, tableId, event, *arglist, **argdict):
    """
    桌子玩家的标准本地日志文件汇报
    """
    pass

def matchStart(gameId, roomId, matchId, matchName, *arglist, **argdict):
    """
    比赛开始的标准本地日志文件汇报
    """
    pass

def matchFinish(gameId, roomId, matchId, matchName, *arglist, **argdict):
    """
    比赛结束大厅的标准本地日志文件汇报
    """
    pass

def matchStartTable(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchLockUser(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchStageStart(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchStageFinish(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchGroupStart(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchGroupFinish(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchUserGameOver(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchUserSignin(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchUserSignout(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchUserKickout(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchUserEnter(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def matchUserLeave(gameId, roomId, matchId, matchName, *arglist, **argdict):
    pass

def reportHttpBi1(user_id, log_type, struct_fmt, *struct_args):
    """
    发送BI消息到BI日志收集服务
    user_id 消息产生的用户ID, 必须是有效的正整数
    log_type 消息的基本大类型, 再poker/global.json中定义的bireportgroup的键值
    struct_fmt 消息的具体格式, struct的格式化格式
    struct_args 消息的参数, 即:struct.pack使用的参数
    注意: 本函数自动会在struct_fmt之前添加基本消息头"<I", 即: 使用little字节序, 添加当前的时间戳
    """
    pass

def reportHttpBi2(user_id, log_type, struct_fmt, *struct_args):
    """
    发送BI消息到BI日志收集服务
    user_id 消息产生的用户ID, 必须是有效的正整数
    log_type 消息的基本大类型, 再poker/global.json中定义的bireportgroup的键值
    struct_fmt 消息的具体格式, struct的格式化格式
    struct_args 消息的参数, 即:struct.pack使用的参数
    注意: 本函数自动会在struct_fmt之前添加基本消息头"<I", 即: 使用little字节序, 添加当前的时间戳
    """
    pass
reportHttpBi = reportHttpBi2

def reportBiChip(user_id, delta, trueDelta, final, eventId, clientId, gameId, appId, eventParam, chipType, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0, arglist=[], argdict={}, logtag='chip_update'):
    """
    用户货币变化的HTTP远程BI汇报
    """
    pass

def reportGameEvent(eventId, user_id, gameId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, finalTableChip=0, finalUserChip=0, arglist=[], argdict={}, logtag='game_event'):
    """
    游戏牌桌阶段事件的HTTP远程BI汇报
    """
    pass

def reportCardEvent(eventId, user_id, gameId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, finalTableChip=0, finalUserChip=0, arglist=[], argdict={}, logtag='card_event'):
    """
    游戏出牌事件的HTTP远程BI汇报
    """
    pass