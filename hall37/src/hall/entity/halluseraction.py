# -*- coding=utf-8
'''
Created on 2015年8月25日
用户行为

@author: zhaoliang
'''
from sre_compile import isstring
from poker.entity.biz.confobj import TYConfableRegister, TYConfable
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.dao import gamedata

class UserAction(TYConfable):
    def doAction(self, gameId, userId, clientId, timestamp, **kwargs):
        raise NotImplemented()


class UserActionSetGameData(UserAction):
    TYPE_ID = 'user.action.set.gamedata'

    def __init__(self):
        super(UserActionSetGameData, self).__init__()

    def doAction(self, gameId, userId, clientId, timestamp, **kwargs):
        '''
        按照配置设置gamedata
        '''
        gamedata.setGameAttr(userId, self.gameId, self.key, self.value)

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', 0)
        if (not isinstance(self.gameId, int)) or (self.gameId <= 0):
            raise TYBizConfException(d, 'UserActionSetGameData.gameId must be int > 0')
        
        self.key = d.get('key', None)
        if (not isstring(self.key)) or (not self.key):
            raise TYBizConfException(d, 'UserActionSetGameData.key must be valid string')
        
        self.value = d.get('value', None)
        if (not isstring(self.value)) or (not self.value):
            raise TYBizConfException(d, 'UserActionSetGameData.value must be valid string')
        
        return self

class UserActionRegister(TYConfableRegister):
    _typeid_clz_map = {
        # 设置GAMEDATA
        UserActionSetGameData.TYPE_ID: UserActionSetGameData,
    }

if __name__ == '__main__':
    pass

