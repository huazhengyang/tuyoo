# -*- coding=utf-8 -*-
"""
@file  : hallalarm
@date  : 2017-04-10
@author: GongXiaobo
"""
from freetime.entity.msg import MsgPack
from poker.entity.dao import daobase
from poker.protocol import router
from poker.util import timestamp, strutil


class AlarmDao:
    MAINKEY = 'alarm:9999:{}'

    def __init__(self):
        pass

    @classmethod
    def save(cls, userId, pluginId, deadline, notice, extparam):
        mainkey = cls.MAINKEY.format(userId)
        subvalue = {
            'pluginId': pluginId,
            'deadline': deadline,
            'notice': notice
        }
        if extparam:
            subvalue['extparam'] = extparam
        subkey = daobase.executeUserCmd(userId, 'HINCRBY', mainkey, 'maxid', 1)
        daobase.sendUserCmd(userId, 'HSET', mainkey, subkey, strutil.dumps(subvalue))
        return subkey

    @classmethod
    def load(cls, userId):
        mainkey = cls.MAINKEY.format(userId)
        kvlist = daobase.executeUserCmd(userId, 'HGETALL', mainkey)
        ret = {}
        dels = []
        curtime = timestamp.getCurrentTimestamp()
        for idx in xrange(1, len(kvlist), 2):
            k = kvlist[idx - 1]
            if k == 'maxid':
                continue
            v = kvlist[idx]
            v = strutil.loads(v)
            if v['deadline'] <= curtime:
                dels.append(k)
            else:
                ret[k] = v
        if dels:
            daobase.sendUserCmd(userId, 'HDEL', mainkey, *dels)
        return ret


def registerAlarm(userId, pluginId, deadline, notice, extparam=None):
    """
    :param userId: 玩家id
    :param pluginId: 插件id
    :param deadline: 到期时间,距1970.1.1零点的秒数
    :param notice: 通知文本
    :param extparam: 可json化的字典,传入自定义参数,诸如roomId
    :return: 闹钟id，0为异常
    """
    if deadline <= timestamp.getCurrentTimestamp():
        return 0
    aid = AlarmDao.save(userId, pluginId, deadline, notice, extparam)
    queryAlarm(userId)
    return aid


def queryAlarm(userId):
    alarms = AlarmDao.load(userId)
    if not alarms:
        return
    mo = MsgPack()
    mo.setCmd('game')
    mo.setAction('alarmList')
    mo.setResult('gameId', 9999)
    mo.setResult('userId', userId)
    mo.setResult('curtime', timestamp.getCurrentTimestamp())
    mo.setResult('alarms', alarms)
    router.sendToUser(mo, userId)
    return mo


def initialize():
    from poker.entity.events.tyevent import EventUserLogin
    from hall.game import TGHall
    TGHall.getEventBus().subscribe(EventUserLogin, _onUserLogin)


def _onUserLogin(event):
    queryAlarm(event.userId)


if __name__ == '__main__':
    pass
