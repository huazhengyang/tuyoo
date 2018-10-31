# -*- coding:utf-8 -*-
"""
Created on 2016年7月4日

@author: zhaojiangang
"""

from dizhu.activitynew.activity import ActivityNewRegister
from dizhu.activitynew.activity_score_ranking import ActivityScoreRanking
from dizhu.activitynew.buy_send_prize import BuySendPrize
from dizhu.activitynew.charge_send_present_num import ChargeSendPresentNum
from dizhu.activitynew.christmas import ActivityChristmas
from dizhu.activitynew.match_promotion_list import MatchPromotionList
from dizhu.activitynew.max_charge_recorder import MaxChargeRecorder
from dizhu.activitynew.play_game_todotask import PlayGameTodotask
from dizhu.activitynew.table_share_recorder import TableShareRecorder
from dizhu.activitynew.tehui_giftbox_new import TeHuiGiftboxNew
from dizhu.activitynew.vip_giftbox import VipGiftbox
import freetime.util.log as ftlog
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import configure as pkconfigure
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from dizhu.activitynew.fttable_finish_recorder import FTTableFinishRecorder
from dizhu.activitynew.quweitask import QuweiTaskActivity
from dizhu.activitynew.sky_egg import SkyEggActivity


_inited = False
# key=actId, value=ActivityNew
_activities = {}

def _initActivities(activities):
    try:
        for act in activities.values():
            act.init()
    except Exception, e:
        ftlog.error('activitysystemnew._initActivities')
        _cleanupActivities(activities)
        raise e

def _cleanupActivities(activities):
    for act in activities.values():
        try:
            act.cleanup()
        except:
            ftlog.error('activitysystemnew._initActivities actId=', act.actId)

def _reloadConf():
    global _activities
    activities = {}
    conf = pkconfigure.getGameJson(6, 'activity.new', {})
    for actConf in conf.get('activities', []):
        act = ActivityNewRegister.decodeFromDict(actConf)
        if act.actId in activities:
            raise TYBizConfException(actConf, 'duplicate actId: %s' % act.actId)
        activities[act.actId] = act

    try:
        _initActivities(activities)
        _cleanupActivities(_activities)
        _activities = activities
        ftlog.debug('activitysystemnew._reloadConf actIds=', _activities.keys())
    except:
        ftlog.error('activitysystemnew._reloadConf')
        
def _onConfChanged(event):
    if _inited and event.isChanged(['game:6:activity.new:0']):
        ftlog.debug('activitysystemnew._onConfChanged')
        _reloadConf()

def _registerClass():
    ActivityNewRegister.registerClass(BuySendPrize.TYPE_ID, BuySendPrize)
    ActivityNewRegister.registerClass(TeHuiGiftboxNew.TYPE_ID, TeHuiGiftboxNew)
    ActivityNewRegister.registerClass(VipGiftbox.TYPE_ID, VipGiftbox)
    ActivityNewRegister.registerClass(MaxChargeRecorder.TYPE_ID, MaxChargeRecorder)
    ActivityNewRegister.registerClass(ChargeSendPresentNum.TYPE_ID, ChargeSendPresentNum)
    ActivityNewRegister.registerClass(PlayGameTodotask.TYPE_ID, PlayGameTodotask)
    ActivityNewRegister.registerClass(TableShareRecorder.TYPE_ID, TableShareRecorder)
    ActivityNewRegister.registerClass(FTTableFinishRecorder.TYPE_ID, FTTableFinishRecorder)
    ActivityNewRegister.registerClass(QuweiTaskActivity.TYPE_ID, QuweiTaskActivity)
    ActivityNewRegister.registerClass(SkyEggActivity.TYPE_ID, SkyEggActivity)
    ActivityNewRegister.registerClass(ActivityScoreRanking.TYPE_ID, ActivityScoreRanking)
    ActivityNewRegister.registerClass(MatchPromotionList.TYPE_ID, MatchPromotionList)
    ActivityNewRegister.registerClass(ActivityChristmas.TYPE_ID, ActivityChristmas)

def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _registerClass()
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)

def findActivity(actId):
    return _activities.get(actId)

