# -*- coding=utf-8
'''
Created on 2015年6月3日

@author: zhaoqh
'''
import freetime.util.log as ftlog
from poker.entity.biz import integrate
from poker.util import timestamp


def _initialize():
    pass

def reportChatLog(userId, message, gameId, roomId, tableId, seatId=0, *argl, **argd):
    if integrate.isEnabled('chatlog') :
        try:
            datas = {'uid' : userId,
                     'gid' : gameId,
                     'rid' : roomId,
                     'tid' : tableId,
                     'sid' : seatId,
                     'msg' : message,
                     'time' : timestamp.formatTimeMs(),
                     'argl' : argl,
                     'argd' : argd
                     }
            integrate.sendTo('chatlog', datas)
        except:
            ftlog.error()

