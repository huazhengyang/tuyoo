# -*- coding:utf-8 -*-
'''
Created on 2018年04月07日

@author: zhaoliang
'''
from poker.entity.game.tables.table_player import TYPlayer
from freetime.util import log as ftlog
from dizhu.servers.util.rpc import table_winlose

def doTableGameStartGT(roomId, tableId, roundId, dizhuUserId, baseCardType, roomMutil, basebet, basemulti, userIds):
    # 触发游戏开始的事件, 在此事件监听中处理用户的winrate以及其他任务或属性的调整和设定
    # 更新宝箱的状态
    tbinfos = {}
    datas = {'tbinfos':tbinfos}
    for userId in userIds:
        if TYPlayer.isRobot(userId):
            continue
        
        try:
            tbinfo = table_winlose._doTableGameStartUT1(userId, roomId, tableId, dizhuUserId, baseCardType, roomMutil, basebet, basemulti)
            tbinfos.update(tbinfo)
        except:
            ftlog.error('table_winlose.doTableGameStartGT userId=', userId,
                        'roomId=', roomId,
                        'tableId=', tableId)
    return datas

table_winlose.doTableGameStartGT = doTableGameStartGT