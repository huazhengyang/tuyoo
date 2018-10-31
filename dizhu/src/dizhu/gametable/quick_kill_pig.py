# -*- coding=utf-8 -*-

from freetime.util import log as ftlog
from poker.entity.dao import sessiondata, gamedata
from dizhu.gametable.dizhu_table import DizhuTable
from poker.util import strutil

def isWaitPigTable(userId, killPigLevel, room, tableId) :
    ftlog.info('isWaitPigTable->', userId, killPigLevel, tableId)
    roomId = strutil.getTableRoomId(tableId)
    uids = DizhuTable.getSavedSeatUserId(room.tableConf['maxSeatN'], roomId, tableId)
    alist = [userId]
    for uid in uids :
        if uid > 0 and uid not in alist :
            alist.append(uid)
    ftlog.debug('isWaitPigTable->uids=', alist)
    return checkIsKillPig(tableId, killPigLevel, alist)


def checkIsKillPig(tableId, killPigLevel, userIds):
    try:
        ftlog.info('checkIsKillPig->', tableId, killPigLevel, userIds)
        lcount = 0
        devids = set()
        ips = set()
        for userId in userIds :
            devId = sessiondata.getDeviceId(userId)
            ip = sessiondata.getClientIp(userId)
            score = gamedata.getGameAttrInt(userId, 6, 'skillscore')
            if score < killPigLevel :
                lcount += 1
            devids.add(devId)
            ips.add(ip)
            ftlog.info('checkIsKillPig->uid=', userId, 'level=', killPigLevel, 'score=', score, 'ip=', ip, 'devid=', devId)

        if lcount >= 2 :
            ftlog.info('checkIsKillPig-> is pig level !!')
            return 1
    
        if len(devids) != len(userIds) :
            ftlog.info('checkIsKillPig-> is pig devids !!')
            return 1

        if len(ips) != len(userIds) :
            ftlog.info('checkIsKillPig-> is pig ip !!')
            return 1
    
    except:
        ftlog.error()

    return 0

