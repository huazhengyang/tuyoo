# -*- coding:utf-8 -*-
# author: wangzhiyao

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import router
from poker.entity.dao import userdata
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils

HALL_ID = 9999

def sendChipExpNotify(gameId, userId, chip_exp, before_chip_exp=0, now_chip_level=0, level=0):
    ftlog.debug('sendChipExpNotify userId:', userId, 'chip_exp:', chip_exp)

    mo = makeChipExpNotifyMsg(gameId, userId, chip_exp, before_chip_exp,  now_chip_level, level)
    # mo是返回
    userdata.setAttr(userId, 'chip_level', level)
    ftlog.debug('sendChipExpNotify mo:', mo)
    router.sendToUser(mo, userId)

    sendLevelUpToHallTask(userId, level, now_chip_level)


def makeChipExpNotifyMsg(gameId, userId, chip_exp, before_chip_exp,  now_chip_level, level):
    msg = MsgPack()
    msg.setCmd('update_chipexp')
    msg.setResult('gameId', gameId)
    msg.setResult('userId', userId)
    msg.setResult('chip_exp', chip_exp)
    msg.setResult('before_chip_exp', before_chip_exp)
    msg.setResult('before_chip_level', now_chip_level)
    msg.setResult('level', level)
    if level - now_chip_level > 0:
        msg.setResult('levelup', 1)
    else:
        msg.setResult('levelup', 0)
    return msg


def sendLevelUpToHallTask(userId, level, now_chip_level):
    try:
        level_upgrade = int(level) - int(now_chip_level)
        if level_upgrade >= 1:
            params = {
                    "user_id": userId,
                    "count": level_upgrade,
            }
            cmd = 'GM_LEVEL_UPGRADE'
            msg = TYPluginUtils.updateMsg(cmd=cmd, params=params)
            TYPluginCenter.event(msg, HALL_ID)
    except Exception as e:
        ftlog.debug('onEvUserChipExp: levelUpdate to hall, e=', e)
