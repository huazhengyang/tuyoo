# -*- coding=utf-8
'''
Created on 2015年7月30日

@author: zhaojiangang
'''

import json
import random
from sre_compile import isstring
import urllib
import urlparse

import freetime.util.log as ftlog
from hall.entity import hallconf, datachangenotify, halldomains
from hall.entity.hall_red_envelope import hall_red_envelope
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskShareUrl, TodoTaskShareGift, \
    TodoTaskHelper, TodoTaskGoldRain
from hall.game import TGHall
from poker.entity.biz import bireport
from poker.entity.biz.confobj import TYConfableRegister
from poker.entity.biz.content import TYContentRegister, TYContentUtils
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message import message as pkmessage
from poker.entity.configure import configure
from poker.entity.dao import gamedata, sessiondata, daobase
import poker.entity.dao.gamedata as pkgamedata
from poker.entity.events.tyevent import EventConfigure, UserEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class HallShareConfigItem(object):
    def __init__(self):
        self.value = None
        self.conditions = None

    def decodeFromDict(self, d):
        from hall.entity.hallusercond import UserConditionRegister
        self.value = d.get('value', '')
        if not isstring(self.value):
            raise TYBizConfException(d, 'hallshare.HallShareConfigItem.value must be string')

        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
        return self

    def isSuitable(self, userId, gameId):
        if len(self.conditions) == 0:
            return True

        clientId = sessiondata.getClientId(userId)
        for cond in self.conditions:
            if not cond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp()):
                return False

        return True

    def getValue(self):
        return self.value


class HallShareConfigs(object):
    def __init__(self):
        self.values = []

    def decodeFromDict(self, dvs):
        for dv in dvs:
            value = HallShareConfigItem().decodeFromDict(dv)
            self.values.append(value)

        return self

    def getValue(self, userId, gameId):
        results = []
        for v in self.values:
            if v.isSuitable(userId, gameId):
                results.append(v)

        if len(results) == 0:
            if ftlog.is_debug():
                ftlog.debug('HallShareConfigs.getValue do not find suitable value!!!!')
            return '0'

        rd = random.randint(0, len(results) - 1)
        if ftlog.is_debug():
            ftlog.debug('HallShareConfigs.getValue have choices: ', len(results), ' choose : ', rd)

        return results[rd].getValue()


