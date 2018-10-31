# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.game.game import TYGame
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class RobotTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    

    def _check_param_userCount(self, msg, key, params):
        userCount = msg.getParam(key)
        if isinstance(userCount, int) and userCount >= 0:
            return None, userCount
        return 'ERROR of userCount !' + str(userCount), None


    def _check_param_seatCount(self, msg, key, params):
        seatCount = msg.getParam(key)
        if isinstance(seatCount, int) and seatCount > 0:
            return None, seatCount
        return 'ERROR of seatCount !' + str(seatCount), None


    def _check_param_users(self, msg, key, params):
        users = msg.getParam(key)
        if isinstance(users, (list, tuple)) and len(users) > 0 :
            return None, users
        return 'ERROR of users !' + str(users), None


    @markCmdActionMethod(cmd='robotmgr', action='callup', clientIdVer=0, lockParamName='tableId')
    def doRobotCallUp(self, gameId, roomId0, tableId0, userCount, seatCount, users):
        '''
        桌子上有人坐下, 唤醒机器人
        '''
        rmgr = TYGame(gameId).getRobotManager()
        if rmgr :
            msg = runcmd.getMsgPack()
            rmgr.callUpRobot(msg, roomId0, tableId0, userCount, seatCount, users)
    

    @markCmdActionMethod(cmd='robotmgr', action='callmatch', clientIdVer=0, lockParamName='roomId')
    def doRobotCallMatch(self, gameId, roomId0):
        '''
        比赛开始阶段, 唤醒比赛机器人
        '''
        ftlog.debug("<<")
        rmgr = TYGame(gameId).getRobotManager()
        if rmgr :
            msg = runcmd.getMsgPack()
            robotCount = msg.getParam("robotCount")
            rmgr.callUpRobotsToMatch(msg, roomId0, robotCount)


    @markCmdActionMethod(cmd='robotmgr', action='shutdown', clientIdVer=0, lockParamName='tableId')
    def doRobotShutDown(self, gameId, roomId0, tableId0, userCount, seatCount, users):
        '''
        桌子上有人站起, 关闭机器人
        '''
        rmgr = TYGame(gameId).getRobotManager()
        if rmgr :
            msg = runcmd.getMsgPack()
            rmgr.shutDownRobot(msg, roomId0, tableId0, userCount, seatCount, users)


    @markCmdActionMethod(cmd='robotmgr', action='detail', clientIdVer=0, lockParamName='')
    def doRobotDetailInfo(self, gameId):
        '''
        查询机器人管理器的详细信息
        '''
        rmgr = TYGame(gameId).getRobotManager()
        datas = {}
        if rmgr :
            msg = runcmd.getMsgPack()
            datas = rmgr.getRobotDetail(msg)
        if router.isQuery() :
            mo = MsgPack()
            mo.setCmdAction('robotmgr', 'detail')
            mo.setResult('detail', datas)
            router.responseQurery(mo)


