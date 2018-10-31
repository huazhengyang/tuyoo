# -*- coding:utf-8 -*-
'''
Created on 2017年11月8日

@author: zhaojiangang
'''
import random
from sre_compile import isstring
import urllib
import urlparse

import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hall_timecycle import HallTimeCycleRegister
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import HallShare2Event
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure, pokerconf
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class RewardCycle(object):
    def __init__(self):
        self.timeCycle = None
        self.count = None
    
    def decodeFromDict(self, d):
        self.timeCycle = HallTimeCycleRegister.decodeFromDict(d.get('timeCycle'))
        self.count = d.get('count')
        if not isinstance(self.count, int):
            raise TYBizConfException(d, 'RewardCycle.count must be int')
        return self


class ShareReward(object):
    def __init__(self):
        self.content = None
        self.cycle = None
    
    def decodeFromDict(self, d):
        content = d.get('content')
        self.content = TYContentRegister.decodeFromDict(content)
        self.cycle = RewardCycle().decodeFromDict(d.get('cycle'))
        return self


class ShareItems(object):
    def __init__(self):
        self.items = []
        self.totalWeight = 0
    
    def addItem(self, shareContent, weight):
        assert(weight >= 0)
        s = self.totalWeight
        self.totalWeight += weight
        self.items.append((shareContent, (s, self.totalWeight)))
    
    def choice(self):
        assert(self.items)
        if self.totalWeight > 0:
            v = random.randint(0, self.totalWeight - 1)
            for shareContent, (s, e) in self.items:
                if v >= s and v < e:
                    return shareContent
        return random.choice(self.items)[0]
    

class SharePointGroup(object):
    def __init__(self):
        # 分组ID
        self.groupId = None
        # 分组说明
        self.desc = None
        # 分享奖励 ShareReward
        self.reward = None
    
    def decodeFromDict(self, d):
        self.groupId = d.get('groupId')
        if not isstring(self.groupId) or not self.groupId:
            raise TYBizConfException(d, 'SharePointGroup.groupId must be not empty string')
        
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'SharePointGroup.desc must be string')
        
        reward = d.get('reward')
        if reward:
            self.reward = ShareReward().decodeFromDict(reward)


class SharePoint(object):
    '''分享点'''
    def __init__(self):
        # 分享点ID
        self.pointId = None
        # 属于哪个分组，分组统一奖池
        self.group = None
        self.groupId = None
        # 分享点描述
        self.desc = None
        # 分享奖励 ShareReward
        self._reward = None
        # 本分享点下面的分享内容 list<(shareId, weight)>
        self.shareIdWeightList = None
        # 渠道对应的所有分享内容map<channel, ShareItems >
        self.channel2Items = {}
        # map<shareId, ShareContent>
        self.shareMap = {}
    
    @property
    def reward(self):
        return self._reward if not self.group else self.group.reward
    
    def decodeFromDict(self, d):
        self.pointId = d.get('pointId')
        if not isinstance(self.pointId, int):
            raise TYBizConfException(d, 'SharePoint.pointId must be int')
        
        self.groupId = d.get('groupId')
        if self.groupId is not None and not isstring(self.groupId):
            raise TYBizConfException(d, 'SharePoint.groupId must be string')
        
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'SharePoint.desc must be string')
        
        reward = d.get('reward')
        if reward:
            self._reward = ShareReward().decodeFromDict(reward)
        
        contents = d.get('contents')
        if not isinstance(contents, list):
            raise TYBizConfException(d, 'SharePoint.contents must be list')
        
        self.shareIdWeightList = []
        for shareIdWeight in contents:
            if not isinstance(shareIdWeight, list) or len(shareIdWeight) != 2:
                raise TYBizConfException(d, 'SharePoint.contents must be (shareId, weight) list')
            if not isinstance(shareIdWeight[0], int) or not isinstance(shareIdWeight[1], int):
                raise TYBizConfException(d, 'SharePoint.contents must be (shareId, weight) int list')
            self.shareIdWeightList.append((shareIdWeight[0], shareIdWeight[1]))
            
        return self


