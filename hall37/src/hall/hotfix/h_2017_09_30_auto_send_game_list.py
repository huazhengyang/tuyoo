# -*- coding:utf-8 -*-
'''
Created on 2017年9月30日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallgamelist, hallgamelist2
from hall.entity.todotask import TodoTaskHelper
from hall.servers.util.hall_handler import HallTcpHandler, HallHelper
from hall.servers.util.util_helper import UtilHelper
from poker.entity.game.game import TYGame
from poker.protocol import router


@classmethod
def sendHallGameList_handler(cls, userId, gameId, clientId):
    pages = hallgamelist.getGameList(gameId, userId, clientId)
    from hall.servers.util import gamelistipfilter
    _, pages, _ = gamelistipfilter.filtergamelist(0, [], pages, [], userId, clientId)
    mo = MsgPack()
    mo.setCmd('hall_game_list')
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('pages', pages)
    router.sendToUser(mo, userId)

@classmethod
def sendHallGameList2_handler(cls, userId, gameId, clientId):
    from poker.util import strutil
    _, clientVer, _ = strutil.parseClientId(clientId)
    template = hallgamelist2.getUITemplate(gameId, userId, clientId)
    if template is None:
        ftlog.exception('sendHallGameList2 error, please check clientId:', clientId)
    else:
        _games, pages, innerGames = HallHelper.encodeHallUITemplage2(gameId, userId, clientId, template)
        from hall.servers.util import gamelistipfilter
        _games, pages, innerGames = gamelistipfilter.filtergamelist(clientVer, _games, pages, innerGames, userId, clientId)
        mo = MsgPack()
        mo.setCmd('hall_game_list')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('games', _games)
        mo.setResult('pages', pages)
        if clientVer >= 3.76:
            mo.setResult('innerGames', innerGames)
        router.sendToUser(mo, userId)
        
        
HallTcpHandler.sendHallGameList = sendHallGameList_handler
HallTcpHandler.sendHallGameList2 = sendHallGameList2_handler


def sendTodoTaskResponse(self, userId, gameId, clientId, isdayfirst):
    '''
    发送当前用户的TODOtask列表消息
    '''
    ftlog.debug('UtilHelper.sendTodoTaskResponse userId=', userId,
                'gameId=', gameId,
                'clientId=', clientId,
                'isdayfirst=', isdayfirst)
    todotasks = TYGame(gameId).getTodoTasksAfterLogin(userId, gameId, clientId, isdayfirst)
    if todotasks:
        TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)

    self.sendHallGameList(userId, gameId, clientId, isdayfirst)

def needSendGameList(self, userId, gameId, clientId, isdayfirst):
    from poker.util import strutil
    from hall.entity import hallconf
    from hall.entity.hallconf import HALL_GAMEID
    from datetime import datetime
    
    if not isdayfirst or gameId != HALL_GAMEID:
        if ftlog.is_debug():
            ftlog.debug('UtilHelper.needSendGameList NotDayFirstOrHallGameId',
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'isdayfirst=', isdayfirst)
        return False
    
    autoSendGameList = hallconf.getPublicConf('autoSendGameList', {})
    if autoSendGameList.get('close', 0):
        if ftlog.is_debug():
            ftlog.debug('UtilHelper.needSendGameList Closed',
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'isdayfirst=', isdayfirst)
        return False
    
    games = autoSendGameList.get('games', [])
    if not games:
        if ftlog.is_debug():
            ftlog.debug('UtilHelper.needSendGameList NotConfGames',
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'isdayfirst=', isdayfirst)
        return False
    
    nowT = datetime.now()
    hallGameId = strutil.getGameIdFromHallClientId(clientId)
    for gameConf in games:
        if gameConf.get('gameId') == hallGameId:
            timeRange = gameConf.get('timeRange')
            if not timeRange:
                return True
            sTime = datetime.strptime(timeRange[0], '%Y-%m-%d %H:%M:%S')
            eTime = datetime.strptime(timeRange[1], '%Y-%m-%d %H:%M:%S')
            if nowT >= sTime and nowT < eTime:
                return True
            
            if ftlog.is_debug():
                ftlog.debug('UtilHelper.needSendGameList NotInTimeRange',
                            'userId=', userId,
                            'gameId=', gameId,
                            'clientId=', clientId,
                            'isdayfirst=', isdayfirst,
                            'timeRange=', timeRange)
            return False
    
    if ftlog.is_debug():
        ftlog.debug('UtilHelper.needSendGameList NotInGames',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'isdayfirst=', isdayfirst,
                    'timeRange=', timeRange)
        
    return False

def sendHallGameList(self, userId, gameId, clientId, isdayfirst):
    try:
        from poker.util import strutil
        from hall.servers.util.hall_handler import HallTcpHandler
        
        if self.needSendGameList(userId, gameId, clientId, isdayfirst):
            _, clientVer, _ = strutil.parseClientId(clientId)
            if clientVer >= 3.7:
                HallTcpHandler.sendHallGameList2(userId, gameId, clientId)
            else:
                HallTcpHandler.sendHallGameList(userId, gameId, clientId)

            ftlog.info('UtilHelper.sendHallGameList Sent',
                       'userId=', userId,
                       'gameId=', gameId,
                       'clientId=', clientId,
                       'isdayfirst=', isdayfirst)
        else:
            if ftlog.is_debug():
                ftlog.debug('UtilHelper.sendHallGameList NotNeedSend',
                            'userId=', userId,
                            'gameId=', gameId,
                            'clientId=', clientId,
                            'isdayfirst=', isdayfirst)
    except:
        ftlog.error('UtilHelper.sendHallGameList Exception',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'isdayfirst=', isdayfirst)

UtilHelper.needSendGameList = needSendGameList
UtilHelper.sendHallGameList = sendHallGameList
UtilHelper.sendTodoTaskResponse = sendTodoTaskResponse



