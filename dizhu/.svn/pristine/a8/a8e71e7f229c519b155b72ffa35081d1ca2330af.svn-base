# -*- coding=utf-8
'''
Created on 2015年7月21日

@author: zhaojiangang
'''
from poker.protocol.decorator import markCmdActionHandler
from hall.servers.util.exchange_handler import HallExchangeHandler
from dizhu.entity import dizhucoupon

@markCmdActionHandler
class DizhuExchangeHandler(HallExchangeHandler):
    def __init__(self):
        super(DizhuExchangeHandler, self).__init__()
        
    def _getCouponService(self):
        return dizhucoupon.couponService
