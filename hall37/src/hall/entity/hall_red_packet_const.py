# -*- coding:utf-8 -*-
'''
Created on 2018年1月12日

@author: zhaojiangang
'''

RP_SOURCE_RP_RAIN = 'rp.rain'
RP_SOURCE_RP_TASK = 'rp.task'
RP_SOURCE_RP_INVITEE = 'rp.invitee'
RP_SOURCE_RP_BOMB = 'rp.bomb'
RP_SOURCE_RP_MAIN = 'rp.main'


RP_SOURCE_NAME_MAP = {
    RP_SOURCE_RP_RAIN:'天降红包',
    RP_SOURCE_RP_TASK:'新手任务',
    RP_SOURCE_RP_INVITEE:'好友返利',
    RP_SOURCE_RP_BOMB:'炸弹红包',
    RP_SOURCE_RP_MAIN:'开门红包'
}


RP_SOURCE_NAME_OTHER = '其它'


def getSourceName(source):
    return RP_SOURCE_NAME_MAP.get(source, RP_SOURCE_NAME_OTHER)


