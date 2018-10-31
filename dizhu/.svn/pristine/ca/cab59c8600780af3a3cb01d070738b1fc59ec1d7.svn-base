# -*- coding:utf-8 -*-
'''
Created on 2016年8月15日

@author: zhaojiangang
'''
from datetime import datetime
import hashlib
import random
from sre_compile import isstring

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.replay import uploader
from dizhucomm.replay.codec import GameRoundCodecDictReplay
from freetime.aio import http
import freetime.util.log as ftlog
from hall.entity import hallshare
from hall.entity.todotask import TodoTaskHelper
from poker.entity.biz.exceptions import TYBizException, TYBizConfException
from poker.entity.configure import gdata, configure
from poker.entity.dao import daobase
from poker.entity.dao.daobase import executeRePlayCmd
from poker.entity.events.tyevent import EventConfigure, EventHeartBeat, \
    UserEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil, webpage
import poker.util.timestamp as pktimestamp


_inited = False
_shareType2ShareIds = {}
_shareDesc = ''
_uploadToken = ''
_uploadUrls = ''
_myListLimit = 100
_defaultTips = '超及精彩的斗地主对决'
_keepCount = 7
_maxTop = 200
_displayTopN = 10

_replay_view_script = '''
    local videoId = KEYS[1]
    local replayKey = KEYS[2]
    local topnKey = KEYS[3]
    local maxCount = tonumber(KEYS[4])
    local addTop = tonumber(KEYS[5])
    local issueNum = KEYS[6]
    local vc = redis.call('hincrby', replayKey, 'viewsCount', 1)
    local curViewsCount = 0
    local lastViewIssueNum = redis.call('hget', replayKey, 'lastViewIssueNum')
    if lastViewIssueNum ~= issueNum then
        -- 重置观看次数和期号
        curViewsCount = 1
        redis.call('hmset', replayKey, 'curViewsCount', curViewsCount, 'lastViewIssueNum', issueNum)
    else
        -- 增加观看次数
        curViewsCount = redis.call('hincrby', replayKey, 'curViewsCount', 1)
    end
    if addTop == 1 then
        redis.call('zadd', topnKey, curViewsCount, videoId)
        local count = redis.call('zcard', topnKey)
        if count > maxCount then
            redis.call('zremrangebyrank', topnKey, 0, 0)
        end
    end
    return {vc, curViewsCount}
'''

_replay_view_alias = 'replay.replay_view'

_replay_add_mine_script = '''
    local videoId = KEYS[1]
    local mineKey = KEYS[2]
    local maxCount = tonumber(KEYS[3])
    local count = redis.call('lpush', mineKey, videoId)
    if count > maxCount then
        local ret = redis.call('rpop', mineKey)
        return {ret}
    end
    return nil
'''

_replay_add_mine_alias = 'replay.replay_add_mine'

class ReplayViewEvent(UserEvent):
    '''
    叫地主阶段, 玩家叫地主
    '''
    def __init__(self, gameId, userId, videoId):
        super(ReplayViewEvent, self).__init__(userId, gameId)
        self.videoId = videoId
        
class Replay(object):
    def __init__(self, videoId, userId, roomId, roomName, details, timestamp, viewsCount,
                 likesCount, lastTopIssueNum='', topnCount=0, lastViewIssueNum='', curViewsCount=0):
        self.videoId = videoId
        self.userId = userId
        self.roomId = roomId
        self.roomName = roomName
        self.details = details
        self.timestamp = timestamp
        self.viewsCount = viewsCount
        self.likesCount = likesCount
        # 最后一次上榜期号
        self.lastTopIssueNum = lastTopIssueNum
        # 连续上榜次数
        self.topnCount = topnCount
        # 最后一次观看期号
        self.lastViewIssueNum = lastViewIssueNum
        # 最后一期观看次数
        self.curViewsCount = curViewsCount
        
    def findWinloseSeatByUserId(self, userId):
        for seat in self.details['seats']:
            if seat['uid'] == userId:
                return seat
        return None
    
def buildReplayKey(videoId):
    return 'replay.info:6:%s' % (videoId)

def buildTopnKey(issueNumber):
    return 'replay.topn:6:%s' % (issueNumber)

