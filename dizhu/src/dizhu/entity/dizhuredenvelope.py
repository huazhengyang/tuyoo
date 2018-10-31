# -*- coding:utf-8 -*-
'''
Created on 2016年7月18日

@author: zhaojiangang
'''

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from hall.entity.hallconf import HALL_GAMEID
from poker.util import strutil


_itemConfList = [
    {
        "itemId":1083,
        "playModes":["123"],
        "winTimes":10
    },
    {
        "itemId":1085,
        "playModes":["happy"],
        "winTimes":10
    },
    {
        "itemId":1086,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    },
    {
        "itemId":1087,
        "playModes":["123"],
        "winTimes":10
    },
    {
        "itemId":4266,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1180,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1181,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1182,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1183,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":2170,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    },
    {
        "itemId":2111,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    },
    {
        "itemId":2231,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    }
]

def _onTableWinlose(event):
    status = gamedata.getGameAttrJson(event.userId, DIZHU_GAMEID, 'item.win.progress', {})
    if ftlog.is_debug():
        ftlog.debug('dizhuredenvelope._onTableWinlose userId=', event.userId,
                    'status=', status)
    if event.winlose.isWin:
        changed = False
        roomConf = gdata.getRoomConfigure(event.roomId)
        playMode = roomConf.get('playMode')
        for itemConf in _itemConfList:
            if not itemConf['playModes'] or playMode in itemConf['playModes']:
                changed = True
                itemId = str(itemConf['itemId'])
                winTimes = itemConf['winTimes']
                progress = status.get(itemId, 0) + 1
                status[itemId] = progress
                if progress >= winTimes:
                    flagName = 'item.open.flag:%s' % (itemId)
                    gamedata.setnxGameAttr(event.userId, HALL_GAMEID, flagName, 1)
        if changed:
            gamedata.setGameAttr(event.userId, DIZHU_GAMEID, 'item.win.progress', strutil.dumps(status))
        if ftlog.is_debug():
            ftlog.debug('dizhuredenvelope._onTableWinlose userId=', event.userId,
                        'status=', status,
                        'changed=', changed)

def _initialize():
    from dizhu.game import TGDizhu
    ftlog.debug('dizhuredenvelope._initialize')
    TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, _onTableWinlose)

