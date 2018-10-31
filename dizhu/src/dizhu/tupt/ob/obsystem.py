# -*- coding:utf-8 -*-
'''
Created on 2017年5月8日

@author: zhaojiangang
'''

import functools
import hashlib
import random
from sre_compile import isstring

from dizhu.tupt.ob import uploader
from dizhucomm.core.events import GameRoundOverEvent, GameRoundAbortEvent
from dizhucomm.replay.codec import GameRoundCodecDictReplay
from freetime.aio import http
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.configure import configure, gdata
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.game.rooms.group_match_ctrl.events import MatchingStartEvent, \
    MatchingFinishEvent
from poker.util import strutil


_inited = False
_replayMatchs = {}
_uploadUrls = []
_uploadToken = ''
_obSwitch = False


class TUPTReplay(object):
    def __init__(self, videoId, userId, roomId,
                 roomName, stageName, details,
                 timestamp):
        self.videoId = videoId
        self.userId = userId
        self.roomId = roomId
        self.roomName = roomName
        self.stageName = stageName
        self.details = details
        self.timestamp = timestamp


def buildDetails(gameRound):
    seats = []
    for i, seat in enumerate(gameRound.seats):
        seatWinloseDetail = gameRound.winloseDetail.seatWinloseDetails[i]
        seats.append({
            'uid':seat.userId,
            'name':seat.userName,
            'headUrl':seat.headUrl,
            'dChip':seatWinloseDetail.deltaChip,
            'fChip':seatWinloseDetail.finalChip
        })
    return {
        'nbomb':gameRound.winloseDetail.bombCount,
        'isChuntian':gameRound.winloseDetail.isChuntian,
        'show':gameRound.winloseDetail.showMulti,
        'base':gameRound.winloseDetail.baseCardMulti,
        'call':gameRound.winloseDetail.callMulti,
        'totalMulti':gameRound.winloseDetail.totalMulti,
        'roomMulti':gameRound.roomMulti,
        'dizhu':gameRound.dizhuSeatIndex,
        'dizhuWin':gameRound.winloseDetail.dizhuWin,
        'seats':seats
    }


def replayFromGameRound(userId, videoId, stageName, gameRound):
    return TUPTReplay(videoId, userId,
                      gameRound.roomId,
                      gameRound.roomName,
                      stageName,
                      buildDetails(gameRound),
                      gameRound.timestamp)


def loadReplay(videoId):
    userId, roomId, roomName, stageName, details, timestamp = \
        daobase.executeRePlayCmd('hmget', 'tupt.replay:6:%s' % (videoId),
                                 'userId', 'roomId', 'roomName',
                                 'stageName', 'details', 'ts')
    if ftlog.is_debug():
        ftlog.debug('obsystem.loadReplay',
                    'videoId=', videoId,
                    'userId=', userId,
                    'roomId=', roomId,
                    'roomName=', roomName,
                    'stageName=', stageName,
                    'details=', details,
                    'timestamp=', timestamp)
    if not userId or not roomId or not details:
        return None
    details = strutil.loads(details)
    return TUPTReplay(videoId, userId, roomId, roomName, stageName, details, timestamp)


def saveReplay(replay):
    daobase.executeRePlayCmd('hmset', 'tupt.replay:6:%s' % (replay.videoId),
                             'userId', replay.userId,
                             'roomId', replay.roomId,
                             'roomName', replay.roomName,
                             'stageName', replay.stageName,
                             'details', strutil.dumps(replay.details),
                             'ts', replay.timestamp)
    ftlog.info('obsystem.saveReplay',
               'videoId=', replay.videoId)


def removeReplay(videoId):
    count = daobase.executeRePlayCmd('del', 'tupt.replay:6:%s' % (videoId))
    ftlog.info('obsystem.removeReplay',
               'videoId=', videoId,
               'count=', count)
    return count


