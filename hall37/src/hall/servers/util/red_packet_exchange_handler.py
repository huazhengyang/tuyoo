# -*- coding:utf-8 -*-
'''
Created on 2017年12月26日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from hall.entity import hall_red_packet_exchange, hallitem,\
    hall_red_packet_const
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from poker.entity.biz.exceptions import TYBizException


@markCmdActionHandler  
class RedPacketExchangeTcpHandler(BaseMsgPackChecker):
    def _check_param_exchangeId(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of exchangeId !' + str(value), None
    
    @classmethod
    def encodeReceived(cls, status):
        ret = []
        for ritem in status.receivedItems[::-1]:
            itemD = {
                'time':ritem.timestamp,
                'count':ritem.count
            }
            source = hall_red_packet_const.getSourceName(ritem.source)
            itemD['desc'] = source
            ret.append(itemD)
        return ret
    
    @classmethod
    def encodeExchanges(cls, status):
        ret = []
        openItem = status.getOpenItem()
        for exchangeItem, state in status.exchangeItems:
            itemD = {
                'exchangeId':exchangeItem.exchangeId,
                'pic':exchangeItem.pic,
                'name':exchangeItem.name,
                'desc':exchangeItem.desc
            }
            rstate = 0
            if state == hall_red_packet_exchange.EXCHANGE_STATE_EXCHANGED:
                rstate = 2
            elif openItem and openItem.exchangeId == exchangeItem.exchangeId:
                rstate = 1
            itemD['state'] = rstate
            ret.append(itemD)
        return ret
    
    @classmethod
    def _doUpdate(cls, gameId, userId, clientId, timestamp=None):
        mo = MsgPack()
        mo.setCmd('hall_rp_exchange')
        mo.setResult('action', 'update')
        mo.setResult('userId', userId)
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        status = hall_red_packet_exchange.loadUserStatus(userId, clientId, timestamp)
        mo.setResult('received', cls.encodeReceived(status))
        mo.setResult('exchanges', cls.encodeExchanges(status))
        return mo
        
    @markCmdActionMethod(cmd='hall_rp_exchange', action='update', clientIdVer=0)
    def doUpdate(self, gameId, userId, clientId):
        '''
        获取弹幕信息
        '''
        mp = self._doUpdate(gameId, userId, clientId)
        if mp:
            router.sendToUser(mp, userId)
    
    @classmethod
    def _doExchange(cls, gameId, userId, clientId, exchangeId, timestamp=None):
        mo = MsgPack()
        mo.setCmd('hall_rp_exchange')
        mo.setResult('action', 'exchange')
        mo.setResult('userId', userId)
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        try:
            status = hall_red_packet_exchange.loadUserStatus(userId, clientId, timestamp)
            cost, assetList = hall_red_packet_exchange.doExchange(status, exchangeId)
            mo.setResult('cost', {'itemId':hallitem.ASSET_COUPON_KIND_ID, 'count':cost})
            delivery = []
            for atup in assetList:
                delivery.append({
                    'itemId':atup[0].kindId,
                    'count':atup[1]
                })
            mo.setResult('delivery', delivery)
        except TYBizException, e:
            mo.setResult('ec', e.errorCode)
            mo.setResult('info', e.message)
        return mo
                
    @markCmdActionMethod(cmd='hall_rp_exchange', action='exchange', clientIdVer=0)
    def doExchange(self, gameId, userId, clientId, exchangeId):
        '''
        获取弹幕信息
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        mo = self._doExchange(gameId, userId, clientId, exchangeId, timestamp)
        if mo:
            router.sendToUser(mo, userId)
            mo = self._doUpdate(gameId, userId, clientId, timestamp)
            if mo:
                router.sendToUser(mo, userId)


