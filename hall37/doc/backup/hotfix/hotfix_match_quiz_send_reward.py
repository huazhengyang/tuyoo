# -*- coding:utf-8 -*-
'''
Created on 2016年6月24日

@author: zhaojiangang
'''
import math

import freetime.util.log as ftlog
from hall.entity import hallconf
from hall.entity.hallactivity import activity_match_quiz
from hall.entity.hallactivity.activity_match_quiz import UserQuizStatus
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.rpc import user_remote
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import daobase


def _getActivityConf(activityId):
    conf = hallconf.getActivityConf()
    activities = conf.get('activities', {})
    return activities.get(activityId)

def _getActUsers(gameId, activityId):
    userIds = daobase.executeMixCmd('smembers', 'act.users:%s:%s' % (gameId, activityId))
    return userIds if userIds else []

def _setAlreadySentReward(gameId, activityId, userId):
    return daobase.executeMixCmd('sadd', 'act.reward.users:%s:%s' % (gameId, activityId), userId) == 1
    
def _isAlreadySentReward(gameId, activityId, userId):
    return daobase.executeMixCmd('sismember', 'act.reward.users:%s:%s' % (gameId, activityId), userId) == 1

def _sendReward(gameId, activityId, quizResult):
    if not quizResult in ('l', 'm', 'r'):
        ftlog.warn('hotfix_match_quiz._sendReward BadQuizResult gameId=', gameId,
                   'activityId=', activityId, 'quizResult=', quizResult)
        return
    
    actConf = _getActivityConf(activityId)
    if not actConf:
        ftlog.warn('hotfix_match_quiz._sendReward NotActConf gameId=', gameId,
                   'activityId=', activityId, 'quizResult=', quizResult)
        return
    
    serverConf = actConf.get('server_config')
    if not serverConf:
        ftlog.warn('hotfix_match_quiz._sendReward NotActServerConf gameId=', gameId,
                   'activityId=', activityId, 'quizResult=', quizResult)
        return
    
    oddsMap = {
        'l':serverConf['leftOdds'],
        'm':serverConf['middleOdds'],
        'r':serverConf['rightOdds'],
    }
    
    odds = oddsMap.get(quizResult)
    gameId = int(serverConf['gameId'])
    intActId = int(serverConf['intActId'])
    chipAssetId = 'user:chip' #serverConf['chipAssetId']
    
    ftlog.info('hotfix_match_quiz._sendReward sending... gameId=', gameId,
               'activityId=', activityId,
               'quizResult=', quizResult,
               'intActId=', intActId,
               'chipAssetId=', chipAssetId,
               'odds=', odds,
               'oddsMap=', oddsMap)
    
    totalBets = {'l':0, 'm':0, 'r':0}
    totalReward = 0
    needTotalReward = 0
    userIds = _getActUsers(gameId, activityId)
    
    for userId in userIds:
#         class UserQuizStatus(object):
#     def __init__(self, userId):
#         self._userId = userId
#         self._betMap = {}
#         self._totalBet = 0
        status = activity_match_quiz.loadUserQuizStatus(gameId, userId, activityId)
        if not status:
            ftlog.error('hotfix_match_quiz._sendReward NotUserStatus gameId=', gameId,
                        'activityId=', activityId,
                        'quizResult=', quizResult,
                        'intActId=', intActId,
                        'chipAssetId=', chipAssetId,
                        'odds=', odds,
                        'oddsMap=', oddsMap,
                        'userId=', userId,
                        'status=', None)
            status = UserQuizStatus(userId)
            
        betAmount = status.getBet(quizResult, 0)
        
        totalBets['l'] += status.getBet('l', 0)
        totalBets['m'] += status.getBet('m', 0)
        totalBets['r'] += status.getBet('r', 0)
        
        quizResultTitleMap = {'l':serverConf['leftTitle']+'获胜', 'm':'平局', 'r':serverConf['rightTitle']+'获胜'}
        
        if betAmount > 0:
            rewardCount = int(math.ceil(betAmount * odds))
            needTotalReward += rewardCount
            addState = 2
            if _setAlreadySentReward(gameId, activityId, userId):
                try:
                    # 给用户发奖
                    addOk = user_remote.addAssets(gameId, userId, [{'itemId':chipAssetId, 'count':rewardCount}],
                                                  'ACTIVITY_CONSUME', intActId)
                    
                    msg = '恭喜您在%s活动%sVS%s场次押注%s金币猜中%s，赔率为%s，获得%s金币奖励。' % (actConf['name'],
                                                                                serverConf['leftTitle'],
                                                                               serverConf['rightTitle'],
                                                                               int(betAmount),
                                                                               quizResultTitleMap[quizResult],
                                                                               odds,
                                                                               rewardCount)
                    pkmessage.sendPrivate(HALL_GAMEID, userId, 0, msg)
                except:
                    ftlog.error('hotfix_match_quiz._sendReward RewardUser gameId=', gameId,
                                'activityId=', activityId,
                                'quizResult=', quizResult,
                                'intActId=', intActId,
                                'chipAssetId=', chipAssetId,
                                'odds=', odds,
                                'oddsMap=', oddsMap,
                                'userId=', userId,
                                'rewardCount=', rewardCount,
                                'status=', status.toDict())
                    addOk = False
                addState = 1 if addOk else 0
                if addOk:
                    totalReward += rewardCount

            ftlog.info('hotfix_match_quiz._sendReward RewardUser gameId=', gameId,
                       'activityId=', activityId,
                       'quizResult=', quizResult,
                       'intActId=', intActId,
                       'chipAssetId=', chipAssetId,
                       'odds=', odds,
                       'oddsMap=', oddsMap,
                       'userId=', userId,
                       'rewardCount=', rewardCount,
                       'addState=', addState,
                       'status=', status.toDict())
        else:
            ftlog.info('hotfix_match_quiz._sendReward NotRewardUser gameId=', gameId,
                       'activityId=', activityId,
                       'quizResult=', quizResult,
                       'intActId=', intActId,
                       'chipAssetId=', chipAssetId,
                       'odds=', odds,
                       'oddsMap=', oddsMap,
                       'userId=', userId,
                       'status=', status.toDict())

    ftlog.info('hotfix_match_quiz._sendReward sent gameId=', gameId,
               'activityId=', activityId,
               'quizResult=', quizResult,
               'intActId=', intActId,
               'chipAssetId=', chipAssetId,
               'odds=', odds,
               'oddsMap=', oddsMap,
               'totalBets=', totalBets,
               'totalReward=', totalReward,
               'needTotalReward=', needTotalReward)
    return {'actId':activityId, 'intActId':intActId,
            'chipAssetId':chipAssetId, 'quizResult':quizResult,
            'totalBets':totalBets,
            'totalReward':totalReward,
            'odds':odds,
            'oddsMap':oddsMap,
            'needTotalReward':needTotalReward,
            }

resp = _sendReward(6, 'activity_ddz_aoyunjingcai_0818', 'r')
if resp:
    results['resp'] = resp


