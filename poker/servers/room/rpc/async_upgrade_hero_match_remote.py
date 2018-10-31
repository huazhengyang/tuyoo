# -*- coding: utf-8 -*-
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata

@markRpcCall(groupName='ctrlRoomId', lockName='', syncCall=1)
def matchSave(userId, gameId, ctrlRoomId):
    """
    RPC调用，保存比赛进度，清楚比赛LOC，用户可以去玩儿别的玩法或者比赛
    前置条件：
    当有比赛loc的时候调用
    
    返回值
    True : 保存成功/比赛loc清理成功
    False : 保存比赛失败
    """
    pass

def _matchSave(userId, gameId, ctrlRoomId):
    pass