class ShareContent(object):
    '''分享'''
    TYPE_URL = 'url'
    TYPE_PIC = 'pic'
    
    def __init__(self):
        # 分享内容ID
        self.shareId = None
        # 分享描述
        self.desc = None
        # 落地页URL
        self.url = None
        # 是否预览
        self.isPreview = None
        # 预览配置
        self.preview = None
        # 分享到哪儿
        self.whereToShare = None
        
        # 关联的渠道 list<"ios.0-hall6.tuyoo.huanle">
        self.channels = []
        # 内容类型 url/pic
        self.shareMethod = None
        # 二维码配置，服务器不关心内容
        self.shareQR = None
    
    def buildUrl(self, userId, parsedClientId, pointId, urlParams):
        from hall.entity import hallshare
        urlParams = urlParams if urlParams is not None else {}
        if -1 != self.url.find('${mixDomain}'):
            domainList = configure.getGameJson(HALL_GAMEID, 'misc', {}).get('mix_domain')
            if not domainList:
                domainList = DEFAULT_MIX_DOMAIN_LIST
            urlParams['mixDomain'] = hallshare.genMixDomain(domainList)
    
        url = strutil.replaceParams(self.url, urlParams)
        
        parsedUrl = urlparse.urlparse(url)
        qparams = urlparse.parse_qs(parsedUrl.query) if parsedUrl.query else {}
        qparams = {k:v[0] for k,v in qparams.iteritems()}
        qparams.update({'uid':userId, 'cid':parsedClientId.cid,
                        'mc':parsedClientId.mc, 'sc':parsedClientId.sc,
                        'time':pktimestamp.getCurrentTimestamp(),
                        'pointId':pointId, 'shareId':self.shareId})
        scode = genSigninCode(qparams)
        qparams['tycode'] = scode
        url = urlparse.urlunparse((parsedUrl[0], parsedUrl[1], parsedUrl[2], parsedUrl[3], urllib.urlencode(qparams), parsedUrl[5]))
        return url
        
    def decodeFromDict(self, d):
        self.shareId = d.get('shareId')
        if not isinstance(self.shareId, int):
            raise TYBizConfException(d, 'ShareContent.shareId must be int')
        
        self.desc = d.get('desc')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'ShareContent.desc must be string')
        
        self.url = d.get('url')
        if not isstring(self.url):
            raise TYBizConfException(d, 'ShareContent.url must be string')
        
        self.isPreview = d.get('isPreview', 0)
        if not isinstance(self.isPreview, int) or self.isPreview not in (0, 1):
            raise TYBizConfException(d, 'ShareContent.isPreview must be int (0, 1)')
        
        if self.isPreview:
            self.preview = d.get('preview')
            if not isinstance(self.preview, dict):
                raise TYBizConfException(d, 'ShareContent.preview must be dict')
        
        self.whereToShare = d.get('whereToShare')
        if not isinstance(self.whereToShare, list):
            raise TYBizConfException(d, 'ShareContent.whereToShare must be list')
        
        channels = d.get('channels', [])
        if not isinstance(channels, list):
            raise TYBizConfException(d, 'ShareContent.channels must be list')
        
        self.channels = []
        for ch in channels:
            self.channels.append(ch.lower())
        
        self.shareMethod = d.get('shareMethod')
        if not self.shareMethod:
            raise TYBizConfException(d, 'ShareContent.shareMethod must be string')
        
        self.shareQR = d.get('shareQR')
        if self.shareQR is not None and not isinstance(self.shareQR, dict):
            raise TYBizConfException(d, 'ShareContent.shareQR must be dict')
        
        self.shareRule = d.get('shareRule')
        if not isinstance(self.shareRule, dict):
            raise TYBizConfException(d, 'ShareContent.shareRule must be dict')

        return self
        

