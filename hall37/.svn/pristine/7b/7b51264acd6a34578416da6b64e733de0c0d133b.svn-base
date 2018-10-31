# -*- coding:utf-8 -*-
from poker.entity.biz import bireport
import freetime.util.log as ftlog
from poker.entity.events.tyevent import EventUserLogin

_inited = False

cmdMap = {
    '邀请':1,
    '开桌':2,
    '分享':3,
    '夺宝':4
}

def getStaticslist(userId, clipboard):
    listStatics = []
    # 时间 2018/3/2 10:00:00  参数:1 新用户id:uid 分享者uid:uid 分享者cid:cid sharedId:shareid
    if clipboard.urlParams and clipboard.cmd: 
        param = cmdMap.get(clipboard.cmd, 0)
        times = clipboard.urlParams.get('time') 
        uid = clipboard.urlParams.get('uid')
        cid = clipboard.urlParams.get('cid')
        shareId = clipboard.urlParams.get('shareId')
        
        if times and param and uid and cid and shareId:
            listStatics.append(int(times))
            listStatics.append(int(param))
            listStatics.append(userId)
            listStatics.append(int(uid))
            listStatics.append(int(cid))
            listStatics.append(int(shareId))
        
    if ftlog.is_debug():
        ftlog.debug('hall_statics.getStaticslist',
                    'userId=', userId,
                    'params=', clipboard.urlParams,
                    'listStatics=', listStatics)

    return listStatics

    
def _onUserLogin(event):
    if _inited and event.clipboard:
        listRes = getStaticslist(event.userId, event.clipboard)
        if listRes:
            bireport.reportGameEvent('CLIPBOARD_STATICS', event.userId, event.gameId, 
                                     0, 0, 0, 0, 0, 0, listRes, event.clientId, 0, 0, 0, 0, 0)
    
    
def _initialize():
    global _inited
    if not _inited:
        _inited = True
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(EventUserLogin, _onUserLogin)  


