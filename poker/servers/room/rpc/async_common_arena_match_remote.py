# -*- coding: utf-8 -*-
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata

@markRpcCall(groupName='ctrlRoomId', lockName='', syncCall=1)
def matchSave(userId, gameId, ctrlRoomId):
    """
    RPC调用，保存比赛进度，清楚比赛LOC，用户可以去玩儿别的玩法或者比赛
    """
    pass

def _matchSave(userId, gameId, ctrlRoomId):
    pass