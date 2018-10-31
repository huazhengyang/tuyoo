# -*- coding:utf-8 -*-
'''
Created on 2017年11月14日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from hall.entity import hall_share2, hall_short_url
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.entity.hall_share2 import ParsedClientId
from sre_compile import isstring


@markCmdActionHandler    
class Share2TcpHandler(BaseMsgPackChecker):
    def _check_param_pointId(self, msg, key, params):
        value = msg.getParam(key)
        if isinstance(value, int) or isstring(value):
            return None, int(value)
        return 'ERROR of pointId !' + str(value), None
    
    def _check_param_shareId(self, msg, key, params):
        value = msg.getParam(key)
        if isinstance(value, int) :
            return None, value
        return 'ERROR of shareId !' + str(value), None

    def _check_param_urlParams(self, msg, key, params):
        value = msg.getParam(key, {})
        if isinstance(value, dict) :
            return None, value
        return 'ERROR of urlParams !' + str(value), None
    
    @classmethod
    def _doCheckShareReward(cls, gameId, userId, clientId, pointId, timestamp=None):
        leftCount = hall_share2.getLeftRewardCount(gameId, userId, clientId, pointId, timestamp)
        mp = MsgPack()
        mp.setCmd('hall_share2')
        mp.setResult('action', 'check_reward')
        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('pointId', pointId)
        mp.setResult('leftCount', leftCount)
        return mp
        
    @markCmdActionMethod(cmd='hall_share2', action='check_reward', clientIdVer=0)
    def doCheckShareReward(self, gameId, userId, clientId, pointId):
        '''
        客户端回调奖励
        '''
        mp = self._doCheckShareReward(gameId, userId, clientId, pointId)
        if mp:
            router.sendToUser(mp, userId)
    
    @classmethod
    def _doGetShareReward(cls, gameId, userId, clientId, pointId, timestamp=None):
        ok, assetList = hall_share2.gainShareReward(gameId, userId, clientId, pointId, timestamp)
        rewards = []
        if ok:
            for atup in assetList:
                rewards.append({'itemId':atup[0].kindId,
                                'name':atup[0].displayName,
                                'url':atup[0].pic,
                                'count':atup[1]})
        mp = MsgPack()
        mp.setCmd('hall_share2')
        mp.setResult('action', 'get_reward')
        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('rewards', rewards)
        return mp
        
    @markCmdActionMethod(cmd='hall_share2', action='get_reward', clientIdVer=0)
    def doGetShareReward(self, gameId, userId, clientId, pointId):
        '''
        客户端回调奖励
        '''
        mp = self._doGetShareReward(gameId, userId, clientId, pointId)
        if mp:
            router.sendToUser(mp, userId)
    
    @classmethod
    def _doGetShareInfo(cls, gameId, userId, clientId, pointId, urlParams):
        mp = MsgPack()
        mp.setCmd('hall_share2')
        mp.setResult('action', 'get_share_info')
        parsedClientId = ParsedClientId.parseClientId(clientId)
        if not parsedClientId:
            mp.setResult('ec', -1)
            mp.setResult('info', 'clientId错误')
            return mp
        
        sharePoint, shareContent = hall_share2.getShareContent(gameId, userId, parsedClientId, pointId)
        
        if not shareContent:
            mp.setResult('ec', -1)
            mp.setResult('info', '没有找到分享')
            return mp
        
        url = shareContent.buildUrl(userId, parsedClientId, sharePoint.pointId, urlParams)
        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('shareId', shareContent.shareId)
        mp.setResult('pointId', sharePoint.pointId)
        mp.setResult('url', url)
        mp.setResult('shareMethod', shareContent.shareMethod)
        mp.setResult('whereToShare', shareContent.whereToShare)
        mp.setResult('shareRule', shareContent.shareRule)
        if shareContent.preview is not None:
            mp.setResult('preview', shareContent.preview)
        if shareContent.shareQR is not None:
            mp.setResult('shareQR', shareContent.shareQR)
        return mp
    
    @markCmdActionMethod(cmd='hall_share2', action='get_share_info', clientIdVer=0)
    def doGetShareInfo(self, gameId, userId, clientId, pointId, urlParams):
        '''
        客户端回调奖励
        '''
        mp = self._doGetShareInfo(gameId, userId, clientId, pointId, urlParams)
        if mp:
            router.sendToUser(mp, userId)
    
    @classmethod
    def _doGetShareUrl(self, gameId, userId, clientId, pointId, shareId, urlParams):
        mp = MsgPack()
        mp.setCmd('hall_share2')
        mp.setResult('action', 'get_share_url')
        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('shareId', shareId)
        mp.setResult('pointId', pointId)
        
        parsedClientId = ParsedClientId.parseClientId(clientId)
        if not parsedClientId:
            mp.setResult('ec', -1)
            mp.setResult('info', 'clientId错误')
            return mp
        
        sharePoint, shareContent = hall_share2.getShareContentWithShareId(gameId, userId, parsedClientId, pointId, shareId)
        
        if not shareContent:
            mp.setResult('ec', -1)
            mp.setResult('info', '没有找到分享')
            return mp
        
        url = shareContent.buildUrl(userId, parsedClientId, sharePoint.pointId, urlParams)
        url = hall_short_url.longUrlToShort(url)
        mp.setResult('url', url)
        return mp
    
    @markCmdActionMethod(cmd='hall_share2', action='get_share_url', clientIdVer=0)
    def doGetShareUrl(self, gameId, userId, clientId, pointId, shareId, urlParams):
        mp = self._doGetShareUrl(gameId, userId, clientId, pointId, shareId, urlParams)
        if mp:
            router.sendToUser(mp, userId)


