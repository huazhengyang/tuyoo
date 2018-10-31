# -*- coding=utf-8
"""
Created on 2017年8月17日

@author: wangjifa
"""

from dizhu.entity import dizhu_score_ranking
from poker.protocol.decorator import markHttpMethod
from dizhu.servers.http import ddz_httpgdss
import freetime.util.log as ftlog


@markHttpMethod(httppath='/_gdss/user/init_user_data_gdss')
def doExecuteCmd(self, userId, rankId, issueNum):
    """
    :param userId: 玩家userId
    :param rankId: 排行榜类型 '0' 万元争霸赛 '1' 千元擂台赛
    :param issueNum: 排行榜期号 格式：20170807
    :return: 返回处理结果信息 
    """
    ret = 0
    if len(str(issueNum)) != 8:
        return self.makeResponse({'score_execute_cmd issueNum Error. rankId': rankId, 'issueNum=': issueNum})
    issueNum = str(issueNum)
    userData = dizhu_score_ranking.loadUserData(userId, rankId, issueNum)
    if userData:
        ftlog.info('init_user_data_gdss del scoreRanking userData=', userData.toDict())

        userData = dizhu_score_ranking.UserData(userId, rankId, issueNum)
        ret = dizhu_score_ranking.saveUserData(userData)
        rankingDefine = dizhu_score_ranking.getConf().findRankingDefine(rankId)
        rankLimit = rankingDefine.rankLimit if rankingDefine else 3000
        dizhu_score_ranking.insertRanklist(rankId, issueNum, userData.userId, userData.score, rankLimit)

        ftlog.info('init_user_data_gdss del scoreRanking userData success. userData=', userData.toDict())
    else:
        ftlog.info('init_user_data_gdss no userData in rankingList userId=', userId,
                   'rankId=', rankId, 'issueNum=', issueNum)
        return self.makeResponse({'init_user_data_gdss no userData in rankingList userId=': userId,
                                  'rankId': rankId, 'issueNum=': issueNum})

    return self.makeResponse({'init_user_data_gdss del scoreRanking userData success. userData=': userData.toDict(), 'execute over ret=': ret})


@markHttpMethod(httppath='/_gdss/user/del_user_score_gdss')
def doDelUserScore(self, userId, rankId, issueNum, score):
    """
    :param userId: 玩家userId
    :param rankId: 排行榜类型 '0' 万元争霸赛 '1' 千元擂台赛
    :param issueNum: 排行榜期号 格式：20170807
    :param score: 扣除的积分数量
    :return: 返回处理结果信息 
    """
    ret = 0
    if len(issueNum) != 8:
        return self.makeResponse({'del_user_score_gdss issueNum Error. rankId': rankId, 'issueNum=': issueNum})

    issueNum = str(issueNum)

    userData = dizhu_score_ranking.loadUserData(userId, rankId, issueNum)
    if userData:
        ftlog.info('del_user_score_gdss del scoreRanking userData=', userData.toDict())

        score = max(0, score)
        userData.score -= score
        userData.score = max(0, userData.score)

        ret = dizhu_score_ranking.saveUserData(userData)
        rankingDefine = dizhu_score_ranking.getConf().findRankingDefine(rankId)
        rankLimit = rankingDefine.rankLimit if rankingDefine else 3000
        dizhu_score_ranking.insertRanklist(rankId, issueNum, userData.userId, userData.score, rankLimit)

        ftlog.info('del_user_score_gdss del scoreRanking userData success. userData=', userData.toDict())
    else:
        ftlog.info('del_user_score_gdss no userData in rankingList userId=', userId, 'rankId=', rankId, 'issueNum=',
                   issueNum)
        return self.makeResponse(
            {'init_user_data_gdss no userData in rankingList userId=': userId, 'rankId': rankId,
             'issueNum=': issueNum})

    return self.makeResponse({'del_user_score_gdss del scoreRanking userData success. userData=': userData.toDict(),
                              'execute over ret=': ret})


ddz_httpgdss.HttpGameHandler.doExecuteCmd = doExecuteCmd
ddz_httpgdss.HttpGameHandler.doDelUserScore = doDelUserScore
ftlog.info('hotfix_ddz_httpgdss init_user_data_gdss over')