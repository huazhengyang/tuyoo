# -*- coding:utf-8 -*-
"""
Created on 2017年10月31日

@author: wangyonghui
"""
import json

import datetime

from dizhu.activitynew.activity import ActivityNew
from dizhu.entity import matchhistory
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.exceptions import TYBizConfException
import freetime.util.log as ftlog
from poker.entity.configure import configure, pokerconf
from poker.entity.dao import sessiondata


class MatchPromotionList(ActivityNew):
    TYPE_ID = 'ddz.act.match_promotion_list'
    def __init__(self):
        super(MatchPromotionList, self).__init__()
        if ftlog.is_debug():
            ftlog.debug('MatchPromotionList.__init__')
        self._clientIds = None
        self._open = None

    @property
    def open(self):
        return self._open

    @property
    def clientIds(self):
        return self._clientIds

    @property
    def matchList(self):
        return self._matchList


    def _decodeFromDictImpl(self, d):
        self._open = d.get('open')
        if not isinstance(self._open, int):
            raise TYBizConfException(d, 'MatchPromotionList._open must be int')

        self._clientIds = d.get('clientIds')
        if not isinstance(self._clientIds, list):
            raise TYBizConfException(d, 'MatchPromotionList._clientIds must be list')

        self._matchList = d.get('matchList')
        if not isinstance(self._matchList, dict):
            raise TYBizConfException(d, 'MatchPromotionList._matchList must be dict')



class TYActivityMatchPromotionList(TYActivity):
    TYPE_ID = 'ddz.act.match_promotion_list'
    MATCH_RANK_ACTION = 'match_rank'

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        if ftlog.is_debug():
            ftlog.debug('TYActivityMatchPromotionList.__init__',
                        'clientConfig=', clientConfig,
                        'serverConfig=', serverConfig)

    def handleRequest(self, msg):
        if ftlog.is_debug():
            ftlog.debug('TYActivityMatchPromotionList.handleRequest',
                        'msg=', msg)
        userId = msg.getParam('userId')
        clientId = msg.getParam('clientId')
        action = msg.getParam("action")

        config = self.getConfigForClient(DIZHU_GAMEID, userId, clientId)

        if action == self.MATCH_RANK_ACTION:
            actId = self._findClientActId(clientId)
            if actId:
                act = self._getActivityByActId(actId)
                if act:
                    # 获取顶级晋级名单
                    classify = []
                    topUsers = self.getTopRankList(act.matchList, act.clientIds)
                    classify.append(topUsers)

                    # 获取子级晋级名单
                    childUsers = self.getChildRankList(act.matchList, act.clientIds)
                    if childUsers:
                        classify.append(childUsers)

                    result = {
                        'action': self.MATCH_RANK_ACTION,
                        'activitId': actId,
                        'name': config.get('name'),
                        'classify': classify

                    }
                    if ftlog.is_debug():
                        ftlog.debug('TYActivityMatchPromotionList.handleRequest',
                                    'userId=', userId,
                                    'clientId=', clientId,
                                    'result=', result)
                    return result

        return {'code': -1, 'info': 'activity configure err'}


    @classmethod
    def getTopRankList(cls, matchListConf, filterClientIds):
        """
        获取顶级栏的晋级用户
        """
        topShowBar = matchListConf.get('showBar', [])[0]
        roundName = topShowBar.get('round')
        topMatchList = matchListConf.get('%s_list' % roundName, [])
        ret = []
        for match in topMatchList:
            # 各个月晋级的
            matchUsers = []
            promotionNum = match.get('promotionNum', 20)
            for matchId in match.get('matches', []):
                for date in match.get('dateList', []):
                    users = cls.getMatchRankUser(matchId, date, filterClientIds)
                    matchUsers.extend(users[:promotionNum])
            ret.append({
                'name': match.get('name'),
                'list': matchUsers,
                'num': match.get('num')
            })

        return {
            'name': topShowBar.get('name'),
            'list': ret
        }

    @classmethod
    def getChildRankList(cls, matchListConf, filterClientIds):
        """
        取子级栏的晋级用户
        """
        childShowBar = matchListConf.get('showBar', [])[-1]
        roundName = childShowBar.get('round')
        childMatchList = matchListConf.get('%s_list' % roundName, [])

        currentDate = datetime.datetime.now().date()
        ret = []
        for childMatch in childMatchList:
            fromDate, toDate = childMatch.get('dateRange').split('-')
            fromDate, toDate = datetime.datetime.strptime(fromDate, '%Y%m%d').date(), datetime.datetime.strptime(toDate, '%Y%m%d').date()
            if currentDate >= fromDate and currentDate <= toDate:
                for match in childMatch.get('round_list', []):
                    # 月下的周
                    matchUsers = []
                    promotionNum = match.get('promotionNum', 20)
                    for matchId in match.get('matches', []):
                        for date in match.get('dateList', []):
                            users = cls.getMatchRankUser(matchId, date, filterClientIds)
                            matchUsers.extend(users[:promotionNum])
                    ret.append({
                        'name': match.get('name'),
                        'list': matchUsers,
                        'num': match.get('num')
                    })
                    if ftlog.is_debug():
                        ftlog.debug('TYActivityMatchPromotionList.getChildRankList',
                                    'name=', match.get('name'),
                                    'num=', match.get('num'),
                                    'list=', matchUsers)
        return {
            'name': childShowBar.get('name'),
            'list': ret
        }


    @classmethod
    def getMatchRankUser(cls, matchId, date, filterClientIds):
        """
        获取比赛的排名用户
        """
        ret = []
        userList = matchhistory.getMatchHistoryRankByDate(matchId, date)

        if not userList:
            return ret
        for matchUser in userList:
            for index in xrange(len(matchUser)):
                if index % 2 == 0:
                    userInfo = json.loads(matchUser[index])
                    clientId = sessiondata.getClientId(userInfo.get('userId'))
                    intClientId = pokerconf.clientIdToNumber(clientId)
                    if intClientId in filterClientIds:
                        ret.append(userInfo)
        if ftlog.is_debug():
            ftlog.debug('TYActivityMatchPromotionList.getMatchRankUser',
                        'matchId=', matchId,
                        'date=', date,
                        'filterClientIds=', filterClientIds,
                        'userList=', userList,
                        'ret=', ret)
        return ret


    @classmethod
    def _getActIdList(cls):
        """
        获取所有榜单下的活动Id
        """
        actConfList = []
        conf = configure.getGameJson(6, 'activity.new', {})
        for actConf in conf.get('activities', []):
            if actConf.get('typeId', '') == cls.TYPE_ID:
                actConfList.append(actConf)
        return actConfList

    @classmethod
    def _findClientActId(cls, clientId):
        """
        用户对应的活动 Id, 没有返回 None
        """
        for actConf in cls._getActIdList():
            intClientId = pokerconf.clientIdToNumber(clientId)
            if intClientId in actConf.get('clientIds', []):
                return actConf.get('actId')
        return

    @classmethod
    def _getActivityByActId(cls, actId):
        """
        获取活动实例
        """
        from dizhu.activitynew import activitysystemnew
        scoreActivity = activitysystemnew.findActivity(actId)
        return scoreActivity











