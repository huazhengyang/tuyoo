# -*- coding=utf-8
'''
Created on 2015年10月15日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallitem
from poker.entity.dao import sessiondata


def _conform(self, gameId, userAssets, item, timestamp, params):
    from poker.entity.game.game import TYGame
    userId = userAssets.userId
    clientId = sessiondata.getClientId(userId)
    dashifen = TYGame(self.gameId).getDaShiFen(userId, clientId)
    level = dashifen.get('level', 0) if dashifen else 0
    
    if ftlog.is_debug():
        ftlog.debug('ItemActionConditionGameDashifenLevel._conform gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'selfGameId=', self.gameId,
                    'dashifen=', dashifen,
                    'level=', level,
                    'minLevel=', self.minLevel,
                    'maxLevel=', self.maxLevel)
        
    return (self.minLevel == -1 or level >= self.minLevel) \
        and (self.maxLevel == -1 or level < self.maxLevel)

hallitem.ItemActionConditionGameDashifenLevel._conform = _conform
