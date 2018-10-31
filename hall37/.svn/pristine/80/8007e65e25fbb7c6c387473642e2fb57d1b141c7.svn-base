# -*- coding:utf-8 -*-
'''
Created on 2017年12月26日

@author: zhaojiangang
'''

from freetime.entity.msg import MsgPack
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.hall_invite_handler import InviteTcpHandler
from hall.servers.util.red_packet_exchange_handler import \
    RedPacketExchangeTcpHandler
from hall.servers.util.red_packet_task_handler import RedPacketTaskTcpHandler
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from hall.entity import hall_red_packet_main
from poker.util import strutil


@markCmdActionHandler  
class RedPacketMainTcpHandler(BaseMsgPackChecker):
    def _check_param_exchangeId(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of exchangeId !' + str(value), None
    
    @classmethod
    def _doUpdate(cls, gameId, userId, clientId, timestamp=None):
        mo = MsgPack()
        mo.setCmd('hall_rp_main')
        mo.setResult('action', 'update')
        mo.setResult('userId', userId)
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        mo.setResult('curTime', timestamp)
        conf = hall_red_packet_main.getConf()
        
        if not conf:
            mo.setResult('startTime', 0)
            mo.setResult('stopTime', 0)
        else:
            startTime = pktimestamp.datetime2Timestamp(conf.startDT) if conf.startDT else 0
            stopTime = pktimestamp.datetime2Timestamp(conf.stopDT) if conf.stopDT else 0
            mo.setResult('startTime', startTime)
            mo.setResult('stopTime', stopTime)
            _, clientVer, _ = strutil.parseClientId(clientId)
            if clientVer >= 4.58:
                if conf.inviteTodotaskFac:
                    todotask = conf.inviteTodotaskFac.newTodoTask(HALL_GAMEID, userId, clientId)
                    if todotask:
                        mo.setResult('todotask', todotask.toDict())
            else:
                if conf.oldInviteTodotaskFac:
                    todotask = conf.oldInviteTodotaskFac.newTodoTask(HALL_GAMEID, userId, clientId)
                    if todotask:
                        mo.setResult('todotask', todotask.toDict())
        return mo
        
    @markCmdActionMethod(cmd='hall_rp_main', action='update', clientIdVer=0)
    def doUpdate(self, gameId, userId, clientId):
        '''
        获取弹幕信息
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        mp = self._doUpdate(gameId, userId, clientId, timestamp)
        if mp:
            router.sendToUser(mp, userId)
        
        mp = RedPacketExchangeTcpHandler._doUpdate(gameId, userId, clientId, timestamp)
        if mp:
            router.sendToUser(mp, userId)
            
        mp = InviteTcpHandler._doInviteeInfo(userId, gameId, clientId)
        if mp:
            router.sendToUser(mp, userId)

        mp = RedPacketTaskTcpHandler._doUpdate(userId, clientId, timestamp)
        if mp:
            router.sendToUser(mp, userId)
    
    @classmethod
    def _doGainReward(cls, gameId, userId, clientId):
        mp = MsgPack()
        mp.setCmd('hall_rp_main')
        mp.setResult('action', 'gain_reward')
        mp.setResult('userId', userId)
        assetList = hall_red_packet_main.gainReward(userId, clientId)
        rewards = [{'itemId':atup[0].kindId, 'name':atup[0].displayName, 'url':atup[0].pic, 'count':atup[1]} for atup in assetList] if assetList else []
        mp.setResult('rewards', rewards)
        return mp

    @markCmdActionMethod(cmd='hall_rp_main', action='gain_reward', clientIdVer=0)
    def doGainReward(self, gameId, userId, clientId):
        mp = self._doGainReward(gameId, userId, clientId)
        if mp:
            router.sendToUser(mp, userId)


