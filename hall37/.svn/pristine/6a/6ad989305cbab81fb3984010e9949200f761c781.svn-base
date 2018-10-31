# -*- coding=utf-8
'''
Created on 2017年7月10日

@author: wangzhen

用户常用功能模块
'''

import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify
from poker.entity.biz.content import TYContentItemGenerator
from poker.entity.biz.item.exceptions import TYAssetNotEnoughException
from poker.entity.biz.item.item import TYAssetUtils
import poker.util.timestamp as pktimestamp



#===============================================================================
# 用户资产相关
#===============================================================================
def assetBalance(gameId, userId, assetKindId):  
    '''
    查询当前资产余量
    :param gameId:
    :param userId:
    :param assetKindId:
    '''
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    timestamp = pktimestamp.getCurrentTimestamp()
    value = userAssets.balance(gameId, assetKindId, timestamp)
    return value

def addAssetNotify(gameId, userId, assetKindId, count, eventId, intEventParam):
    '''
    增加用户资产并通知
    一般一次减少一种时用此接口，一次减少多种时用addAssets
    :param gameId:         
    :param userId:         
    :param assetKindId:    资产种类id，形如  user:chip   item:6001  等，详见 findAssetKind 方法
    :param count:          资产数量
    :param eventId:        哪个事件触发的，配置见 poker/map.bieventid.json
    :param intEventParam:  eventId相关的参数
    '''
    try:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assertKind, addCount, final = userAssets.addAsset(gameId, assetKindId, count, pktimestamp.getCurrentTimestamp(), eventId, intEventParam)
        changeNames = TYAssetUtils.getChangeDataNames([(assertKind, addCount, final)])
        datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
        return addCount, final
    except:
        ftlog.error('user_remote.addAsset gameId=', gameId,
                    'userId=', userId,
                    'assetKindId=', assetKindId,
                    'count=', count,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam)
        return 0, 0


def consumeAssetNotify(gameId, userId, assetKindId, count, eventId, intEventParam):
    '''
    减少用户资产并通知
    一般一次减少一种时用此接口，一次减少多种时用consumeAssets
    :param gameId:         
    :param userId:         
    :param assetKindId:    资产种类id，形如  user:chip   item:6001  等，详见 findAssetKind 方法
    :param count:          资产数量
    :param eventId:        哪个事件触发的，配置见 poker/map.bieventid.json
    :param intEventParam:  eventId相关的参数
    '''
    try:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assertKind, consumeCount, final = userAssets.consumeAsset(gameId, assetKindId, count, pktimestamp.getCurrentTimestamp(), eventId, intEventParam)
        changeNames = TYAssetUtils.getChangeDataNames([(assertKind, consumeCount, final)])
        datachangenotify.sendDataChangeNotify(gameId, userId, changeNames)
        return consumeCount, final
    except:
        ftlog.error('user_remote.consumeAsset gameId=', gameId,
                    'userId=', userId,
                    'assetKindId=', assetKindId,
                    'count=', count,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam)
        return 0, 0

def addAssets(gameId, userId, contentItems, eventId, intEventParam):
    '''
    增加多种用户资产
    :param gameId:
    :param userId:
    :param contentItems:
    :param eventId:
    :param intEventParam:
    '''
    if ftlog.is_debug():
        ftlog.debug('addAssets gameId=', gameId,
                    'userId=', userId,
                    'contentItems=', contentItems,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam)
    try:
        contentItems = _decodeContentItems(contentItems)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContentItemList(gameId, contentItems, 1, True,
                                                   pktimestamp.getCurrentTimestamp(), eventId, intEventParam)
        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
        return True
    except:
        ftlog.error()
        return False

def consumeAssets(gameId, userId, contentItems, eventId, intEventParam):
    '''
    减少多种用户资产
    :param gameId:
    :param userId:
    :param contentItems:
    :param eventId:
    :param intEventParam:
    '''
    if ftlog.is_debug():
        ftlog.debug('consumeAssets gameId=', gameId,
                    'userId=', userId,
                    'contentItems=', contentItems,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam)
    try:
        contentItems = _decodeContentItems(contentItems)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.consumeContentItemList(gameId, contentItems, True,
                                                      pktimestamp.getCurrentTimestamp(), eventId, intEventParam)
        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
        return None, 0
    except TYAssetNotEnoughException, e:
        return e.assetKind.kindId, e.required - e.actually

def _decodeContentItems(contentItems):
    ret = []
    genList = TYContentItemGenerator.decodeList(contentItems)
    for gen in genList:
        ret.append(gen.generate())
    return ret

