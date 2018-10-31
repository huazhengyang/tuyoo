# -*- coding=utf-8
'''
Created on 2017年6月27日

@author: wangzhen

金币场，累计奖池抽奖
'''

import time
import random
import copy
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata, sessiondata
import poker.entity.biz.message.message as pkmessage
from hall.entity import hallconf
from hall.servers.util import util_user
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.biz import bireport



_inited = False
_all_config = {}     # 抽奖总配置



def isOpen(gameId):
    '''
    是否开启抽奖
    :param gameId:
    '''
    return True if _getConfig(gameId) else False

def getNowAndNextLevel(userId, gameId):
    config = _getConfig(gameId)
    if not config:
        return 0,0,0
    winCount = getWinCount(userId, gameId)
    total = config['totalWin']
    pool = getPool(userId, gameId)
    if winCount < total:
        return 0, 1, config['lotteryInfos'][0]['needPool']-pool
    for info in config['lotteryInfos']:
        if pool < info['needPool']:
            return info['level']-1,info['level'],max(0,info['needPool']-pool)
        else:
            continue
    return info['level'],info['level'],max(0,info['needPool']-pool)

def getTakePool(gameId):
    '''
    获取奖池抽取比例
    :param gameId:
    '''
    config = _getConfig(gameId)
    if not config:
        return 0
    return config['takePool']

def getTotal(gameId):
    '''
    获取抽奖需要的赢的总局数
    :param gameId:
    '''
    config = _getConfig(gameId)
    if not config:
        return 0
    return config['totalWin']

def getLotteryTaskInfos(userId, gameId):
    '''
    获取抽奖信息
    :param userId:
    :param gameId:
    '''
    config = _getConfig(gameId)
    if not config:
        return
    
    mo = MsgPack()
    mo.setCmd('getLotteryTask')
    mo.setResult('userId', userId)
    mo.setResult('gameId', gameId)
    mo.setResult('total', config['totalWin'])
    mo.setResult('now', getWinCount(userId, gameId))
    mo.setResult('pool', getPool(userId, gameId))
    nowLevel,nextLevel,nextDistance = getNowAndNextLevel(userId, gameId)
    mo.setResult('nowLevel', nowLevel)
    mo.setResult('nextLevel', nextLevel)
    mo.setResult('nextDistance', nextDistance)
    mo.setResult('lotteryInfos', _getLotteryInfos(gameId))
    router.sendToUser(mo, userId)

def doLottery(userId, gameId):
    '''
    用户抽奖
    :param userId:
    :param gameId:
    :param clientId:
    '''
    config = _getConfig(gameId)
    if not config:
        return
    
    nowLevel, _, _ = getNowAndNextLevel(userId, gameId)
    if nowLevel == 0:
        ftlog.warn('doLottery error, nowLevel = 0', 'userId =', userId, 'gameId =', gameId)
        _doLotteryFailed(userId, gameId, 'doLottery error, nowLevel = 0')
        return
    
    nowItems = config['lotteryInfos'][nowLevel-1]['items']
    length = len(nowItems)
    if length <= 0:
        ftlog.error('doLottery error, items is []')
        _doLotteryFailed(userId, gameId, 'doLottery error, items is []')
        return
    
    nowItems= copy.deepcopy(nowItems)
    nowItems.sort(key= lambda x: x['value'])
    pool = int(getPool(userId, gameId) * config['lotteryInfos'][nowLevel-1]['times'])
    poolUsed = pool
    if pool < nowItems[0]['value']:
        pool = nowItems[0]['value']
    if pool > nowItems[-1]['value']:
        pool = nowItems[-1]['value']
    
    intervals = []
    if length == 1:
        intervals.append( (nowItems[0],nowItems[0]) )
    else:
        for i in range(length - 1):
            for j in range(i+1, length):
                if pool >= nowItems[i]['value'] and pool <= nowItems[j]['value']:
                    intervals.append( (nowItems[i],nowItems[j]) )
    
    interval = random.choice(intervals)
    randValue = random.randint(interval[0]['value'], interval[1]['value'])
    if randValue > pool:
        selected = interval[0]
    else:
        selected = interval[1]
    
    ftlog.debug('doLottery success, userId =', userId, 'gameId =', gameId, 'selected =', selected['index'], 'randValue =', randValue, 'pool =', getPool(userId, gameId))
    # 重置奖池，添加奖品
    _resetPoolAndWinCount(userId, gameId, nowLevel, poolUsed, selected['value'])
    util_user.addAssetNotify(hallconf.HALL_GAMEID, userId, selected['itemId'], selected['count'], 'HALL_LOTTERY_TASK_REWARD', 0)
    # 给客户端发中奖消息
    mo = MsgPack()
    mo.setCmd('lotteryTask')
    mo.setResult('userId', userId)
    mo.setResult('gameId', gameId)
    mo.setResult('reward', selected['index'])
    router.sendToUser(mo, userId)
    # 发邮件提示
    mailInfo = config.get('mail', None)
    if mailInfo:
        mail = mailInfo[0] % (time.strftime(mailInfo[1]), selected['fullname'])
        pkmessage.send(hallconf.HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)

