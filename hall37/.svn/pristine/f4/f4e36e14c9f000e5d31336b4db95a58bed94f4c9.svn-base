# -*- coding=utf-8
'''
Created on 2015年7月31日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallshare
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp

GAMEID = 9999

@markCmdActionHandler    
class ShareTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(ShareTcpHandler, self).__init__()
    
    def _check_param_shareId(self, msg, key, params):
        try:
            shareId = msg.getParam(key, msg.getParam('id'))
            return None, int(shareId)
        except:
            return None, -1
            
    def _check_param_shareLoc(self, msg, key, params):
        try:
            shareLoc = msg.getParam(key, 'SHARE_URL')
            return None, shareLoc
        except:
            return 'ERROR of shareLoc !', None
    
    def _check_param_code(self, msg, key, params):
        try:
            code = msg.getParam(key, '-1')
            return None, int(code)
        except:
            return 'ERROR of code !', None
    def _check_param_source(self, msg, key, params):
        try:
            code = msg.getParam(key, '')
            return None, str(code)
        except:
            return 'ERROR of source !', None
        
    def _getShareReward(self, gameId, userId, shareId, shareLoc, code):
        if (shareId == '-') or (shareId == '-1') or (code != 0):
            ftlog.debug('ShareTcpHandler._getShareReward gameId=', gameId,
                       'userId=', userId,
                       'shareId=', shareId,
                       'shareLoc=', shareLoc,
                       'code=', code,
                       'err=', 'BadShareId')
            return
        
        share = hallshare.findShare(int(shareId))
        if not share:
            ftlog.debug('ShareTcpHandler._getShareReward gameId=', gameId,
                       'userId=', userId,
                       'shareId=', shareId,
                       'shareLoc=', shareLoc,
                       'code=', code,
                       'err=', 'UnknownShareId')
            return
        
        hallshare.getShareReward(gameId, userId, share, shareLoc, pktimestamp.getCurrentTimestamp())
        
    @markCmdActionMethod(cmd='share_hall', action="reward", clientIdVer=0)
    def doGetShareReward(self, gameId, userId, shareId, shareLoc, code):
        '''
        客户端回调奖励
        '''
        self._getShareReward(gameId, userId, shareId, shareLoc, code)
        
    @markCmdActionMethod(cmd='share_url', clientIdVer=0)
    def doGetShareRewardOld(self, gameId, userId, shareId, shareLoc, code):
        '''
        客户端回调奖励
        '''
        self._getShareReward(gameId, userId, shareId, shareLoc, code)
    @markCmdActionMethod(cmd='share_hall', action="geturl", clientIdVer=0)
    def doGetShareDownloadUrl(self, gameId, userId, source):
        '''
        客户端获取下载地址
        '''
        ftlog.debug('ShareHandler.doGetShareDownloadUrl gameId=', gameId, 'userId', userId, 'source', source)
        hallshare.getShareDownloadUrl(gameId, userId, source)
        

