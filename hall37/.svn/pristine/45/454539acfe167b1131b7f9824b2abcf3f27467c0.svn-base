# -*- coding=utf-8

from datetime import datetime
import json

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallconf
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskObserve, TodoTaskQuickStart
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.events.tyevent import EventConfigure, EventHeartBeat
import poker.entity.events.tyeventbus as pkeventbus
from poker.protocol import router
from poker.util import strutil


_initialize_ok = 0
_LEDS = {}

# 彩色LED头
RICH_TEXT_LED_MSG_HEADER = 'richTextLedMsg'

def _initialize(isCenter):
    ftlog.debug('hallled._initialize begin', isCenter)
    global _initialize_ok
    if not _initialize_ok :
        _initialize_ok = 1
        if isCenter :
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)
    ftlog.debug('hallled._initialize end')

def makeLedMsg(gameId, msgDict, scope, clientVer):
    if clientVer >= 3.6:
        mo = MsgPack()
        mo.setCmd('led')
        for k, v in msgDict.iteritems():
            mo.setResult(k, v)
        mo.setResult('scope', scope)
    else:
        mo = MsgPack()
        mo.setCmd('led')
        if gameId in (1, 8):
            msgDictV2 = translateToMsgDictV2(msgDict)
            if msgDictV2:
                mo.setKey('richText', msgDictV2.get('richText'))
        msgV1 = translateToMsgDictV1(msgDict)
        if msgV1:
            gameId = msgDict.get('gameId', gameId)
            mo.setKey('result', [[0, gameId, msgV1]])
    return mo

def canSendToUser(userId, clientId, led):
    isStopServer = led[5] if len(led) > 5 else False
    
    clientId = sessiondata.getClientId(userId)
    if not isStopServer and clientId in _ledClosesConf:
        if ftlog.is_debug():
            ftlog.debug('hallled.canSendToUser ClientIdClosed',
                        'userId=', userId,
                        'clientId=', clientId,
                        'led=', led)
        return False
    
    clientIdFilter = led[4]
    if clientIdFilter and clientId in clientIdFilter:
        if ftlog.is_debug():
            ftlog.debug('hallled.canSendToUser ClientIdFilter',
                        'userId=', userId,
                        'clientId=', clientId,
                        'led=', led)
        return False
    
    return True
    
    
