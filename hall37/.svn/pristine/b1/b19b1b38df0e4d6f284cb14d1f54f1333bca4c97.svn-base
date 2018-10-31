# -*- coding=utf-8

from datetime import datetime
import json
import random

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallconf
from hall.entity.todotask import TodoTaskObserve, TodoTaskQuickStart
from poker.entity.dao import onlinedata, sessiondata, userdata
from poker.entity.events.tyevent import EventHeartBeat
from poker.protocol import router
from poker.util import strutil
from freetime.util.log import catchedmethod
import time
from freetime.core.lock import locked, FTLock
from poker.entity.configure import gdata
from freetime.support.tcpagent import wrapper
from hall.entity.todotask import TodoTaskEnterGame
from poker.protocol.conn import protocols
from freetime.core.tasklet import FTTasklet
from hall.entity.hallled import LedUtils


_initialize_ok = 0
_LEDS = {}

def _initialize(isCenter):
    ftlog.debug('hallled._initialize begin', isCenter)
    global _initialize_ok
    if not _initialize_ok :
        _initialize_ok = 1
        if isCenter :
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)
    ftlog.debug('hallled._initialize end')

def doSendLedToUser(userId):
    gameIdList = onlinedata.getGameEnterIds(userId)
    if not gameIdList:
        return
    
    clientId = sessiondata.getClientId(userId)
    _, clientVer, _ = strutil.parseClientId(clientId)
    for gameId in gameIdList:
        try:
            leds = getLedMsgList(gameId)
            if ftlog.is_debug():
                ftlog.debug('hallled.doSendLedToUser gameId=', gameId,
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'leds=', leds)
            if leds:
                msgDict = leds[0][2]
                if clientVer >= 3.6:
                    mo = MsgPack()
                    mo.setCmd('led')
                    for k, v in msgDict.iteritems():
                        mo.setResult(k, v)
                else:
                    mo = MsgPack()
                    mo.setCmd('led')
                    if gameId in (1, 8):
                        msgDictV2 = translateToMsgDictV2(msgDict)
                        if msgDictV2:
                            mo.setKey('richText', msgDictV2.get('richText'))
                    msgV1 = translateToMsgDictV1(msgDict)
                    if msgV1:
                        gameId = msgDict.get('gameId', leds[0][1])
                        mo.setKey('result', [[leds[0][0], gameId, msgV1]])
                router.sendToUser(mo, userId)
        except:
            ftlog.error()
        
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
        header = 'richTextLedMsg'
        if not msgstr.startswith(header):
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
        d = json.loads(msgstr[len(header):])
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
            msgstr += text
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
    
def sendLed(gameId, msgstr, ismgr):
    
    if ftlog.is_debug():
        ftlog.debug('hallled.sendLed gameId=', gameId,
                    'msgstr=', msgstr,
                    'ismgr=', ismgr)
    if not ismgr :
        ledRandomMod = hallconf.getHallPublic().get('led.manager.timeout', 3)
        randint = random.randint(0, ledRandomMod - 1)
        if randint % ledRandomMod != 0 :
            if ftlog.is_debug():
                ftlog.debug('hallled.sendLed Failed gameId=', gameId,
                            'msgstr=', msgstr,
                            'ismgr=', ismgr,
                            'noRandom')
            return
        
    try:
        msgDict = decodeMsg(gameId, msgstr)
        msg = [0, gameId, msgDict]
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
                timeouts = hallconf.getHallPublic().get('led.manager.timeout', 30)
                secondes = (datetime.now() - timeout).seconds
                if secondes < timeouts :
                    if ftlog.is_debug():
                        ftlog.debug('hallled.sendLed Failed gameId=', gameId,
                                    'msgstr=', msgstr,
                                    'ismgr=', ismgr,
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
                        'leds=', leds,
                        'LEDS=', _LEDS)
        return msg
    except:
        ftlog.error('hallled.sendLed gameId=', gameId,
                    'msgstr=', msgstr,
                    'ismgr=', ismgr)
        return None

def getLedMsgList(gameId):
    leds = _LEDS
    kmsg = 'm:' + str(gameId)
    ktime = 't:' + str(gameId)
    msgList = leds.get(kmsg, [])
    if msgList:
        timeouts = hallconf.getHallPublic().get('led.manager.timeout', 30)
        sendTime = leds.get(ktime)
        if (sendTime
            and (datetime.now() - sendTime).seconds >= timeouts):
            return []
    return msgList