def saveVideo(userId, stageName, gameRound):
    videoId = saveVideoData(userId, gameRound)
    replay = replayFromGameRound(userId, videoId, stageName, gameRound)
    saveReplay(replay)
    return replay


def saveVideoData(userId, gameRound):
    if ftlog.is_debug():
        ftlog.debug('obsystem.saveVideoData mode=', gdata.mode(),
                    'in', gdata.RUN_MODE_TINY_TEST, gdata.RUN_MODE_ONLINE, gdata.RUN_MODE_SIMULATION)

    if gdata.mode() in (gdata.RUN_MODE_TINY_TEST, gdata.RUN_MODE_ONLINE, gdata.RUN_MODE_SIMULATION):
        return saveVideoDataToCDN(userId, gameRound)
    else:
        return saveVideoDataToHttp(userId, gameRound)
    
    
def calcPath(videoId):
    filePath = '%s.json' % (videoId)
    m = hashlib.md5()
    names = []
    for _ in xrange(3):
        m.update(filePath)
        name = str(int(m.hexdigest()[-3:], 16) % 1024)
        filePath = name + '/' + filePath
        names.append(name)
    return filePath


def saveVideoDataToHttp(userId, gameRound):
    # 调用http
    videoId = '%s_%s' % (userId, gameRound.roundId)
    url = '%s/dizhu/tupt/replay/video/save?videoId=%s' % (gdata.httpGame(), videoId)
    gameRoundDict = GameRoundCodecDictReplay().encode(gameRound)
    gameRoundDict['uid'] = userId

    if ftlog.is_debug():
        ftlog.debug('obsystem.saveVideoDataToHttp userId=', userId,
                    'videoId=', videoId,
                    'url=', url,
                    'gameRoundDict=', gameRoundDict)

    response = None
    try:
        _, response = http.runHttp('POST', url, None, strutil.dumps(gameRoundDict), 3, 6)
        datas = strutil.loads(response)
        ec = datas.get('ec', 0)
        if ec == 0:
            return videoId
        raise TYBizException(ec, datas.get('info', ''))
    except TYBizException:
        raise
    except:
        ftlog.error(url, 'response=', response)
        raise TYBizException(-1, '保存失败')


def saveVideoDataToCDN(userId, gameRound):
    videoId = '%s_%s' % (userId, gameRound.roundId)
    gameRoundDict = GameRoundCodecDictReplay().encode(gameRound)
    gameRoundDict['uid'] = userId
    uploadPath = 'dizhu/tupt/replay/videos/' + calcPath(videoId)

    if ftlog.is_debug():
        ftlog.debug('obsystem.saveVideoDataToCDN userId=', userId,
                    'videoId=', videoId,
                    'path=', uploadPath,
                    'gameRoundDict=', gameRoundDict)

    upurl = None
    try:
        upurl = random.choice(_uploadUrls)
        ec, info = uploader.uploadVideo(upurl, _uploadToken, 'cdn37/' + uploadPath, strutil.dumps(gameRoundDict))
        if ec == 0:
            return videoId
        raise TYBizException(ec, info)
    except TYBizException:
        raise
    except:
        ftlog.error('obsystem.saveVideoDataToCDN',
                    'userId=', userId,
                    'videoId=', videoId,
                    'url=', upurl,
                    'path=', uploadPath)
        raise TYBizException(-1, '保存失败')


def buildVideoDataUrl(videoId):
    return gdata.httpDownload() + '/dizhu/tupt/replay/videos/' + calcPath(videoId)


class MatchInfo(object):
    def __init__(self, matchId):
        self.matchId = matchId
        self.curId = None
        self.histories = []
    
    def matchingStart(self, matchingId):
        self.curId = matchingId
        self.histories.append(matchingId)
        
    def fromDict(self, d):
        self.curId = d.get('cur', '')
        self.histories = d.get('histories', [])
        if not isstring(self.curId):
            raise TYBizException(-1, 'Bad matchInfo.curId:%s for %s' % (d, self.matchId))
        if not isinstance(self.histories, list):
            raise TYBizException(-1, 'Bad matchInfo.histories:%s for %s' % (d, self.matchId))
        return self
    
    def toDict(self):
        d = {}
        if self.curId:
            d['cur'] = self.curId
        if self.histories:
            d['histories'] = self.histories
        return d


