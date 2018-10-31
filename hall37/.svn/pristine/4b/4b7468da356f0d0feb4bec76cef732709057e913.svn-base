# -*- coding:utf-8 -*-
'''
Created on 2017年12月8日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hall_red_packet_rain, hallitem
from hall.entity.hall_red_packet_rain import RedPacketRainStopped
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.content import TYContentUtils
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp


@markCmdActionHandler    
class RedPacketRainTcpHandler(BaseMsgPackChecker):
    def _check_param_rainTime(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of rainTime !' + str(value), None
    
    def _check_param_danmuPos(self, msg, key, params):
        value = msg.getParam(key, -1)
        if isinstance(value, int) and value >= 0:
            return None, value
        return 'ERROR of danmuPos !' + str(value), None
    
    @markCmdActionMethod(cmd='hall_red_packet_rain', action='get_next_rain', clientIdVer=0)
    def doGetNextRain(self, gameId, userId, clientId):
        '''
        请求下一场红包雨的信息
        '''
        mp = self._doGetNextRain(gameId, userId, clientId)
        if mp:
            router.sendToUser(mp, userId)

    @markCmdActionMethod(cmd='hall_red_packet_rain', action='grab', clientIdVer=0)
    def doGrab(self, gameId, userId, clientId, rainTime):
        '''
        请求下一场红包雨的信息
        '''
        mp = self._doGrab(gameId, userId, clientId, rainTime)
        if mp:
            router.sendToUser(mp, userId)

    @markCmdActionMethod(cmd='hall_red_packet_rain', action='get_danmu', clientIdVer=0)
    def doGetDanmu(self, gameId, userId, clientId, rainTime, danmuPos):
        '''
        获取弹幕信息
        '''
        mp = self._doGetDanmu(gameId, userId, clientId, rainTime, danmuPos)
        if mp:
            router.sendToUser(mp, userId)
            
    @markCmdActionMethod(cmd='hall_red_packet_rain', action='get_result', clientIdVer=0)
    def doGetResult(self, gameId, userId, clientId, rainTime):
        '''
        请求红包雨结果
        '''
        mp = self._doGetResult(gameId, userId, clientId, rainTime)
        if mp:
            router.sendToUser(mp, userId)

    @classmethod
    def _doGetNextRain(self, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('hall_red_packet_rain')
        mo.setResult('action', 'get_next_rain')
        timestamp = pktimestamp.getCurrentTimestamp()
        mo.setResult('curTime', timestamp)
        if hall_red_packet_rain.isStop(timestamp):
            return mo

        rainStatus = hall_red_packet_rain.getRainStatus()
        if not rainStatus or not rainStatus.curRain:
            return mo

        conf = hall_red_packet_rain.getConf()
        mo.setResult('notify', conf.notifyList)
        mo.setResult('rain', {
            'rainTime':rainStatus.curRain.rainTime,
            'duration':rainStatus.curRain.duration
        })
        
        return mo
    
    @classmethod
    def encodeDanmuList(cls, userId, danmuList):
        ret = []
        for dmUserId, msg in danmuList:
            if dmUserId != userId:
                ret.append(msg)
        return ret
    
    @classmethod
    def _doGetDanmu(cls, gameId, userId, clientId, rainTime, danmuPos):
        mo = MsgPack()
        mo.setCmd('hall_red_packet_rain')
        mo.setResult('action', 'get_danmu')
        mo.setResult('rainTime', rainTime)
        mo.setResult('danmuPos', danmuPos)
        try:
            nextPos, danmuList = hall_red_packet_rain.getDanmu(userId, rainTime, danmuPos)
            mo.setResult('nextPos', nextPos)
            mo.setResult('danmus', cls.encodeDanmuList(userId, danmuList))
        except:
            ftlog.error('RedPacketRainTcpHandler._doGetDanmu',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'rainTime=', rainTime,
                        'danmuPos=', danmuPos)
        return mo
    
    @classmethod
    def encodeContent(cls, value, items):
        if not isinstance(items, list):
            items = [items]
        
        ret = {'value':value}
        ret['items'] = hallitem.buildItemInfoList(items)
        return ret
    
    @classmethod
    def mergeContent(cls, packets):
        contentItems = []
        for p in packets:
            contentItems.append(p.reward)
        return TYContentUtils.mergeContentItemList(contentItems)
    
    @classmethod
    def encodeNo1(cls, no1):
        items = cls.mergeContent(no1.userGains.packets)
        return {
            'userId':no1.userId,
            'userAttrs':no1.userAttrs,
            'content':cls.encodeContent(no1.userGains.value, items)
        }
    
    @classmethod
    def _doGrab(cls, gameId, userId, clientId, rainTime):
        mo = MsgPack()
        mo.setCmd('hall_red_packet_rain')
        mo.setResult('action', 'grab')
        mo.setResult('rainTime', rainTime)
        timestamp = pktimestamp.getCurrentTimestamp()
        try:
            mo.setResult('rainInfo', hall_red_packet_rain.getRainInfo(userId, clientId, rainTime))
            redPacket = hall_red_packet_rain.grabRedPacket(userId, clientId, rainTime, timestamp)
            if redPacket:
                mo.setResult('content', cls.encodeContent(redPacket.value, redPacket.reward))

            # 分享相关(sharePoint、shareDoubleReward)增加到协议中
            pointId, doubleReward = hall_red_packet_rain.getShareInfo(userId)
            mo.setResult('doubleReward', doubleReward)
            if pointId:
                mo.setResult('share', {"pointId": pointId})

        except RedPacketRainStopped:
            mo.setResult('ec', 1)
            mo.setResult('info', '红包雨已经结束')
        except:
            ftlog.error('RedPacketRainTcpHandler._doGrab',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'rainTime=', rainTime)
        return mo
    
    @classmethod
    def _doGetResult(cls, gameId, userId, clientId, rainTime):
        mo = MsgPack()
        mo.setCmd('hall_red_packet_rain')
        mo.setResult('action', 'get_result')
        mo.setResult('rainTime', rainTime)
        try:
            _rain, no1, userGains = hall_red_packet_rain.getRainResult(userId, rainTime)
            if no1 and no1.userGains:
                mo.setResult('no1', cls.encodeNo1(no1))

                if userGains:
                    items = cls.mergeContent(userGains.packets)
                    mo.setResult('content', cls.encodeContent(userGains.value, items))
        except:
            ftlog.error('RedPacketRainTcpHandler._doGetResult',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'rainTime=', rainTime)
        return mo
