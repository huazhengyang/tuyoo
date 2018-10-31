# -*- coding=utf-8 -*-
"""
@file  : activity_share_click
@date  : 2016-09-07
@author: GongXiaobo
"""
import copy

from hall.entity import hallshare
from hall.entity.hallactivity.activity_type import TYActivityType
from poker.entity.biz import bireport
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.message import message
from poker.entity.dao import daobase
from poker.entity.dao import gamedata
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from poker.entity.dao import sessiondata
from poker.util import strutil
from hall.entity.hallactivity.activity import ACTIVITY_KEY


class TYActShareClick(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_SHARE_CLICK
    FIELD_TOTAL_CNT = 'share_click_total_cnt'
    FIELD_WEEK_CNT = 'share_click_week_cnt'
    FIELD_DAY_CNT = 'share_click_day_cnt'
    FIELD_TIME = 'share_click_time'

    def getConfigForClient(self, gameId, userId, clientId):
        client = copy.deepcopy(self._clientConf)
        shareid = self._serverConf['share']
        share = hallshare.findShare(shareid)
        if share:
            winrate = gamedata.getGameAttr(userId, 6, 'winrate')
            winrate = strutil.loads(winrate, ignoreException=True, execptionValue={})
            todotask = share.buildTodotask(HALL_GAMEID, userId, 'share_click',
                                           {'userId': userId, 'actName': client['id'],
                                            'dizhuPlayNum': winrate.get('pt', 0)})
            client['config']["share"] = todotask.toDict()

        actkey = ACTIVITY_KEY.format(HALL_GAMEID, userId, client['id'])
        total = daobase.executeUserCmd(userId, 'HGET', actkey, self.FIELD_TOTAL_CNT)
        client['config']['total'] = total if total else 0
        client['config']['today'] = self._get_click_cnt(userId, actkey)[1]
        return client

    def _get_click_cnt(self, userid, actkey, curtime=None):
        if not curtime:
            curtime = pktimestamp.getCurrentTimestamp()
        oldtime = daobase.executeUserCmd(userid, 'HGET', actkey, self.FIELD_TIME)
        if oldtime:
            if pktimestamp.is_same_day(oldtime, curtime):
                return daobase.executeUserCmd(userid, 'HGET', actkey, self.FIELD_WEEK_CNT), \
                       daobase.executeUserCmd(userid, 'HGET', actkey, self.FIELD_DAY_CNT)

            daobase.executeUserCmd(userid, 'HMSET', actkey, self.FIELD_TIME, curtime, self.FIELD_DAY_CNT, 0)
            if pktimestamp.is_same_week(oldtime, curtime):
                return daobase.executeUserCmd(userid, 'HGET', actkey, self.FIELD_WEEK_CNT), 0

            daobase.executeUserCmd(userid, 'HSET', actkey, self.FIELD_WEEK_CNT, 0)
            return 0, 0

        daobase.executeUserCmd(userid, 'HMSET', actkey, self.FIELD_TIME, curtime, self.FIELD_DAY_CNT, 0, self.FIELD_WEEK_CNT, 0)
        return 0, 0

    def get_award(self, uid):
        if not self.checkOperative():
            return 'acitivity expired!'

        actkey = ACTIVITY_KEY.format(HALL_GAMEID, uid, self.getid())
        weekcnt, daycnt = self._get_click_cnt(uid, actkey)
        if weekcnt >= self._clientConf['config']['weeklimit'] or daycnt >= self._clientConf['config']['daylimit']:
            return 'awardcnt:({},{}) expand limitcnt!'.format(weekcnt, daycnt)

        shareid = self._serverConf["share"]
        share = hallshare.findShare(shareid)
        if not share:
            return 'share:{} not exist!'.format(shareid)

        daobase.executeUserCmd(uid, 'HINCRBY', actkey, self.FIELD_DAY_CNT, 1)
        daobase.executeUserCmd(uid, 'HINCRBY', actkey, self.FIELD_WEEK_CNT, 1)
        daobase.executeUserCmd(uid, 'HINCRBY', actkey, self.FIELD_TOTAL_CNT, 1)
        hallshare.sendReward(HALL_GAMEID, uid, share, 'share_click')
        # 分享BI日志汇报
        clientid = sessiondata.getClientId(uid)
        bireport.reportGameEvent('SHARE_CALLBACK', uid, HALL_GAMEID, shareid, 0, 0, 0, 0, 0, [], clientid)
        if share.mail:
            message.send(HALL_GAMEID, message.MESSAGE_TYPE_SYSTEM, uid, share.mail)
        return 'ok'


if __name__ == '__main__':
    pass
