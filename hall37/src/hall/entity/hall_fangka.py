# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaojiangang
'''
from hall.entity import hallconf
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router

def queryFangKaItem(gameId, userId, clientId):
    '''
    @return: 房卡道具ID
    '''
    item = hallconf.getClientFangKaConf(clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_fangka.queryFangKaItem gameId:', gameId
                    , ' userId:', userId
                    , ' clientId:', clientId
                    , ' fangkaItem:', item)

    return item

def sendFangKaItemToClient(gameId, userId, clientId):
    item = queryFangKaItem(gameId, userId, clientId)
    if item:
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'get_fangka_item')
        mo.setResult('gameId', gameId)
        mo.setResult('fangKa', item)
        router.sendToUser(mo, userId)
    return item