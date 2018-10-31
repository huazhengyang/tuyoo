# -*- coding:utf-8 -*-
'''
Created on 2017年7月24日

@author: wangjifa
'''

import freetime.util.log as ftlog
from dizhu.entity import dizhu_score_ranking

def punishUser(userIdList, rankId, issueNum):
    for userId in userIdList:
        oldUserData = dizhu_score_ranking.loadUserData(userId, rankId, issueNum)
        if oldUserData:
            ftlog.info('punish cheat user in scoreRanking old_user_info=', oldUserData.toDict())

            userData = dizhu_score_ranking.UserData(userId, rankId, issueNum)
            dizhu_score_ranking.saveUserData(userData)
            rankingDefine = dizhu_score_ranking.getConf().findRankingDefine(rankId)
            dizhu_score_ranking.insertRanklist(rankId, issueNum, userId, userData.score, max(rankingDefine.rankLimit, 500))

            ftlog.info('punish cheat user in scoreRanking userId=', userId, 'rankId=', rankId, 'issueNum=', issueNum)
        else:
            ftlog.info('punish cheat user in scoreRanking userId=', userId, 'rankId=', rankId, 'issueNum=', issueNum,
                       'no ScoreRanking Data')
    ftlog.info('punish cheat user in scoreRanking. over')


'''
266014407,
266670513,
267345504,
267715699,
267454470,
266022297,
267722878,
267887747,
267888559,
267860677,
267860676,
267860475,
267860481,
267500583

248051052  赖糖糖
269039923  仙咪咪
261374894  简单愿望
248202875  今晚杀两亿
268982785  番薯克

248051052,
269039923,
261374894,
248202875,
268982785
'''

# 20170818日清理20170814期作弊玩家
punishUserIdList = [
    110411491,
    270895021,
    148094800
]
punishRankId = '0'
punishIssueNum = '20170814'
punishUser(punishUserIdList, punishRankId, punishIssueNum)