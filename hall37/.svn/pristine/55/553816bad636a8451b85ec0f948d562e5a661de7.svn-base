# -*- coding: utf-8 -*-
import freetime.util.log as ftlog
import hall_friend_table
from poker.entity.game.game import TYGame
from hall.entity.hallevent import EventAfterUserLogin

def hasLoc(loc):
    return loc and '0.0.0.0' != loc

def _onUserAfterLogin(event):
    if event.clipboard and event.clipboard.cmd == '开桌' and not hasLoc(event.loc):
        if ftlog.is_debug():
            ftlog.debug('hall_joinfriendgame._onUserAfterLogin',
                        'userId=', event.userId,
                        'clipboard=', event.clipboard.content)
        
        ftId = event.clipboard.urlParams.get('ftId')
        if ftId:
            pluginId = hall_friend_table.queryFriendTable(ftId)
            TYGame(pluginId).enterFriendTable(event.userId, event.gameId, event.clientId, ftId)

 
def _initialize():
    from hall.game import TGHall
    TGHall.getEventBus().subscribe(EventAfterUserLogin, _onUserAfterLogin)


