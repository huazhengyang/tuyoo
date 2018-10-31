# -*- coding=utf-8
'''
Created on 2015年7月3日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from hall.entity import hallitem, hallvip
from hall.entity.hallitem import TYDecroationItem, TYDecroationItemKind
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
import poker.util.timestamp as pktimestamp
from hall.servers.util.rpc import user_remote
from hall.servers.util.decroation_handler import DecroationHelper


@classmethod
def makeDecroationQueryResponse(cls, gameId, userIds):
    mo = MsgPack()
    mo.setCmd('decoration')
    mo.setResult('action', 'query')
    users = []
    for userId in userIds:
        if userId :
            itemIds = user_remote.queryUserWeardItemKindIds(gameId, userId)
            users.append({
                'userId':userId,
                'itemIds':itemIds
            })
    mo.setResult('users', users)
    return mo

DecroationHelper.makeDecroationQueryResponse = makeDecroationQueryResponse

