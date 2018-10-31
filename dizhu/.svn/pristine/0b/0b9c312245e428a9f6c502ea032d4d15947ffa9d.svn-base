# -*- coding:utf-8 -*-
'''
Created on 2016年5月11日

@author: zhaojiangang
'''
from dizhu.erdayimatch.match import ErdayiMatch
from dizhucomm.room.base import DizhuRoom
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class DizhuRoomTcpHandler(BaseMsgPackChecker):
    def _check_param_signinParams(self, msg, key, params):
        signinParams = msg.getParam(key)
        if signinParams and not isinstance(signinParams, dict):
            return 'ERROR of signinParams !' + str(signinParams), None
        return None, signinParams
    
    def _check_param_cardNo(self, msg, key, params):
        cardNo = msg.getParam(key)
        try:
            cardNo = int(cardNo)
            return None, cardNo
        except:
            return 'ERROR of cardNo !' + str(cardNo), None
    
    @markCmdActionMethod(cmd='room', action='enter', clientIdVer=0, scope='game')
    def doRoomEnter(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doEnter(userId)
    
    @markCmdActionMethod(cmd='room', action='leave', clientIdVer=0, scope='game')
    def doRoomLeave(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doLeave(userId, msg)
        
    @markCmdActionMethod(cmd='room', action='quick_start', clientIdVer=0, scope='game')
    def doRoomQuickStart(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            msg = runcmd.getMsgPack()
            room.doQuickStart(msg)
        if router.isQuery():
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, '', str(userId))
    
    @markCmdActionMethod(cmd='room', action="signin", clientIdVer=0, scope="game")
    def doRoomSigIn(self, roomId, userId, signinParams):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if ftlog.is_debug():
            ftlog.debug('msg=', msg, 'mode=', gdata.mode(),
                        caller=self)
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            if not signinParams and gdata.enableTestHtml():
                room = gdata.rooms()[roomId]
                signinParams = gamedata.getGameAttrJson(userId, room.gameId, 'test.signinParams')
    
            feeIndex = msg.getParam('feeIndex', 0)
            room.doSignin(userId, signinParams, feeIndex)

    @markCmdActionMethod(cmd='room', action="quicksignin", clientIdVer=0, scope="game")
    def doRoomQuickSigIn(self, roomId, userId, signinParams):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if ftlog.is_debug():
            ftlog.debug('msg=', msg, 'mode=', gdata.mode(),
                        caller=self)
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            if not signinParams and gdata.enableTestHtml():
                room = gdata.rooms()[roomId]
                signinParams = gamedata.getGameAttrJson(userId, room.gameId, 'test.signinParams')
            feeIndex = msg.getParam('feeIndex', 0)
            room.doSignin(userId, signinParams, feeIndex)

    @markCmdActionMethod(cmd='room', action='signout', clientIdVer=0, scope='game')
    def doRoomSigOut(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doSignout(userId)
    
    @markCmdActionMethod(cmd='room', action='giveup', clientIdVer=0, scope='game')
    def doRoomGiveup(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doGiveup(userId)
    
    @markCmdActionMethod(cmd='room', action='update', clientIdVer=0, scope='game')
    def doRoomUpdate(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doUpdateInfo(userId)
    
    @markCmdActionMethod(cmd='room', action='des', clientIdVer=0, scope='game')
    def doRoomDes(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doGetDescription(userId)
    
    @markCmdActionMethod(cmd='room', action='m_winlose', clientIdVer=0, lockParamName='', scope='game')
    def doRoomMatchWinLose(self, roomId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            room.doWinlose(msg)
        
    @markCmdActionMethod(cmd='room', action='myCardRecords', clientIdVer=0, scope='game')
    def doRoomMyCardRecords(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            if ftlog.is_debug():
                ftlog.debug('DizhuRoomTcpHandler.doRoomMyCardRecords msg=', msg)
                
            match = gdata.rooms()[roomId].match
            if not match:
                ftlog.warn('DizhuRoomTcpHandler.doRoomMyCardRecords NoMatch msg=', msg)
                return
                
            player = match.findPlayer(userId)
            if not player:
                ftlog.warn('DizhuRoomTcpHandler.doRoomMyCardRecords NoPlayer msg=', msg)
                return
                
            mo = MsgPack()
            mo.setCmd('room')
            mo.setResult('action', 'myCardRecords')
            records = []
            for i, cardResult in enumerate(player.cardResults):
                records.append({
                    'cardNo':str(i + 1),
                    'score':ErdayiMatch.fmtScore(cardResult.score),
                    'rate':'%s%s' % (ErdayiMatch.fmtScore(cardResult.mpRate * 100), '%'),
                    'mscore':ErdayiMatch.fmtScore(cardResult.mpRatioScore)
                })
            mo.setResult('records', records)
            router.sendToUser(mo, player.userId)

    @markCmdActionMethod(cmd='room', action='cardRank', clientIdVer=0, scope='game')
    def doRoomCardRank(self, roomId, userId, cardNo):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            if ftlog.is_debug():
                ftlog.debug('DizhuRoomTcpHandler.doRoomCardRank msg=', msg)
                
            match = gdata.rooms()[roomId].match
            if not match:
                ftlog.warn('DizhuRoomTcpHandler.doRoomCardRank NoMatch msg=', msg)
                return
                
            player = match.findPlayer(userId)
            if not player:
                ftlog.warn('DizhuRoomTcpHandler.doRoomCardRank NoPlayer msg=', msg)
                return
            
            cardRanking = player.group.stage.findCardRanking(cardNo - 1)
            if not cardRanking:
                ftlog.warn('DizhuRoomTcpHandler.doRoomCardRank NoCardRanking msg=', msg)
                return
            
            mo = MsgPack()
            mo.setCmd('room')
            mo.setResult('action', 'cardRank')
            ranks = []
            for cardResultSet in cardRanking.rankingList:
                for cardResult in cardResultSet:
                    ranks.append({
                        'score':ErdayiMatch.fmtScore(cardResult.score),
                        'mscore':ErdayiMatch.fmtScore(cardResult.mpRatioScore),
                        'pcount':len(cardResultSet)
                    })
                    break
            mo.setResult('ranks', ranks)
            router.sendToUser(mo, player.userId)

    @markCmdActionMethod(cmd='room', action='revival', clientIdVer=0, scope="game")
    def doRoomRevival(self, roomId, userId):
        msg = runcmd.getMsgPack()
        room = gdata.rooms()[roomId]
        if ftlog.is_debug():
            ftlog.debug('DizhuRoomTcpHandler.doRoomRevival',
                        'userId=', userId,
                        'msg=', msg,
                        'mode=', gdata.mode(),
                        caller=self)
        if isinstance(room, DizhuRoom):
            room.handleMsg(msg)
        else:
            pass


