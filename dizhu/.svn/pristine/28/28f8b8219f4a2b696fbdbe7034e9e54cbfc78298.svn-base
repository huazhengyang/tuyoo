'''
Created on Feb 2, 2015

@author: hanwenfang
'''
'''
表情管理
'''   

from dizhu.entity import dizhuconf
import freetime.util.log as ftlog
from hall.entity import hallvip


def getConfDict(bigRoomId, uid):
    level = 0
    userVip = hallvip.userVipSystem.getUserVip(uid)
    if userVip :
        level = userVip.vipLevel.level
    conf = dizhuconf.getTableSmilesInfo(bigRoomId, level)
    ftlog.debug('smile.getConfDict', bigRoomId, uid, level, conf)
    return conf

# def statistics(uid, smilies, roomid, price):
#     TyContext.BiReport.gcoin('out.smilies.' + smilies + '.' + str(roomid), 6, price)
#     ftlog.info('GameTable->SmiliesManager', uid, roomid, smilies, price)

