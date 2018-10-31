# -*- coding:utf-8 -*-
'''
Created on 2018年1月26日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallconf, hallled
from datetime import datetime


def sendLed(gameId, msgstr, ismgr = 0, scope = 'hall', clientIds = []):
    '''
    发送LED
    @param gameId: 游戏gameId，gameId部分起到了过滤/范围的作用
    @param msgstr: LED消息内容
    @param ismgr: 是否是GDSS发的，默认非GDSS发送的
    @param scope: string类型，LED显示级别/范围，详见http://192.168.10.93:8090/pages/viewpage.action?pageId=1281059
        scope摘要
        - '6': 只在地主插件里面播放
        - 'hall': 在大厅界面播放
        - 'hall6': 在大厅和地主插件里面播放
        - 'global': 在大厅任何界面都播放
    @param clientIds: 发送的clientId集合，默认全发送
    '''
    
    assert isinstance(msgstr, basestring)
    
    closeLedGameIds = hallconf.getPublicConf('closeLedGameIds', [])
    
    if closeLedGameIds and gameId in closeLedGameIds:
        if ftlog.is_debug():
            ftlog.debug('hallled.sendLed closed',
                        'gameId=', gameId,
                        'msgstr=', msgstr,
                        'scope=', scope,
                        'ismgr=', ismgr)
        return None
    
    if ftlog.is_debug():
        ftlog.debug('hallled.sendLed gameId=', gameId,
                    'msgstr=', msgstr,
                    'scope=', scope,
                    'ismgr=', ismgr)
        
    try:
        msgDict = hallled.decodeMsg(gameId, msgstr)
        msg = [0, gameId, msgDict, scope, clientIds]
        leds = hallled._LEDS
        kmsg = 'm:' + str(gameId)
        ktime = 't:' + str(gameId)
        
        if ismgr :
            leds[kmsg] = [msg]
            leds[ktime] = datetime.now()
        else:
            if not kmsg in leds :
                leds[kmsg] = []
                leds[ktime] = None
                
            timeout = leds[ktime]
            if timeout != None :
                timeouts = hallconf.getHallPublic().get('led.manager.timeout', 40)
                secondes = (datetime.now() - timeout).seconds
                if secondes < timeouts :
                    if ftlog.is_debug():
                        ftlog.warn('hallled.sendLed Failed gameId=', gameId,
                                    'msgstr=', msgstr,
                                    'ismgr=', ismgr,
                                    'scope=', scope,
                                    'timeouts=', timeouts,
                                    'secondes=', secondes)
                    return
            msgq = leds[kmsg]
            msgq.append(msg)
            ledlength = 3
            leds[ktime] = datetime.now()
            leds[kmsg] = msgq[-ledlength:]
            
        if ftlog.is_debug():
            ftlog.debug('hallled.sendLed gameId=', gameId,
                        'msgstr=', msgstr,
                        'ismgr=', ismgr,
                        'msg=', msg,
                        'leds=', hallled._LEDS)
        return msg
    except:
        ftlog.error('hallled.sendLed gameId=', gameId,
                    'msgstr=', msgstr,
                    'scope=', scope,
                    'ismgr=', ismgr,
                    'leds=', hallled._LEDS)
        return None


hallled.sendLed = sendLed