def _doLotteryFailed(userId, gameId, failedMsg):
    '''
    抽奖失败，需通知客户端，index 为 0 即可
    :param userId:
    :param gameId:
    :param failedMsg:    失败信息
    '''
    # 给客户端发中奖消息
    mo = MsgPack()
    mo.setCmd('lotteryTask')
    mo.setResult('userId', userId)
    mo.setResult('gameId', gameId)
    mo.setResult('reward', 0)
    ftlog.debug("doLottery failed sendToUser",userId, gameId, failedMsg)
    router.sendToUser(mo, userId)

def addPool(userId, gameId, value):
    '''
    增加奖池
    :param userId:
    :param gameId:
    :param count:
    '''
    if not isOpen(gameId):
        return 0
    bireport.reportGameEvent('HALL_LOTTERY_TASK_ADD', userId, gameId, 0, 0, 0, value, 0, 0, [], sessiondata.getClientId(userId))
    return gamedata.incrGameAttr(userId, gameId, "lotterytask_pool", value)

def getPool(userId, gameId):
    '''
    获取奖池
    :param userId:
    :param gameId:
    '''
    if not isOpen(gameId):
        return 0
    return gamedata.getGameAttrInt(userId, gameId, "lotterytask_pool")

def addWinCount(userId, gameId):
    '''
    增加获胜次数
    :param userId:
    :param gameId:
    :param count:
    '''
    if not isOpen(gameId):
        return 0
    return gamedata.incrGameAttr(userId, gameId, "lotterytask_win", 1)

def getWinCount(userId, gameId):
    '''
    获取获胜次数
    :param userId:
    :param gameId:
    '''
    if not isOpen(gameId):
        return 0
    return gamedata.getGameAttrInt(userId, gameId, "lotterytask_win")

def resetWinCount(userId, gameId):
    '''
    重置获胜次数
    :param userId:
    :param gameId:
    '''
    if not isOpen(gameId):
        return
    gamedata.setGameAttr(userId, gameId, "lotterytask_win", 0)

def _resetPoolAndWinCount(userId, gameId, nowLevel, poolUsed, rewardValue):
    '''
    重置奖池和获胜次数
    :param userId:
    :param gameId:
    '''
    pool = getPool(userId, gameId)
    gamedata.setGameAttrs(userId, gameId, ["lotterytask_pool", "lotterytask_win"], [0, 0])
    bireport.reportGameEvent('HALL_LOTTERY_TASK_CONSUME', userId, gameId, 0, 0, 0, -pool, nowLevel, 0, [], sessiondata.getClientId(userId), -poolUsed, rewardValue)

def _getConfig(gameId):
    global _all_config
    config = _all_config
    if not config:
        return None
    key = str(gameId)
    if not config.has_key(key):
        return None
    if not config[key]['isOpen']:
        return None
    return config[key]

def _getLotteryInfos(gameId):
    config = _getConfig(gameId)
    if not config:
        return None
    lotteryInfos = []
    for info in config['lotteryInfos']:
        data = {}
        data['level'] = info['level']
        data['needPool'] = info['needPool']
        data['items'] = []
        for item in info['items']:
            data['items'].append({'name':item['name'], 'count':item['count'], 'pic':item['pic']})
        lotteryInfos.append(data)
    return lotteryInfos

def _getNowLevelItems(userId, gameId):
    nowLevel, _, _ = getNowAndNextLevel(userId, gameId)
    if nowLevel == 0:
        return None
    else:
        return
    
def _reloadConf():
    global _all_config
    ftlog.debug('begin ... reload hall lottery_task config =', _all_config)
    config = hallconf.getHallLotteryTaskConf()
    if not config:
        return
    _all_config = config
    for key in _all_config:
        value = _all_config[key]
        for info in value['lotteryInfos']:
            assert len(info['items']) > 0
            #info['items'].sort(key= lambda x: x['value'])
    ftlog.debug('end ... reload hall lottery_task config =', _all_config)

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:lottery_task:0'):
        ftlog.debug('hall lottery_task config _onConfChanged')
        _reloadConf()
    
def _initialize():
    ftlog.debug('hall lottery_task initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall lottery_task initialize end')
    