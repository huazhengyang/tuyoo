# -*- coding:utf-8 -*-
'''
Created on 2016年8月22日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.replay import replay_service
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import userdata
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp

    
@markCmdActionHandler
class DizhuReplayHandler(BaseMsgPackChecker):
    def __init__(self):
        super(DizhuReplayHandler, self).__init__()
        
    def _check_param_videoId(self, msg, key, params):
        videoId = msg.getParam(key)
        if not videoId or not isstring(videoId) :
            return 'ERROR of videoId !' + str(videoId), None
        return None, videoId
    
    def _check_param_shareType(self, msg, key, params):
        shareType = msg.getParam('shareType', msg.getParam('type'))
        if not shareType or not isstring(shareType) :
            return 'ERROR of shareType !' + str(shareType), None
        return None, shareType
    
    @classmethod
    def buildDesc(cls, replay):
        nbomb = replay.details.get('nbomb', 0)
        multi = replay.details.get('totalMulti', 1)
        if nbomb < 1:
            return '无炸，%s倍' % (multi)
        return '%s炸，%s倍' % (nbomb, multi)
    
    @classmethod
    def encodeReplayForWonderful(cls, userId, replay):
        seats = []
        for seat in replay.details.get('seats'):
            name = seat.get('name', '')
            headUrl = seat.get('headUrl', '')
            if not name or not headUrl:
                nowName, nowHeadUrl = userdata.getAttrs(seat.get('uid'), ['name', 'purl'])
                if not name:
                    name = nowName
                if not headUrl:
                    headUrl = nowHeadUrl
            seats.append({
                'uid':seat.get('uid'),
                'name':strutil.ensureString(name, ''),
                'img':strutil.ensureString(headUrl, '')
            })
        return {
            'id':replay.videoId,
            'name':replay.roomName,
            'mark':'',
            'desc':cls.buildDesc(replay),
            'views':replay.viewsCount,
            'time':replay.timestamp,
            'dizhuwin':replay.details.get('dizhuWin'),
            'dizhu':replay.details.get('dizhu'),
            'owner':replay.userId,
            'url':'',
            'seats':seats
        }
    
    @classmethod
    def encodeReplaysForWonderful(cls, userId, replays):
        ret = []
        for replay in replays:
            ret.append(cls.encodeReplayForWonderful(userId, replay))
        return ret
    
    @markCmdActionMethod(cmd='dizhu', action='replay_wonderful_list', clientIdVer=0, scope='game')
    def doListWonderful(self, userId, gameId, clientId):
        issueNum = replay_service.getIssueNumber(pktimestamp.getCurrentTimestamp() - 86400)
        self._doListWonderful(userId, gameId, clientId, issueNum)
    
    @classmethod
    def _doListWonderful(self, userId, gameId, clientId, issueNum):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'replay_wonderful_list')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        replays = replay_service.getDisplayTopNReplay(issueNum)
        msg.setResult('videos', self.encodeReplaysForWonderful(userId, replays))
        router.sendToUser(msg, userId)
        return msg
        
    @classmethod
    def encodeReplayForMine(cls, userId, replay, lastView):
        if ftlog.is_debug():
            ftlog.debug('DizhuReplayHandler.encodeReplayForMine userId=', userId,
                        'videoId=', replay.videoId,
                        'createTime=', replay.timestamp,
                        'lastView=', lastView)
        return {
            'id':replay.videoId,
            'name':replay.roomName,
            'time':replay.timestamp,
            'new':1 if replay.timestamp > lastView else 0,
            'url':''
        }
    
    @classmethod
    def encodeReplaysForMine(cls, userId, replays, lastView):
        ret = []
        for replay in replays:
            ret.append(cls.encodeReplayForMine(userId, replay, lastView))
        return ret
    
    @markCmdActionMethod(cmd='dizhu', action='replay_mine_list', clientIdVer=0, scope='game')
    def doMineList(self, userId, gameId, clientId):
        self._doListMine(userId, gameId, clientId)
    
    @classmethod
    def _doListMine(cls, userId, gameId, clientId):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'replay_mine_list')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('shareMsg', replay_service.getShareDesc(userId, gameId, clientId))
        timestamp = pktimestamp.getCurrentTimestamp()
        lastView = replay_service.getLastView(userId)
        replays = replay_service.getMine(userId, timestamp)
        msg.setResult('videos', cls.encodeReplaysForMine(userId, replays, lastView))
        router.sendToUser(msg, userId)
        replay_service.setLastView(userId, timestamp)
        return msg

    @markCmdActionMethod(cmd='dizhu', action='replay_mine_cleanup_tip', clientIdVer=0, scope='game')
    def doMineCleanupTip(self, userId, gameId, clientId):
        self._doMineCleanupTip(userId, gameId, clientId)
        
    @classmethod
    def _doMineCleanupTip(self, userId, gameId, clientId):
        timestamp = pktimestamp.getCurrentTimestamp()
        replay_service.setLastView(userId, timestamp)
        # 不需要返回
        
    @markCmdActionMethod(cmd='dizhu', action='replay_view', clientIdVer=0, scope='game')
    def doView(self, userId, gameId, clientId, videoId):
        self._doView(userId, gameId, clientId, videoId)
        
    @classmethod
    def _doView(cls, userId, gameId, clientId, videoId, timestmap=None):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'replay_view')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        try:
            timestamp = timestmap or pktimestamp.getCurrentTimestamp()
            replay = replay_service.view(videoId, userId, timestamp)
            msg.setResult('video', {'views':replay.viewsCount, 'likes':replay.likesCount, 'url':''})
            msg.setResult('videoUrl', replay_service.buildVideoDataUrl(videoId))
        except TYBizException, e:
            msg.setResult('code', e.errorCode)
            msg.setResult('info', e.message)
        router.sendToUser(msg, userId)
        return msg
        
    @markCmdActionMethod(cmd='dizhu', action='replay_like', clientIdVer=0, scope='game')
    def doLike(self, userId, gameId, clientId, videoId):
        self._doLike(userId, gameId, clientId, videoId)
        
    @classmethod
    def _doLike(cls, userId, gameId, clientId, videoId):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'replay_like')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('videoId', videoId)
        try:
            replay_service.like(videoId, userId)
        except TYBizException, e:
            msg.setResult('code', e.errorCode)
            msg.setResult('info', e.message)
        router.sendToUser(msg, userId)
        return msg
        
    @markCmdActionMethod(cmd='dizhu', action='replay_mine_rem', clientIdVer=0, scope='game')
    def doMineRem(self, userId, gameId, clientId, videoId):
        self._doMineRem(userId, gameId, clientId, videoId)
        
    @classmethod
    def _doMineRem(cls, userId, gameId, clientId, videoId):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'replay_mine_rem')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('videoId', videoId)
        try:
            replay_service.removeVideo(userId, videoId)
            router.sendToUser(msg, userId)
        except TYBizException, e:
            msg.setResult('code', e.errorCode)
            msg.setResult('info', e.message)
        router.sendToUser(msg, userId)
        return msg

    @markCmdActionMethod(cmd='dizhu', action='replay_share', clientIdVer=0, scope='game')
    def doShare(self, userId, gameId, clientId, videoId, shareType):
        self._doShare(userId, gameId, clientId, videoId, shareType)

    @classmethod
    def _doShare(cls, userId, gameId, clientId, videoId, shareType):
        return replay_service.share(userId, gameId, videoId, shareType)



