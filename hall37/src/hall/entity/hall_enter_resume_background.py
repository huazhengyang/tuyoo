# -*- coding=utf-8
'''
Created on 2016年9月5日
标记用户游戏前台/后台的状态

@author: zhaol
'''
from poker.entity.dao import onlinedata
from freetime.entity.msg import MsgPack
from poker.protocol import router

def enterBackGround(userId, gameId, clientId):
    '''
    用户离开了
    '''
    locList = onlinedata.getOnlineLocList(userId)
    for loc in locList:
        roomId, tableId, _ = loc
        
        mo = MsgPack()
        mo.setCmd('table_manage')
        mo.setAction('enter_background')
        mo.setParam('userId', userId)
        mo.setParam('clientId', clientId)
        mo.setParam('roomId', roomId)
        mo.setParam('tableId', tableId)
        router.sendTableServer(mo, roomId)

def resumeForeGround(userId, gameId, clientId):
    '''
    用户回来了
    '''
    locList = onlinedata.getOnlineLocList(userId)
    for loc in locList:
        roomId, tableId, _ = loc
        
        mo = MsgPack()
        mo.setCmd('table_manage')
        mo.setAction('resume_foreground')
        mo.setParam('userId', userId)
        mo.setParam('clientId', clientId)
        mo.setParam('roomId', roomId)
        mo.setParam('tableId', tableId)
        router.sendTableServer(mo, roomId)        
        
