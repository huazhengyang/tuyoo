# -*- coding=utf-8
import json
import random
import datetime
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack

from hall.entity.hallconf import HALL_GAMEID, getNewCheckinTCConf
from hall.entity import hallitem, datachangenotify, hallvip
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
from hall.entity.localservice.localServiceConfig import _DEBUG, CLIENT_VER

import poker.util.timestamp as pktimestamp
from poker.entity.dao import userdata, gamedata, userchip
from poker.entity.dao.userchip import ChipNotEnoughOpMode
from poker.entity.configure import configure, pokerconf
from poker.protocol import router
from poker.util import strutil




def deductionVipComplement(event):
    userId = event.userId

    ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|enter", userId, event.rmbs)

    if event.rmbs and event.rmbs > 0:
        chargeDate = datetime.datetime.now().strftime('%Y-%m-%d')
        gamedata.setGameAttr(userId, HALL_GAMEID, 'chargeDate', chargeDate)
        vipcominfo = gamedata.getGameAttr(userId, HALL_GAMEID, 'vip_complement')
        ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|vipcominfo", userId, event.rmbs, vipcominfo)
        if vipcominfo:
            vipcominfo = json.loads(vipcominfo)
            vipcom = vipcominfo['vipcom']
            if vipcom == 0:
                ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|vipcom|zero", userId, event.rmbs, vipcominfo)
                return

            vip_complement_deduction = configure.getGameJson(HALL_GAMEID, "misc").get("vip_complement_deduction", 10000)
            deduction = int(event.rmbs) * vip_complement_deduction
            delta = vipcom - deduction

            ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|vip_complement_deduction", userId, event.rmbs, vipcominfo, vip_complement_deduction, deduction, vipcom, delta)
            if delta < 0:
                delta = 0

            gamedata.setGameAttr(userId, HALL_GAMEID, 'vip_complement',
                                 json.dumps({'vipLevel': vipcominfo['vipLevel'], 'vipcom': int(delta)}))

            ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement", userId, event.rmbs, vipcominfo['vipLevel'], vipcom, delta)


from hall.entity import newcheckin
newcheckin.deductionVipComplement = deductionVipComplement

def onVipChargeNotifyEvent(event):
    from hall.entity import newcheckin
    newcheckin.deductionVipComplement(event)
    ftlog.info("onVipChargeNotifyEvent|2", event.userId, event.rmbs if event.rmbs else 1)


from hall.game import TGHall
from poker.entity.events.tyevent import ChargeNotifyEvent

TGHall.getEventBus().subscribe(ChargeNotifyEvent, onVipChargeNotifyEvent)