RICH_TEXT_LED_MSG_HEADER = 'richTextLedMsg'  # 彩色 LED 头

class LedUtils2(object):
    
    locker = FTLock("LedUtils")
    
    @classmethod
    def _mkRichTextBody(cls, content):
        return [{'color': color, 'text': text} for color, text in content]
    
    
    @classmethod
    def _mkRichTextLedBody(cls, content, _type='led', roomId=0, tableId=0):
        """ _type:
        led      纯LED消息，带颜色
        watch    LED消息，带颜色，观战按钮
        vip      LED消息，带颜色，进入（坐下）按钮
        mtt
        """
    
        richText = {
            'text': cls._mkRichTextBody(content),
            'type': _type,
            'roomId': roomId,
            'tableId': tableId
            }
    
        return RICH_TEXT_LED_MSG_HEADER + json.dumps({'richText': richText})
    

    @classmethod
    def sendToAllCoServer(cls, mo):
        ''' 发送消息到所有TCP管理服务器'''
        msgpack = mo.pack()
        coSrvIds = gdata.serverTypeMap()[gdata.SRV_TYPE_CONN]
        for coSrvId in coSrvIds:
            wrapper.send(coSrvId, msgpack, "S1", "")
            
            
    @classmethod
    def sendRealTimeLed(cls, gameId, plain_text, receivers=[]):
        """ 发送一条实时LED消息
        receivers: 接收者USERID列表。如果为[]，发给所有在线玩家 """ 

        content = [['FFFFFF', plain_text]]
        cls.sendRealTimeColorfulLed(gameId, content, receivers)


    @classmethod
    def sendRealTimeColorfulLed(cls, gameId, content, receivers=[]):
        """ 发送一条实时LED消息
        receivers: 接收者USERID列表。如果为[]，发给所有在线玩家 """

        mo = MsgPack()
        mo.setCmd('game_public_led')
        mo.setParam('gameId', gameId)
        mo.setParam('receivers', receivers)
        mo.setParam('msg', cls._mkRichTextLedBody(content))
        mo.setParam('ledWithTodoTask', {'text': cls._mkRichTextBody(content)})

        cls.sendToAllCoServer(mo)


    @classmethod
    def sendled(cls, gameId, plain_text):
        """ 发送一条实时GDSS那样的LED消息。玩家会在心跳协议中陆续收到该消息""" 
        mo = MsgPack()
        mo.setCmd('send_led')
        mo.setParam('msg', plain_text)
        mo.setParam('gameId', gameId)
        mo.setParam('ismgr', 1)
        router.sendUtilServer(mo)


    @classmethod
    @locked
    def _doGamePublicLed(cls, mi):
        '''
        这个方法在CO进程中由game_public_led的消息handler进行调用,
        不允许在其它进程中调用
        '''
        assert(gdata.serverType() == gdata.SRV_TYPE_CONN)

        ftlog.debug("<< |msgPackIn:", mi, caller=cls)
        
        # 如果从 result 中获取不到数据，从 param 中获取，还取不到，用默认值
        gameId = mi.getResult('gameId', 0) or mi.getParam('gameId') or 0
        receivers = mi.getResult('receivers') or mi.getParam('receivers') or []
        excludeUsers = mi.getResult('excludeUsers') or mi.getParam('excludeUsers') or set()
        msg = mi.getResult('msg') or mi.getParam('msg')
        timelimit = mi.getResult('timelimit') or mi.getResult('timelimit') or {}
        force = mi.getResult('force') or mi.getParam('force') or []  # 这里指定的用户不能过滤，必须收

        intervals = timelimit.get('timeLimitIntervals')  # 这个时间内收过led的不再收
        limitName = timelimit.get('timeLimitName')  # 时间间隔的种类，反射机制设置到 user 对象中去

        msg = cls._tryParseRichTextLed(msg)
        leds = [[0, gameId, msg]]
        ftlog.debug("|leds:", leds, caller=cls)

        popWinInfo = mi.getResult('popWin')
        ledWithTodoTask = mi.getResult('ledWithTodoTask') or mi.getParam('ledWithTodoTask')
