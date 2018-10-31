# -*- coding=utf-8

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.events.tyevent import MatchWinloseEvent
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName="userId", lockName="userId", syncCall=0)
def publishMatchWinloseEvent(gameId, userId, matchId, isWin, rank, signinUserCount, rewards=None, mixId=None):
    ftlog.debug("<< |gameId, userId, matchId, isWin, rank:", gameId, userId, matchId, isWin, rank)
    eventBus = gdata.games()[gameId].getEventBus()
    if eventBus:
        eventBus.publishEvent(MatchWinloseEvent(userId, gameId, matchId, isWin, rank, signinUserCount, rewards, mixId))