# 初始化标记
_inited = False
# map<gameId, map<sharePointId, SharePoint> >
_gameSharePointMap = {}
# 分组配置 map<gameId, map<groupId, SharePointGroup> >
_gameSharePointGroupMap = {}


def _onConfChanged(event):
    if _inited and event.isModuleChanged('share2'):
        for gameId in pokerconf.getConfigGameIds():
            if event.isChanged('game:%s:share2:0' % (gameId)):
                _reloadGameConf(gameId)


def _reloadGameConf(gameId):
    sharePointMap, sharePointGroupMap = _loadGameConf(gameId)
    if sharePointMap:
        _gameSharePointMap[gameId] = sharePointMap
        ftlog.info('hall_share2._reloadGameConf',
                   'gameId=', gameId,
                   'sharePoints=', [(sharePoint.pointId, sharePoint.groupId,
                                     [(channel, [item[0].shareId for item in shareItems.items]) for channel, shareItems in sharePoint.channel2Items.iteritems()])
                                    for sharePoint in sharePointMap.values()])
    else:
        _gameSharePointMap.pop(gameId, None)
    
    if sharePointGroupMap:
        ftlog.info('hall_share2._reloadGameConf',
                   'gameId=', gameId,
                   'sharePointGroups=', sharePointMap.keys())
        _gameSharePointGroupMap[gameId] = sharePointGroupMap
    else:
        _gameSharePointGroupMap.pop(gameId, None)


def _reloadConf():
    _gameSharePointMap.clear()
    for gameId in pokerconf.getConfigGameIds():
        _reloadGameConf(gameId)


def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)


def _loadGameConf(gameId):
    conf = configure.getGameJson(gameId, 'share2', {}, 0)
    if not conf:
        return None, None
    
    sharePointMap = {}
    sharePointGroupMap = {}
    shareContentMap = {}
    
    for gp in conf.get('groups', []):
        sharePointGroup = SharePointGroup().decodeFromDict(gp)
        if sharePointGroup.groupId in sharePointGroupMap:
            raise TYBizConfException(gp, 'Duplicate sharePointGroupId %s' % (sharePointGroup.groupId))
        sharePointGroupMap[sharePointGroup.groupId] = sharePointGroup

    for sp in conf.get('points', []):
        sharePoint = SharePoint().decodeFromDict(sp)
        if sharePoint.pointId in sharePointMap:
            raise TYBizConfException(sp, 'Duplicate sharePointId %s' % (sharePoint.pointId))
        if sharePoint.groupId:
            group = sharePointGroupMap.get(sharePoint.groupId)
            if not group:
                raise TYBizConfException(sp, 'Not found groupId %s for sharePoint %s' % (sharePoint.groupId, sharePoint.pointId))
            sharePoint.group = group
        sharePointMap[sharePoint.pointId] = sharePoint
    
    for sc in conf.get('contents', []):
        shareContent = ShareContent().decodeFromDict(sc)
        if shareContent.shareId in shareContentMap:
            raise TYBizConfException(sp, 'Duplicate shareId %s' % (shareContent.shareId))
        shareContentMap[shareContent.shareId] = shareContent
    
    # 把shareContent对象和sharePoint关联
    for sharePoint in sharePointMap.values():
        for shareId, weight in sharePoint.shareIdWeightList:
            shareContent = shareContentMap.get(shareId)
            if shareContent:
                sharePoint.shareMap[shareId] = shareContent
                channels = shareContent.channels or ['']
                for channel in channels:
                    shareItems = sharePoint.channel2Items.get(channel)
                    if not shareItems:
                        shareItems = ShareItems()
                        sharePoint.channel2Items[channel] = shareItems
                    shareItems.addItem(shareContent, weight)
            else:
                ftlog.warn('Unknown shareId %s in sharePoint %s' % (shareId, sharePoint.pointId))
    
    return sharePointMap, sharePointGroupMap