def doSendLedToUser(userId):
    global _ledClosesConf
    
    gameIdList = onlinedata.getGameEnterIds(userId)
    lastGameId = onlinedata.getLastGameId(userId)
    if not HALL_GAMEID in gameIdList:
        gameIdList.append(HALL_GAMEID)
    if not lastGameId in gameIdList:
        gameIdList.append(lastGameId)

    clientId = sessiondata.getClientId(userId)
    
    gameIdInClientId = strutil.getGameIdFromHallClientId(clientId)
    if not gameIdInClientId in gameIdList:
        gameIdList.append(gameIdInClientId)
    
    if ftlog.is_debug():
        ftlog.debug('hallled.doSendLedToUser userId=', userId,
                    'gameIdList=', gameIdList,
                    'clientId=', clientId,
                    'gameIdInClientId=', gameIdInClientId,
                    'lastGameId=', lastGameId)
    
    _, clientVer, _ = strutil.parseClientId(clientId)
    for gameId in gameIdList:
        try:
            leds = getLedMsgList(gameId)
            if ftlog.is_debug():
                ftlog.debug('hallled.doSendLedToUser gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'leds=', leds)
            if leds:
                for led in leds:
                    if canSendToUser(userId, clientId, led):
                        msgDict = led[2]
                        if clientVer >= 3.6:
                            mo = MsgPack()
                            mo.setCmd('led')
                            for k, v in msgDict.iteritems():
                                mo.setResult(k, v)
                            mo.setResult('scope', led[3])
                        else:
                            mo = MsgPack()
                            mo.setCmd('led')
                            if gameId in (1, 8):
                                msgDictV2 = translateToMsgDictV2(msgDict)
                                if msgDictV2:
                                    mo.setKey('richText', msgDictV2.get('richText'))
                            msgV1 = translateToMsgDictV1(msgDict)
                            if msgV1:
                                gameId = msgDict.get('gameId', led[1])
                                mo.setKey('result', [[led[0], gameId, msgV1]])
                                
                        router.sendToUser(mo, userId)
        except:
            ftlog.error("error leds:", leds)
        
def onTimer(evt):
    ftlog.debug('hallled onTimer', evt.count)
    
def decodeMsgV3(gameId, msgstr):
    try:
        if len(msgstr) > 0 and msgstr[0] in ('{', '[') :
            d = json.loads(msgstr)
            if not isinstance(d, dict):
                return None
            d['gameId'] = gameId
            return d
    except:
        if ftlog.is_debug():
            ftlog.error()
        return None

def decodeMsgV2(gameId, msgstr):
    try:
        if not msgstr.startswith(RICH_TEXT_LED_MSG_HEADER):
            return None
        '''msg json 格式示例:
        {
            'richText': {
                'text': [{
                    "color": "RRGGBB",
                    "text": "aaa"
                },{
                    "color": "RRGGBB",
                    "text": "bbbccc"
                }],
            },
            'excludeUsers': [123456, 32134534],
            'type':'led', #type://“led”为无按钮,”watch”为观战 “vip”: quick_start
            'roomId':roomId,
            'tableId':tableId
        }
        '''
        # 德州版本的富文本协议
        d = json.loads(msgstr[len(RICH_TEXT_LED_MSG_HEADER):])
        msgDict = {}
        msgDict['gameId'] = d.get('gameId', gameId)
        msgDict['text'] = d.get('richText', {}).get('text', [])
        ledType = d.get('type', 'led')
        if ledType == 'watch':
            msgDict['lbl'] = '观战'
            msgDict['tasks'] = [TodoTaskObserve(gameId, d.get('roomId', 0), d.get('tableId', 0)).toStr()]
        elif ledType == 'vip':
            msgDict['lbl'] = '进入'
            msgDict['tasks'] = [TodoTaskQuickStart(gameId, d.get('roomId', 0), d.get('tableId', 0), d.get('seatId', 0)).toStr()]
        excludeUsers = d.get('excludeUsers')
        if excludeUsers:
            msgDict['excludeUsers'] = d.get('excludeUsers') 
        return msgDict
    except:
        if ftlog.is_debug():
            ftlog.debug('hallled.decodeMsgV2 gameId=', gameId,
                        'msgstr=', msgstr,
                        'err=', 'JsonLoadException')
        return None

def translateToMsgDictV2(msgDict):
    tasks = msgDict.get('tasks')
    extDict = {}
    if tasks:
        if len(tasks) > 1:
            return None
        # V2只支持旁观，quickstart
        todotask = tasks[0]
        action = todotask.getAction()
        if action == 'quick_start':
            extDict['type'] = 'vip'
            extDict['roomId'] = todotask.getParams('roomId', 0)
            extDict['tableId'] = todotask.getParams('tableId', 0)
            extDict['seatId'] = todotask.getParams('seatId', 0)
        elif action == 'observe':
            extDict['type'] = 'watch'
            extDict['roomId'] = todotask.getParams('roomId', 0)
            extDict['tableId'] = todotask.getParams('tableId', 0)
        else:
            return None
    msgDictV2 = {'richText':{'text':msgDict.get('text')}}
    excludeUsers = msgDict.get('excludeUsers')
    if excludeUsers:
        msgDictV2['excludeUsers'] = excludeUsers
    msgDictV2.update(extDict)
    if 'gameId' in msgDict:
        msgDictV2['gameId'] = msgDict.get('gameId')
    return msgDictV2
        
def translateToMsgDictV1(msgDict):
    tasks = msgDict.get('tasks')
    if tasks:
        # 有tasks的只有V2, V3支持
        return None
    
    msgstr = ''
    richTextList = msgDict.get('text', [])
    for richText in richTextList:
        text = richText.get('text')
        if text:
            msgstr += str(text)
    if ftlog.is_debug():
        ftlog.debug('hallled.translateToMsgDictV1 msgDict=', msgDict, 'msgstr=', msgstr)
    return msgstr

def decodeMsg(gameId, msgstr):
    msgDict = decodeMsgV2(gameId, msgstr)
    if msgDict:
        return msgDict
    
    msgDict = decodeMsgV3(gameId, msgstr)
    if msgDict:
        return msgDict
    
    return {
        'text':[{'color':'FFFFFF', 'text':msgstr, 'gameId':gameId}]
    }
    
def sendLed(gameId, msgstr, ismgr = 0, scope = 'hall', clientIds = [], isStopServer=False, **kwargs):
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
    @param isStopServer: 是否是停服led
    '''
    if not kwargs.get('active', 0):
        return
    
    assert isinstance(msgstr, basestring)
    
    closeLedGameIds = hallconf.getPublicConf('closeLedGameIds', [])
    
    if not isStopServer and closeLedGameIds and gameId in closeLedGameIds:
        if ftlog.is_debug():
            ftlog.debug('hallled.sendLed closed',
                        'gameId=', gameId,
                        'msgstr=', msgstr,
                        'scope=', scope,
                        'ismgr=', ismgr,
                        'isStopServer=', isStopServer)
        return None
    
    if ftlog.is_debug():
        ftlog.debug('hallled.sendLed gameId=', gameId,
                    'msgstr=', msgstr,
                    'scope=', scope,
                    'ismgr=', ismgr,
                    'isStopServer=', isStopServer)
        
    try:
        msgDict = decodeMsg(gameId, msgstr)
        msg = [0, gameId, msgDict, scope, clientIds, isStopServer]
        leds = _LEDS
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
                        'leds=', _LEDS)
        return msg
    except:
        ftlog.error('hallled.sendLed gameId=', gameId,
                    'msgstr=', msgstr,
                    'scope=', scope,
                    'ismgr=', ismgr,
                    'leds=', _LEDS)
        return None

def getLedMsgList(gameId):
    leds = _LEDS
    kmsg = 'm:' + str(gameId)
    ktime = 't:' + str(gameId)
    msgList = leds.get(kmsg, [])
    if msgList:
        timeouts = hallconf.getHallPublic().get('led.manager.timeout', 40) #从测试数据看客户端heartBeat间隔时间有10秒误差，也就是在30到40秒之间
        sendTime = leds.get(ktime)
        isTimeout = sendTime and (datetime.now() - sendTime).seconds >= timeouts
        if ftlog.is_debug():
            ftlog.debug('halllend.getLedMsgList gameId=', gameId,
                        'leds=', leds,
                        'sendTime=', sendTime,
                        'nowTime=', datetime.now(),
                        'isTimeout=', isTimeout)
        if isTimeout:
            return []
    return msgList


_ledClosesConf = []
_inited = False

def _reloadConf():
    global _ledClosesConf
    
    conf = hallconf.getLedConf()
    closes = conf.get('closes', [])
    _ledClosesConf = closes
    
    if ftlog.is_debug():
        ftlog.debug('hallled._reloadConf _ledClosesConf:', _ledClosesConf)
        
def _onConfChanged(event):
    if _inited and event.isModuleChanged('led'):
        ftlog.debug('hallled._reloadConf')
        _reloadConf()

def _initializeConfig():
    ftlog.debug('hallled._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallled._initialize end')