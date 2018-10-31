# -*- coding=utf-8 -*-
'''
Created on 2016年05月05日

@author: luwei

比赛历史记录
'''
import json

from datetime import datetime

from dizhu.activities.toolbox import Tool, JsonQueue
from dizhu.entity import dizhuconf
import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.dao import daobase
from poker.entity.game.rooms.group_match_ctrl.events import MatchingFinishEvent
from poker.util import strutil


def getMatchHistoryConfig():
    '''
    获得比赛历时记录的配置
    '''
    return dizhuconf.getPublic().get('match_history', {})


class MatchHistoryDatabaseNew(object):
    '''
    比赛历史记录数据库
    '''
    @classmethod
    def redis(cls, userId, command, *args):
        '''
        内部访问redis的统一接口
        :param command:redis命令
        :param args:参数
        '''
        rpath = 'mrecord:' + str(userId)
        return daobase.executeUserCmd(userId, command, rpath, *args)

    @classmethod
    def getMaxHistoryNumber(cls):
        conf = getMatchHistoryConfig()
        return conf.get('record_number', 10)

    @classmethod
    def buildField(cls, recordId, mixId):
        if mixId:
            return '%s_%s' % (recordId, mixId)
        return recordId
    
    @classmethod
    def addingHistoryEntry(cls, userId, recordId, record, mixId=None):
        '''
        存储比赛历史记录
        :param recordId 比赛ID,不是roomId,是在matchConf中配置的那个recordId
        :param record 比赛记录数据
        @param mixId: 混房的Id
        '''
        ftlog.debug('MatchHistoryDatabaseNew.addingHistoryEntry:',
                    'userId=', userId,
                    'recordId=', recordId,
                    'record=', record,
                    'mixId=', mixId)
        if not record:
            return

        # 获取需要存储的最大条数
        maxNumber = cls.getMaxHistoryNumber()
        
        # 读取比赛的所有记录
        j = cls.redis(userId, 'hget', cls.buildField(recordId, mixId))
            
        jq = JsonQueue(maxNumber)
        if j:
            jq.fromJson(j)
        jq.enqueue(record)
        d = jq.toJson()
        
        cls.redis(userId, 'hset', cls.buildField(recordId, mixId), d)
        
    @classmethod
    def getLeastHistory(cls, userId, recordId, number, mixId=None):
        '''
        获取最近加入的历史记录
        :param recordId 比赛ID,不是roomId,是在matchConf中配置的那个recordId
        :param number: 要获取的条数,若不足则只返回已存在的条数
        :return 顺序为，数组前面的记录是最早(老旧)的
        '''
        ftlog.debug('MatchHistoryDatabaseNew.getLeastHistory:',
                    'userId=', userId,
                    'recordId=', recordId,
                    'number=', number,
                    'mixId=', mixId)
        if number <= 0:
            return []
        
        # 获取需要存储的最大条数
        maxNumber = cls.getMaxHistoryNumber()
        
        # 读取比赛的所有记录
        j = cls.redis(userId, 'hget', cls.buildField(recordId, mixId))
        if not j:
            return []

        jq = JsonQueue(maxNumber)
        jq.fromJson(j)
        l = jq.tail(number)

        return l


class MatchHistoryHandler(object):


    @classmethod
    def getMatchHistory(cls, userId, recordId, number=0, mixId=None):
        '''
        获取比赛历史
        '''

        # # 若请求的历史记录数量小于等于0,则返回记录的所有条数
        if number <= 0:
            number = MatchHistoryDatabaseNew.getMaxHistoryNumber()

        # # 获得格式化字符串
        conf = getMatchHistoryConfig()
        reward_case = conf.get('reward_format', '')
        noreward_case = conf.get('no_reaward_format', '')
        history_group_word = conf.get('history_group_word', '')

        response = []
        histories = MatchHistoryDatabaseNew.getLeastHistory(userId, recordId, number, mixId)
        ftlog.debug('MatchHistoryHandler.onFetchMatchHistory:',
                    'userId=', userId,
                    'recordId=', recordId,
                    'number=', number,
                    'mixId=', mixId,
                    'histories=', histories)

        for i in xrange(0, len(histories)):
            historyrecord = histories[i]
            historytime = historyrecord.get('time', 0)
            historyrank = historyrecord.get('rank', 0)
            historyreward = historyrecord.get('reward')
            historyIsGroping = historyrecord.get('isGroping', False)
            historyExchangeCode = historyrecord.get('exchangeCode', 0)

            dictionary = {
                'history_reward':historyreward,
                'history_rank': historyrank,
                'history_group': history_group_word if historyIsGroping else ''
            }
            if historyreward:  # # 有奖励的情况下
                resultdesc = strutil.replaceParams(reward_case, dictionary)
            else:  # # 无奖励的情况
                resultdesc = strutil.replaceParams(noreward_case, dictionary)
            response.insert(i, {'timestamp':historytime, 'desc': resultdesc, 'rank': historyrank, 'exchangeCode': historyExchangeCode})
        response.reverse()
        return response

    @classmethod
    def onMatchOver(cls, userId, recordId, rank, iswin, rewards, isGroping, mixId=None, exchangeCode=None):
        '''
        比赛结束会被调用
        :param userId:
        :param recordId:
        :param rank:
        :param iswin:
        :param rewards:
        :param isGroping: 是否是分组阶段
        :param mixId: 混房Id
        :param exchangeCode: 红包兑换码
        :return:
        '''
        if userId < 10000:  # robot
            return

        ftlog.debug('MatchHistoryHandler.onMatchOver: ',
                    'userId=', userId,
                    'recordId=', recordId,
                    'rank=', rank,
                    'isWin=', iswin,
                    'rewards=', rewards,
                    'isGroping=', isGroping,
                    'mixId=', mixId,
                    'exchangeCode=', exchangeCode)

        if not rewards:
            rewards = {}

        MatchHistoryDatabaseNew.addingHistoryEntry(userId, recordId, {
            'time': Tool.datetimeToTimestamp(datetime.now()),
            'rank': rank,
            'reward': rewards.get('desc'),
            'isGroping': isGroping,
            'exchangeCode': exchangeCode
        }, mixId)



