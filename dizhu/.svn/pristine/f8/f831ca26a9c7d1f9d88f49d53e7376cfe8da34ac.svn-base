# -*- coding=utf-8
'''
Created on 2015年8月19日

@author: zhaojiangang
'''
import random

import freetime.util.log as ftlog
from poker.entity.events import tyeventbus
from poker.entity.events.tyevent import EventHeartBeat
import poker.util.timestamp as pktimestamp
from hall.entity import hallled
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.dao import userdata
from dizhu.entity import dizhuconf
from poker.entity.game.rooms.big_match_ctrl.config import StartConfig
from poker.entity.configure import gdata

_lastMakeTime = 0

def _initialize():
    ftlog.debug('dizhuled._initialize begin')
    tyeventbus.globalEventBus.subscribe(EventHeartBeat, _onHeartBeat)
    ftlog.debug('dizhuled._initialize end')
    
def _randName():
    uid = random.randrange(10000, 30000000)
    name = userdata.getAttr(uid, 'name')#cls.getName(uid)
    if not name:
        pre = ['360', '91_', 'momo', 'ly_', 'tx_', 'kugou']
        tail = 'ABCDEFGHIGKLMNOPQRSTUVWXYZ123456789'
        head = random.choice(pre)
        count = random.randrange(3, 7)
        for _ in xrange(count):
            head += random.choice(tail)
        name = head
    return str(name)

def _winFruit():
    ftlog.debug('dizhuled._winFruit begin')
    result = random.randrange(1000000, 6000000)
    led = u'%s在水果大亨赢彩池,获得%s金币.' % (_randName(), result)
    ftlog.debug('dizhuled._winFruit led=', led)
    return led

def _openBoxLed():
    ftlog.debug('dizhuled._openBoxLed begin')
    if random.randrange(0, 2) > 0:
        result = u'%d金币' % (random.randrange(20000, 100000))
    else:
        result = u'%d奖券' % (random.randrange(100, 800))
    led = u'%s在8元抽奖中额外获得%s.' % (_randName(), result)
    ftlog.debug('dizhuled._openBoxLed led=', led)
    return led

def _getMatchTimeLedText(startconf, ledconf, matchname, matchreward):
    signintime = startconf.get("signin.times")
    startConf = StartConfig.parse(startconf)
    seconds = startConf.getTodayNextLater()
    
    #ftlog.debug('matchled _getMatchTimeLedText signintime=', signintime, 'seconds=', seconds)
    if seconds == -1:
        return ''
    
    if seconds > signintime:
        return '' # 比赛未开始报名
    else:
        for led in ledconf:
            stage = led.get("stage")
            if stage == "signin":
                if seconds + 1 >= signintime: # 控制led个数
                    ftlog.debug('matchled_signin _getMatchTimeLedText signintime=', signintime, 'seconds=', seconds)
                    return led.get("text",'').format(MATCH_NAME=matchname, WIN1st_REWARD=matchreward) # 比赛开始报名
            elif stage == "start":
                if seconds <= led.get("seconds") and seconds + 1 >= led.get("seconds"):
                    ftlog.debug('matchled_start _getMatchTimeLedText signintime=', signintime, 'seconds=', seconds, 'config_seconds=', led.get("seconds"))
                    return led.get("text",'').format(MATCH_NAME=matchname) # 比赛即将开始
            else:
                pass
    return ''


def _getWinnerReward(conf):
    for reward in conf:
        rank = reward.get("ranking")
        if rank["start"] == 1 and rank["end"] == 1:
            return reward["desc"]
    return ''

def _getMatchLed():
    results = []
    matchLed = dizhuconf.getLedNotifyConf()
    for led in matchLed:
        try:
            if led.get("type", '') != "match":
                continue
            
            matchId = led.get("matchId", None)
            if not matchId:
                continue
            
            conf = gdata.getRoomConfigure(int(matchId))
            if not conf:
                ftlog.debug('match conf not found id matchId=', matchId)
                continue
            
            matchConf = conf.get("matchConf", {})
            
            if not matchConf:
                continue
            
            startConf = matchConf.get('start')
            if not startConf:
                continue
            
            ledtext = led.get('ledtext', [])
            matchname = conf.get("name")
            matchreward = _getWinnerReward(matchConf.get("rank.rewards", []))
            result = _getMatchTimeLedText(startConf, ledtext, matchname, matchreward)
            
            if result:
                results.append(result)
            #ftlog.debug('matchled get matchId=', matchId, 'result=s', results, 'matchname=', matchname, 'matchreward=', matchreward)
        except:
            ftlog.exception('dizhuled._getMatchLed ledMatchId=', led.get('matchId'))
        
    return results
        
    
def _randLed():
    global _lastMakeTime
    now_ = pktimestamp.getCurrentTimestamp()
    if now_ > _lastMakeTime:
        _lastMakeTime = now_ + random.randrange(1800, 2700)
        
        if random.randrange(0, 100) > 50: 
            return _openBoxLed(), 0
        else:
            return _winFruit(), 0
    return None, 0


def matchLed():
    leds = _getMatchLed()
    if leds:
        return leds, 1
    else:
        return None, 0
    
def _onHeartBeat(event):
    leds, ismgr = matchLed()
    if leds:
        for led in leds:
            hallled.sendLed(DIZHU_GAMEID, led, ismgr)
        return
    
    led, ismgr = _randLed()
    if ftlog.is_debug():
        ftlog.debug('dizhuled._onHeartBeat, led=', led)
    if led:
        hallled.sendLed(DIZHU_GAMEID, led, ismgr)
    
    
def sendLed(text, scope = '6', clientIds = []):
    if text:
        ftlog.debug('matchled sendLed text=', text, ' scope=', scope, ' clientIds:', clientIds)
        hallled.sendLed(DIZHU_GAMEID, text, 1, scope, clientIds)


## ----------------------------
## 定义一系列富文本格式生成函数
## ----------------------------

# 纯文本颜色
RICH_COLOR_PLAIN = 'FFFFFF'
# 黄色文本
RICH_COLOR_YELLOW = 'FCF02D'

def _mk_match_champion_rich_text(user_name, room_name, reward_show):
    return [
        [RICH_COLOR_PLAIN, '哇！'],
        [RICH_COLOR_YELLOW, user_name],
        [RICH_COLOR_PLAIN, '在斗地主'],
        [RICH_COLOR_YELLOW, room_name],
        [RICH_COLOR_PLAIN, '中过五关斩六将夺得冠军，获得'],
        [RICH_COLOR_YELLOW, reward_show]
    ]

def _mk_open_box_rich_text(userName, boxName, rewardShow):
    return [
        [RICH_COLOR_YELLOW, '喜从天降！'],
        [RICH_COLOR_PLAIN, '恭喜'],
        [RICH_COLOR_YELLOW, userName],
        [RICH_COLOR_PLAIN, '在'],
        [RICH_COLOR_YELLOW, boxName],
        [RICH_COLOR_PLAIN, '中获得'],
        [RICH_COLOR_YELLOW, rewardShow],
        [RICH_COLOR_YELLOW, '！']
    ]