class ParsedClientId(object):
    def __init__(self, clientId, cid, clientOS, clientVer,
                 login, pay, special, mc, sc):
        self.clientId = clientId
        self.cid = cid
        self.clientOS = clientOS
        self.clientVer = clientVer
        self.login = login
        self.pay = pay
        self.special = special
        self.mc = mc
        self.sc = sc
        self._channel = None
        self._hallGameId = None
        
    @property
    def channel(self):
        if not self._channel:
            self._channel = '%s.%s.%s.%s' % (self.clientOS, self.special, self.mc, self.sc)
        return self._channel
    
    @property
    def hallGameId(self):
        if self._hallGameId is None:
            self._hallGameId = strutil.getGameIdFromHallClientId(self.clientId)
        return self._hallGameId
    
    @classmethod
    def parseClientId(cls, clientId):
        cid = configure.clientIdToNumber(clientId)
        if cid == 0:
            return None
    
        clientOS, clientVer, info = strutil.parseClientId(clientId)
        parts = info.split('.')
        if len(parts) < 5:
            return None
        
        return ParsedClientId(clientId, cid, clientOS.lower(), clientVer,
                              parts[0], parts[1], parts[2], parts[3], parts[4])


def getSharePoint(gameId, parsedClientId, sharePointId):
    '''
    获取分享点
    '''
    gameId = gameId if gameId != 9999 else parsedClientId.hallGameId
    return _gameSharePointMap.get(gameId, {}).get(sharePointId)
    

def getShareContentWithShareId(gameId, userId, parsedClientId, sharePointId, shareId):
    sharePoint = getSharePoint(gameId, parsedClientId, sharePointId)
    if ftlog.is_debug():
        ftlog.debug('hall_share2.getShareContent',
                    'gameId=', gameId,
                    'userId=', userId,
                    'clientId=', parsedClientId.clientId,
                    'sharePointId=', sharePointId,
                    'sharePoint=', sharePoint)

    if not sharePoint:
        if ftlog.is_debug():
            ftlog.debug('hall_share2.getShareContent UnknownSharePoint',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', parsedClientId.clientId,
                        'sharePointId=', sharePointId,
                        'sharePoint=', sharePoint)
        return None, None
    
    return sharePoint, sharePoint.shareMap.get(shareId)
    

def getShareContent(gameId, userId, parsedClientId, sharePointId):
    sharePoint = getSharePoint(gameId, parsedClientId, sharePointId)
    if ftlog.is_debug():
        ftlog.debug('hall_share2.getShareContent',
                    'gameId=', gameId,
                    'userId=', userId,
                    'clientId=', parsedClientId.clientId,
                    'sharePointId=', sharePointId,
                    'sharePoint=', sharePoint)

    if not sharePoint:
        if ftlog.is_debug():
            ftlog.debug('hall_share2.getShareContent UnknownSharePoint',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', parsedClientId.clientId,
                        'sharePointId=', sharePointId,
                        'sharePoint=', sharePoint)
        return None, None
    
    shareItems = sharePoint.channel2Items.get(parsedClientId.channel)

    if not shareItems:
        shareItems = sharePoint.channel2Items.get('')

    shareContent = shareItems.choice() if shareItems else None
    
    if ftlog.is_debug():
        ftlog.debug('hall_share2.getShareContent',
                    'gameId=', gameId,
                    'userId=', userId,
                    'clientId=', parsedClientId.clientId,
                    'sharePointId=', sharePointId,
                    'sharePoint=', sharePoint,
                    'content=', shareContent.shareId if shareContent else None)
    
    return (sharePoint, shareContent)


def getStatusField(sharePoint):
    return 'pt:%s' % (sharePoint.pointId) if not sharePoint.group else 'gp:%s' % (sharePoint.groupId)


