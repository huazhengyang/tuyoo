# -*- coding:utf-8 -*-
'''
Created on 2016年9月19日

@author: zhaojiangang
'''
import random
from sre_compile import isstring

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.room.rpc import ft_room_remote
from freetime.util import log as ftlog
from hall.entity import hallitem, hall_friend_table, hallshare
from hall.entity.todotask import TodoTaskHelper
from poker.entity.biz.exceptions import TYBizException, TYBizConfException
from poker.entity.configure import gdata
from poker.entity.dao import daobase, sessiondata, onlinedata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.biz.content import TYContentRegister
from hall.servers.util.rpc import user_remote
from dizhu.entity import dizhuconf


_inited = False
# FTCreatorConf缓存Map<clientId, FTCreatorConf>
_creatorconf_cache = {}

class FTConf(object):
    def __init__(self):
        self.nRound = None
        self.fee = None
        self.canDouble = False
        self.playMode = None
        
    def fromDict(self, d):
        self.nRound = d.get('nRound')
        if not isinstance(self.nRound, int) or self.nRound <= 0:
            raise TYBizConfException(d, 'FTConf.nRound must be int > 0')
        self.fee = d.get('fee')
        if not isinstance(self.fee, int) or self.fee <= 0:
            raise TYBizConfException(d, 'FTConf.fee must be int > 0')
        self.canDouble = d.get('canDouble')
        if self.canDouble not in (0, 1):
            raise TYBizConfException(d, 'FTConf.canDouble must be int int (0, 1)')
        self.playMode = d.get('playMode')
        if not self.playMode or not isstring(self.playMode):
            raise TYBizConfException(d, 'FTConf.playMode must be not empty string')
        return self
    
    def toDict(self):
        ret = {
            'nRound':self.nRound,
            'canDouble':self.canDouble,
            'playMode':self.playMode,
            'fee':self.fee
        }
        return ret
      
class RoundConf(object):
    def __init__(self):
        self.nRound = None
        self.fee = None
        
    def fromDict(self, d):
        self.nRound = d.get('nRound')
        if not isinstance(self.nRound, int) or self.nRound <= 0:
            raise TYBizConfException(d, 'RoundConf.nRound must be int > 0')
        self.fee = d.get('fee')
        if not isinstance(self.fee, int) or self.fee < 0:
            raise TYBizConfException(d, 'RoundConf.fee must be int >= 0')
        return self
    
    def toDict(self):
        ret = {
            'nRound':self.nRound,
            'fee':self.fee
        }
        return ret


class PlayModeConfMin(object):
    def __init__(self):
        self.name = None
        self.displayName = None

    def fromDict(self, d):
        self.name = d.get('type')
        if not self.name or not isstring(self.name):
            raise TYBizConfException(d, 'PlayModeConfMin.name must be not empty string')
        self.displayName = d.get('name')
        if not self.displayName or not isstring(self.displayName):
            raise TYBizConfException(d, 'PlayModeConfMin.displayName must be not empty string')
        return self

    def toDict(self):
        return {
            'name': self.name,
            'displayName': self.displayName
        }

        
class PlayModeConf(object):
    def __init__(self):
        self.name = None
        self.mode = None
    
    def fromDict(self, d):
        self.name = d.get('name')
        if not self.name or not isstring(self.name):
            raise TYBizConfException(d, 'PlayModeConf.name must be not empty string') 

        self.mode = d.get('mode')
        if not self.mode or not isinstance(self.mode, list):
            raise TYBizConfException(d, 'PlayModeConf.mode must be not empty list')
        try:
            for m in self.mode:
                name = m['name']
                type = m['type']
                assert isstring(name), name
                assert isstring(type), type
        except Exception, e:
            raise TYBizConfException(d, 'PlayModeConf.mode elements must be like {"name": "经典","type": "happy"}, err=%s' % e.message)
        return self
    
    def toDict(self):
        return {
            'name':self.name,
            'mode':self.mode
        }
        
