# -*- coding=utf-8
'''
Created on 2015年7月21日

@author: zhaojiangang
'''

from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from poker.entity.configure import configure as pkconfigure
from poker.entity.events.tyevent import EventUserLogin
from hall.entity.hallcoupon import CouponService

    
_inited = False
couponService = CouponService(DIZHU_GAMEID)

def _reloadConf():
    global couponService
    conf = pkconfigure.getGameJson(6, 'coupon', {})
    couponService.reloadConf(conf)

def _onConfChanged(event):
    global _inited
    ftlog.debug('dizhucoupon._onConfChanged')
    if _inited:
        _reloadConf()

def _initialize():
    ftlog.debug('dizhucoupon initialize begin')
    from dizhu.game import TGDizhu
    global _inited
    global flipCard
    if not _inited:
        _inited = True
        TGDizhu.getEventBus().subscribe(EventUserLogin, couponService.onUserLogin)
        _reloadConf()
    ftlog.debug('dizhucoupon initialize end')
    

