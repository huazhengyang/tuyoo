# -*- coding:utf-8 -*-
'''
Created on 2017年5月9日

@author: zhaojiangang
'''

import os

from dizhu.tupt.ob import obsystem
import freetime.util.log as ftlog
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.entity.configure import gdata
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod


@markHttpHandler
class OBHttpHandler(BaseHttpMsgChecker):
    def _check_param_matchId(self, key, params):
        matchId = runhttp.getParamInt(key, 0)
        if not matchId:
            return 'ERROR of matchId !' + str(matchId), None
        return None, matchId
    
    def _check_param_pageNo(self, key, params):
        pageNo = runhttp.getParamInt(key, 0)
        if not pageNo:
            return 'ERROR of pageNo !' + str(pageNo), None
        return None, pageNo
    
    def _check_param_pageSize(self, key, params):
        pageSize = runhttp.getParamInt(key, 0)
        if not pageSize:
            return 'ERROR of pageSize !' + str(pageSize), None
        return None, pageSize
    
    def _check_param_videoId(self, key, params):
        videoId = runhttp.getParamStr(key, '')
        if videoId:
            return None, videoId
        return 'param videoId error', None
    
    def _check_param_videoData(self, key, params):
        videoData = runhttp.getBody()
        if not videoData:
            return 'param videoData error', None
        return None, videoData
    
    @classmethod
    def makePath(cls, videoId):
        return gdata.pathWebroot() + '/dizhu/tupt/replay/videos/' + obsystem.calcPath(videoId)
    
    @markHttpMethod(httppath='/dizhu/tupt/replay/video/save')
    def doTuptVideoSave(self, videoId, videoData):
        filepath = self.makePath(videoId)
        filedir = os.path.dirname(filepath)
        ftlog.info('OBHttpHandler.doReplaySave videoId=', videoId,
                   'filepath=', filepath)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        with open(filepath, 'w') as f:
            f.write(videoData)
        return {'ec':0}
    
    @markHttpMethod(httppath='/dizhu/tupt/match/list')
    def doTuptMatchList(self):
        matchInfos = obsystem.getReplayMatchs()
        ml = []
        for matchId, matchInfo in matchInfos.iteritems():
            ml.append({'name':matchInfo['name'], 'matchId':matchId})
        return {'list':ml}
    
    @markHttpMethod(httppath='/dizhu/tupt/match/info')
    def doTuptMatchInfo(self, matchId):
        matchInfo = obsystem.loadMatchInfo(matchId)
        if ftlog.is_debug():
            ftlog.debug('OBHttpHandler.doTuptMatchInfo matchId=', matchId,
                        'matchInfo=', matchInfo.toDict())
        return {'info':matchInfo.toDict()}
    
    @classmethod
    def buildDesc(cls, replay):
        nbomb = replay.details.get('nbomb', 0)
        multi = replay.details.get('totalMulti', 1)
        if nbomb < 1:
            return '无炸，%s倍' % (multi)
        return '%s炸，%s倍' % (nbomb, multi)
    
    @markHttpMethod(httppath='/dizhu/tupt/match/video/list')
    def doTuptVideoList(self, matchId, pageNo, pageSize):
        start = (pageNo - 1) * pageSize
        end = start + pageSize
        matchingId = obsystem.getCurMatchingId(matchId)
        if ftlog.is_debug():
            ftlog.debug('OBHttpHandler.doTuptVideoList',
                        'matchId=', matchId,
                        'pageNo=', pageNo,
                        'pageSize=', pageSize,
                        'start=', start,
                        'end=', end,
                        'matchingId=', matchingId)
        vl = []
        totalCount = 0
        if matchingId:
            totalCount = obsystem.getReplaysTotalCount(matchingId)
            replays = obsystem.getReplays(matchingId, start, end)
            for replay in replays:
                vl.append({
                    'videoId':replay.videoId,
                    'time':replay.timestamp,
                    'name':replay.roomName,
                    'stage':replay.stageName,
                    'desc':self.buildDesc(replay),
                    'videoUrl':obsystem.buildVideoDataUrl(replay.videoId)
                })
        return {'total':totalCount, 'list':vl}
    
    @markHttpMethod(httppath='/dizhu/tupt/match/video/wonderfullist')
    def doTuptVonderfulList(self, matchId):
        matchingId = obsystem.getCurMatchingId(matchId)
        vl = []
        if matchingId:
            replays = obsystem.getReplayRank(matchingId, 0, 9)
            for replay in replays:
                vl.append({
                    'videoId':replay.videoId,
                    'time':replay.timestamp,
                    'name':replay.roomName,
                    'stage':replay.stageName,
                    'desc':self.buildDesc(replay),
                    'videoUrl':obsystem.buildVideoDataUrl(replay.videoId)
                })
        return {'list':vl}


if __name__ == '__main__':
    def pathWebroot():
        return '/Users/zhaojiangang/webroot'
    
    handler = OBHttpHandler()
    gdata.pathWebroot = pathWebroot
    handler.doTuptVideoSave('videoId', 'hellodata')
    


