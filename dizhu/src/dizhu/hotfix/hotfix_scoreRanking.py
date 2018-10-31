# -*- coding:utf-8 -*-
'''
Created on 2017年7月24日

@author: wangjifa
'''

import freetime.util.log as ftlog
from dizhu.entity import dizhu_score_ranking


def addUserScore(userId, rankId, issueNum, score=0):

    issueNum = str(issueNum)

    userData = dizhu_score_ranking.loadUserData(userId, rankId, issueNum)
    if userData:
        ftlog.info('hotfix.addUserScore',
                   'userId=', userId,
                   'rankId=', rankId,
                   'issueNum=', issueNum,
                   'score=', score,
                   'userData=', userData.toDict())

        try:
            score = int(score)
        except ValueError, e:
            ftlog.warn('hotfix.addUserScore.valueError',
                       'userId=', userId,
                       'rankId=', rankId,
                       'issueNum=', issueNum,
                       'err=', e)
            return

        userData.score += score
        userData.score = max(0, userData.score)

        ret = dizhu_score_ranking.saveUserData(userData)
        rankingDefine = dizhu_score_ranking.getConf().findRankingDefine(rankId)
        rankLimit = rankingDefine.rankLimit if rankingDefine else 3000
        dizhu_score_ranking.insertRanklist(rankId, issueNum, userData.userId, userData.score, rankLimit)

        ftlog.info('hotfix.addUserScore.over',
                   'userId=', userId,
                   'rankId=', rankId,
                   'issueNum=', issueNum,
                   'score=', score,
                   'userData=', userData.toDict())
    else:
        ftlog.warn('hotfix.addUserScore.warning.noUserData',
                   'userId=', userId,
                   'rankId=', rankId,
                   'issueNum=', issueNum,
                   'score=', score)


"""
236080859
补偿：2200分
29134898
补偿：35000分
"""


def runReport():
    # 大榜玩家29134898补偿积分35000
    addUserScore(29134898, "0", "20180122", 35000)
    # 小榜玩家236080859补偿积分2200
    addUserScore(236080859, "1", "20180122", 2200)
    ftlog.info('hotfix.addUserScore.ok.20180125')

from freetime.core.timer import FTLoopTimer
FTLoopTimer(0, 0, runReport).start()

