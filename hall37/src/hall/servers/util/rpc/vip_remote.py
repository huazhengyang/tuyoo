# -*- coding=utf-8
'''
Created on 2015年8月11日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallvip
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.vip_handler import VipHelper
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addVipExp(gameId, userId, addExp):
    ftlog.info('RemoteVipTestRpc.addVipExp gameId=', gameId,
               'userId=', userId,
               'addExp=', addExp)
    hallvip.userVipSystem.addUserVipExp(HALL_GAMEID, userId, addExp, 'TEST_ADJUST', 0)
    userVip, vipGiftStates = hallvip.userVipSystem.getUserVipGiftStates(HALL_GAMEID, userId)
    return VipHelper.makeVipInfoResponse(HALL_GAMEID, userVip, vipGiftStates)._ht

