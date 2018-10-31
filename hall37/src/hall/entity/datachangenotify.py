# -*- coding=utf-8
'''
Created on 2015年7月28日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from poker.protocol import router
# from hall.entity.hallconf import HALL_GAMEID


_notify_map = {
    'chip':['udata', 'gdata'],
    'item':['item'],
    'coupon':['udata'],
    'diamond':['udata'],
    'udata':['udata'],
    'gdata':['gdata'],
    'assistance':['udata'],
    'promotion_loc':['promotion_loc'],
    'vip':['udata'],
    'charm':['udata']
}

def sendDataChangeNotify(gameId, userId, changedDataNames):
    if changedDataNames:
        mo = makeDataChangeNotifyMsg(gameId, userId, changedDataNames)
        router.sendToUser(mo, userId)

def makeDataChangeNotifyMsg(gameId, userId, changedDataNames):
    msg = MsgPack()
    msg.setCmd('update_notify')
    msg.setResult('gameId', gameId)
    msg.setResult('userId', userId)
    msg.setResult('changes', list(translateChangeDataNames(changedDataNames)))
    return msg

def translateChangeDataNames(changedDataNames):
    changes = set()
    if not isinstance(changedDataNames, (list, set)):
        changedDataNames = [changedDataNames] 
    for c in changedDataNames:
        if c in _notify_map:
            changes.update(_notify_map[c])
        else:
            changes.add(c)
    return changes


# def pushDetalNotifyOfChip(userId, finalChip):
#     msg = MsgPack()
#     msg.setCmd('user_info')
#     msg.setResult('gameId', HALL_GAMEID)
#     msg.setResult('userId', userId)
#     msg.setResult('detal_update', 1)
#     msg.setResult('udata', {'chip' : finalChip})
#     router.sendToUser(msg, userId)


if __name__ == '__main__':
    print _notify_map
    print translateChangeDataNames('item')
    
    
    

