# -*- coding=utf-8
'''
Created on 2015年8月12日

@author: zhaojiangang
'''

import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem, datachangenotify, sdkclient
from poker.entity.dao import userdata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp


_inited = False
stringRenameDesc = ''
stringRenameDescFirst = ''
stringRenameCardRequired = ''
stringRenameSuccessed = ''
stringRenameContainsSensitive = ''
payOrder = None

def _reloadConf():
    global stringRenameDesc
    global stringRenameDescFirst
    global stringRenameCardRequired
    global stringRenameSuccessed
    global stringRenameContainsSensitive
    global payOrder
    conf = hallconf.getRenameConf()
    strings = conf.get('strings', {})
    stringRenameDesc = strings.get('string.rename.desc', '')
    stringRenameDescFirst = strings.get('string.rename.desc.first', '')
    stringRenameCardRequired = strings.get('string.renameCard.required', '')
    stringRenameSuccessed = strings.get('string.rename.successed', '')
    stringRenameContainsSensitive = strings.get('string.rename.contains.sensitive', '')
    payOrder = conf.get('payOrder', {})
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:rename:0'):
        ftlog.debug('hallrename._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hallrename._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallrename._initialize end')

def getRenameSum(gameId, userId):
    return userdata.getAttr(userId, 'set_name_sum')

def checkRename(gameId, userId):
    #set_name_sum
    setNameSum = userdata.getAttr(userId, 'set_name_sum')
    if not setNameSum:
        # 第一次改名，直接改
        return True, stringRenameDescFirst
    else:
        # 第一次以后需要消耗1张改名卡
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        if userAssets.balance(gameId, hallitem.ASSET_RENAME_CARD_KIND_ID, timestamp) > 0:
            return True, stringRenameDesc
        return False, stringRenameCardRequired

SDK_UNIQUE_NAME = 1

def _rename(gameId, userId, newName):
    if SDK_UNIQUE_NAME :
        params = {'userId' : userId, 'userName' : newName}
        sdkres = sdkclient._requestSdk('/open/v4/user/changeName', params, needresponse=1)
        ftlog.debug('hallrename._rename->', sdkres)
        if isinstance(sdkres, dict) :
            result = sdkres.get('result', {})
            code = result.get('code', -1)
            info = result.get('info', '改名失败，请重试')
            return code, info
        return -1, '改名失败，请重试.'
    else:
        userdata.setAttr(userId, 'name', newName)
        return 0, ''

def tryRename(gameId, userId, newName):
    consumeCount = 0
    oldName, setNameSum = userdata.getAttrs(userId, ['name', 'set_name_sum'])
    if ftlog.is_debug():
        ftlog.info('hallrename.tryRename gameId=', gameId, 'setNameSum=', setNameSum,
                           'userId=', userId, 'oldName=', oldName, 'newName=', newName, )
    if oldName == newName :
        if ftlog.is_debug():
            ftlog.info('hallrename.tryRename gameId=', gameId,
                           'userId=', userId, 'name not changed !')
        return -3, 'not changed'

    setNameSum = userdata.incrAttr(userId, 'set_name_sum', 1)
    if setNameSum > 1:
        # 消耗一个改名卡
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _, consumeCount, final = userAssets.consumeAsset(gameId, hallitem.ASSET_RENAME_CARD_KIND_ID, 1,
                                                         timestamp, 'USER_RENAME', 0)
        if consumeCount < 1:
            if ftlog.is_debug():
                ftlog.info('hallrename.tryRename gameId=', gameId,
                           'userId=', userId, 'no rename card !')
            return -2, 'no rename card'

        ftlog.info('hallrename.tryRename gameId=', gameId,
                   'userId=', userId,
                   'newName=', newName,
                   'consumeCount=', consumeCount,
                   'setNameSum=', setNameSum,
                   'final=', final)
    code, info = _rename(gameId, userId, newName)
    if code != 0 and consumeCount > 0 :
        # 改名失败，退回改名卡
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _, addCount, final = userAssets.addAsset(gameId, hallitem.ASSET_RENAME_CARD_KIND_ID, 1, timestamp, 'USER_RENAME', 0)
        ftlog.info('hallrename.tryRename rollback gameId=', gameId,
                   'userId=', userId,
                   'newName=', newName,
                   'addCount=', addCount,
                   'setNameSum=', setNameSum,
                   'final=', final)
    if code != 0 and setNameSum == 1 :
        # 第一次修改失败，退回
        userdata.incrAttr(userId, 'set_name_sum', -1)

    datachangenotify.sendDataChangeNotify(gameId, userId, ['item', 'udata'])

    return code, info
        


