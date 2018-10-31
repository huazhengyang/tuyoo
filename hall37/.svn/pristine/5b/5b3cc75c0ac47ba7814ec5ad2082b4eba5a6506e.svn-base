# -*- coding=utf-8
'''
Created on 2016年11月14日

@author: zhaol
'''
from hall.entity import hallconf
import freetime.util.log as ftlog

def queryWXAppid(gameId, userId, clientId):
    '''
    @return: 查询红包发奖的微信APPID
    '''
    wxConfig = hallconf.getWXAppidConf(clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_wxappid.queryWXAppid gameId:', gameId
            , ' userId:', userId
            , ' clientId:', clientId
            , ' wxConfig:', wxConfig)
    
    return wxConfig
