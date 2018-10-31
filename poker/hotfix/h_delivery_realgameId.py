# -*- coding: utf-8 -*-
"""
Created on 2017年7月3日

@author: zhaojiangang
"""
import freetime.util.log as ftlog
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.store.store import TYOrderDeliveryResult, TYStoreSystemImpl
from poker.entity.configure import pokerconf
from poker.util import strutil
import poker.util.timestamp as pktimestamp

def _deliveryOrder(self, order):
    pass
TYStoreSystemImpl._deliveryOrder = _deliveryOrder