# -*- coding:utf-8 -*-
"""
Created on 2017年10月10日

@author: wangjifa
"""

import freetime.util.log as ftlog
from dizhu.activitynew.activity_score_ranking import loadActivityScoreRankingInfo, \
    getRankList, loadOrCreateUserData, getUserRank

# 在CT服执行
def activity_getScoreRankingInfo(rankId, issueNumList):
    rewardLimit = 500

    info = []
    for issueNum in issueNumList:
        rankInfo = []
        rankList = getRankList(rankId, issueNum, 0, rewardLimit - 1)
        if rankList:
            for rankUserId in rankList:
                rankUserData = loadOrCreateUserData(rankUserId, rankId, issueNum)
                rank = rankUserData.rank or getUserRank(rankUserId, rankId, issueNum)
                rankUserInfo = {'userId': rankUserId, 'name': rankUserData.name, 'rank': rank, 'score': rankUserData.score}
                rankInfo.append(rankUserInfo)
        info.append({'issueNum': issueNum, 'rankInfo': rankInfo})
        ftlog.info('activity_getScoreRankingInfo issueNum=', issueNum, 'rankInfo=', rankInfo)
    ftlog.info('20171010 ActivityScoreRankingInfo activity_getScoreRankingInfo rankId=', rankId, 'info=', info)
    return info

def activity_getRankingInfoByRankId(rankId):
    scoreRankingInfo = loadActivityScoreRankingInfo(rankId)
    if scoreRankingInfo.itemCount > 0:
        itemList = scoreRankingInfo.toDict().get('items')
        issnList = []
        for item in itemList:
            issn = item.get('issn')
            if issn:
                issnList.append(issn)
        activity_getScoreRankingInfo(rankId, issnList)

    ftlog.info('20171010 ActivityScoreRankingInfo loaded. actId=', rankId, 'count=', scoreRankingInfo.itemCount)

activity_getRankingInfoByRankId('act60930')
ftlog.info('20171010 ActivityScoreRankingInfo load over')









