# -*- coding=utf-8
'''
Created on 2015年10月9日

@author: zhaojiangang
'''
from datetime import datetime
import json, time
import freetime.util.log as ftlog
from hall.entity import hallconf, datachangenotify, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskPopFiveStarWnd, TodoTaskHelper, TodoTaskGoldRain
from poker.entity.dao import gamedata, daobase
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.biz.item.item import TYAssetUtils

class FiveStarRate(object):
    def __init__(self, channel, version, rateTime=-1, popTime=-1):
        # 渠道
        self.channel = channel
        # 版本
        self.rateVersion = version
        # 评价时间
        self.rateTime = rateTime
        # 最后弹框时间
        self.popTime = popTime
    
_channels = {}
_inited = False

def _reloadConf():
    global _channels
    conf = hallconf.getFiveStarConf()
    channels = conf.get('channels', {})
    for name, channel in channels.iteritems():
        channel['name'] = name
    _channels = channels
    ftlog.debug('fivestarrate._reloadConf channels=', channels.keys())
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:fivestar:0'):
        ftlog.debug('fivestarrate._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('fivestarrate._initialize begin')
    global _channels
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('fivestarrate._initialize end')

def _parseClientId(clientId):
    clientOS, ver, info = strutil.parseClientId(clientId)
    channelName = info.split('.', 2)[-1]
    return ver, clientOS.lower() + '.' + channelName

def _deltaDays(t1, t2):
    return (pktimestamp.getDayStartTimestamp(t1) - pktimestamp.getDayStartTimestamp(t2)) / 86400
    
def _buildCountKey(fsRate, timestamp):
    datestr = datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    return 'fivestar.%s.%s' % (fsRate.channel['name'], datestr)

def _getRateCount(fsRate, timestamp):
    countKey = _buildCountKey(fsRate, timestamp)
    count = daobase.executeMixCmd('get', countKey)
    if count is None:
        return 0
    return int(count)

def _incrRateCount(fsRate, timestamp):
    countKey = _buildCountKey(fsRate, timestamp)
    count = daobase.executeMixCmd('incrby', countKey, 1)
    if count == 1:
        daobase.executeMixCmd('expire', countKey, 86400*2)
    return count

def _canPopFiveStarRate(userId, ver, fsRate, timestamp):
    # 每个版本只能评价一次
    if ver <= fsRate.rateVersion:
        return False
    
    # 两次弹框推送的时间间隔至少需要3天。
    if fsRate.popTime >= 0 and _deltaDays(timestamp, fsRate.popTime) < 3:
        return False
    
    # 每天的量保持稳定(评价次数)；
    # 获取当天所有评论数
    count = _getRateCount(fsRate, timestamp)
    return count < fsRate.channel['rateCountPerDay']
        
def _loadFiveStarRate(userId, channel):
    try:
        field = 'fivestar.%s' % (channel['name'])
        jstr = gamedata.getGameAttr(userId, HALL_GAMEID, field)
        if jstr:
            d = json.loads(jstr)
            return FiveStarRate(channel, d.get('ver', 0), d.get('rateTime'), d.get('popTime'))
    except:
        ftlog.error()
    return FiveStarRate(channel, 0, -1, -1)
    
def _saveFiveStarRate(userId, fsRate):
    d = {'ver':fsRate.rateVersion, 'rateTime':fsRate.rateTime, 'popTime':fsRate.popTime}
    jstr = json.dumps(d)
    field = 'fivestar.%s' % (fsRate.channel['name'])
    gamedata.setGameAttr(userId, HALL_GAMEID, field, jstr)

def findChannel(clientId):
    _ver, channelName = _parseClientId(clientId)
    return _channels.get(channelName)

def clearFiveStarRate(userId, clientId):
    channel = findChannel(clientId)
    if channel:
        field = 'fivestar.%s' % (channel['name'])
        gamedata.delGameAttr(userId, HALL_GAMEID, field)
        
def checkCanTriggleFiveStartRate(userId, clientId, timestamp):
    ver, channelName = _parseClientId(clientId)
    channel = _channels.get(channelName)
    
    if ftlog.is_debug():
        ftlog.debug('fivestarrate.checkCanTriggleFiveStartRate userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', timestamp,
                    'channelName=', channelName,
                    'channel=', channel)
        
    if not channel:
        return False, None
    
    clientConf = hallconf.getFiveStarClientConf(clientId)
    if clientConf.get('disable', 0):
        if ftlog.is_debug():
            ftlog.debug('fivestarrate.checkCanTriggleFiveStartRate userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'clientConf=', clientConf)
        return False, channel

    fsRate = _loadFiveStarRate(userId, channel)
    if _canPopFiveStarRate(userId, ver, fsRate, timestamp):
        return True, channel
    return False, channel
    
def triggleFiveStarRateIfNeed(userId, clientId, timestamp, desc):
    clientConf = hallconf.getFiveStarClientConf(clientId)
    if clientConf.get('disable', 0):
        if ftlog.is_debug():
            ftlog.debug('fivestarrate.triggleFiveStarRateIfNeed userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'desc=', desc,
                        'clientConf=', clientConf)
        return False, None
        
    ver, channelName = _parseClientId(clientId)
    channel = _channels.get(channelName)
    if ftlog.is_debug():
        ftlog.debug('fivestarrate.triggleFiveStarRateIfNeed userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', timestamp,
                    'desc=', desc,
                    'channelName=', channelName,
                    'channel=', channel)
    
    if channel:
        fsRate = _loadFiveStarRate(userId, channel)
        if _canPopFiveStarRate(userId, ver, fsRate, timestamp):
            if 'appendDesc' in channel and _canSendPrize(channel):
                desc += "\n" + channel['appendDesc']
            todotask = TodoTaskPopFiveStarWnd(desc, channel['rateUrl'])
            TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, todotask)
            fsRate.popTime = timestamp
            _saveFiveStarRate(userId, fsRate)
            ftlog.debug('fivestarrate.triggleFiveStarRateIfNeed userId=', userId,
                       'clientId=', clientId,
                       'timestamp=', timestamp,
                       'desc=', desc,
                       'channelName=', channelName,
                       'channel=', channel,
                       'rateUrl=', channel['rateUrl'])
            return True, todotask
    return False, None

def _canSendPrize(channel):
    nowHour = time.localtime().tm_hour
    openHour = channel.get('openHour', 0)
    closeHour = channel.get('openHour', 24)
    return nowHour >= openHour and nowHour < closeHour
            
def onFiveStarRated(userId, clientId, timestamp):
    ver, channelName = _parseClientId(clientId)
    channel = _channels.get(channelName)
    if channel:
        fsRate = _loadFiveStarRate(userId, channel)
        if ver <= fsRate.rateVersion:
            ftlog.warn('fivestarrate.onFiveStarRated not allow !!', userId, clientId, 'clientVersion=', ver, 'rateVersion=', fsRate.rateVersion)
            # 不允许降低版本进行评价，同时也限定每个版本只能评价一次
            return False
        fsRate.rateTime = timestamp
        fsRate.rateVersion = ver
        _saveFiveStarRate(userId, fsRate)
        count = _incrRateCount(fsRate, timestamp)

        # 添加好评奖励
        if 'appendItems' in channel and _canSendPrize(channel):
            items = channel.get('appendItems', [])
            ftlog.debug('fivestarrate.onFiveStarRated appendItems=', items)
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            bSendCoin = False
            changed = []
            for item in items:
                assetKind = userAssets.addAsset(9999, item["itemId"], item["count"], int(time.time()), 'FIVE_STAR_SEND', 0)
                changed.append(assetKind)
                if item['itemId'] == 'user:chip':
                    bSendCoin = True
                    
            changeNames = TYAssetUtils.getChangeDataNames(changed)
            changeNames.add('free')
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, changeNames)
            
            #金币雨
            if bSendCoin == True:
                TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskGoldRain(channel.get('feedback', '感谢您的五星好评')))
            
        ftlog.debug('fivestarrate.onFiveStarRated userId=', userId,
                   'clientId=', clientId,
                   'timestamp=', timestamp,
                   'count=', count)
        return True
    return False
    
if __name__ == '__main__':
    clientId = 'IOS_3.71_tyGuest,weixin.appStore.0-hall6.tuyoo.huanle'
    clientId = 'IOS_3.711_tyAccount,tyGuest,weixin.appStore.0-hall6.tuyoo.huanle'
    print _parseClientId(clientId)
    print _deltaDays(1444447396, 1444447366)

