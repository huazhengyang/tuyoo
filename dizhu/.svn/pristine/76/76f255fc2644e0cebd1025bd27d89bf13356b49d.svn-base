# -*- coding:utf-8 -*-
'''
Created on 2017年7月24日

@author: wangjifa
'''

import freetime.util.log as ftlog
from dizhu.entity import dizhu_score_ranking

def fixScoreRankingRank():
    issueNum = '20170717'
    for rankId in ['0', '1']:
        rank = 0
        userInfos = dizhu_score_ranking.getRanklist(rankId, issueNum, 0 ,-1)
        for userId in userInfos:
            rank += 1
            userData = dizhu_score_ranking.loadUserData(userId, rankId, issueNum)
            if userData.rank != rank:
                ftlog.info('hotfxi_score_ranking userId=', userId,
                           'rankId=', rankId,
                           'issueNum=', issueNum,
                           'oldRank=', userData.rank,
                           'rank=', rank,
                           'state=', userData.rewardState)
                userData.rank = rank
                dizhu_score_ranking.saveUserData(userData)
            ftlog.info('hotfxi_score_ranking userId=', userId, 'rankId=', rankId,
                       'issueNum=', issueNum, 'rank=', userData.rank, 'state=', userData.rewardState)

    ftlog.info('hotfxi_score_ranking_rank over issueNum=', issueNum)

fixScoreRankingRank()