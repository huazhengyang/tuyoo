import functools
import json

import datetime

import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
from dizhu.entity.official_counts import wx_official
from poker.entity.configure import configure
from dizhu.entity.official_counts.dao import official_dao
from dizhu.entity.dizhuconf import DIZHU_GAMEID, PROMOTE, WITHDRAW, RED_ENVELOPE


def _checkSendCondition(userId, gameId, eventId, timeStamp):
    startTime = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('startTime')
    stopTime = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('stopTime')
    start = datetime.datetime.strptime(startTime, "%H:%M").time()
    stop = datetime.datetime.strptime(stopTime, "%H:%M").time()
    now = datetime.datetime.now().time()
    if start >= stop or now < start or now > stop:
        if ftlog.is_debug():
            ftlog.debug('wx_official._checkSendCondition',
                        'userId=', userId,
                        'gameId=', gameId,
                        'start=', start,
                        'stop=', stop,
                        'now=', now,
                        'eventId=', eventId)
        return None, None
    hasSend = official_dao.getOfficialPushRecord(userId, gameId)
    if not hasSend:
        return 1, 'ok'
    hasSendAttrNames = [json.loads(i).keys()[0] for i in hasSend]
    hasSendTimes = [json.loads(i).values()[0] for i in hasSend]
    if not pktimestamp.is_same_day(timeStamp, hasSendTimes[-1]):
        return 1, None
    if timeStamp - hasSendTimes[-1] < 5 * 60:
        return None, 'ok'
    if len(hasSend) < 5:
        if eventId not in hasSendAttrNames:
            return 1, 'ok'
        if eventId in [PROMOTE, WITHDRAW, RED_ENVELOPE] and hasSendAttrNames.count(eventId) == 1:
            return 1, 'ok'
    return None, None


wx_official._checkSendCondition = _checkSendCondition