class HallShare(object):
    def __init__(self):
        # 分享ID
        self.shareId = None
        self.type = None
        self.subType = None
        self.desc = None
        self.def_desc = None
        self.smsDesc = None
        self.tips = None
        self.title = None
        self.def_title = None
        self.url = None
        self.def_url = None
        # 每日最大领奖次数
        self.maxRewardCount = None
        self.rewardContent = None
        self.mail = None
        self.shareIcon = None
        self.def_shareIcon = None
        self.rewardTimeCycle = None

    def setUrl(self, url):
        '''
        设置分享时的url
        '''
        self.def_url = url

    def setDesc(self, desc):
        '''
        设置分享描述文案，允许在配置之外设置文案
        '''
        self.def_desc = desc

    def setSmsDesc(self, smsDesc):
        '''
        设置短信文案，允许在配置之外设置文案
        '''
        self.smsDesc = smsDesc

    def setTitle(self, title):
        '''
        设置分享标题，允许在配置之外自定义
        '''
        self.def_title = title

    def setTips(self, tips):
        '''
        设置分享提示信息，允许在配置之外自定义
        '''
        self.tips = tips

    def setMail(self, mail):
        '''
        设置邮件内容，允许在配置之外自定义
        '''
        self.mail = mail

    def setShareIcon(self, shareIcon):
        '''
        设置分享标题，允许在配置之外自定义
        '''
        self.def_shareIcon = shareIcon

    def encryptCode(self, userId):
        """加密用户ID"""
        from hashlib import md5
        m = md5()
        md5str = 'wx.tuyoo.com-api-' + str(userId) + '-wx.tuyoo.com-api'
        m.update(md5str)
        md5code = m.hexdigest()
        return str(userId) + '&tycode=' + md5code.lower()

    def setNotifyInfo(self, userId, notifyInfo, module):
        info = {}
        info['shareId'] = self.shareId
        info['info'] = notifyInfo
        info['module'] = module

        infoStr = json.dumps(info)
        if ftlog.is_debug():
            ftlog.debug('HallShare.setNotifyInfo : ', infoStr)

        pkgamedata.setGameAttr(userId, HALL_GAMEID, 'shareInfo', infoStr)

    @classmethod
    def parseClientId(cls, clientId):
        #os_version_login.pay.special.main.sub 
        cid = configure.clientIdToNumber(clientId)
        if cid == 0:
            return False, 0, '', ''
        
        _, _, info = strutil.parseClientId(clientId)
        parts = info.split('.')
        if len(parts) < 5:
            return False, 0, '', ''
        
        return True, cid, parts[3], parts[4]

    @classmethod
    def randomUrlPrefix(cls):
        import string
        letters = string.ascii_lowercase + string.digits
        return ''.join([random.choice(letters) for _ in range(8)])
    
    def getUrl(self, gameId, userId, url_replace_dict=None):
        if self.def_url:
            return self.def_url

        shareUrl = self.url.getValue(userId, gameId)
        if ftlog.is_debug():
            ftlog.debug('HallShare.getUrl url: ', shareUrl)

        url_replace_dict = url_replace_dict if url_replace_dict else {'promoteCode': userId, 'encryptCode': self.encryptCode(userId)}
        url_replace_dict['uid'] = userId
        
        clientId = sessiondata.getClientId(userId)
        ok, cid, mc, sc = self.parseClientId(clientId)
        if ok:
            url_replace_dict['mc'] = mc
            url_replace_dict['sc'] = sc
            url_replace_dict['cid'] = cid
        
        if shareUrl.find('${urlPrefix}'):
            url_replace_dict['urlPrefix'] = self.randomUrlPrefix()
        # 替换域名
        return halldomains.replacedDomain(shareUrl, url_replace_dict)

    def getDesc(self, gameId, userId, randChoise=False):
        if self.def_desc and not randChoise:
            return self.def_desc

        shareDesc = self.desc.getValue(userId, gameId)
        if ftlog.is_debug():
            ftlog.debug('HallShare.getDesc desc: ', shareDesc)

        return strutil.replaceParams(shareDesc, {'promoteCode': userId, 'url': self.getUrl(gameId, userId)})

    def getTitle(self, gameId, userId):
        if self.def_title:
            return self.def_title

        shareTitle = self.title.getValue(userId, gameId)
        return shareTitle

    def getShareIcon(self, gameId, userId):
        if self.def_shareIcon:
            return self.def_shareIcon

        icon = self.shareIcon.getValue(userId, gameId)
        return icon

    def getSmsDesc(self, gameId, userId):
        return strutil.replaceParams(self.smsDesc, {'promoteCode': userId, 'url': self.getUrl(gameId, userId)})

    def buildTodotask(self, gameId, userId, shareLoc):
        '''
        @param shareLoc: 触发分享的位置或模块之类的
        '''
        raise NotImplemented()

    def decodeFromDict(self, d):
        from hall.entity.hall_exmall import TimeCycleRegister
        from hall.entity.hall_exmall import TimeCyclePerDay
        
        self.shareId = d.get('shareId', '')
        if not isinstance(self.shareId, int):
            raise TYBizConfException(d, 'HallShare.shareId must be int')

        self.type = d.get('type', '')
        if not isstring(self.type):
            raise TYBizConfException(d, 'HallShare.type must be string')

        self.subType = d.get('subType', '')
        if not isstring(self.subType):
            raise TYBizConfException(d, 'HallShare.subType must be string')

        self.desc = HallShareConfigs().decodeFromDict(d.get('desc', []))

        self.smsDesc = d.get('smsDesc', '')
        if not isstring(self.smsDesc):
            raise TYBizConfException(d, 'HallShare.smsDesc must be string')

        self.tips = d.get('tips', '')
        if not isstring(self.tips):
            raise TYBizConfException(d, 'HallShare.tips must be string')

        self.title = HallShareConfigs().decodeFromDict(d.get('title', []))

        self.url = HallShareConfigs().decodeFromDict(d.get('url', []))

        self.maxRewardCount = d.get('maxRewardCount')
        if not isinstance(self.maxRewardCount, int):
            raise TYBizConfException(d, 'HallShare.maxRewardCount must be int')

        self.rewardContent = None
        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.rewardContent = TYContentRegister.decodeFromDict(rewardContent)

        self.mail = d.get('mail', '')
        if not isstring(self.mail):
            raise TYBizConfException(d, 'HallShare.mail must be string')

        self.shareIcon = HallShareConfigs().decodeFromDict(d.get('shareIcon', []))

        rewardTimeCycleD = d.get('rewardTimeCycle')
        if rewardTimeCycleD:
            self.rewardTimeCycle = TimeCycleRegister.decodeFromDict(rewardTimeCycleD)
        else:
            self.rewardTimeCycle = TimeCyclePerDay()
        self._decodeFromDictImpl(d)
        
        return self

    def _decodeFromDictImpl(self, d):
        pass