def loadMatchInfo(matchId):
    jstr = None
    try:
        jstr = daobase.executeRePlayCmd('hget', 'tupt.match.info:6', matchId)
        if ftlog.is_debug():
            ftlog.debug('obsystem.loadMatchInfo',
                        'matchId=', matchId,
                        'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            return MatchInfo(matchId).fromDict(d)
    except:
        ftlog.error('obsystem.loadMatchInfo',
                    'matchId=', matchId,
                    'jstr=', jstr)
    return MatchInfo(matchId)


def saveMatchInfo(matchInfo):
    d = matchInfo.toDict()
    jstr = strutil.dumps(d)
    if ftlog.is_debug():
        ftlog.debug('obsystem.saveMatchInfo',
                    'matchId=', matchInfo.matchId,
                    'jstr=', jstr)
    daobase.executeRePlayCmd('hset', 'tupt.match.info:6', matchInfo.matchId, jstr)


def _reloadConf():
    global _replayMatchs
    global _uploadToken
    global _uploadUrls
    global _obSwitch
    
    conf = configure.getGameJson(6, 'tupt.ob', {})
    replayMatchs = {}
    for matchInfo in conf.get('matchs', []):
        matchId = matchInfo.get('matchId')
        if not isinstance(matchId, int):
            raise TYBizConfException(matchInfo, 'matchId must be int')
        if matchId in replayMatchs:
            raise TYBizConfException(matchInfo, 'Duplicate matchId')
        
        startStageIndex = matchInfo.get('startStageIndex')
        if startStageIndex and not isinstance(startStageIndex, int):
            raise TYBizConfException(matchInfo, 'startStageIndex must be int')
        
        startRank = matchInfo.get('startRank')
        if startRank and not isinstance(startRank, int):
            raise TYBizConfException(matchInfo, 'startRank must be int')

        conditions = matchInfo.get('condition')
        if conditions and not isinstance(conditions, dict):
            raise TYBizConfException(matchInfo, 'condiction must be dict')

        historyLen = matchInfo.get('historyLen')
        if historyLen and not isinstance(historyLen, int):
            raise TYBizConfException(matchInfo, 'historyLen must be int')

        stageName = matchInfo.get('stageName')
        if stageName and not isstring(stageName):
            raise TYBizConfException(matchInfo, 'stageName must be string')

        replayMatchs[matchId] = matchInfo

    uploadUrls = conf.get('uploadUrls', [])
    if not uploadUrls:
        raise TYBizConfException(uploadUrls, 'uploadUrls must be not empty list')
    
    uploadToken = conf.get('uploadToken')
    if not uploadToken or not isstring(uploadToken):
        raise TYBizConfException(conf, 'uploadToken must be not empty string')

    obSwitch = conf.get('open', 0)

    _uploadUrls = uploadUrls
    _uploadToken = uploadToken
    _replayMatchs = replayMatchs
    _obSwitch = obSwitch
    ftlog.info('obsystem._reloadConf successed',
               'switch=', _obSwitch,
               'matchIds=', _replayMatchs.keys(),
               'uploadToken=', _uploadToken,
               'uploadUrls=', _uploadUrls)


def _onConfChanged(event):
    global _inited
    if _inited and event.isChanged(['game:6:tupt.ob:0']):
        ftlog.info('obsystem._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.info('obsystem initialize begin')
    from dizhu.game import TGDizhu
    global _inited
    if not _inited:
        _inited = True
        TGDizhu.getEventBus().subscribe(MatchingStartEvent, onMatchingStart)
        TGDizhu.getEventBus().subscribe(MatchingFinishEvent, onMatchingFinish)
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.info('obsystem initialize end')


def addReplayToRank(matchingId, replay):
    multi = replay.details.get('totalMulti', 1)
    daobase.executeRePlayCmd('zadd', 'tupt.replayRank:6:%s' % (matchingId), -multi, replay.videoId)
    daobase.executeRePlayCmd('zrem', 'tupt.replayRank:6:%s' % (matchingId), 10, -1)


def getReplayRank(matchingId, start, end):
    replays = []
    videoIds = daobase.executeRePlayCmd('zrange', 'tupt.replayRank:6:%s' % (matchingId), start, end)
    for videoId in videoIds:
        replay = loadReplay(videoId)
        if replay:
            replays.append(replay)
    return replays


def removeVideos(matchId, matchingId):
    ftlog.info('obsystem._removeVideos',
               'matchId=', matchId,
               'matchingId=', matchingId)
    
    count = 20
    videoIds = daobase.executeRePlayCmd('lrange', 'tupt.replayList:6:%s' % (matchingId), 0, count - 1)
    while videoIds:
        for videoId in videoIds:
            removeReplay(videoId)
        if len(videoIds) < count:
            break
        videoIds = daobase.executeRePlayCmd('lrange', 'tupt.replayList:6:%s' % (matchingId), 0, count - 1)

    daobase.executeRePlayCmd('del', 'tupt.replayList:6:%s' % (matchingId))
    daobase.executeRePlayCmd('del', 'tupt.replayRank:6:%s' % (matchingId))


def getReplayMatchs():
    return _replayMatchs


def getReplaysTotalCount(matchingId):
    return daobase.executeRePlayCmd('llen', 'tupt.replayList:6:%s' % (matchingId))
    
    
def getReplays(matchingId, start, end):
    replays = []
    videoIds = daobase.executeRePlayCmd('lrange', 'tupt.replayList:6:%s' % (matchingId), start, end)
    for videoId in videoIds:
        replay = loadReplay(videoId)
        if replay:
            replays.append(replay)
    return replays


def getCurMatchingId(matchId):
    matchInfo = loadMatchInfo(matchId)
    return matchInfo.curId if matchInfo else None
    

def _onMatchingStart(matchId, matchingId):
    if not _obSwitch:
        return

    ftlog.info('obsystem.onMatchingStart',
               'matchId=', matchId,
               'matchingId=', matchingId)
    info = loadMatchInfo(matchId)
    info.matchingStart(matchingId)

    confInfo = getReplayMatchs().get(matchId)
    historyLen = confInfo.get('historyLen', 3) if confInfo else 3

    removeCount = max(0, len(info.histories) - historyLen)
    if removeCount > 0:
        removeList = info.histories[0:removeCount]
        info.histories = info.histories[removeCount:]
        daobase.executeRePlayCmd('lpush', 'tupt.match.expiresList:6:%s' % (matchId), *removeList)
    saveMatchInfo(info)


def onMatchingStart(event):
    _onMatchingStart(event.matchId, event.matchingId)
    

def removeMatchings(matchId):
    if not _obSwitch:
        return
    ftlog.info('obsystem._removeMatchings matchId=', matchId)
    matchingId = daobase.executeRePlayCmd('rpop', 'tupt.match.expiresList:6:%s' % (matchId))
    while matchingId:
        removeVideos(matchId, matchingId)
        matchingId = daobase.executeRePlayCmd('rpop', 'tupt.match.expiresList:6:%s' % (matchId))

def removeTableMatchings(matchId):
    info = getReplayMatchs().get(matchId)
    confHistoryLen = info.get('historyLen', 3) if info else 3

    matchingLen = daobase.executeRePlayCmd('llen', 'tupt.match.expiresList:6:%s' % (matchId))
    if matchingLen > confHistoryLen:
        matchingId = daobase.executeRePlayCmd('rpop', 'tupt.match.expiresList:6:%s' % (matchId))
        while matchingId:
            if ftlog.is_debug():
                ftlog.debug('obsystem._removeTableMatchings', 'matchId=', matchId,
                            'matchingId=', matchingId,
                            'confHistoryLen=', confHistoryLen)
            removeVideos(matchId, matchingId)
            matchingId = daobase.executeRePlayCmd('rpop', 'tupt.match.expiresList:6:%s' % (matchId))


def onMatchingFinish(event):
    ftlog.info('obsystem.onMatchingFinish',
               'matchId=', event.matchId,
               'matchingId=', event.matchingId)

    FTTimer(0, functools.partial(removeMatchings, event.matchId))


def _getMinRank(matchTableInfo):
    minUserId = None
    minRank = None
    for seatInfo in matchTableInfo['seats']:
        seatRank = seatInfo['rank']
        if minRank is None or seatRank < minRank:
            minUserId = seatInfo['userId']
            minRank = seatRank
    return minUserId, minRank


def _saveGameRound(matchId, matchingId, userId, stageName, gameRound):
    if ftlog.is_debug():
        ftlog.debug('obsystem._saveGameRound',
                    'matchId=', matchId,
                    'matchingId=', matchingId,
                    'userId=', userId,
                    'stageName=', stageName,
                    'roundId=', gameRound.roundId)
    replay = saveVideo(userId, stageName, gameRound)
    daobase.executeRePlayCmd('lpush', 'tupt.replayList:6:%s' % (matchingId), replay.videoId)
    addReplayToRank(matchingId, replay)
    ftlog.info('obsystem._saveGameRound',
               'matchId=', matchId,
               'matchingId=', matchingId,
               'userId=', userId,
               'stageName=', stageName,
               'videoId=', replay.videoId)


def _checkSaveGameRound(table):
    matchTableInfo = table.matchTableInfo
    matchId = matchTableInfo.get('matchId')
    stageIndex = matchTableInfo.get('step', {}).get('stageIndex')
    info = getReplayMatchs().get(matchId)
    if info and stageIndex >= info['startStageIndex']:
        minUserId, minRank = _getMinRank(matchTableInfo)
        if minRank <= info['startRank']:
            return True, minUserId, minRank
    return False, 0, -1


def _checkSaveCoinTableGameRound(table, result):
    mixRoomId = _getMixRoomId(table, result)
    bigRoomId = mixRoomId or gdata.getBigRoomId(table.roomId)
    info = getReplayMatchs().get(bigRoomId)

    if ftlog.is_debug():
        ftlog.debug('obsystem._checkSaveCoinTableGameRound',
                    'roomId=', table.roomId,
                    'bigRoomId=', bigRoomId,
                    'info=', info)

    condition = info.get('condiction') if info else None
    if condition:
        totalMulti = condition.get('totalMulti')
        chuntian = condition.get('chuntian')
        isSlam = condition.get('slam')
        stageName = info.get('stageName', '')

        if ftlog.is_debug():
            ftlog.debug('obsystem._checkSaveCoinTableGameRound condiction=', condition,
                        'multi=', totalMulti, 'result.multi=', result.baseScore,
                        'dizhu.mulit=', result.dizhuStatement.seat.status.totalMulti,
                        'chuntian=', chuntian, 'result.chuntian=', result.isChuntian,
                        'isSlam=', isSlam, 'result.winslam=', result.slam,
                        'userId=', result.dizhuStatement.seat.userId if result.dizhuStatement else 'gameAbort')

        if not result.dizhuStatement:
            # 流局不保存
            return False, 0, ''
        if isSlam and not result.slam:
            return False, 0, ''
        if chuntian and not result.isChuntian:
            return False, 0, ''
        if totalMulti and totalMulti > result.dizhuStatement.seat.status.totalMulti:
            return False, 0, ''

        _onMatchingStart(bigRoomId, str(table.tableId) + str(result.dizhuStatement.seat.userId))

        return True, result.dizhuStatement.seat.userId, stageName

    return False, 0, ''


def _getMixRoomId(table, result):
    if not result.dizhuStatement:
        return None
    return result.dizhuStatement.seat.player.mixConf.get('roomId') if table.room.roomConf.get('isMix') else None


def _onGameRoundOverOrAbort(event):
    if not _obSwitch:
        return

    from dizhu.games.normal.table import DizhuTableNormal
    from dizhu.games.groupmatch.table import DizhuTableGroupMatch
    from dizhu.games.mix.table import DizhuTableMix

    if isinstance(event.table, DizhuTableNormal) or isinstance(event.table, DizhuTableMix):
        # 流局不保存
        if not event.gameResult.dizhuStatement:
            return

        needSave, userId, stageName = _checkSaveCoinTableGameRound(event.table, event.gameResult)
        if ftlog.is_debug():
            ftlog.debug('obsystem._onGameRoundOverOrAbort coinTable',
                        'tableId=', event.table.tableId,
                        'needSave=', needSave,
                        'userId=', userId,
                        'stageName=', stageName)
        if needSave:
            tableCtrl = event.table.room.maptable.get(event.table.tableId)
            if tableCtrl and tableCtrl.replay.curRound:
                mixRoomId = _getMixRoomId(event.table, event.gameResult)
                matchId = mixRoomId or gdata.getBigRoomId(event.table.roomId)
                matchingId = str(event.table.tableId) + str(userId)

                if mixRoomId:
                    # 混房结算金币飘屏处理
                    dizhuSeat = event.gameResult.dizhuStatement
                    ops = tableCtrl.replay.curRound.ops

                    from dizhucomm.replay.gameround import GameWinloseOp
                    if isinstance(ops[-1], GameWinloseOp):
                        for seatWinloseDetail in ops[-1].winloseDetail.seatWinloseDetails:
                            if seatWinloseDetail.deltaChip != dizhuSeat.delta:
                                seatWinloseDetail.deltaChip = -dizhuSeat.delta / 2

                FTTimer(0, functools.partial(_saveGameRound, matchId, matchingId, userId, stageName, tableCtrl.replay.curRound))
                FTTimer(0, functools.partial(removeTableMatchings, matchId))

                if ftlog.is_debug():
                    ftlog.debug('obsystem._onGameRoundOverOrAbort infos',
                                'matchId=', matchId,
                                'mixRoomId=', mixRoomId,
                                'matchingId=', matchingId,
                                'userId=', userId,
                                'stageName=', stageName,
                                'gameRoundDict=', GameRoundCodecDictReplay().encode(tableCtrl.replay.curRound))


    elif isinstance(event.table, DizhuTableGroupMatch):
        needSave, userId, rank = _checkSaveGameRound(event.table)
        if ftlog.is_debug():
            ftlog.debug('obsystem._onGameRoundOverOrAbort',
                        'tableId=', event.table.tableId,
                        'needSave=', needSave,
                        'userId=', userId,
                        'rank=', rank)

        if needSave:
            tableCtrl = event.table.room.maptable.get(event.table.tableId)
            if tableCtrl.replay.curRound:
                matchTableInfo = event.table.matchTableInfo
                matchId = matchTableInfo.get('matchId')
                matchingId = matchTableInfo.get('matchingId')
                stageName = matchTableInfo.get('step', {}).get('name')
                FTTimer(0, functools.partial(_saveGameRound, matchId, matchingId, userId, stageName, tableCtrl.replay.curRound))

def setupTable(table):
    if ftlog.is_debug():
        ftlog.debug('obsystem.setupTable tableId=', table.tableId)
    table.on(GameRoundOverEvent, _onGameRoundOverOrAbort)
    table.on(GameRoundAbortEvent, _onGameRoundOverOrAbort)


