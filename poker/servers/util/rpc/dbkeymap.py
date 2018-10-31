# -*- coding: utf-8 -*-
from poker.entity.dao import daobase
from poker.protocol.rpccore import markRpcCall

@markRpcCall(groupName='', lockName='', syncCall=1)
def _setKeyValue(key, val):
    pass

@markRpcCall(groupName='', lockName='', syncCall=1)
def _getKeyValue(key):
    pass