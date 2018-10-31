# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from freetime.util.metaclasses import Singleton
from hall.entity import halluser
from hall.entity.todotask import TodoTaskHelper
from poker.entity.game.game import TYGame
from poker.protocol import router


class UtilHelper(object):


    __metaclass__ = Singleton

    addictionTime = {
        'warn':9000,
        'kick':10800
    }

    def __init__(self):
        pass


    def sendUserInfoResponse(self, userId, gameId, clientId, loc, isudata, isgdata):
        '''
        仅发送user_info命令, USER的主账户信息和游戏账户信息至客户端
        '''
        mo = MsgPack()
        if isudata :
            mo.setCmd('user_info')
        else:
            mo.setCmd('game_data')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        if isudata :
            if self.addictionTime:
                mo.setResult('addictionTime', self.addictionTime)
            mo.setResult('udata', halluser.getUserInfo(userId, gameId, clientId))
            if loc :
                mo.setResult('loc', loc)
        if isgdata :
            mo.setResult('gdata', halluser.getGameInfo(userId, gameId, clientId))
        router.sendToUser(mo, userId)

    def sendTodoTaskResponse(self, userId, gameId, clientId, isdayfirst):
        '''
        发送当前用户的TODOtask列表消息
        '''
        ftlog.debug('UtilHelper.sendTodoTaskResponse userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'isdayfirst=', isdayfirst)
        # 3.7 - 4.56版本走这里的登录弹窗
        todotasks = TYGame(gameId).getTodoTasksAfterLogin(userId, gameId, clientId, isdayfirst)
        if todotasks:
            TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)
