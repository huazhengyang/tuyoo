'''
Created on 2015-03-11

@author: zhaojiangang, zhouhao
'''
import json

import freetime.util.log as ftlog
from poker.entity.dao import gamedata
from dizhu.activities.toolbox import Tool
from datetime import datetime


class MatchRecord(object):
    class Record(object):
        def __init__(self, bestRank, bestRankDate, isGroup, crownCount, playCount):
            assert(isinstance(bestRank, (int, float)) and bestRank >= 0)
            assert(isinstance(bestRankDate, int) and bestRankDate >= 0)
            assert(isinstance(isGroup, int) and isGroup >= 0)
            assert(isinstance(crownCount, int) and crownCount >= 0)
            assert(isinstance(playCount, int) and playCount >= 0)
            self.bestRank = int(bestRank)
            self.bestRankDate = bestRankDate
            self.isGroup = isGroup
            self.crownCount = crownCount
            self.playCount = playCount

        def update(self, rank, isGroup):
            if isGroup == 0 and self.isGroup == 1:
                self.bestRank = int(rank)
                self.bestRankDate = int(Tool.datetimeToTimestamp(datetime.now()))
                self.isGroup = 0
            elif isGroup == self.isGroup:
                if self.bestRank <= 0 or rank < self.bestRank:
                    self.bestRank = int(rank)
                    self.bestRankDate = int(Tool.datetimeToTimestamp(datetime.now()))
            if rank == 1 and self.isGroup == 0:
                self.crownCount += 1
            self.playCount += 1


        @classmethod
        def fromDict(cls, d):
            bestRank = d.get('bestRank', 0)
            bestRankDate = d.get('bestRankDate', 0)
            isGroup = d.get('isGroup', 1)
            crownCount = d.get('crownCount', 0)
            playCount = d.get('playCount', 0)
            if (not isinstance(bestRank, (int, float)) or
                not isinstance(crownCount, int) or
                not isinstance(playCount, int) or
                not isinstance(bestRankDate, int) or
                not isinstance(isGroup, int)):
                return None
            return MatchRecord.Record(int(bestRank), bestRankDate, isGroup, crownCount, playCount)

        def toDict(self):
            return {'bestRank':int(self.bestRank), 'bestRankDate': self.bestRankDate, 'isGroup':self.isGroup, 'crownCount':self.crownCount, 'playCount':self.playCount}

    @classmethod
    def initialize(cls, eventBus):
        # eventBus.subscribe(MatchWinloseEvent, cls.onMatchWinlose)
        pass

    @classmethod
    def updateAndSaveRecord(cls, event):
        if event['userId'] < 10000: # robot
            return
        record = cls.loadRecord(event['gameId'], event['userId'], event['matchId'], event.get('mixId'))
        if record is None:
            record = MatchRecord.Record(0, 0, 1, 0, 0)
        record.update(event['rank'], event['isGroup'])
        cls.saveRecord(event['gameId'], event['userId'], event['matchId'], record, event.get('mixId'))

    @classmethod
    def loadRecord(cls, gameId, userId, matchId, mixId=None):
        try:
            jstr = gamedata.getGameAttr(userId, gameId, cls.__buildField(matchId, mixId))

            if ftlog.is_debug():
                ftlog.debug('MatchRecord.loadRecord gameId=', gameId,
                                      'userId=', userId,
                                      'matchId=', matchId,
                                      'data=', jstr,
                                      caller=cls)
            if jstr:
                return MatchRecord.Record.fromDict(json.loads(jstr))
        except:
            ftlog.exception()
        return None

    @classmethod
    def saveRecord(cls, gameId, userId, matchId, record, mixId=None):
        if ftlog.is_debug():
            ftlog.debug('MatchRecord.saveRecord gameId=', gameId,
                        'userId=', userId,
                        'matchId=', matchId,
                        'record=', json.dumps(record.toDict()),
                        'mixId=', mixId)
        gamedata.setGameAttr(userId, gameId, cls.__buildField(matchId, mixId), json.dumps(record.toDict()))

    @classmethod
    def __buildField(cls, matchId, mixId):
        if mixId is None:
            return 'm.%s' % (matchId)
        return 'm.%s.%s' % (matchId, mixId)

# if __name__ == '__main__':
#     from freetime.util.testbase import initContext
#     from freetime.games.dizhu.game import GameDizhu
#     initContext()
#     TyContext.RedisGame.execute(10001, 'del', 'gamedata:6:10001')
#     MatchRecord.initialize(GameDizhu)
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record is None)
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 10))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 0)
#     assert(record.bestRank == 10)
#     assert(record.playCount == 1)
#
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 9))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 0)
#     assert(record.bestRank == 9)
#     assert(record.playCount == 2)
#
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 1))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 1)
#     assert(record.bestRank == 1)
#     assert(record.playCount == 3)
#
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 10))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 1)
#     assert(record.bestRank == 1)
#     assert(record.playCount == 4)
#
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 1))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 2)
#     assert(record.bestRank == 1)
#     assert(record.playCount == 5)
#
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 1))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 3)
#     assert(record.bestRank == 1)
#     assert(record.playCount == 6)
#
#     GameDizhu.eventBus.publishEvent(MatchWinloseEvent(6, 10001, 610, True, 100))
#     record = MatchRecord.loadRecord(6, 10001, 610)
#     assert(record.crownCount == 3)
#     assert(record.bestRank == 1)
#     assert(record.playCount == 7)
#     print 'test ok'