#         if not ledWithTodoTask:
#             ledWithTodoTask = Message._richText2Todotask(mi, msg) #TODO:
     
        if gameId <= 0:
            ftlog.error("doGamePublicLed: error: game not found or gameid is 0", gameId)
            return

        mo_cache = {}  # 缓存不同版本的 led消息，避免每次生成，浪费CPU

        def mo_cache_key(gameId, clientVer, clientId):
            if gameId == 8 and clientVer == 3.37 and 'hall8' in clientId:
                return gameId, clientVer, 'hall8'
            return gameId, clientVer

        def make_led_mo(newleds, clientVer, clientId):
            mo = MsgPack()
            mo.setCmd('led')
            
            if clientVer >= 3.6:
                if ledWithTodoTask:
                    mo.setKey('result', ledWithTodoTask)
                    return mo.pack()
                return None

            if newleds['origLeds']:
                mo.setKey('result', newleds['origLeds'])
            if newleds['richLeds']:
                mo.setKey('result', newleds['richLeds'])
                mo.setKey('richText', newleds['richLeds'])
                mo.setResult('gameId', gameId)

                if gameId == 8:
                    if clientVer < 3.0:
                        # 德州老单包有问题，所有格式都转为没有按钮的LED (也就是type='led')
                        newleds['richLeds']['type'] = 'led'
                    elif newleds['richLeds']['type'] == 'vip' and clientVer == 3.37 and 'hall8' in clientId:
                        # 德州大厅3.37版本BUG: 如果消息中有 richText，则收不到消息
                        mo.rmKey('richText')
            if popWinInfo and clientId.startswith('Winpc'):
                mo.setResult('popWin', popWinInfo)
            return mo.pack()

        def sendled():
            newleds = cls._getLedMsgLists(leds, gameId, userId)
            clientVer = sessiondata.getClientIdVer(userId)
            clientId = sessiondata.getClientId(userId)
            if newleds['richLeds'] or newleds['origLeds']:
                key = mo_cache_key(gameId, clientVer, clientId)
                if key not in mo_cache:
                    mo_cache[key] = make_led_mo(newleds, clientVer, clientId)
                mo = mo_cache[key]
                if mo:
                    protocols.sendCarryMessage(mo, [userId])
                    
        if receivers:
            receivers = receivers + force
        else:
            receivers = protocols._ONLINE_USERS.keys()

        #需求：两次同类型led之间需要相隔intervals
        now = time.time()
        sc = 0
        for userId in receivers:
            sc += 1
            if sc % 20 == 0 :
                FTTasklet.getCurrentFTTasklet().sleepNb(0.1)
            if userId in force:
                if limitName:
#                     setattr(user, limitName, now)
                    userdata.setAttr(userId, limitName, now)
                sendled()
                continue
 
            if userId not in excludeUsers:
                if limitName and intervals:  # 时间限制
#                     lastSendTime = getattr(user, limitName, 0)
                    lastSendTime = userdata.getAttr(userId, limitName)
                    if not lastSendTime:
                        lastSendTime = 0
                    ftlog.debug('|userId, limitName, intervals, lastSendTime:', userId, limitName, intervals, lastSendTime, caller=cls)
                    if lastSendTime + intervals <= now:
                        userdata.setAttr(userId, limitName, now)
                        sendled()
                else:
                    sendled()
                    
                    
    @classmethod
    def _getLedMsgLists(cls, leds, gameId, userId):
        if not leds:
            return
 
        newleds = {
                'richLeds': [],  # 带格式的 led 消息
                'origLeds': [],  # 纯文本的 led 消息
        }
 
        clientVer = sessiondata.getClientIdVer(userId)
 
        # 过滤 led 消息。过滤器把通过过滤器的消息加入到 richLeds 或者 origLeds 里
        for led in leds:
            if cls._ledMsgFilterRich(gameId, userId, clientVer, led, newleds):
                continue
            if cls._ledMsgFilterOrig(gameId, userId, clientVer, led, newleds):
                continue
 
        return newleds
    
    
    @classmethod
    def _ledMsgFilterOrig(cls, gameId, userId, clientVer, led, newleds):
        """ 这是以前的过滤方法 """

        _id, _gid, ledmsg = led
        if isinstance(ledmsg, str) and ledmsg[0] == '#':