def loadShareStatus(gameId, userId, sharePoint, timestamp):
    jstr = None
    key = 'share2.status:%s:%s' % (gameId, userId)
    field = getStatusField(sharePoint)
    
    try:
        jstr = daobase.executeUserCmd(userId, 'hget', key, field)
        if ftlog.is_debug():
            ftlog.debug('hall_share2.loadShareStatus',
                        'gameId=', gameId,
                        'userId=', userId,
                        'pointId=', sharePoint.pointId,
                        'groupId=', sharePoint.groupId,
                        'field=', field,
                        'timestamp=', timestamp,
                        'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            if ftlog.is_debug():
                ftlog.debug('hall_share2.loadShareStatus',
                            'gameId=', gameId,
                            'userId=', userId,
                            'pointId=', sharePoint.pointId,
                            'groupId=', sharePoint.groupId,
                            'field=', field,
                            'timestamp=', timestamp,
                            'jstr=', jstr,
                            'd=', d,
                            'isSameCycle=', sharePoint.reward.cycle.timeCycle.isSameCycle(d['ts'], timestamp))
            if not sharePoint.reward.cycle.timeCycle.isSameCycle(d['ts'], timestamp):
                d['ts'] = timestamp
                d['rct'] = 0
            return d['ts'], d['rct']
    except:
        ftlog.error('hall_share2.getShareStatus',
                    'userId=', userId,
                    'pointId=', sharePoint.pointId,
                    'groupId=', sharePoint.groupId,
                    'field=', field,
                    'timestamp=', timestamp,
                    'jstr=', jstr)
    return timestamp, 0


def saveShareStatus(gameId, userId, sharePoint, timestamp, rewardCount):
    jstr = strutil.dumps({'ts':timestamp, 'rct':rewardCount})
    key = 'share2.status:%s:%s' % (gameId, userId)
    field = getStatusField(sharePoint)
    daobase.executeUserCmd(userId, 'hset', key, field, jstr)
    if ftlog.is_debug():
        ftlog.debug('hall_share2.saveShareStatus',
                    'gameId=', gameId,
                    'userId=', userId,
                    'pointId=', sharePoint.pointId,
                    'groupId=', sharePoint.groupId,
                    'field=', field,
                    'timestamp=', timestamp,
                    'jstr=', jstr)


def sendReward(gameId, userId, sharePoint):
    from hall.entity import hallitem
    if not sharePoint.reward.content:
        return None

    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetList = userAssets.sendContent(gameId, sharePoint.reward.content, 1, True,
                                       pktimestamp.getCurrentTimestamp(),
                                       'SHARE2_REWARD', sharePoint.pointId)
    ftlog.info('hall_share2.sendReward',
               'gameId=', gameId,
               'userId=', userId,
               'pointId=', sharePoint.pointId,
               'groupId=', sharePoint.groupId,
               'rewards=', [(atup[0].kindId, atup[1]) for atup in assetList])
    changedDataNames = TYAssetUtils.getChangeDataNames(assetList)
    datachangenotify.sendDataChangeNotify(gameId, userId, changedDataNames)

    return assetList


def incrRewardCount(gameId, userId, sharePoint, timestamp):
    _, rewardCount = loadShareStatus(gameId, userId, sharePoint, timestamp)
    
    if sharePoint.reward.cycle.count != -1 and rewardCount >= sharePoint.reward.cycle.count:
        return False, rewardCount
    
    rewardCount += 1
    saveShareStatus(gameId, userId, sharePoint, timestamp, rewardCount)
    
    return True, rewardCount

def getLeftRewardCount(gameId, userId, clientId, sharePointId, timestamp=None):
    '''
    获取分享点还有几次奖励
    '''
    parsedClientId = ParsedClientId.parseClientId(clientId)
    if not parsedClientId:
        ftlog.warn('hall_share2.getLeftRewardCount BadClientId',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return 0

    sharePoint = getSharePoint(gameId, parsedClientId, sharePointId)
    
    if not sharePoint:
        ftlog.warn('hall_share2.getLeftRewardCount UnknownSharePoint',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return 0
    
    if not sharePoint.reward:
        ftlog.warn('hall_share2.getLeftRewardCount NotHaveReward',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return 0

    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    _, rewardCount = loadShareStatus(gameId, userId, sharePoint, timestamp)
    if sharePoint.reward.cycle.count != -1 and rewardCount >= sharePoint.reward.cycle.count:
        return 0
    
    return sharePoint.reward.cycle.count - rewardCount
    

def gainShareReward(gameId, userId, clientId, sharePointId, timestamp=None):
    parsedClientId = ParsedClientId.parseClientId(clientId)
    if not parsedClientId:
        ftlog.warn('hall_share2.gainShareReward BadClientId',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return False, None

    sharePoint = getSharePoint(gameId, parsedClientId, sharePointId)
    
    if not sharePoint:
        ftlog.warn('hall_share2.gainShareReward UnknownSharePoint',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return False, None
    
    if not sharePoint.reward:
        ftlog.warn('hall_share2.gainShareReward NotHaveReward',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return False, None
    
    from hall.game import TGHall
    TGHall.getEventBus().publishEvent(HallShare2Event(gameId, userId, sharePointId))
    
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    
    ok, rewardCount = incrRewardCount(gameId, userId, sharePoint, timestamp)
    
    if not ok:
        if ftlog.is_debug():
            ftlog.debug('hall_share2.gainShareReward UpperLimit',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'sharePointId=', sharePointId,
                        'rewardCount=', rewardCount,
                        'maxRewardCount=', sharePoint.reward.cycle.count)
        return False, None

    rewards = sendReward(gameId, userId, sharePoint)
    return True, rewards
    

DEFAULT_MIX_DOMAIN_LIST = ['3g.tuyoo.com']

API_KEY = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'

def genSigninCode(params):
    sk = sorted(params.keys())
    strs = ['%s=%s' % (k, str(params[k]).strip()) for k in sk]
    cstr = '&'.join(strs)
    cstr += API_KEY
    return strutil.md5digest(cstr)


def checkCode(params):
    code = ''
    if 'code' in params:
        code = params['code']
        del params['code']
    
    sk = sorted(params.keys())
    strs = ['%s=%s' % (k, str(params[k]).strip()) for k in sk]
    cstr = '&'.join(strs)
    cstr += API_KEY
    if code != strutil.md5digest(cstr):
        return -1, 'Verify code error'

    acttime = int(params.get('time', 0))
    if abs(pktimestamp.getCurrentTimestamp() - acttime) > 10:
        return -1, 'verify time error'
    return 0, None


def buildShareTodoTask(gameId, userId, clientId, sharePointId, urlParams):
    from hall.entity.todotask import TodoTaskNewShareRulePop
    
    parsedClientId = ParsedClientId.parseClientId(clientId)
    if not parsedClientId:
        ftlog.warn('hall_share2.buildShareTodoTask BadClientId',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return None
    
    sharePoint, shareContent = getShareContent(gameId, userId, parsedClientId, sharePointId)
    if not sharePoint:
        ftlog.warn('hall_share2.buildShareTodoTask UnknownSharePoint',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return None
    
    if not shareContent:
        ftlog.warn('hall_share2.buildShareTodoTask NoShareContent',
                   'gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'sharePointId=', sharePointId)
        return None
    
    url = shareContent.buildUrl(userId, parsedClientId, sharePointId, urlParams)
    return TodoTaskNewShareRulePop(gameId, sharePointId, shareContent.shareId, url,
                                   shareContent.shareMethod, shareContent.whereToShare,
                                   shareContent.shareRule, shareContent.preview, shareContent.shareQR)
    

