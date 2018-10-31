# -*- coding:utf-8 -*-
'''
Created on 2016年9月26日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.friendtable import ft_service
from dizhu.servers.room.rpc import ft_room_remote
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from hall.entity.todotask import TodoTaskHelper, TodoTaskGotoShop
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class FTHandler(BaseMsgPackChecker):
    def __init__(self):
        super(FTHandler, self).__init__()
        
    def _check_param_ftId(self, msg, key, params):
        ftId = msg.getParam(key)
        if not ftId or not isstring(ftId):
            return 'ERROR of ftId !' + str(ftId), None
        return None, ftId
        
    def _check_param_count(self, msg, key, params):
        count = msg.getParam(key, 1)
        if count and isinstance(count, int) :
            return None, count
        return 'ERROR of count !' + str(count), None
    
    def _check_param_conf(self, msg, key, params):
        conf = msg.getParam(key)
        if not conf or not isinstance(conf, dict):
            return 'ERROR of conf !' + str(conf), None
        nRound = conf.get('nRound')
        if not isinstance(nRound, int) or nRound <= 0:
            return 'ERROR of conf.nRound must be int > 0', None
        canDouble = conf.get('double')
        if canDouble not in (0, 1):
            return 'ERROR of conf.double must be int > 0', None
        playMode = conf.get('playMode')
        if not isstring(playMode):
            return 'ERROR of conf.playMode must be string', None
        return None, conf
    
    @markCmdActionMethod(cmd='dizhu', action='ft_get_conf', clientIdVer=0, lockParamName='', scope='game')
    def doFTGetConf(self, userId, gameId, clientId):
        self._doFTGetConf(userId, gameId, clientId)
        
    @classmethod
    def encodeCreatorConf(cls, creatorConf):
        rounds = []
        playModes = []
        for roundConf in creatorConf.roundList:
            roundD = {
                'nRound':roundConf.nRound,
                'fee':roundConf.fee
            }
            rounds.append(roundD)
        for playModeConf in creatorConf.playModeList:
            playModes.append({
                'name':playModeConf.name,
                'mode':playModeConf.mode
            })
        return {
            'rounds':rounds,
            'playModes':playModes,
            'cardPrice':creatorConf.cardPrice,
            'cardProduct':creatorConf.cardProductId
        }
            
    @classmethod
    def _doFTGetConf(cls, userId, gameId, clientId):
        creatorConf = ft_service.getCreatorConf(userId)
        conf = cls.encodeCreatorConf(creatorConf)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'ft_get_conf')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('conf', conf)
        msg.setResult('cardCount', ft_service.getCardCount(userId))
        router.sendToUser(msg, userId)
        return conf
    
    @markCmdActionMethod(cmd='dizhu', action='ft_create', clientIdVer=0, lockParamName='', scope='game')
    def doFTCreate(self, userId, gameId, clientId, conf):
        self._doFTCreate(userId, gameId, clientId, conf)
        
    @classmethod
    def _doFTCreate(cls, userId, gameId, clientId, conf):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'ft_create')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        try:
            ftId = ft_service.createFT(userId, conf['nRound'], conf['playMode'], conf['double'], conf.get('goodCard', 0))
            msg.setResult('ftId', ftId)
            msg.setResult('cardCount', ft_service.getCardCount(userId))
            router.sendToUser(msg, userId)
            return 0, ftId
        except TYBizException, e:
            msg.setResult('code', e.errorCode)
            msg.setResult('info', e.message)
            router.sendToUser(msg, userId)
            return e.errorCode, e.message

    @markCmdActionMethod(cmd='dizhu', action='ft_enter', clientIdVer=0, lockParamName='', scope='game')
    def doFTEnter(self, userId, gameId, clientId, ftId):
        self._doFTEnter(userId, gameId, clientId, ftId)
    
    @classmethod
    def _doFTEnter(cls, userId, gameId, clientId, ftId):
        try:
            roomId = ft_service.roomIdForFTId(ftId)
            if not roomId:
                raise TYBizException(-1, '没有找到该牌桌')
            ec, result = ft_room_remote.enterFT(roomId, userId, ftId)
            if ec == 0:
                ftlog.info('FTHandler._doFTEnter Succ',
                           'userId=', userId,
                           'gameId=', gameId,
                           'clientId=', clientId,
                           'ftId=', ftId,
                           'tableId=', result)
                msg = MsgPack()
                msg.setCmd('dizhu')
                msg.setResult('action', 'ft_enter')
                msg.setResult('gameId', DIZHU_GAMEID)
                msg.setResult('userId', userId)
                msg.setResult('ftId', ftId)
                msg.setResult('code', ec)
                router.sendToUser(msg, userId)
                return 0, result
            raise TYBizException(ec, result)
        except TYBizException, e:
            ftlog.warn('FTHandler._doFTEnter Exception',
                       'userId=', userId,
                       'gameId=', gameId,
                       'clientId=', clientId,
                       'ftId=', ftId,
                       'ec=', e.errorCode,
                       'info=', e.message)
            msg = MsgPack()
            msg.setCmd('dizhu')
            msg.setResult('action', 'ft_enter')
            msg.setResult('gameId', DIZHU_GAMEID)
            msg.setResult('userId', userId)
            msg.setResult('ftId', ftId)
            msg.setResult('code', e.errorCode)
            msg.setResult('info', e.message)
            router.sendToUser(msg, userId)
            return e.errorCode, e.message

    @markCmdActionMethod(cmd='dizhu', action='ft_buy_card', clientIdVer=0, lockParamName='', scope='game')
    def doFTBuyCard(self, userId, gameId, clientId, count):
        TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskGotoShop('coupon'))

