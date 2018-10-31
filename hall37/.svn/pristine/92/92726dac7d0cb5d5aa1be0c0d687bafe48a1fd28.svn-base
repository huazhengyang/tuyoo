# -*- coding: utf-8 -*-
'''
Created on 2017年8月22日
@author: ljh
'''
from poker.protocol.rpccore import markRpcCall
from hall.entity import hallnewnotify
from hall.entity import hall_sport_manual_end
import freetime.util.log as ftlog


@markRpcCall(groupName='', lockName='', syncCall=1)
def addHallNotifyInfo(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType, hall, gameId,
                      package, userId, timelimit):
    '''
    typeId 发送类型 1公告通知 2消息通知 3系统推送 必须选一个,没有默认
    ntimeId 发送时间 -2立即、-1定时、0每天、1周一、2周二、3周三、4周四、5周五、6周六、7周日 必须选一个,没有默认
    ntime 时间12:35 如果是ntimeId-2立即 可以不填 ,ntimeId-1定时 20170822|12:35,其他的 ntimeId,必须填一个时间,没有默认
    iconAddr 路径 必须填,没有默认
    context 文本内容 存文本 不超过50字 必须填,没有默认
    passthrough 透传消息,json{todotask} 可以不填,默认为空字符串
    platform 1 ios、2 android 必须选一个,没有默认
    buttonType 按钮类型 1确定 2忽略+前往  不选 默认确定
    hall 不需要手动填写的,根据用户权限给分配, 例如:'hall6', 'hall30'
    gameId 插件gameId  比如斗地主大厅的'30'插件,  不选发送所有插件,不填就是空字符串
    package 多个clientId,以 | 分割 'clientId1|clientId2|' 例如'Android_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu|
    Ios_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu' 不填就是空字符串
    userId 不填发送给所有的用户 'userId1|userId2|' 例如 '123456|78923' 不填就是空字符串
    '''

    return hallnewnotify.addNotifyInfo(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType,
                                       hall, gameId, package, userId, timelimit)

@markRpcCall(groupName='', lockName='', syncCall=0)
def addHallNotifyInfo_asyn(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType, hall, gameId,
                      package, userId, timelimit):
    '''
    typeId 发送类型 1公告通知 2消息通知 3系统推送 必须选一个,没有默认
    ntimeId 发送时间 -2立即、-1定时、0每天、1周一、2周二、3周三、4周四、5周五、6周六、7周日 必须选一个,没有默认
    ntime 时间12:35 如果是ntimeId-2立即 可以不填 ,ntimeId-1定时 20170822|12:35,其他的 ntimeId,必须填一个时间,没有默认
    iconAddr 路径 必须填,没有默认
    context 文本内容 存文本 不超过50字 必须填,没有默认
    passthrough 透传消息,json{todotask} 可以不填,默认为空字符串
    platform 1 ios、2 android 必须选一个,没有默认
    buttonType 按钮类型 1确定 2忽略+前往  不选 默认确定
    hall 不需要手动填写的,根据用户权限给分配, 例如:'hall6', 'hall30'
    gameId 插件gameId  比如斗地主大厅的'30'插件,  不选发送所有插件,不填就是空字符串
    package 多个clientId,以 | 分割 'clientId1|clientId2|' 例如'Android_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu|
    Ios_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu' 不填就是空字符串
    userId 不填发送给所有的用户 'userId1|userId2|' 例如 '123456|78923' 不填就是空字符串
    '''
    ftlog.hinfo("addHallNotifyInfo_asyn",typeId, ntimeId, ntime, len(userId), hall, gameId)
    hallnewnotify.addNotifyInfo(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType,
                                       hall, gameId, package, userId, timelimit)

@markRpcCall(groupName='', lockName='', syncCall=1)
def getHallNotifyInfo(hall):
    ftlog.debug("getHallNotifyInfo|", hall)
    return hallnewnotify.getHallNotifyInfo(hall)


@markRpcCall(groupName='', lockName='', syncCall=1)
def delHallNotifyInfo(ntimeId, uuid, hall, ntime):
    ftlog.debug("delHallNotifyInfo|", ntimeId, uuid, hall, ntime)
    return hallnewnotify.delHallNotifyInfo(ntimeId, uuid, hall, ntime)

@markRpcCall(groupName='', lockName='', syncCall=1)
def doSportEnd(matchId, leagueId, homeTeamId, awayTeamId, timestamp, score, odds, status):
    ftlog.debug("do_sport_end|", matchId, leagueId, homeTeamId, awayTeamId, timestamp, score, odds, status)
    return hall_sport_manual_end.doResultOne(matchId, leagueId, homeTeamId, awayTeamId, timestamp, score, odds, status)