class FTCreatorConf(object):
    def __init__(self):
        self.inviteShareId = None
        self.tableExpires = 86400
        self.goodCard = 0
        # key=nRound, value=RoundConf
        self.roundMap = {}
        self.roundList = []
        # key=name, value=PlayModeConf
        self.playModeMap = {}
        self.playModeList = []
        self.cardAssetKindId = None
        self.cardPrice = None
        self.cardProductId = None
        self.bigWinnerRewardContent = None
        
    def getRoundConf(self, nRound):
        return self.roundMap.get(nRound)
    
    def getPlayModeConf(self, playMode):
        return self.playModeMap.get(playMode)
    
    def fromDict(self, d):
        self.cardAssetKindId = d.get('cardAssetKindId')
        if not self.cardAssetKindId or not isstring(self.cardAssetKindId):
            raise TYBizConfException(d, 'cardAssetKindId must be not empty string')
        self.cardPrice = d.get('cardPrice')
        if not isinstance(self.cardPrice, int) or self.cardPrice <= 0:
            raise TYBizConfException(d, 'cardPrice must be int > 0')
        self.cardProductId = d.get('cardProduct')
        if not self.cardProductId or not isstring(self.cardProductId):
            raise TYBizConfException(d, 'cardProduct must be not empty string')
        for roundD in d.get('rounds'):
            roundConf = RoundConf().fromDict(roundD)
            if self.roundMap.get(roundConf.nRound):
                raise TYBizConfException(d, 'Duplicate nRound %s' % (roundConf.nRound))
            self.roundMap[roundConf.nRound] = roundConf
            self.roundList.append(roundConf)
        
        for playModeD in d.get('playModes'):
            playModeConf = PlayModeConf().fromDict(playModeD)

            for mode in playModeConf.mode:
                playModeConfMin = PlayModeConfMin().fromDict(mode)
                if self.playModeMap.get(playModeConfMin.name):
                    raise TYBizConfException(d, 'Duplicate playMode %s' % (playModeConfMin.name))
                self.playModeMap[playModeConfMin.name] = playModeConfMin

            self.playModeList.append(playModeConf)
        self.inviteShareId = d.get('inviteShareId')
        if not isinstance(self.inviteShareId, int):
            raise TYBizConfException(d, 'FTCreatorConf.inviteShare must be int')
        
        self.goodCard = d.get('goodCard', 0)
        if self.goodCard not in (0, 1):
            raise TYBizConfException(d, 'FTCreatorConf.goodCard must in (0, 1)')
        
        bigWinnerRewardContent = d.get('bigWinnerRewardContent')
        if bigWinnerRewardContent:
            self.bigWinnerRewardContent = TYContentRegister.decodeFromDict(bigWinnerRewardContent)
        self.tableExpires = d.get('tableExpires', 86400)
        if not isinstance(self.tableExpires, int) or self.tableExpires <= 0:
            raise TYBizConfException(d, 'FTCreatorConf.tableExpires must be int')
        return self

# _creatorConf = FTCreatorConf()

def ftExists(ftId):
    ret = False
    try:
        ftBind = ftFind(ftId)
        if ftBind:
            ret = ft_room_remote.ftExists(ftBind.get('roomId'), ftId)
    except:
        # 异常，有可能在用
        ret = True
        ftlog.error('ft_service.ftExists ftId=', ftId)
        
    if ftlog.is_debug():
        ftlog.debug('ft_service.ftExists ftId=', ftId,
                    'ret=', ret)
    return ret

def ftFind(ftId):
    jstr = None
    try:
        jstr = daobase.executeMixCmd('get', 'ft:6:%s' % (ftId))
        if ftlog.is_debug():
            ftlog.debug('ft_service.ftFind ftId=', ftId,
                        'jstr=', jstr)
        if not jstr:
            return None
        return strutil.loads(jstr)
    except:
        ftlog.error('ft_service.ftFind ftId=', ftId,
                    'jstr=', jstr)
        return None
    
def ftBindRoomId(ftId, roomId):
    daobase.executeMixCmd('set', 'ft:6:%s' % (ftId), strutil.dumps({'roomId':roomId}))
    
def sendBigWinnerRewards(userId, roomId):
    creatorConf = getCreatorConf(userId)
    if creatorConf.bigWinnerRewardContent:
        items = creatorConf.bigWinnerRewardContent.getItems()
        if items:
            contentItems = [item.toDict() for item in items]
            user_remote.addAssets(DIZHU_GAMEID, userId, contentItems, 'DIZHU_BIG_WINNER', roomId)
            ftlog.info('ft_service.sendBigWinnerRewards',
                       'userId=', userId,
                       'roomId=', roomId,
                       'rewards=', contentItems)
            
def genFTId():
    for _ in xrange(10):
        ftId = hall_friend_table.createFriendTable(DIZHU_GAMEID)
        if ftId:
            return ftId
    return None

def releaseFTId(ftId):
    try:
        daobase.executeMixCmd('del', 'ft:6:%s' % (ftId))
        hall_friend_table.releaseFriendTable(DIZHU_GAMEID, ftId)
    except:
        ftlog.error('ft_service.releaseFTId',
                    'ftId=', ftId)
    
def collectCtrlRoomIdsByFTPlayMode(ftPlayMode):
    bigRoomIds = gdata.gameIdBigRoomidsMap().get(DIZHU_GAMEID)
    ctrlRoomIds = []
    for bigRoomId in bigRoomIds:
        roomConf = gdata.getRoomConfigure(bigRoomId)
        if ((roomConf.get('typeName') in ('dizhuFT', 'dizhu_friend')) 
            and ftPlayMode == roomConf.get('ftPlayMode')):
            ctrlRoomIds.extend(gdata.bigRoomidsMap().get(bigRoomId, []))
    ctrlRoomIds.sort()
    return ctrlRoomIds

def roomIdForFTId(ftId):
    try:
        ftBind = ftFind(ftId)
        if ftBind:
            return ftBind.get('roomId', 0)
    except:
        ftlog.error('ft_server.roomIdForFTId',
                    'ftId=', ftId)
    return 0

