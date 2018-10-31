# -*- coding=utf-8 -*-
'''
Created on 2016-11-05
dizhu.servers.util.rpc.act_remote
@author: luwei
'''
from poker.protocol.rpccore import markRpcCall
import freetime.util.log as ftlog
import hall.entity.hallactivity.activity as hallactivity


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def sendRewards(userId, countChipLeft, countChipRight, resultState, activityGameId, activityId, issueNumber):
    ftlog.debug('act_betguess_remote.sendRewards:',
                'userId=', userId,
                'countChipLeft=', countChipLeft,
                'countChipRight=', countChipRight,
                'resultState=', resultState,
                'activityGameId=', activityGameId,
                'activityId=', activityId,
                'issueNumber=', issueNumber)
    
    actobj = hallactivity.activitySystem.getActivityObj(activityId)
    ftlog.debug('act_betguess_remote.sendRewards:',
                'userId=', userId,
                'actobj=', actobj)
    
    if not actobj:
        return {'err':'activity not found! activityId maybe error', 'chip':0}
    
    chip = actobj.sendRewardToUser(userId, countChipLeft, countChipRight, resultState, activityGameId, activityId, issueNumber)
    return {'err':None, 'chip':chip}


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def userBet(userId, betChip, isLeft, issueNumber, activityId):
    ftlog.debug('act_betguess_remote.userBet:',
                'userId=', userId,
                'betChip=', betChip,
                'isLeft=', isLeft,
                'issueNumber=', issueNumber)
    
    actobj = hallactivity.activitySystem.getActivityObj(activityId)
    ftlog.debug('act_betguess_remote.userBet:',
                'userId=', userId,
                'actobj=', actobj)
    
    if not actobj:
        return 'activity not found! activityId maybe error', None
    
    return None, actobj.onActionBetChip(userId, betChip, isLeft, issueNumber)
