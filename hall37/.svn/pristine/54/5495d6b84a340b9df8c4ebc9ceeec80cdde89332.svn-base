# -*- coding:utf-8 -*-
'''
Created on 2017年7月13日

@author: zhaojiangang
'''
from poker.protocol.rpccore import markRpcCall
import poker.util.timestamp as pktimestamp
from poker.util.keylock import KeyLock
import freetime.util.log as ftlog


_stockLock = KeyLock()

@markRpcCall(groupName='', lockName='', syncCall=1)
def getStock(exchangeId):
    '''
    @return: True/False, balance
    '''
    from hall.entity import hall_exmall
    with _stockLock.lock(exchangeId):
        timestamp = pktimestamp.getCurrentTimestamp()
        stockObj = hall_exmall.getStock(exchangeId, timestamp)
        return stockObj.stock


@markRpcCall(groupName='', lockName='', syncCall=1)
def lockStock(exchangeId, count):
    '''
    @return: True/False, balance, stockTimestamp
    '''
    from hall.entity import hall_exmall
    with _stockLock.lock(exchangeId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            count, balance = hall_exmall.lockStock(exchangeId, count, timestamp)
            return True, balance, timestamp
        except:
            ftlog.error('stock_remote.lockStock',
                        'exchangeId=', exchangeId,
                        'count=', count)
            return False, None, None
    

@markRpcCall(groupName='', lockName='', syncCall=1)
def backStock(exchangeId, count, stockTimestamp):
    '''
    '''
    from hall.entity import hall_exmall
    
    with _stockLock.lock(exchangeId):
        timestamp = pktimestamp.getCurrentTimestamp()
        hall_exmall.backStock(exchangeId, count, stockTimestamp, timestamp)

