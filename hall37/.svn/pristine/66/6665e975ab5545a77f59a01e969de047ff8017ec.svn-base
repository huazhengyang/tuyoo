# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from datetime import datetime
from sre_compile import isstring

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallranking, hallconf
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.dao import userdata
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from poker.util import strutil


@markCmdActionHandler
class RankTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(RankTcpHandler, self).__init__()
        self._cacheRankings = {}
        
    def _check_param_rankKey(self, msg, key, params):
        rankKey = msg.getParam('rankKey')
        if not isstring(rankKey):
            return 'must be set rankKey', None
        return None, rankKey
    
    @markCmdActionMethod(cmd='custom_rank', action="query", clientIdVer=0)
    def doRankQuery(self, gameId, userId, clientId, rankKey):
        mo = MsgPack()
        mo.setCmd('custom_rank')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('rankKey', rankKey)
        mo.setResult('tabs', self.getRankingTabs(gameId, userId, rankKey, clientId))
        router.sendToUser(mo, userId)
        return mo
    
    def getRankingTabs(self, gameId, userId, rankingKey, clientId):
        templateName = hallconf.getClientRankTemplateName(rankingKey, clientId) or 'default'
        rankingDefines = hallranking.rankingSystem.getRankingDefinesForRankingKey(rankingKey, templateName)
        if ftlog.is_debug():
            ftlog.debug('RankTcpHandler.getRankingTabs gameId=', gameId,
                        'userId=', userId,
                        'rankKey=', rankingKey,
                        'templateName=', templateName,
                        'rankingIds=', [rd.rankingId for rd in rankingDefines])
        tabs = []
        for rankingDefine in rankingDefines:
            cacheRanking = self.getRanking(userId, rankingDefine)
            if cacheRanking:
                rankingUser = cacheRanking[0].rankingUserMap.get(userId)
                if rankingUser:
                    cacheRanking = strutil.cloneData(cacheRanking)
                    cacheRanking[2]['rankInfo'] = cacheRanking[0].rankingDefine.inRankDesc.replace('${rank}', str(rankingUser.rank+1))
                tabs.append(cacheRanking[2])
        return tabs
    
    def getRanking(self, userId, rankingDefine):
        '''
        @return: (TYRankingList, timestamp, rankingList)
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        cacheRanking = self._cacheRankings.get(rankingDefine.rankingId)
        if (not cacheRanking
            or (timestamp-cacheRanking[1]) >= cacheRanking[0].rankingDefine.cacheTimes
            or pktimestamp.getDayStartTimestamp(timestamp)
                != pktimestamp.getDayStartTimestamp(cacheRanking[1])):
            cacheRanking = self._getRanking(rankingDefine, timestamp)
            if cacheRanking:
                self._cacheRankings[rankingDefine.rankingId] = cacheRanking
                if ftlog.is_debug():
                    ftlog.debug('RankTcpHandler.getRanking cache userId=', userId,
                                'rankingId=', rankingDefine.rankingId,
                                'rankingIssueNumber=', cacheRanking[0].issueNumber,
                                'rankingCycle=', ('[%s,%s)' % (cacheRanking[0].timeCycle.startTime, cacheRanking[0].timeCycle.endTime)),
                                'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                                'data=', cacheRanking[2])
            else:
                if rankingDefine.rankingId in self._cacheRankings:
                    del self._cacheRankings[rankingDefine.rankingId]
                    if ftlog.is_debug():
                        ftlog.debug('RankTcpHandler.getRanking remove userId=', userId,
                                    'rankingId=', rankingDefine.rankingId)

        return cacheRanking
    
    def _filterScore(self, score):
        l = [
            (100000000, '亿', 2),
            (10000, '万', 2)
        ]
        for divisor, units, ndigits in l:
            if score >= divisor:
                unitsScore = round(score / float(divisor), ndigits)
                fmt = '%d%s' if unitsScore == int(unitsScore) else '%%.%sf%%s' % (ndigits)
                return fmt % (unitsScore, units)
        return str(score)
    
    def _getRanking(self, rankingDefine, timestamp):
        rankingList = hallranking.rankingSystem.getTopN(rankingDefine.rankingId,
                                                        rankingDefine.totalN, timestamp)
        if not rankingList:
            return None
        rankDatas = []
        for index, user in enumerate(rankingList.rankingUserList):
            if index >= rankingDefine.topN:
                break
            name, purl = userdata.getAttrs(user.userId, ['name', 'purl'])
            detail = {}
            detail['name'] = str(name) if name else ''
            detail['headUrl'] = str(purl) if purl else ''
            detail['rankValue'] = self._filterScore(user.score)
            rankDatas.append({
                'rank':user.rank + 1,
                'rankPic':rankingList.rankingDefine.getPicByRank(user.rank),
                'userId':user.userId,
                'detail':detail,
            })
        return (rankingList, timestamp, {
                'rankId':rankingDefine.rankingId,
                'issueNum':rankingList.issueNumber,
                'name':rankingList.rankingDefine.name,
                'desc':rankingList.rankingDefine.desc,
                'rankInfo':rankingList.rankingDefine.outRankDesc,
                'type':rankingList.rankingDefine.rankingType,
                'rankDatas':rankDatas
            })
        

