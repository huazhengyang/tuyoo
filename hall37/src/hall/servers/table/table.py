# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.events.tyevent import TableStandUpEvent
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class TableTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    

#     @markCmdActionMethod(cmd='room', action="enter", clientIdVer=0)
#     def doRoomEnter(self, roomId, userId):
#         msg = runcmd.getMsgPack()
#         ftlog.debug('msg=', msg, caller=self)
#         gdata.rooms()[roomId].doEnter(userId)
# 
# 
#     @markCmdActionMethod(cmd='room', action="leave", clientIdVer=0)
#     def doRoomLeave(self, roomId, userId):
#         msg = runcmd.getMsgPack()
#         ftlog.debug('msg=', msg, caller=self)
#         from poker.entity.game.rooms.room import TYRoom
#         reason = msg.getParam("reason", TYRoom.LEAVE_ROOM_REASON_ACTIVE)
#         assert isinstance(reason, int)
#         needSendRes = msg.getParam("needSendRes", True)
#         assert isinstance(needSendRes, bool)
#         gdata.rooms()[roomId].doLeave(userId, reason, needSendRes)


    @markCmdActionMethod(cmd='room', action="vipTableList", clientIdVer=0)
    def doRoomVipTableList(self, roomId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGetVipTableList(userId, clientId)


    @markCmdActionMethod(cmd='room', action="playingTableList", clientIdVer=0, lockParamName="")
    def doRoomGetPlayingTableList(self, roomId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        result = gdata.rooms()[roomId].doGetPlayingTableList()
        if router.isQuery() :
            mo = MsgPack()
            mo.setCmd("room")
            mo.setResult("action", "playingTableList")
            mo.updateResult(result)
            router.responseQurery(mo)


    @markCmdActionMethod(cmd='room', action="rank_list", clientIdVer=0)
    def doRoomRankList(self, roomId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doGetRankList(userId, msg)
        
    
    @markCmdActionMethod(cmd='room', action="change_betsConf", clientIdVer=0, lockParamName="")
    def doRoomChangeBetsConf(self, roomId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        betsConf = msg.getParam("betsConf")
        gdata.rooms()[roomId].doChangeBetsConf(betsConf)

        
    @markCmdActionMethod(cmd='table', action="enter", clientIdVer=0)
    def doTableEnter(self, userId, roomId, tableId, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        table.doEnter(msg, userId, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))


    @markCmdActionMethod(cmd='table', action="leave", clientIdVer=0)
    def doTableLeave(self, userId, roomId, tableId, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        table.doLeave(msg, userId, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))


    @markCmdActionMethod(cmd='table', action="sit", clientIdVer=0)
    def doTableSit(self, userId, roomId, tableId, seatId0, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        table.doSit(msg, userId, seatId0, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))


    @markCmdActionMethod(cmd='table', action="stand_up", clientIdVer=0)
    def doTableStandUp(self, userId, roomId, tableId, seatId, clientId):
        '''
        此命令一定是由客户端发送的命令, 如果是内部控制命令,那么需要进行区分命令,不能混合调用
        主要是为了避免站起的原因混乱,
        '''
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        table.doStandUp(msg, userId, roomId, tableId, seatId, TableStandUpEvent.REASON_USER_CLICK_BUTTON, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))


    @markCmdActionMethod(cmd='table', action="info", clientIdVer=0)
    def doTableInfo(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTableInfo, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='table', action="change", clientIdVer=0)
    def doTableChange(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTableChange, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='table_call', action='*', clientIdVer=0)
    def doTableCall(self, userId, roomId, tableId, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        action = msg.getParam('action')
        seatId = msg.getParam('seatId', -1) # 旁观时没有seatId参数
        assert isinstance(seatId, int)
        table.doTableCall(msg, userId, seatId, action, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))


    @markCmdActionMethod(cmd='table_manage', action='*', clientIdVer=0, lockParamName='')
    def doTableManage(self, roomId, tableId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        action = msg.getParam('action')
        result = table.doTableManage(msg, action)
        if router.isQuery() :
            mo = MsgPack()
            mo.setCmd('table_manage')
            mo.setResult('action', action)
            mo.updateResult(result)
            router.responseQurery(mo)


    @markCmdActionMethod(cmd='room', action="detail_infos", clientIdVer=0, lockParamName='')
    def getRoomOnlineInfoDetails(self, roomId):
        msg = runcmd.getMsgPack()
        cp = gdata.curProcess.cpu_percent()
        datas = {'cpu' : cp}
        if roomId in gdata.rooms() :
            room = gdata.rooms()[roomId]
            ucount, pcount, users = room.getRoomOnlineInfoDetail()
            datas[roomId] = [ucount, pcount, users]
        else:
            datas[roomId] = 'not on this server'
        msg.setResult('datas', datas)
        return msg
