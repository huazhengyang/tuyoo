# -*- coding=utf-8
'''
Created on 2015年6月24日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from poker.protocol import runhttp


class BaseHttpMsgChecker(object):

    def _check_param_gameId(self, key, params):
        gameId = runhttp.getParamInt(key, 0)
        if not gameId :
            gameId = runhttp.getParamInt('appId', 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_gameId key=', key,
                    'params=', params,
                    'gameId=', gameId,
                    'gameIds=', gdata.gameIds())
        if not gameId in gdata.gameIds():
            return 'param gameId error', None
        return None, gameId


    def _check_param_appId(self, key, params):
        appId = runhttp.getParamInt(key, 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_appId key=', key,
                    'params=', params,
                    'appId=', appId,
                    'gameIds=', gdata.gameIds())
        if not appId in gdata.gameIds():
            return 'param appId error', None
        return None, appId


    def _check_param_userId(self, key, params):
        userId = runhttp.getParamInt(key, 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_userId key=', key,
                    'params=', params,
                    'userId=', userId)
        if userId <= 0:
            return 'param userId error', None
        return None, userId
    
    # 带0的是http接口中的，不带0的是msg里面的
    def _check_param_roomId0(self, key, params):
        roomId = runhttp.getParamInt(key, -1)
        if isinstance(roomId, int) and roomId >= 0:
            return None, roomId
        return None, 0
    
    # 带0的是http接口中的，不带0的是msg里面的
    def _check_param_tableId0(self, key, params):
        tableId = runhttp.getParamInt(key, -1)
        if isinstance(tableId, int) and tableId >= 0:
            return None, tableId
        return None, 0
    
    def _check_param_uid(self, key, params):
        uid = runhttp.getParamInt(key, 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_uid key=', key,
                    'params=', params,
                    'userId=', uid)
        if uid <= 0:
            return 'param uid error', None
        return None, uid


    def _check_param_prodId(self, key, params):
        prodId = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_prodId key=', key,
                    'params=', params,
                    'prodId=', prodId)
        if not prodId :
            return 'param prodId error', None
        return None, prodId


    def _check_param_orderId(self, key, params):
        orderId = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_orderId key=', key,
                    'params=', params,
                    'orderId=', orderId)
        if not orderId :
            return 'param orderId error', None
        return None, orderId


    def _check_param_prodOrderId(self, key, params):
        prodOrderId = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_prodId key=', key,
                    'params=', params,
                    'prodOrderId=', prodOrderId)
        if not prodOrderId :
            return 'param prodOrderId error', None
        return None, prodOrderId


    def _check_param_buttonId(self, key, params):
        buttonId = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_buttonId key=', key,
                    'params=', params,
                    'buttonId=', buttonId)
        return None, buttonId


    def _check_param_platformOrder(self, key, params):
        platformOrder = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_platformOrder key=', key,
                    'params=', params,
                    'platformOrder=', platformOrder)
        return None, platformOrder


    def _check_param_clientId(self, key, params):
        clientId = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_clientId key=', key,
                    'params=', params,
                    'clientId=', clientId)
        if clientId and isinstance(clientId, (str, unicode)) :
            return None, clientId
        userId = runhttp.getParamInt('userId', 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_clientId key=', key,
                    'params=', params,
                    'clientId=', clientId,
                    'userId=', userId)
        if userId :
            clientId = sessiondata.getClientId(userId)
            if clientId and isinstance(clientId, (str, unicode)) :
                return None, clientId
        return 'ERROR of clientId !' + str(clientId), None


    def _check_param_prodCount(self, key, params):
        prodCount = runhttp.getParamInt(key, 1)
        ftlog.debug('BaseHttpMsgChecker._check_param_prodCount key=', key,
                    'params=', params,
                    'prodCount=', prodCount)
        if prodCount <= 0:
            return 'param prodCount error', None
        return None, prodCount


    def _check_param_orderPrice(self, key, params):
        orderPrice = runhttp.getParamInt(key, 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_orderPrice key=', key,
                    'params=', params,
                    'orderPrice=', orderPrice)
        return None, orderPrice


    def _check_param_isError(self, key, params):
        isError = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_isError key=', key,
                    'params=', params,
                    'isError=', isError)
        return None, isError


    def _check_param_error(self, key, params):
        error = runhttp.getParamStr(key, '')
        ftlog.debug('BaseHttpMsgChecker._check_param_error key=', key,
                    'params=', params,
                    'error=', error)
        return None, error


    def _check_param_diamonds(self, key, params):
        diamonds = runhttp.getParamInt(key, 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_diamonds key=', key,
                    'params=', params,
                    'diamonds=', diamonds)
        return None, diamonds


    def _check_param_rmbs(self, key, params):
        rmbs = runhttp.getParamFloat(key, 0.0)
        ftlog.debug('BaseHttpMsgChecker._check_param_rmbs key=', key,
                    'params=', params,
                    'rmbs=', rmbs)
        return None, rmbs
    
    def _check_param_matchId(self, key, params):
        matchId = runhttp.getParamInt(key, 0)
        ftlog.debug('BaseHttpMsgChecker._check_param_matchId key=', key,
                    'params=', params,
                    'matchId=', matchId)
        if matchId <= 0:
            return 'param matchId error', None
        return None, matchId


if __name__ == '__main__':
    pass
