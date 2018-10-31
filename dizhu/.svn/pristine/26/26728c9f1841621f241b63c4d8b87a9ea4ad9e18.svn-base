# -*- coding=utf-8
'''
Created on 2018年7月13日

@author: wangyonghui
'''
from hall.entity import hallitem
from hall.entity.hallconf import HALL_GAMEID
from poker.protocol.rpccore import markRpcCall
from poker.util import timestamp as pktimestamp


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def getUserAssetBalanceRpc(userId, itemId):
    ''' RPC 远程调用 '''
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    balance = userAssets.balance(HALL_GAMEID, itemId, pktimestamp.getCurrentTimestamp())
    return balance


def getUserAssetBalance(userId, itemId):
    ''' UT 进程直接调用 '''
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    balance = userAssets.balance(HALL_GAMEID, itemId, pktimestamp.getCurrentTimestamp())
    return balance
