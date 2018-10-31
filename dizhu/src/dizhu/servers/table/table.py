# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from sre_compile import isstring

from dizhu.replay import replay_service
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from dizhucomm.table.tablectrl import DizhuTableCtrl


@markCmdActionHandler
class TableTcpHandler(BaseMsgPackChecker):
    def _check_param_chatMsg(self, msg, key, params):
        chatMsg = msg.getParam('msg')
        if chatMsg and isinstance(chatMsg, (str, unicode)) :
            return None, chatMsg
        return 'ERROR of chatMsg !' + str(chatMsg), None

    def _check_param_isFace(self, msg, key, params):
        isFace = msg.getParam(key)
        if not isinstance(isFace, int) :
            isFace = 0
        return None, isFace

    def _check_param_voiceIdx(self, msg, key, params):
        voiceIdx = msg.getParam(key)
        if not isinstance(voiceIdx, int) :
            voiceIdx = -1
        return None, voiceIdx

    def _check_param_roundId(self, msg, key, params):
        roundId = msg.getParam(key)
        if not roundId or not isstring(roundId) :
            return 'ERROR of roundId !' + str(roundId), None
        return None, roundId

    def _check_param_smilies(self, msg, key, params):
        smilies = msg.getParam(key)
        if isinstance(smilies, (str, unicode)) :
            return None, smilies
        return 'ERROR of smilies !' + str(smilies), None

    def _check_param_toseat(self, msg, key, params):
        seatId = msg.getParam(key)
        if isinstance(seatId, int) and seatId > 0:
            return None, seatId
        return 'ERROR of toseat !' + str(seatId), None

    def _check_param_number(self, msg, key, params):
        number = msg.getParam(key, 1)
        if isinstance(number, int) and number > 0:
            return None, number
        return 'ERROR of number !', 0

    @markCmdActionMethod(cmd='table_manage', action='*', clientIdVer=0, lockParamName='', scope='game')
    def doTableManage(self, roomId, tableId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        action = msg.getParam('action')
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            table = room.maptable[tableId]
            result = table.doTableManage(msg, action)
        if router.isQuery():
            mo = MsgPack()
            mo.setCmd('table_manage')
            mo.setResult('action', action)
            mo.updateResult(result)
            router.responseQurery(mo)

    @markCmdActionMethod(cmd='table', action='sit', clientIdVer=0, scope='game')
    def doTableSit(self, userId, roomId, tableId, seatId0, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            table.doSit(msg, userId, seatId0, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))
    
    @markCmdActionMethod(cmd='table', action='leave', clientIdVer=0, scope='game')
    def doTableLeave(self, userId, roomId, tableId, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            table.doLeave(msg, userId, clientId)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, str(tableId), str(userId))
            
    @markCmdActionMethod(cmd='table', action='chat', clientIdVer=0, scope='game')
    def doTableChat(self, userId, roomId, tableId, seatId, isFace, voiceIdx, chatMsg):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            table.doTableChat(userId, seatId, isFace, voiceIdx, chatMsg)

    @markCmdActionMethod(cmd='table', action='smilies', clientIdVer=0, scope='game')
    def doTableSmilies(self, userId, roomId, tableId, seatId, smilies, toseat, number):
        ftlog.debug('TableTcpHandler.doTableSmilies:',
                    'userId=', userId,
                    'roomId=', roomId,
                    'smilies=', smilies,
                    'number=', number)
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            table.doTableSmilies(userId, seatId, smilies, toseat, number)

    @markCmdActionMethod(cmd='table', action='tbox', clientIdVer=0, scope='game')
    def doTableTreasureBox(self, userId, roomId, tableId, seatId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            table.doTableTreasureBox(userId, seatId)

    @markCmdActionMethod(cmd='table', action='replay_save', clientIdVer=0, scope='game')
    def doReplaySave(self, userId, roomId, tableId, roundId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            return table.proto.handleMsg(msg)
        else:
            mo = MsgPack()
            mo.setCmd('table')
            mo.setResult('action', 'replay_save')
            try:
                gameRound, savedUserIds = table.findGameRound(roundId)
                if gameRound and gameRound.findSeatByUserId(userId):
                    if not gameRound.gameOverTimestamp:
                        raise TYBizException(-1, '牌局还没结束')
                    if userId in savedUserIds:
                        raise TYBizException(-1, '牌局已经保存')
                    replay_service.saveVideo(userId, gameRound)
                    savedUserIds.add(userId)
                else:
                    raise TYBizException(-1, '没有找到该牌局')
            except TYBizException, e:
                mo.setResult('code', e.errorCode)
                mo.setResult('info', e.message)
            router.sendToUser(mo, userId)
            return mo
    
    @markCmdActionMethod(cmd='table_call', action='*', clientIdVer=0, scope='game')
    def doTableCall(self, userId, roomId, tableId, clientId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        if isinstance(table, DizhuTableCtrl):
            table.proto.handleMsg(msg)
        else:
            action = msg.getParam('action')
            seatId = msg.getParam('seatId', -1) # 旁观时没有seatId参数
            assert isinstance(seatId, int)
            table.doTableCall(msg, userId, seatId, action, clientId)
            if router.isQuery() :
                mo = runcmd.newOkMsgPack(1)
                router.responseQurery(mo, str(tableId), str(userId))