#             cutVer = TyContext.Configure.get_game_item_float(gameId, 'version.2.2', 2.15)
            cutVer = 2.15 # TODO:
            if clientVer and clientVer < cutVer:
                ledmsg = ledmsg[7:]
        newleds['origLeds'].append([_id, _gid, ledmsg])

        return True

    @classmethod
    def _ledMsgFilterRich(cls, gameId, userId, clientVer, led, newleds):
        """ 过滤富文本 led 消息 """

        _id, _gid, ledmsg = led
        isRichTextLed = isinstance(ledmsg, dict) and ledmsg.has_key('richText')
        if not isRichTextLed:
            # 德州1.67版本LED有bug,这是bug处理，3.37解决bug，不对3.37以上的版本做处理，但是3.37的插件又存在这个bug
            if gameId == 8:
                # 可以接收富文本格式的LED消息的客户端最低版本
                versionCanReceiveRichTextLed = 1.67
                versionHaveLedBug = 1.67
                versionLedBugFixed = 3.37
                clientId = sessiondata.getClientId(userId);
                if versionLedBugFixed > clientVer >= versionHaveLedBug or 'hall8' not in clientId:
                    ledmsg = {"richText": {"text": [{"color": "FFFFFF", "text": ledmsg}], "type":"led", "gameId":8},
                            "excludeUsers": set()}
                    ftlog.debug("convert orig  led to richtext led", ledmsg)
                else:
                    return False
            else:
                return False

        # 加入 exclude 机制：业务需求要求一部分LED实时发送给用户，其余用户
        # 保留现有心跳时接收 LED 方式。为了让收过LED的用户不再重复接收，
        # 凡是在 excludeUsers 中的用户就不再接收 LED 了。
        if userId in ledmsg['excludeUsers']:
            return False

        if gameId == 8:
            # 可以接收富文本格式的LED消息的客户端最低版本
            versionCanReceiveRichTextLed = 1.67
            versionHaveLedBug = 1.67
            versionLedBugFixed = 3.37
            # 德州 1.67 版本加入富文本消息
            if clientVer < versionCanReceiveRichTextLed:
                newleds['origLeds'].append([_id, _gid, ledmsg['plainText']])

            # 1.67版本LED有bug,这是bug处理
            elif clientVer >= versionHaveLedBug:
                newleds['richLeds'] = ledmsg['richText']
                newleds['origLeds'] = ledmsg['richText']
            else:
                newleds['richLeds'].append(ledmsg['richText'])
            return True
        elif gameId == 1:
            newleds['richLeds'] = ledmsg['richText']
            newleds['origLeds'] = ledmsg['richText']
            return True

        return False


    @classmethod
    def _tryParseRichTextLed(cls, msg):
        """检查led消息是否富文本格式。
        如果是，解析格式并返回；如否，原样返回；如果出错，返回None

        msg json 格式示例:
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
            'excludeUsers': [123456, 32134534]
        }
        """

        header = 'richTextLedMsg'
        if not msg.startswith(header):
            return msg

        try:
            ledmsg = json.loads(msg[len(header):])
            ledmsg['excludeUsers'] = set(ledmsg.get('excludeUsers', []))
            ledmsg['plainText'] = u''.join((unicode(seg['text']) for seg in ledmsg['richText']['text']))
            return ledmsg
        except:
            ftlog.error("load led json error", msg)
            

    @classmethod
    @catchedmethod
    def _richText2Todotask(cls, gamePublicLedMsg, ledMsg):
        '''richTextLed 消息转换为 game_enter todotask 格式消息
        因为 decodeMsgV2 用的 todotask 不是 enter_game，且不知道有没有游戏已经用了那个，所以才写了这个
        在实时LED里用(conn.py: doGamePublicLed)
        '''
        text = ledMsg.get('richText', {}).get('text', [])
        gameId = gamePublicLedMsg.getResult('gameId')
        roomId = ledMsg.get('roomId')
        tableId = ledMsg.get('tableId')
        ledType = ledMsg.get('type')
        gameMark = {1: 't3card', 3: 'chess', 6: 'ddz', 7: 'majiang', 8: 'texas', 10: 'douniu'}.get(gameId)
        lbl = {'vip': u'进入', 'watch': u'观战'}.get(ledType)
        if not (text and gameId and roomId and tableId and ledType and gameMark and lbl):
            return

        gameType = ledMsg.get('gameType', 1)
        todotaskParams = {'gameId': gameId, 'roomId': roomId, 'tableId': tableId, 'type': ledType}
        tasks = [TodoTaskEnterGame(gameMark, gameType, **todotaskParams).toDict()]
        ledresult = {'text': text, 'lbl': lbl, 'tasks': tasks}

        return ledresult

LedUtils._doGamePublicLed = LedUtils2._doGamePublicLed

