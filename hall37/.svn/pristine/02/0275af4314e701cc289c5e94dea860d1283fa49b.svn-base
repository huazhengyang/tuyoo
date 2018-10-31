# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata


class BaseMsgPackChecker(object):

    
    def _check_param_userId(self, msg, key, params):
        userId = msg.getParam(key)
        if userId and isinstance(userId, int) :
            return None, userId
        return 'ERROR of userId !' + str(userId), None


    def _check_param_gameId(self, msg, key, params):
        gameId = msg.getParam(key)
        if gameId and isinstance(gameId, int) :
            return None, gameId
        appId = msg.getParam('appId')
        if appId and isinstance(appId, int) :
            return None, appId
        return 'ERROR of gameId !' + str(gameId), None


    def _check_param_clientId(self, msg, key, params):
        clientId = msg.getKey(key)
        if clientId and isinstance(clientId, (str, unicode)) :
            return None, clientId
        clientId = msg.getParam(key)
        if clientId and isinstance(clientId, (str, unicode)) :
            return None, clientId
        ftlog.debug('ERROR !! the msg clientId is not found use session clientId !', msg)
        userId = msg.getParam('userId')
        if userId :
            clientId = sessiondata.getClientId(userId)
            if clientId and isinstance(clientId, (str, unicode)) :
                return None, clientId
        return 'ERROR of clientId !' + str(clientId), None


    def _check_param_isMust(self, msg, key, params):
        must = msg.getParam('must')
        if must == 1 :
            return None, 1
        return None, 0


    def _check_param_starId(self, msg, key, params):
        starId = msg.getParam(key)
        if isinstance(starId, int) and starId >= 0:
            return None, starId
        return 'ERROR of starId !' + str(starId), None


    def _check_param_roomId0(self, msg, key, params):
        roomId = msg.getParam('roomId')
        try:
            roomId = int(roomId)
            if isinstance(roomId, int) and roomId >= 0:
                return None, roomId
        except:
            return None, 0
        return None, 0


    def _check_param_tableId0(self, msg, key, params):
        tableId = msg.getParam('tableId')
        if isinstance(tableId, int) and tableId >= 0:
            return None, tableId
        return None, 0


    def _check_param_seatId0(self, msg, key, params):
        tableId = msg.getParam('seatId')
        if isinstance(tableId, int) and tableId >= 0:
            return None, tableId
        return None, 0


    def _check_param_playMode(self, msg, key, params):
        playMode = msg.getParam('playMode')
        if playMode and isinstance(playMode, (str, unicode)) :
            return None, playMode
        return None, None


    def _check_param_roomId(self, msg, key, params):
        roomId = msg.getParam('roomId')
        try:
            roomId = int(roomId)
            if roomId in gdata.rooms() :
                return None, roomId
        except:
            pass
        return 'ERROR of roomId !' + str(roomId), None


    def _check_param_bigRoomId(self, msg, key, params):
        roomId = msg.getParam('roomId')
        if roomId in gdata.bigRoomidsMap() :
            return None, roomId
        return 'ERROR of big roomId !' + str(roomId), None


    def _check_param_tableId(self, msg, key, params):
        roomId = params.get('roomId')
        room = gdata.rooms().get(roomId)
        tableId = msg.getParam('tableId')
        if room and tableId in room.maptable:
            return None, tableId
        return 'ERROR of tableId !' + str(tableId), None


    def _check_param_seatId(self, msg, key, params):
        seatId = msg.getParam('seatId')
        if isinstance(seatId, int): # 德州客户端seatId从0开始，-1也有特殊含义
            return None, seatId
        return 'ERROR of seatId !' + str(seatId), None


    def _check_param_isFirstuserInfo(self, msg, key, params):
        firstUserInfo = msg.getKey('firstUserInfo')
        if isinstance(firstUserInfo, int) and firstUserInfo  == 1:
            return None, 1
        return None, 0


    def _check_param_version(self, msg, key, params):
        version = msg.getParam('version')
        if version and isinstance(version, (str, unicode)) :
            return None, version
        return None, None
    
    def _check_param_updateVersion(self, msg, key, params):
        updateVersion = msg.getParam('updateVersion')
        if isinstance(updateVersion, int) :
            return None, updateVersion
        return None, 0
    
    def _check_param_module(self, msg, key, params):
        module = msg.getParam('module')
        if module and isinstance(module, (str, unicode)) :
            return None, module
        return None, None
    
    def _check_param_pluginId(self, msg, key, params):
        pluginId = msg.getParam('pluginId')
        if isinstance(pluginId, int) and pluginId >= 0:
            return None, pluginId
        return None, None
    
    def _check_param_config(self, msg, key, params):
        config = msg.getParam('config')
        if config:
            return None, config
        return None, None
    
    def _check_param_ftId(self, msg, key, params):
        ftId = msg.getParam('ftId')
        if ftId and isinstance(ftId, (str, unicode)) :
            return None, ftId
        return None, None
    
    def _check_param_matchId(self, msg, key, params):
        '''
        比赛ID
        '''
        matchId = msg.getParam('matchId')
        if isinstance(matchId, int) and matchId >= 0:
            return None, matchId
        return None, None