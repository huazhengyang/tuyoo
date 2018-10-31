# -*- coding:utf-8 -*-
'''
Created on 2018年5月7日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

from hall.entity import hall_share3
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from hall.servers.util.share3_handler import Share3TcpHandler
from poker.entity.configure import gdata
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp


@markHttpHandler
class TestHttpHandler(BaseHttpMsgChecker):

    def __init__(self):
        pass
    
    def isEnable(self):
        return gdata.enableTestHtml()
    
    def makeErrorResponse(self, ec, message):
        return {'error':{'ec':ec, 'message':message}}
    
    def makeResponse(self, result):
        return {'result':result}
    
    def _check_param_pointId(self, key, params):
        value = runhttp.getParamInt(key)
        if value <= 0:
            return self.makeErrorResponse(-1, 'pointId必须是>0的整数'), None
        return None, value
    
    def _check_param_burialId(self, key, params):
        value = runhttp.getParamStr(key)
        if not value or not isstring(value):
            return 'burialId必须是字符串', None
        return None, value
    
    def _check_param_whereToShare(self, key, params):
        value = runhttp.getParamStr(key)
        if not value or not isstring(value):
            return 'whereToShare必须是字符串', None
        return None, value
    
    def _check_param_urlParams(self, key, params):
        value = runhttp.getParamStr(key)
        if not value:
            return None, {}
        try:
            value = strutil.loads(value)
        except:
            return 'urlParams必须是json字符串', None
        return None, value
    
    def _check_param_count(self, key, params):
        count = runhttp.getParamInt(key, 0)
        return None, count
    
    def _check_param_curTime(self, key, params):
        value = runhttp.getParamStr(key)
        if not value:
            return None, pktimestamp.getCurrentTimestamp()
        if not isstring(value):
            return self.makeErrorResponse(-1, '当前时间格式错误'), None
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return None, pktimestamp.datetime2Timestamp(dt)
        except:
            return self.makeErrorResponse(-1, '当前时间格式错误'), None
        
    @markHttpMethod(httppath='/gtest/hall/share3/getBurials')
    def share3GetBurials(self, gameId, userId, clientId):
        mp = Share3TcpHandler._doGetBurials(gameId, userId, clientId)
        return mp._ht
    
    @markHttpMethod(httppath='/gtest/hall/share3/getBurialShare')
    def share3GetBurialShare(self, gameId, userId, clientId, burialId, urlParams):
        mp = Share3TcpHandler._doGetBurialShare(gameId, userId, clientId, burialId, urlParams)
        if not mp:
            return {'ec':-1, 'info':'Not found burialId: %s' % (burialId)}
        return mp._ht
    
    @markHttpMethod(httppath='/gtest/hall/share3/rewardStatus')
    def share3RewardStatus(self, gameId, userId, clientId, pointId, curTime):
        sharePoint = hall_share3.getSharePoint(gameId, userId, clientId, pointId)
        ts, count = hall_share3.loadShareStatus(gameId, userId, sharePoint, curTime)
        return {'time':datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'), 'count':count}

    @markHttpMethod(httppath='/gtest/hall/share3/setRewardStatus')
    def share3SetRewardStatus(self, gameId, userId, clientId, pointId, curTime, count):
        sharePoint = hall_share3.getSharePoint(gameId, userId, clientId, pointId)
        hall_share3.saveShareStatus(gameId, userId, sharePoint, curTime, count)
        return {'time':datetime.fromtimestamp(curTime).strftime('%Y-%m-%d %H:%M:%S'), 'count':count}
    
    @markHttpMethod(httppath='/gtest/hall/share3/gainReward')
    def share3GainReward(self, gameId, userId, clientId, pointId, whereToShare, curTime):
        mp = Share3TcpHandler._doGetShareReward(gameId, userId, clientId, pointId, whereToShare)
        return mp._ht