def getFeeForConf(creatorConf, ftConf):
    for item in creatorConf.get('rounds', []):
        if item.get('nRound') == ftConf.nRound:
            return item.get('fee')
    return None

def getCreatorConf(userId):
    '''
    获取房间创建配置
    '''
    global _creatorconf_cache
    clientId = sessiondata.getClientId(userId)
    creatorConf = _creatorconf_cache.get(clientId)
    if not creatorConf:
        conf = dizhuconf.getFriendTableConf(clientId)
        creatorConf = FTCreatorConf().fromDict(conf)
        _creatorconf_cache[clientId] = creatorConf
    if ftlog.is_debug():
        ftlog.debug('getCreatorConf',
                    'userId=', userId,
                    'clientId=', clientId,
                    'creatorConf=', creatorConf)
    return creatorConf
 
def getCardCount(userId):
    creatorConf = getCreatorConf(userId)
    return hallitem.itemSystem.loadUserAssets(userId).balance(DIZHU_GAMEID, creatorConf.cardAssetKindId, pktimestamp.getCurrentTimestamp())

def inviteFriend(userId, ftTable):
    creatorConf = getCreatorConf(userId)
    share = hallshare.findShare(creatorConf.inviteShareId)
    if ftlog.is_debug():
        ftlog.debug('ft_service.inviteFriend',
                    'userId=', userId,
                    'ftId=', ftTable.ftId,
                    'shareId=', creatorConf.inviteShareId,
                    'share=', share)
    if share:
        params = {
            'ftId':ftTable.ftId,
            'playMode':ftTable.playMode.get('displayName', ''),
            'nRound':ftTable.nRound,
            'canDouble':'可加倍' if ftTable.canDouble else '不可加倍'
        }
        todotask = share.buildTodotask(DIZHU_GAMEID, userId, 'ftInvite', params)
        title = todotask.getParam('title', '')
        des = todotask.getParam('des', '')
        todotask.setParam('title', strutil.replaceParams(title, params))
        todotask.setParam('des', strutil.replaceParams(des, params))
        return TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, todotask)
    return None

def createFT(userId, nRound, playMode, canDouble, goodCard=0):
    '''
    创建自建桌
    @param userId: 谁创建
    @param conf: 桌子配置
    '''
    # 获取creatorConf
    creatorConf = getCreatorConf(userId)
    # 收取创建自建桌费用
    if not creatorConf:
        raise TYBizException(-1, '不支持自建桌')
     
    roundConf = creatorConf.getRoundConf(nRound)
    if not roundConf:
        raise TYBizException(-1, '不支持的局数: %s' % (nRound))
     
    playModeConf = creatorConf.getPlayModeConf(playMode)
    if not playModeConf:
        raise TYBizException(-1, '不支持的玩法: %s' % (playMode))
    
    # check loc
    locList = onlinedata.getOnlineLocList(userId)
    for loc in locList:
        roomId, _, _ = loc
        gameId = strutil.getGameIdFromInstanceRoomId(roomId)
        if gameId == DIZHU_GAMEID:
            raise TYBizException(-1, '正在其他桌游戏')
        
    ctrlRoomIds = collectCtrlRoomIdsByFTPlayMode(playMode)
    if not ctrlRoomIds:
        ftlog.warn('ft_service.createFT userId=', userId,
                   'nRound=', nRound,
                   'playMode=', playMode,
                   'canDouble=', canDouble)
        raise TYBizException(-1, '不支持的玩法: %s' % (playMode))
    
    ctrlRoomId = ctrlRoomIds[random.randint(0, len(ctrlRoomIds) - 1)]
    if ftlog.is_debug():
        ftlog.debug('ft_service.createFT userId=', userId,
                    'nRound=', nRound,
                    'playMode=', playMode,
                    'canDouble=', canDouble,
                    'goodCard=', goodCard,
                    'ctrlRoomId=', ctrlRoomId,
                    'ctrlRoomIds=', ctrlRoomIds)
    
    fee = None
    if roundConf.fee > 0:
        fee = {'itemId':creatorConf.cardAssetKindId, 'count':roundConf.fee}
    return ft_room_remote.createFT(ctrlRoomId,
                                   userId,
                                   nRound,
                                   playModeConf.toDict(),
                                   canDouble,
                                   fee,
                                   goodCard)

def _onConfChanged(event):
    if _inited and event.isModuleChanged(['friendtable']):
        ftlog.debug('ft_service._onConfChanged')
        _reloadConf()

def _reloadConf():
    if ftlog.is_debug():
        ftlog.debug('ft_service._reloadConf')
    global _creatorconf_cache
    _creatorconf_cache = {}
#     global _creatorConf
#     conf = configure.getGameJson(DIZHU_GAMEID, 'friendtable', {}, configure.DEFAULT_CLIENT_ID)
#     creatorConf = FTCreatorConf().fromDict(conf)
#     _creatorConf = creatorConf
#     ftlog.debug('ft_service._reloadConf nRounds=', creatorConf.roundMap.keys(),
#                'playModes=', creatorConf.playModeMap.keys())
    
def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        ftlog.debug('ft_service._initialize Succ')


