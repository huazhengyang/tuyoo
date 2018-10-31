# -*- coding:utf-8 -*-
'''
Created on 2017年9月20日

@author: wangjifa
'''

from dizhu.tupt.ob import obsystem
import freetime.util.log as ftlog

def _getMixRoomId(table, result):
    if not result.dizhuStatement:
        return None
    return result.dizhuStatement.seat.player.mixConf.get('roomId') if table.room.roomConf.get('isMix') else None

obsystem._getMixRoomId = _getMixRoomId
ftlog.info("h_2017_9_21_obsystem hotfix ok")