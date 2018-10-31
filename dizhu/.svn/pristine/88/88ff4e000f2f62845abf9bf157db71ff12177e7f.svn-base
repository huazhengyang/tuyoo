# -*- coding:utf-8 -*-
'''
Created on 2016年9月2日

@author: zhaojiangang
'''
import hashlib
import os
import time

from dizhu.replay import replay_service
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from dizhu.servers.util.rpc import event_remote
from dizhu.entity.dizhuconf import DIZHU_GAMEID


@markHttpHandler
class ReplayHttpHandler(BaseHttpMsgChecker):
    def _check_param_topn(self, key, params):
        topn = runhttp.getParamInt(key, 0)
        return None, topn
    
    def _check_param_videoData(self, key, params):
        videoData = runhttp.getBody()
        if not videoData:
            return 'param videoData error', None
        return None, videoData
    
    def _check_param_videoId(self, key, params):
        videoId = runhttp.getParamStr(key, '')
        if videoId:
            return None, videoId
        return 'param videoId error', None
    
    def _check_param_videoIdList(self, key, params):
        try:
            jstr = runhttp.getParamStr(key)
            videoIdList = jstr.split(',')
            ret = []
            for videoId in videoIdList:
                videoId = videoId.strip()
                ret.append(videoId)
            return None, ret
        except:
            return 'Error param videoIdList !!', None
        
    def _check_param_issueNum(self, key, params):
        issueNum = runhttp.getParamStr(key, '')
        if not issueNum:
            issueNum = replay_service.getIssueNumber(pktimestamp.getCurrentTimestamp() - 86400)
        return None, issueNum
    
    @classmethod
    def calcPath(cls, videoId):
        filePath = '%s.json' % (videoId)
        m = hashlib.md5()
        names = []
        for _ in xrange(3):
            m.update(filePath)
            name = str(int(m.hexdigest()[-3:], 16) % 1024)
            filePath = name + '/' + filePath
            names.append(name)
        return filePath
        
    @classmethod
    def makePath(cls, videoId):
        return gdata.pathWebroot() + '/dizhu/replay/videos/' + cls.calcPath(videoId)
    
    @markHttpMethod(httppath='/replay/video/save')
    def doVideoSave(self, videoId, videoData):
        filepath = self.makePath(videoId)
        filedir = os.path.dirname(filepath)
        ftlog.info('ReplayHttpHandler.doReplaySave videoId=', videoId,
                   'filepath=', filepath)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        with open(filepath, 'w') as f:
            f.write(videoData)
        return {'ec':0}
    
    @markHttpMethod(httppath='/replay/video/remove')
    def doVideoRemove(self, videoId):
        try:
            filepath = self.makePath(videoId)
            ftlog.info('ReplayHttpHandler.doVideoRemove videoId=', videoId,
                       'filepath=', filepath)
            os.remove(filepath)
        except:
            pass
        return {'ec':0}
    
    @markHttpMethod(httppath='/replay/video/load')
    def doVideoLoad(self, videoId):
        try:
            filepath = self.makePath(videoId)
            with open(filepath, 'r') as f:
                videoData = f.read()
                return {'ec':0, 'data':videoData}
        except:
            return {'ec':-1, 'info':''}
        
    @markHttpMethod(httppath='/dizhu/v1/replay/video/view')
    def doNotifyVideoView(self, videoId):
        try:
            if ftlog.is_debug():
                ftlog.debug('ReplayHttpHandler.doNotifyVideoView',
                            'videoId=', videoId)
            replay = replay_service.view(videoId, 0, pktimestamp.getCurrentTimestamp())
            event_remote.publishReplayViewEvent(DIZHU_GAMEID, replay.userId, videoId)
            return {'ec':0, 'vc':replay.viewsCount}
        except TYBizException, e:
            return {'ec':e.errorCode, 'info':e.message}
    
    def checkCode(self):
        code = ''
        datas = runhttp.getDict()
        if 'code' in datas:
            code = datas['code']
            del datas['code']
        keys = sorted(datas.keys())
        checkstr = ''
        for k in keys:
            checkstr += k + '=' + datas[k] + '&'
        checkstr = checkstr[:-1]

        apikey = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'
        checkstr = checkstr + apikey
        if code != strutil.md5digest(checkstr):
            return -1, 'Verify code error'

        acttime = int(datas.get('time', 0))
        if abs(time.time() - acttime) > 10:
            return -1, 'verify time error'
        return 0, None
    
    @classmethod
    def buildReplay(cls, replay):
        seat = replay.findWinloseSeatByUserId(replay.userId)
        params = {
            'videoId':replay.videoId,
            'totalMulti':replay.details.get('totalMulti', 1),
            'bombCount':replay.details.get('nbomb', 0),
            'deltaChip':seat.get('dChip', 0) if seat else 0
        }
        url = 'http://ddz.replay.qqweibo.cc/index.html?videoId=${videoId}&multi=${totalMulti}&bombCount=${bombCount}&deltaChip=${deltaChip}'
        url = strutil.replaceParams(url, params)
        return {
            'userId':replay.userId,
            'videoId':replay.videoId,
            'url':url
        }
        
    def needCheckCode(self):
        mode = gdata.mode()
        return (mode == gdata.RUN_MODE_ONLINE
                or 'test' not in runhttp.getDict())
        
    @markHttpMethod(httppath='/_gdss/dizhu/replay/list')
    def doGdssReplayList(self, issueNum):
        mo = MsgPack()
        ec, info = 0, ''
        if self.needCheckCode():
            ec, info = self.checkCode()
        if ec == 0:
            try:
                videos = []
                replays = replay_service.getTopNReplay(issueNum, replay_service._maxTop)
                for replay in replays:
                    videos.append(self.buildReplay(replay))
                mo.setResult('videos', videos)
            except TYBizException, e:
                ec = e.errorCode
                info = e.message
        if ec != 0:
            mo.setError(ec, info)
        return mo
    
    @markHttpMethod(httppath='/_gdss/dizhu/replay/getManualTopN')  
    def doGdssReplayGetManualTopN(self):
        mo = MsgPack()
        ec, info = 0, ''
        if self.needCheckCode():
            ec, info = self.checkCode()
        if ec == 0:
            topn = replay_service.getManualTopN(10)
            mo.setResult('topn', topn)
        else:
            mo.setError(ec, info)
        return mo
    
    @markHttpMethod(httppath='/_gdss/dizhu/replay/setManualTopN')  
    def doGdssReplaySetManualTopN(self, videoIdList):
        mo = MsgPack()
        ec, info = 0, ''
        if self.needCheckCode():
            ec, info = self.checkCode()
        if ec == 0:
            replay_service.setManualTopN(videoIdList)
            topn = replay_service.getManualTopN(10)
            mo.setResult('topn', topn)
        else:
            mo.setError(ec, info)
        return mo