class HallShareUrl(HallShare):
    TYPE_ID = 'hall.share.url'

    def __init__(self):
        super(HallShareUrl, self).__init__()
        # 二维码展现机制改动
        self.contentType = None
        self.picurl = None
        self._qrcodeUrl = None

    def buildTodotask(self, gameId, userId, shareLoc, url_replace_dict=None):
        '''
        @param shareLoc: 触发分享的位置或模块之类的
        '''
        return TodoTaskShareUrl(self.shareId, self.type, self.subType,
                                self.getDesc(gameId, userId), self.getUrl(gameId, userId, url_replace_dict),
                                self.tips, self.getTitle(gameId, userId), self.getShareIcon(gameId, userId),
                                self.contentType, self.picurl, self.getQrcodeUrl(gameId, userId))

    def _decodeFromDictImpl(self, d):
        self.contentType = d.get('contentType')
        self.picurl = d.get('picurl')
        qrcodeUrl = d.get('qrcodeUrl')
        if qrcodeUrl:
            self._qrcodeUrl = HallShareConfigs().decodeFromDict(qrcodeUrl)

    def getQrcodeUrl(self, gameId, userId):
        if self._qrcodeUrl:
            qrcodeUrl = self._qrcodeUrl.getValue(userId, gameId)
            # 替换域名
            return halldomains.replacedDomain(qrcodeUrl, {})


class HallSharePromote(HallShare):
    '''
    以前的内推广
    '''
    TYPE_ID = 'hall.share.promote'

    def __init__(self):
        super(HallSharePromote, self).__init__()
        self.topRewardContent = None
        self.bottomRewardContent = None

    def buildTodotask(self, gameId, userId, shareLoc, url_replace_dict=None):
        '''
        @param shareLoc: 触发分享的位置或模块之类的
        '''
        from hall.entity import hallitem
        descUpper = TYContentUtils.getMinFixedAssetCount(self.topRewardContent, hallitem.ASSET_CHIP_KIND_ID)
        descLower = TYContentUtils.getMinFixedAssetCount(self.bottomRewardContent, hallitem.ASSET_CHIP_KIND_ID)
        return TodoTaskShareGift(self.shareId
                                 , shareLoc
                                 , self.getDesc(gameId, userId)
                                 , self.getUrl(gameId, userId, url_replace_dict)
                                 , self.getTitle(gameId, userId)
                                 , descUpper
                                 , descLower
                                 , self.getShareIcon(gameId, userId)
                                 , self.tips)

    def _decodeFromDictImpl(self, d):
        self.topRewardContent = self.bottomRewardContent = self.rewardContent
        topRewardContent = d.get('topRewardContent')
        if topRewardContent:
            self.topRewardContent = TYContentRegister.decodeFromDict(topRewardContent)
        bottomRewardContent = d.get('bottomRewardContent')
        if bottomRewardContent:
            self.bottomRewardContent = TYContentRegister.decodeFromDict(bottomRewardContent)


class HallShareRegister(TYConfableRegister):
    _typeid_clz_map = {
        HallShareUrl.TYPE_ID: HallShareUrl,
        HallSharePromote.TYPE_ID: HallSharePromote
    }


