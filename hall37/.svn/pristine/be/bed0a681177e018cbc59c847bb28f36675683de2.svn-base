# -*- coding:utf-8 -*-
'''
Created on 2017年11月27日

@author: zhaojiangang
'''
from poker.entity.biz.exceptions import TYBizException
from poker.protocol.rpccore import markRpcCall
from hall.entity import hall_yyb_gifts


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def gainYYBGift(userId, giftKindId, timestamp):
    try:
        state, _ = hall_yyb_gifts.gainUserGift(userId, giftKindId, timestamp)
        return 0, state
    except TYBizException, e:
        return e.errorCode, e.message