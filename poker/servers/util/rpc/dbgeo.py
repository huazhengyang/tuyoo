# -*- coding: utf-8 -*-
import time
from poker.entity.dao import daobase
from poker.entity.dao.daoconst import GameGeoSchema
from poker.protocol.rpccore import markRpcCall

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setUserGeoOffline(userId, gameId):
    pass