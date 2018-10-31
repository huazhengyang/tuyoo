# -*- coding: utf-8 -*-
"""
Created on 2015年6月3日

@author: zhaoqh
"""
import re
from poker.entity.configure import gdata
from poker.entity.dao import daobase
from poker.util import webpage
import freetime.util.log as ftlog
from datetime import datetime
orderIdVer1 = 'a'
consumeOrderIdVer1 = 'b'
orderIdVer3 = 'c'
consumeOrderIdVer3 = 'd'
danjiOrderIdVer3 = 'f'
smsBindOrderIdVer3 = 's'
changTianYouOrderIdVer3 = 'y'

def is_valid_orderid_str(orderid):
    pass

def get_appid_frm_order_id(orderId):
    pass

def get_order_id_info(orderId):
    pass

def makeConsumeOrderIdV3(userId, appId, clientId):
    pass

def makeChargeOrderIdV3(userId, appId, clientId):
    pass

def makeSmsBindOrderIdV3(userId, appId, clientId):
    pass

def makeChangTianYouOrderIdV3(userId, appId, clientId):
    pass

def makePlatformOrderIdV1(userId, params):
    pass

def makeGameOrderIdV1(userId, params):
    pass

def make_order_id(appId, orderIdVer62, httpcallback=None, isRemote=False):
    pass

def getOrderIdHttpCallBack(orderId):
    pass

def is_short_order_id_format(shortOrderId):
    pass

def get_short_order_id(orderPlatformId):
    pass

def get_long_order_id(shortOrderId):
    pass