_inited = False
# key=name, value=HallShare
_shareMap = {}
# 分享的配置
_shareConfig = {}


def _reloadConf():
    global _shareMap
    global _shareConfig

    shareMap = {}
    conf = hallconf.getShareConf()
    shares = conf.get('shares', [])
    for shareDict in shares:
        share = HallShareRegister.decodeFromDict(shareDict)
        if share.shareId in shareMap:
            raise TYBizConfException(shareDict, 'Duplicate shareId %s' % (share.shareId))
        shareMap[share.shareId] = share
    _shareMap = shareMap
    ftlog.debug('hallshare._reloadConf successed shareIds=', shareMap.keys())

    tcConf = hallconf.getShareTCConf()
    if ftlog.is_debug():
        ftlog.debug('hallshare._reloadConf tc config = ', tcConf)

    _shareConfig = {}
    for keySetting in tcConf:
        _shareConfig[keySetting] = HallShareConfigs().decodeFromDict(tcConf.get(keySetting, []))
    if ftlog.is_debug():
        ftlog.debug('hallshare._reloadConf _shareConfig = ', _shareConfig)


def _onConfChanged(event):
    if _inited and event.isModuleChanged('share'):
        ftlog.debug('hallshare._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.debug('hallshare initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallshare initialize end')


def findShare(shareId):
    ftlog.debug('sendShare _shareMap=', _shareMap)
    return _shareMap.get(shareId, None)


def getAllShare():
    return _shareMap.values()


def getShareId(shareKey, userId, gameId):
    '''
        获取分享ID
    '''
    if not isstring(shareKey):
        return 0
    if shareKey not in _shareConfig:
        return 0

    sc = _shareConfig[shareKey]
    return int(sc.getValue(userId, gameId))


class HallShareGetRewardEvent(UserEvent):
    def __init__(self, gameId, userId, assetList):
        super(HallShareGetRewardEvent, self).__init__(userId, gameId)
        self.assetList = assetList


class HallShareEvent(UserEvent):
    def __init__(self, gameid, userid, shareid, shareLoc=''):
        super(HallShareEvent, self).__init__(userid, gameid)
        self.shareid = shareid
        self.shareLoc = shareLoc


def getShareStatus(userId, share, timestamp):
    jstr = None
    key = 'share.status:%s:%s' % (HALL_GAMEID, userId)

    try:
        jstr = daobase.executeUserCmd(userId, 'hget', key, share.shareId)
        if ftlog.is_debug():
            ftlog.debug('hallshare.getShareStatus',
                        'userId=', userId,
                        'shareId=', share.shareId,
                        'timestamp=', timestamp,
                        'jstr=', jstr)
        if jstr:
            d = strutil.loads(jstr)
            if (share.rewardTimeCycle.calcIssueNum(d['ts'])
                == share.rewardTimeCycle.calcIssueNum(timestamp)):
                return d['ts'], d['rct']
    except:
        ftlog.error('hallshare.getShareStatus',
                    'userId=', userId,
                    'shareId=', share.shareId,
                    'timestamp=', timestamp,
                    'jstr=', jstr)
    return timestamp, 0


def saveShareStatus(userId, share, timestamp, rewardCount):
    key = 'share.status:%s:%s' % (HALL_GAMEID, userId)
    d = {'ts':timestamp, 'rct':rewardCount}
    jstr = strutil.dumps(d)
    if ftlog.is_debug():
        ftlog.debug('hallshare.saveShareStatus',
                    'userId=', userId,
                    'shareId=', share.shareId,
                    'timestamp=', timestamp,
                    'jstr=', jstr)
    daobase.executeUserCmd(userId, 'hset', key, share.shareId, jstr)


def canReward(userId, share, timestamp):
    ret, rewardCount = checkCanReward(userId, share, timestamp)
    if ftlog.is_debug():
        ftlog.debug('hallshare.canReward',
                    'shareId=', share.shareId,
                    'timestamp=', timestamp,
                    'rewardCount=', rewardCount,
                    'ret=', ret)
    return ret


def checkCanReward(userId, share, timestamp):
    if not share.rewardTimeCycle.isTimestampIn(timestamp):
        return False, 0
    
    rewardTimestamp, rewardCount = getShareStatus(userId, share, timestamp)
    if ftlog.is_debug():
        ftlog.debug('hallshare.checkCanReward',
                    'rewardTimestamp=', rewardTimestamp,
                    'rewardCount=', rewardCount,
                    'share.maxRewardCount=', share.maxRewardCount,
                    'timestamp=', timestamp)

    return rewardCount < share.maxRewardCount, rewardCount


def incrRewardCount(userId, share, timestamp):
    if not share.rewardTimeCycle.isTimestampIn(timestamp):
        return False, 0
    _, rewardCount = getShareStatus(userId, share, timestamp)
    if rewardCount >= share.maxRewardCount:
        return False, rewardCount
    saveShareStatus(userId, share, timestamp, rewardCount + 1)
    return True, rewardCount + 1


def getShareReward(gameId, userId, share, shareLoc, timestamp):
    '''
    给用户发放分享奖励
    '''
    # 分享BI日志汇报
    clientId = sessiondata.getClientId(userId)
    bireport.reportGameEvent('SHARE_CALLBACK', userId, gameId, share.shareId, 0, 0, 0, 0, 0, [], clientId)

    # 记录分享次数
    gamedata.incrGameAttr(userId, HALL_GAMEID, 'shareCount', 1)
    TGHall.getEventBus().publishEvent(HallShareEvent(gameId, userId, share.shareId, shareLoc))

    # 首先处理 分享相关的通知
    notifyInfoStr = pkgamedata.getGameAttr(userId, HALL_GAMEID, 'shareInfo')
    newInfo = {}
    pkgamedata.setGameAttr(userId, HALL_GAMEID, 'shareInfo', json.dumps(newInfo))

    if notifyInfoStr:
        notifyInfo = json.loads(notifyInfoStr)
        shareId = notifyInfo.get('shareId', 0)
        if shareId == share.shareId:
            # 通知
            info = notifyInfo.get('info', '')
            module = notifyInfo.get('module', '')
            if module == hall_red_envelope.TYRedEnvelope.EVENTID:
                hall_red_envelope.TYRedEnvelopeMgr.changeRedEnvelopeState(info,
                                                                          hall_red_envelope.TYRedEnvelope.STATE_SHARED)

                from poker.entity.game.game import TYGame
                clientId = sessiondata.getClientId(userId)
                gameids = hallconf.getDaShiFenFilter(clientId)
                for gid in gameids:
                    TYGame(gid).sendTuyooRedEnvelopeCallBack(userId, clientId, info)

    # 分享奖励
    ok, rewardCount = incrRewardCount(userId, share, timestamp)
    if not ok:
        if ftlog.is_debug():
            ftlog.debug('hallshare.getShareReward already no share, check update share promote ...')
            ftlog.debug('hallshare.getShareReward fail gameId=', gameId,
                        'userId=', userId,
                        'shareId=', share.shareId,
                        'shareLoc=', shareLoc,
                        'rewardCount=', rewardCount,
                        'maxRewardCount=', share.maxRewardCount)
        return False

    assetList = sendReward(gameId, userId, share, shareLoc)
    if assetList and share.mail:
        TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskGoldRain(share.mail))

    ftlog.debug('hallshare.getShareReward ok gameId=', gameId,
                'userId=', userId,
                'shareId=', share.shareId,
                'shareLoc=', shareLoc,
                'rewardCount=', rewardCount,
                'maxRewardCount=', share.maxRewardCount,
                'reward=', [(at[0].kindId, at[1]) for at in assetList] if assetList else [])
    if share.mail:
        pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, share.mail)
    # udpate free & promotion_loc
    datachangenotify.sendDataChangeNotify(gameId, userId, ['free', 'promotion_loc'])
    # 深圳研发中心修改，增加领奖后的返回指令
    from freetime.entity.msg import MsgPack
    from poker.protocol import router
    mp = MsgPack()
    mp.setCmd('share_hall')
    mp.setAction('reward')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.setResult('shareId', share.shareId)
    mp.setResult('rewards', [(at[0].kindId, at[1]) for at in assetList] if assetList else [])
    router.sendToUser(mp, userId)
    return True