# 比赛排名存储系统
_inited = False
def _initialize():
    ftlog.info('matchhistory initialize begin')
    from dizhu.game import TGDizhu
    global _inited
    if not _inited:
        _inited = True
        TGDizhu.getEventBus().subscribe(MatchingFinishEvent, onMatchingFinish)
    ftlog.info('matchhistory initialize end')



def onMatchingFinish(event):
    try:
        sequence = int(event.instId.split('.')[1])
        key = buildMatchPromotionKey(event.matchId, sequence)
        datas = daobase.executeRePlayCmd('zrange', key, 0, -1, 'withscores')
        if not datas:
            ftlog.info('matchhistory onMatchingFinish',
                       'gameId=', event.gameId,
                       'matchId=', event.matchId,
                       'instId=', event.instId,
                       'does not support persist')
            return

        dateStr = datas[0]
        value = getMatchHistoryRankByDate(event.matchId, dateStr)
        if value:
            value.append(datas[2:])
        else:
            value = [datas[2:]]
        saveMatchHistoryRank(event.matchId, dateStr, json.dumps(value))
        daobase.executeRePlayCmd('del', key)
    except Exception, e:
        ftlog.error('matchhistory onMatchingFinish',
                    'gameId=', event.gameId,
                    'matchId=', event.matchId,
                    'instId=', event.instId,
                    'err=', e.message)


# 数据持久化的相关处理
def buildMatchPromotionKey(matchId, sequence):
    return 'match.promotion_list:%s:%s:%s' % (DIZHU_GAMEID, matchId, sequence)

def buildMatchHistoryRankKey(matchId):
    return 'match.history_rank:%s:%s' % (DIZHU_GAMEID, matchId)

def insertMatchHistoryRank(matchId, sequence, rank, startTime, info):
    try:
        key = buildMatchPromotionKey(matchId, sequence)

        ret = daobase.executeRePlayCmd('zrange', key, 0, -1, 'withscores')
        if not ret:
            daobase.executeRePlayCmd('zadd', key, 0, startTime)
        daobase.executeRePlayCmd('zadd', key, rank, info)

        if ftlog.is_debug():
            ftlog.debug('matchhistory insertMatchHistoryRank',
                        'matchId=', matchId,
                        'sequence=', sequence,
                        'startTime=', startTime,
                        'rank=', rank,
                        'info=', info)
    except Exception, e:
        ftlog.error('matchhistory insertMatchHistoryRank',
                    'matchId=', matchId,
                    'sequence=', sequence,
                    'rank=', rank,
                    'info=', info,
                    'err=', e.message)

def saveMatchHistoryRank(matchId, dateStr, value):
    key = buildMatchHistoryRankKey(matchId)
    ftlog.info('matchhistory saveMatchHistoryRank',
               'matchId=', matchId,
               'key=', key,
               'dateStr=', dateStr,
               'value=', value)
    daobase.executeRePlayCmd('hset', key, dateStr, value)


def getMatchHistoryRankByDate(matchId, dateStr):
    key = buildMatchHistoryRankKey(matchId)
    value = daobase.executeRePlayCmd('hget', key, dateStr)
    if ftlog.is_debug():
        ftlog.debug('matchhistory getMatchHistoryRankByDate',
                    'matchId=', matchId,
                    'dateStr=', dateStr,
                    'key=', key,
                    'value=', value)
    return json.loads(value) if value else None