def buildManualTopnKey():
    return 'replay.manual.topn:6'

def buildMyListKey(userId):
    return 'replay.myList:6:%s' % (userId)

def buildUserReplayKey(userId):
    return 'replay:6:%s' % (userId)

def addMine(userId, videoId, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    videoIds = daobase.executeUserLua(userId, _replay_add_mine_alias, 3,
                                      videoId,
                                      buildMyListKey(userId),
                                      _myListLimit)
    if videoIds:
        # 删除超限的视频
        for toRemoveVideoId in videoIds:
            removeReplay(toRemoveVideoId)
    
def getLastView(userId):
    lastView = daobase.executeUserCmd(userId, 'hget', buildUserReplayKey(userId), 'lastView') or 0
    if ftlog.is_debug():
        ftlog.debug('replay_service.getLastView userId=',
                    'userId=', userId,
                    'lastView=', lastView)
    return lastView

def setLastView(userId, timestamp):
    if ftlog.is_debug():
        ftlog.debug('replay_service.setLastView userId=',
                    'userId=', userId,
                    'lastView=', timestamp)
    daobase.executeUserCmd(userId, 'hset', buildUserReplayKey(userId), 'lastView', timestamp)

def getMine(userId, timestamp=None):
    ret = []
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    videoIds = daobase.executeUserCmd(userId, 'lrange', buildMyListKey(userId), 0, -1)
    if ftlog.is_debug():
        ftlog.debug('replay_service.getMine userId=', userId,
                    'videoIds=', videoIds)
    if videoIds:
        for videoId in videoIds:
            replay = loadReplay(videoId)
            if replay:
                ret.append(replay)
    return ret

def removeMine(userId, videoId):
    count = daobase.executeUserCmd(userId, 'lrem', buildMyListKey(userId), 1, videoId)
    if count > 0:
        replay = loadReplay(videoId)
        if replay and replay.userId == userId:
            removeReplay(videoId)
            ftlog.info('replay_service.removeMine userId=', userId,
                       'videoId=', videoId)
            return True
    return False
    
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

def _replayFromGameRound(userId, videoId, gameRound):
    return Replay(videoId,
                  userId,
                  gameRound.roomId,
                  gameRound.roomName,
                  buildDetails(gameRound),
                  gameRound.timestamp, 0, 0)

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

def buildVideoDataUrl(videoId):
    return gdata.httpDownload() + '/dizhu/replay/videos/' + calcPath(videoId)

def saveVideoData(userId, gameRound):
    if gdata.mode() in (gdata.RUN_MODE_ONLINE, gdata.RUN_MODE_SIMULATION):
        return saveVideoDataToCDN(userId, gameRound)
    else:
        return saveVideoDataToHttp(userId, gameRound)
    
def saveVideoDataToHttp(userId, gameRound):
    # 调用http
    videoId = '%s_%s' % (userId, gameRound.roundId)
    url = '%s/replay/video/save?videoId=%s' % (gdata.httpGame(), videoId)
    gameRoundDict = GameRoundCodecDictReplay().encode(gameRound)
    gameRoundDict['uid'] = userId
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
    # 调用http
    videoId = '%s_%s' % (userId, gameRound.roundId)
    gameRoundDict = GameRoundCodecDictReplay().encode(gameRound)
    gameRoundDict['uid'] = userId
    try:
        uploadPath = 'dizhu/replay/videos/' + calcPath(videoId)
        upurl = random.choice(_uploadUrls)
        ec, info = uploader.uploadVideo(upurl, _uploadToken, 'cdn37/' + uploadPath, strutil.dumps(gameRoundDict))
        if ec == 0:
            return videoId
        raise TYBizException(ec, info)
    except TYBizException:
        raise
    except:
        raise TYBizException(-1, '保存失败')
        
def removeVideoData(videoId):
    url = '%s/replay/video/remove' % (gdata.httpGame())
    response = None
    try:
        _, response = webpage.webgetJson(url, {'videoId':videoId}, timeout=3)
    except:
        ftlog.error(url, 'response=', response)
        
def loadVideoData(videoId):
    url = '%s/replay/video/load' % (gdata.httpGame())
    datas = None
    try:
        datas, _ =  webpage.webgetJson(url, {'videoId':videoId}, timeout=3)
        if ftlog.is_debug():
            ftlog.debug('replay_service.loadVideoData videoId=', videoId,
                        'datas=', datas)
        ec = datas.get('ec', 0)
        if ec == 0:
            return strutil.loads(datas.get('data'))
        return None
    except:
        ftlog.error(url, 'datas=', datas)
        return None
        
def saveVideo(userId, gameRound):
    try:
        videoId = saveVideoData(userId, gameRound)
        # 保存replay
        replay = _replayFromGameRound(userId, videoId, gameRound)
        addReplay(replay, pktimestamp.getCurrentTimestamp())
        ftlog.info('replay_service.saveVideo Succ userId=', userId,
                   'roundId=', gameRound.roundId,
                   'videoId=', videoId)
    except:
        ftlog.error('replay_service.saveVideo Fail userId=', userId,
                    'roundId=', gameRound.roundId)
        
def removeVideo(userId, videoId):
    # 删除replay
    removeMine(userId, videoId)
    
    # 删除牌局数据和网页观看代码
    #removeVideoData(videoId)

#     replay = Replay(roundId, userId, gameRound.roomId, gameRound.roomName, buildDetails(gameRound), timestamp, 0, 0)
def addReplay(replay, timestamp):
    daobase.executeRePlayCmd('hmset', buildReplayKey(replay.videoId),
                             'userId', replay.userId,
                             'roomId', replay.roomId,
                             'roomName', replay.roomName,
                             'details', strutil.dumps(replay.details),
                             'viewsCount', replay.viewsCount,
                             'likesCount', replay.likesCount,
                             'ts', replay.timestamp,
                             'lastTopIssueNum', replay.lastTopIssueNum,
                             'topnCount', replay.topnCount,
                             'lastViewIssueNum', replay.lastViewIssueNum,
                             'curViewsCount', replay.curViewsCount)
    addMine(replay.userId, replay.videoId)
    ftlog.info('replay_service.addReplay videoId=', replay.videoId,
               'userId=', replay.userId,
               'roomId=', replay.roomId,
               'roomName=', replay.roomName,
               'details=', replay.details,
               'timestamp=', replay.timestamp,
               'lastTopIssueNum=', replay.lastTopIssueNum,
               'topnCount=', replay.topnCount,
               'lastViewIssueNum=', replay.lastViewIssueNum,
               'curViewsCount=', replay.curViewsCount)
    return replay

def loadReplay(videoId):
    userId, roomId, roomName, details, timestamp, viewsCount, likesCount, lastTopIssueNum, \
    topnCount, lastViewIssueNum, curViewsCount = daobase.executeRePlayCmd('hmget', buildReplayKey(videoId),
                                                                          'userId', 'roomId', 'roomName',
                                                                          'details', 'ts', 'viewsCount',
                                                                          'likesCount', 'lastTopIssueNum',
                                                                          'topnCount', 'lastViewIssueNum',
                                                                          'curViewsCount')
    if ftlog.is_debug():
        ftlog.debug('replay_service.loadReplay videoId=', videoId,
                    'userId=', userId,
                    'roomId=', roomId,
                    'roomName=', roomName,
                    'details=', details)
    if not userId or not roomId or not details:
        return None
    lastTopIssueNum = lastTopIssueNum or ''
    lastViewIssueNum = lastViewIssueNum or ''
    topnCount = topnCount or 0
    curViewsCount = curViewsCount or 0
    return Replay(videoId, userId, roomId, roomName,
                  strutil.loads(details), timestamp,
                  int(viewsCount), int(likesCount),
                  str(lastTopIssueNum), int(topnCount),
                  str(lastViewIssueNum), int(curViewsCount))

def getTopnInfo(videoId):
    lastTopIssueNum, topnCount = daobase.executeRePlayCmd('hmget', buildReplayKey(videoId), 'lastTopIssueNum', 'topnCount')
    lastTopIssueNum = lastTopIssueNum or ''
    topnCount = topnCount or 0
    return str(lastTopIssueNum), topnCount

def setTopnInfo(videoId, lastTopIssueNum, topnCount):
    daobase.executeRePlayCmd('hmset', buildReplayKey(videoId),
                             'lastTopIssueNum', lastTopIssueNum,
                             'topnCount', int(topnCount))
    
def removeReplay(videoId):
    # 删除replay
    daobase.executeRePlayCmd('del', buildReplayKey(videoId))
    ftlog.info('replay_service.removeReplay videoId=', videoId)
    
def view(videoId, userId, timestamp=None):
    replay = loadReplay(videoId)
    if not replay:
        if ftlog.is_debug():
            ftlog.info('replay_service.view videoId=', videoId,
                       'userId=', userId)
        raise TYBizException(-1, '没有找到该视频')
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    issueNum = getIssueNumber(timestamp)
    viewsCount, curViewCount = daobase.executeRePlayLua(_replay_view_alias, 6,
                                                        videoId,
                                                        buildReplayKey(videoId),
                                                        buildTopnKey(issueNum),
                                                        _maxTop,
                                                        1 if replay.topnCount < 2 else 0,
                                                        issueNum)
    curViewCount = curViewCount or 0
    ftlog.info('replay_service.view videoId=', videoId,
               'userId=', userId,
               'issueNum=', issueNum,
               'viewsCount=', viewsCount,
               'topnCount=', replay.topnCount,
               'curViewCount=', curViewCount)
    replay.viewsCount = int(viewsCount)
    replay.lastViewIssueNum = issueNum
    replay.curViewsCount = int(curViewCount)
    return replay

def like(videoId, userId):
    replay = loadReplay(videoId)
    if not replay:
        raise TYBizException(-1, '没有找到该视频')
    
    likesCount = daobase.executeRePlayCmd('hincrby', buildReplayKey(videoId), 'likesCount', 1)
    ftlog.info('replay_service.like videoId=', videoId,
               'userId=', userId,
               'replay.likesCount=', replay.likesCount,
               'likesCount=', likesCount)
    replay.likesCount = likesCount
    return replay

def unlike(videoId, userId):
    replay = loadReplay(videoId)
    if not replay:
        raise TYBizException(-1, '没有找到该视频')
    likesCount = daobase.executeRePlayCmd('hincrby', buildReplayKey(videoId), 'likesCount', -1)
    ftlog.info('replay_service.unlike videoId=', videoId,
               'userId=', userId,
               'replay.likesCount=', replay.likesCount,
               'likesCount=', likesCount)
    replay.likesCount = likesCount
    return replay

def getIssueNumber(timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d')

def getTopN(issueNum, topn):
    return daobase.executeRePlayCmd('zrevrange', buildTopnKey(issueNum), 0, topn - 1)

def getTopNWithViewsCount(issueNum, topn):
    return daobase.executeRePlayCmd('zrevrange', buildTopnKey(issueNum), 0, topn - 1, 'WITHSCORES')

def removeFromTopn(issueNum, videoId):
    return daobase.executeRePlayCmd('zrem', buildTopnKey(issueNum), videoId)

def setManualTopN(videoIdList):
    ftlog.info('replay_service.setManualTopN videoIdList=', videoIdList)
    daobase.executeRePlayCmd('del', buildManualTopnKey())
    if videoIdList:
        vids = []
        for vid in videoIdList:
            vids.append(vid.strip())
        daobase.executeRePlayCmd('set', buildManualTopnKey(), ','.join(vids))

def getManualTopN(n):
    if n <= 0:
        n = _displayTopN
    n = min(n, 100)
    topnStr = daobase.executeRePlayCmd('get', buildManualTopnKey())
    if not topnStr:
        return []
    return topnStr.split(',')

def getTopNReplayWithViewsCount(issueNum, n):
    ret = []
    datas = getTopNWithViewsCount(issueNum, n)
    for i in xrange(len(datas) / 2):
        vid = datas[i * 2]
        viewsCount = int(datas[i * 2 + 1])
        replay = loadReplay(vid)
        if replay:
            ret.append((replay, viewsCount))
        else:
            ftlog.warn('replay_service.getTopNReplayWithViewsCount',
                       'issueNum=', issueNum,
                       'topn=', n,
                       'vid=', vid,
                       'viewsCount=', viewsCount,
                       'index=', i,
                       'err=', 'LoadReplay')
    return ret

def getTopNReplay(issueNum, n):
    topnIds = getTopN(issueNum, n)
    ret = []
    for vid in topnIds:
        replay = loadReplay(vid)
        if replay:
            ret.append(replay)
        else:
            ftlog.warn('replay_service.getTopNReplay',
                       'issueNum=', issueNum,
                       'topn=', n,
                       'topnIds=', topnIds,
                       'videoId=', vid,
                       'err=', 'LoadReplay')
    return ret

def getDisplayTopNReplay(issueNum):
    vids = []
    manualIds = getManualTopN(_displayTopN)
    topnIds = getTopN(issueNum, _maxTop)
    
    if ftlog.is_debug():
        ftlog.debug('replay_service.getDisplayTopNReplay',
                    'issueNum=', issueNum,
                    'manualTopN=', manualIds,
                    'topn=', topnIds,
                    'issueNum=', issueNum)
    
    # 先去重
    for vid in topnIds:
        if vid not in manualIds:
            vids.append(vid)
    
    for i, vid in enumerate(manualIds):
        vid = vid.strip()
        if vid:
            vids.insert(i, vid)
    
    ret = []
    for vid in vids:
        replay = loadReplay(vid)
        if replay:
            ret.append(replay)
            if len(ret) >= _displayTopN:
                break
        else:
            ftlog.warn('replay_service.getDisplayTopNReplay',
                       'issueNum=', issueNum,
                       'topn=', topnIds,
                       'manualTopN=', manualIds,
                       'videoId=', vid,
                       'err=', 'LoadReplay')
    return ret

def getShareDesc(userId, gameId, clientId):
    return _shareDesc

def getAllShareIds():
    return _shareType2ShareIds.values()

def share(userId, gameId, videoId, shareType):
    shareId = _shareType2ShareIds.get(shareType)
    if shareId is None:
        ftlog.error('replay_service.share UnknownShareType userId=', userId,
                    'gameId=', gameId,
                    'videoId=', videoId,
                    'shareType=', shareType)
        raise TYBizException(-1, '不支持的分享类型')
    
    share = hallshare.findShare(shareId)
    if not share:
        ftlog.error('replay_service.share NoShare userId=', userId,
                    'gameId=', gameId,
                    'videoId=', videoId,
                    'shareType=', shareType)
        raise TYBizException(-1, '不支持的分享')

    replay = loadReplay(videoId)
    if not replay:
        ftlog.warn('replay_service.share NoReplay userId=', userId,
                   'gameId=', gameId,
                   'videoId=', videoId,
                   'shareType=', shareType)
        raise TYBizException(-1, '视频已被删除')
    
    seat = replay.findWinloseSeatByUserId(replay.userId)
    params = {
        'videoId':videoId,
        'totalMulti':replay.details.get('totalMulti', 1),
        'bombCount':replay.details.get('nbomb', 0),
        'deltaChip':seat.get('dChip', 0) if seat else 0
    }
    todotask = share.buildTodotask(DIZHU_GAMEID, userId, 'replay', params)
    title = todotask.getParam('title', '')
    desc = todotask.getParam('des', '')
    todotask.setParam('title', strutil.replaceParams(title, params))
    todotask.setParam('des', strutil.replaceParams(desc, params))
    return TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, todotask)
    
def processTopN(timestamp=None):
    try:
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        # 处理前一天的排行榜，看是否连续上榜了
        issueNum = getIssueNumber(timestamp - 86400)
        # 删除7天前的排行榜数据，最少保留7天
        removeTopnKey = buildTopnKey(getIssueNumber(timestamp - 86400 * max(7, _keepCount)))
        
        executeRePlayCmd('del', removeTopnKey)
        
        topnIds = getTopN(issueNum, _displayTopN)
        if ftlog.is_debug():
            ftlog.debug('replay_service.processTopN timestamp=', pktimestamp.timestamp2timeStr(timestamp),
                        'issueNum=', issueNum,
                        'removeTopnKey=', removeTopnKey,
                        'topnIds=', topnIds)
        for videoId in topnIds:
            lastTopIssueNum, topnCount = getTopnInfo(videoId)
            if lastTopIssueNum == issueNum:
                # 已经处理过了
                continue
            if lastTopIssueNum == getIssueNumber( timestamp - 86400 * 2):
                newTopnCount = topnCount + 1
            else:
                newTopnCount = 1
            setTopnInfo(videoId, issueNum, newTopnCount)
            ftlog.info('replay_service.processTopN timestamp=', pktimestamp.timestamp2timeStr(timestamp),
                       'issueNum=', issueNum,
                       'videoId=', videoId,
                       'lastTopIssueNum=', lastTopIssueNum,
                       'topnCount=', topnCount,
                       'newTopnCount=', newTopnCount,
                       'removeTopnKey=', removeTopnKey)
    except:
        ftlog.error('replay_service.processTopN timestamp=', timestamp)

def _onConfChanged(event):
    if _inited and event.isModuleChanged(['replay']):
        ftlog.info('replay_service._onConfChanged')
        _reloadConf()

def _reloadConf():
    global _myListLimit
    global _shareType2ShareIds
    global _uploadUrls
    global _uploadToken
    global _shareDesc
    
    conf = configure.getGameJson(DIZHU_GAMEID, 'replay', {}, configure.DEFAULT_CLIENT_ID)
    myListLimit = conf.get('myListLimit', 100)
    shareType2ShareIds = {}
    if not isinstance(myListLimit, int) or myListLimit <= 0:
        raise TYBizConfException(conf, 'replay.myListLimit must be int > 0')
    for share in conf.get('shares', []):
        shareType = share.get('type')
        if not shareType or not isstring(shareType):
            raise TYBizConfException(conf, 'replay.shares.item.type must be string')
        shareId = share.get('shareId')
        if not isinstance(shareId, int):
            raise TYBizConfException(conf, 'replay.shares.item.shareId must be int')
        shareType2ShareIds[shareType] = shareId
    
    shareDesc = conf.get('shareDesc', '')
    if not isstring(shareDesc):
        raise TYBizConfException(conf, 'replay.shareDesc must be string')
    
#     uploadUrl = conf.get('uploadUrl')
#     if not uploadUrl or not isstring(uploadUrl):
#         raise TYBizConfException(conf, 'replay.uploadUrl must be string')
 
    uploadUrls = conf.get('uploadUrls')
    if not uploadUrls or not isinstance(uploadUrls, list):
        raise TYBizConfException(conf, 'replay.uploadUrl must be list')

    uploadToken = conf.get('uploadToken')
    if not uploadToken or not isstring(uploadToken):
        raise TYBizConfException(conf, 'replay.uploadToken must be string')
    
    _uploadUrls = uploadUrls
    _uploadToken = uploadToken
    _myListLimit = myListLimit
    _shareType2ShareIds = shareType2ShareIds
    _shareDesc = shareDesc
    ftlog.info('replay_service._reloadConf Succ myListLimit=', myListLimit,
                'shareType2ShareIds=', _shareType2ShareIds,
                'uploadUrls=', _uploadUrls,
                'uploadToken=', _uploadToken,
                'shareDesc=', _shareDesc)

_prevProcessTime = 0
_processInterval = 60 * 10

def _onTimer(evt):
    global _prevProcessTime
    timestamp = pktimestamp.getCurrentTimestamp()
    if ftlog.is_debug():
        ftlog.debug('replay_service._onTimer',
                    'timestamp=', timestamp,
                    '_prevProcessTime=', _prevProcessTime,
                    '_processInterval=', _processInterval,
                    'isSameDay=', pktimestamp.is_same_day(timestamp, _prevProcessTime))
    if (not _prevProcessTime
        or not pktimestamp.is_same_day(timestamp, _prevProcessTime)
        or timestamp - _prevProcessTime > _processInterval):
        _prevProcessTime = timestamp
        processTopN(timestamp)
        
def _initialize():
    global _inited
    if not _inited:
        _inited = True
        daobase.loadLuaScripts(_replay_view_alias, _replay_view_script)
        daobase.loadLuaScripts(_replay_add_mine_alias, _replay_add_mine_script)
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        if gdata.serverType() == gdata.SRV_TYPE_CENTER:
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, _onTimer)
            # 重放排行榜发奖
            from dizhu.replay import replay_ranking_prize_sender
            replay_ranking_prize_sender.initialize()        
        ftlog.info('replay_service._initialize Succ')