def sendReward(gameId, userId, share, shareLoc):
    from hall.entity import hallitem
    if not share.rewardContent:
        return None

    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetList = userAssets.sendContent(gameId, share.rewardContent, 1, True,
                                       pktimestamp.getCurrentTimestamp(),
                                       'SHARE_REWARD', share.shareId)
    ftlog.info('hallshare.sendReward gameId=', gameId,
               'userId=', userId,
               'shareId=', share.shareId,
               'shareLoc=', shareLoc,
               'rewards=', [(atup[0].kindId, atup[1]) for atup in assetList])
    changedDataNames = TYAssetUtils.getChangeDataNames(assetList)
    datachangenotify.sendDataChangeNotify(gameId, userId, changedDataNames)
    TGHall.getEventBus().publishEvent(HallShareGetRewardEvent(gameId, userId, assetList))

    return assetList
def parseClientIdForDL(clientId):
    cid = configure.clientIdToNumber(clientId)
    if cid == 0:
        return False, '', 0, '', '', ''
    clientOs, _, info = strutil.parseClientId(clientId)
    parts = info.split('.')
    if len(parts) < 5:
        return False, '', 0, '', '', ''
    return True, clientOs.lower(), cid, parts[2], parts[3], parts[4]

def genDomainPrefix():
    import string
    letters = string.ascii_lowercase + string.digits
    return ''.join([random.choice(letters) for _ in range(8)])

