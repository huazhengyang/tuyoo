# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh, Zhouhao
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz import bireport
from poker.entity.dao import gamedata
from poker.util import strutil


@markCmdActionHandler
class RoomTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        pass

    @markCmdActionMethod(cmd='room', action="enter", clientIdVer=0)
    def doRoomEnter(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doEnter(userId)

    @markCmdActionMethod(cmd='room', action="leave", clientIdVer=0)
    def doRoomLeave(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doLeave(userId, msg)

    @markCmdActionMethod(cmd='room', action="quick_start", clientIdVer=0)
    def doRoomQuickStart(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doQuickStart(msg)
        if router.isQuery():
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, '', str(userId))

    def _check_param_signinParams(self, msg, key, params):
        signinParams = msg.getParam(key)
        if signinParams and not isinstance(signinParams, dict):
            return 'ERROR of signinParams !' + str(signinParams), None
        return None, signinParams

    @markCmdActionMethod(cmd='room', action="signin", clientIdVer=0)
    def doRoomSigIn(self, roomId, userId, signinParams):
        msg = runcmd.getMsgPack()
        if ftlog.is_debug():
            ftlog.debug('msg=', msg, 'mode=', gdata.mode(),
                        caller=self)
        if not signinParams and gdata.enableTestHtml():
            room = gdata.rooms()[roomId]
            signinParams = gamedata.getGameAttrJson(userId, room.gameId, 'test.signinParams')

        gdata.rooms()[roomId].doSignin(userId, signinParams)

    @markCmdActionMethod(cmd='room', action="signout", clientIdVer=0)
    def doRoomSigOut(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doSignout(userId)

    @markCmdActionMethod(cmd='room', action="giveup", clientIdVer=0)
    def doRoomGiveup(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGiveup(userId)
        
    @markCmdActionMethod(cmd='room', action="match_giveup", clientIdVer=0)
    def doMatchRoomGiveup(self, userId, gameId, roomId, matchId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchGiveup(userId, gameId, roomId, matchId, msg)
        
    @markCmdActionMethod(cmd='room', action="save", clientIdVer=0)
    def doMatchSave(self, userId, gameId, roomId, matchId):
        '''
        保存比赛进度
        '''
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchSave(userId, gameId, roomId, matchId, msg)
        
    @markCmdActionMethod(cmd='room', action="resume", clientIdVer=0)
    def doMatchResume(self, userId, gameId, roomId, matchId):
        '''
        保存比赛进度
        '''
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchResume(userId, gameId, roomId, matchId, msg)

    @markCmdActionMethod(cmd='room', action="update", clientIdVer=0)
    def doRoomUpdate(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doUpdateInfo(userId)

    @markCmdActionMethod(cmd='room', action="des", clientIdVer=0)
    def doRoomDes(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGetDescription(userId)

    @markCmdActionMethod(cmd='room', action="match_des", clientIdVer=0)
    def doRoomMatchDes(self, userId, gameId, roomId, matchId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGetMatchDescription(userId, gameId, roomId, matchId, msg)
        
    @markCmdActionMethod(cmd='room', action="match_challenge", clientIdVer=0)
    def doMatchChallenge(self, userId, gameId, roomId, matchId):
        '''
        开始挑战
        '''
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchChallenge(userId, gameId, roomId, matchId, msg)
        
    @markCmdActionMethod(cmd='room', action="match_back", clientIdVer=0)
    def doMatchBack(self, userId, gameId, roomId, matchId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchBack(userId, gameId, roomId, matchId, msg)
        
    @markCmdActionMethod(cmd='room', action="m_winlose", clientIdVer=0, lockParamName='')
    def doRoomMatchWinLose(self, roomId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doWinlose(msg)
        
    @markCmdActionMethod(cmd='room', action="m_matchTableError", clientIdVer=0, lockParamName='')
    def doRoomMatcTablehError(self, roomId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchTableError(msg)    

    @markCmdActionMethod(cmd='room', action="adjust_table_players", clientIdVer=0, lockParamName='roomId')
    def doRoomAdjustTablePlayers(self, roomId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doAdjustTablePlayers(msg)

    @markCmdActionMethod(cmd='room', action="return_queue", clientIdVer=0, lockParamName='')
    def doRoomReturnQueue(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doReturnQueue(userId)
        mo = MsgPack()
        mo.setCmd('room')
        mo.setResult('action', 'return_queue')
        router.responseQurery(mo)

    @markCmdActionMethod(cmd='room', action="result_list", clientIdVer=0)
    def doRoomResultList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doRoomResultList, msg=', msg, caller=self)
        return runcmd.newOkMsgPack(code=1)

    @markCmdActionMethod(cmd='room', action="match_list", clientIdVer=0)
    def doRoomMatchList(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        page = msg.getParam("page", 0)
        num = msg.getParam("number", 0)
        tag = msg.getParam("tag", "all")
        gdata.rooms()[roomId].doGetMatchList(userId, page, num, tag)

    @markCmdActionMethod(cmd='room', action="rank_list", clientIdVer=0)
    def doRoomRankList(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGetRankList(userId, msg)

    @markCmdActionMethod(cmd='room', action="update_rank_all", clientIdVer=0, lockParamName='')
    def doRoomUpdateRankOfAll(self, roomId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doRoomUpdateRankOfAll()

    @markCmdActionMethod(cmd='room', action="leave_match", clientIdVer=0)
    def doRoomLeaveMatch(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        tableId = msg.getParam("tableId", 0)
        gdata.rooms()[roomId].doLeaveMatch(userId, tableId)
        mo = MsgPack()
        mo.setCmd('room')
        mo.setResult('action', 'leave_match')
        router.responseQurery(mo)

    @markCmdActionMethod(cmd='room', action="event", clientIdVer=0)
    def doRoomEvent(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doRoomEvent, msg=', msg, caller=self)
        return runcmd.newOkMsgPack(code=1)

    @markCmdActionMethod(cmd='room', action="state", clientIdVer=0)
    def doRoomState(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doRoomState, msg=', msg, caller=self)
        return runcmd.newOkMsgPack(code=1)

    @markCmdActionMethod(cmd='room', action="create_table", clientIdVer=0)
    def doRoomCreateTable(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doRoomCreateTable, msg=', msg, caller=self)
        return runcmd.newOkMsgPack(code=1)

    @markCmdActionMethod(cmd='room', action="detail_infos", clientIdVer=0, lockParamName='')
    def getRoomOnlineInfoDetails(self, roomId):
        msg = runcmd.getMsgPack()
        cp = gdata.curProcess.cpu_percent()
        datas = {'cpu': cp}
        if roomId in gdata.rooms():
            room = gdata.rooms()[roomId]
            ucount, pcount, users = room.getRoomOnlineInfoDetail()
            datas[roomId] = [ucount, pcount, users]
        else:
            datas[roomId] = 'not on this server'
        msg.setResult('datas', datas)
        return msg

    @markCmdActionMethod(cmd='room', action="get_match_buyin", clientIdVer=0)
    def doGetMatchBuyin(self, roomId, userId):
        # TODO
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGetMatchBuyin(userId)

    @markCmdActionMethod(cmd='room', action="match_buyin", clientIdVer=0)
    def doMatchBuyin(self, roomId, userId):
        # TODO
        msg = runcmd.getMsgPack()
        buy = msg.getParam('buy')
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doMatchBuyin(userId, buy)

    @markCmdActionMethod(cmd='room', action="try_notify_rebuy", clientIdVer=0, lockParamName='')
    def doTryNotifyRebuy(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        userId = msg.getParam("userId")
        ret = gdata.rooms()[roomId].doTryNotifyRebuy(userId)
        router.responseQurery(strutil.dumps({'ret': ret}))


def reportRoomOnlineInfos(event):
    if event.count % 10 != 0:
        return
    cp = gdata.curProcess.cpu_percent()
    for room in gdata.rooms().values():
        roomId = room.roomId
        gameId = room.gameId
        ucount, pcount, ocount = room.getRoomOnlineInfo()
        bireport.roomUserOnline(gameId, roomId, ucount, pcount, ocount, cp)