def genMixDomain(domainList):
    prefix = genDomainPrefix()
    domain = random.choice(domainList)
    return strutil.replaceParams(domain, {'rdStr':prefix})

def getShareDownloadUrl(gameId, userId, source):
    clientId = sessiondata.getClientId(userId)
    ok, clientOs, cid, special, mc, sc = parseClientIdForDL(clientId)
    if not ok:
        ftlog.warn("getShareDownloadUrl|parseClientId|error", gameId, userId, source, cid, special, mc, sc)
        return

    channels = configure.getGameJson(HALL_GAMEID, "download").get("channels", {})
    channel = clientOs + '.' + special + '.' + mc + '.' + sc

    downloadurl = channels['default']
    if channel in channels:
        downloadurl = channels[channel]

    mix_domain = [
    "dspkm.cc",
    "lkxjv.cc",
    "qkpwdfo.cc",
    "sijas.cc",
    "023i.cc",
    "lkjsdf.cc",
    "vdlskm.cc",
    "iojpdvs.cc",
    "sdvnkl.cc",
    "owirhj.cc",
    "lvsdp.cc",
    "msvdkn.cc",
    "dvslkm.cc",
    "odnsvk.cc",
    "p0joefipq.cc",
    "mvsdpok.cc",
    "02r389u.cc",
    "sdlknv.cc",
    "sdfioj.cc",
    "klsdvm.cc"
  ]

    domainList = configure.getGameJson(HALL_GAMEID, "misc").get("mix_domain", mix_domain)
    replaceDict = {
        'mc':mc,
        'sc':sc,
        'cid':str(cid),
        'uid':userId,
        'mixDomain':genMixDomain(domainList)
    }
    downloadurl = strutil.replaceParams(downloadurl, replaceDict)
    parsedUrl = urlparse.urlparse(downloadurl)
    qparams = urlparse.parse_qs(parsedUrl.query) if parsedUrl.query else {}
    qparams = {k:v[0] for k,v in qparams.iteritems()}
    qparams.update({'source':source})

    results = {}
    results['action'] = 'geturl'
    results['downloadurl'] = urlparse.urlunparse((parsedUrl[0], parsedUrl[1], parsedUrl[2], parsedUrl[3], urllib.urlencode(qparams), parsedUrl[5]))

    from freetime.entity.msg import MsgPack
    from poker.protocol import router
    mp = MsgPack()

    mp.setCmd('share_hall')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    if ftlog.is_debug():
        ftlog.debug("getShareDownloadUrl|", gameId, userId, results)


