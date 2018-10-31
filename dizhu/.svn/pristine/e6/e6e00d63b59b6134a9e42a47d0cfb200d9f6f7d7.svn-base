# -*- coding:utf-8 -*-
'''
Created on 2016年12月12日

@author: zhaojiangang
'''
import random
from sre_compile import isstring

import freetime.util.log as ftlog
from dizhu.entity.dizhuversion import SessionDizhuVersion
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.configure import configure as pkconfigure, configure
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.dao import gamedata
from poker.util import strutil
from hall.entity import hallitem, datachangenotify
import poker.util.timestamp as pktimestamp
from hall.entity import hallvip

class ErrorCode(object):
    E_UNKNOWN_VERSION = -2
    E_UNKNOWN_SKIN = -3
    E_REQUIRED_BUY = -4
    E_FEE_NOT_ENOUGH = -5
    E_BUY_FREE = -6
    
class FeeItem(object):
    def __init__(self):
        self.itemId = None
        self.count = None
        self.pic = None
        self.desc = None

    def decodeFromDict(self, d):
        self.itemId = d.get('itemId')
        if not isstring(self.itemId):
            raise TYBizConfException(d, 'TableSkin.fee.itemId must be string')
        self.count = d.get('count')
        if not isinstance(self.count, int):
            raise TYBizConfException(d, 'TableSkin.fee.count must be int')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TableSkin.fee.pic must be string')
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TableSkin.fee.desc must be string')
        return self

class TableSkin(object):
    def __init__(self):
        self.skinId = None
        self.name = None
        self.type = None
        self.displayName = None
        self.updateVersion = None
        self.icon = None
        self.preview = None
        self.feeItem = None
        self.url = None
        self.md5 = None
        
    def decodeFromDict(self, d):
        self.skinId = d.get('id')
        if not isstring(self.skinId):
            raise TYBizConfException(d, 'TableSkin.skinId must be string')
        self.name = d.get('name')
        if not isstring(self.name):
            raise TYBizConfException(d, 'TableSkin.name must be string')
        self.type = d.get('type', '2d')
        if not isstring(self.type):
            raise TYBizConfException(d, 'TableSkin.type must be string')
        self.displayName = d.get('display')
        if not isstring(self.displayName):
            raise TYBizConfException(d, 'TableSkin.display must be string')
        self.updateVersion = d.get('update')
        if not isinstance(self.updateVersion, int):
            raise TYBizConfException(d, 'TableSkin.display must be int')
        self.icon = d.get('icon')
        if not isstring(self.icon):
            raise TYBizConfException(d, 'TableSkin.icon must be string')
        self.preview = d.get('preview')
        if not isstring(self.preview):
            raise TYBizConfException(d, 'TableSkin.preview must be string')
        
        feeItem = d.get('fee')
        if feeItem:
            self.feeItem = FeeItem().decodeFromDict(feeItem)
        self.url = d.get('url')
        if not isstring(self.url):
            raise TYBizConfException(d, 'TableSkin.url must be string')
        self.md5 = d.get('md5')
        if not isstring(self.md5):
            raise TYBizConfException(d, 'TableSkin.md5 must be string')
        return self

class TableSkinVersion(object):
    def __init__(self, version):
        self.version = version
        self.localIds = None
        self.skinList = None
        self.skinMap = None

    def findSkin(self, skinId):
        return self.skinMap.get(skinId)
    
    def decodeFromDict(self, d):
        localIds = d.get('local', [])
        self.localIds = localIds
        self.skinList = []
        self.skinMap = {}
        for conf in d.get('list', []):
            skin = TableSkin()
            skin.decodeFromDict(conf)
            self.skinList.append(skin)
            self.skinMap[skin.skinId] = skin
        return self

_inited = False
_setUserSkin = False

_skinVersionMap = {}

def loadSkinVersion(version):
    skinVersion = _skinVersionMap.get(version)
    if not skinVersion:
        try:
            conf = pkconfigure.getGameJson(6, 'table.skin.versions:%s' % (version), [], None)
            if conf:
                skinVersion = TableSkinVersion(version)
                skinVersion.decodeFromDict(conf)
        except:
            ftlog.error('tableskin.loadSkinVersion version=', version)
            return None
    return skinVersion

def getClientSkins(userId, clientId, version):
    ret = []
    skinVersion = loadSkinVersion(version)
    if skinVersion:
        skinIds = configure.getTcContentByGameId('table.skin', None, DIZHU_GAMEID, clientId, [])
        for skinId in skinIds:
            skin = skinVersion.findSkin(skinId)
            if skin:
                ret.append(skin)
            else:
                ftlog.warn('tableskin.getClientSkins userId=', userId,
                           'clientId=', clientId,
                           'version=', version,
                           'skinId=', skinId,
                           'err=', 'NoSkin')
    return ret

def findSkinForClient(userId, clientId, skinVersion, skinId):
    skinIds = configure.getTcContentByGameId('table.skin', None, DIZHU_GAMEID, clientId, [])
    # 看该clientId是否配置了skinId
    if skinId not in skinIds:
        return None
    return skinVersion.findSkin(skinId)

class MySkinModel(object):
    def __init__(self, userId):
        self.userId = userId
        self.curSkin = None
        self.mySkins = set()
    
    def addMySkin(self, skinId):
        self.mySkins.add(skinId)

    def fromDict(self, d):
        self.curSkin = d.get('curSkin')
        mySkins = d.get('mySkins')
        if mySkins:
            self.mySkins.update(mySkins)
        return self
    
    def toDict(self):
        ret = {}
        if self.curSkin:
            ret['curSkin'] = self.curSkin
        if self.mySkins:
            ret['mySkins'] = list(self.mySkins)
        return ret

def newUserSetRandomSkin(userId, model):
    conf = configure.getGameJson(6, 'table.skin', {}, configure.DEFAULT_CLIENT_ID)
    if conf:
        newerConf = conf.get('changeNewUserSkin', {})
        if newerConf:
            newerSwitch = newerConf.get('switch', 0)
            newerSkinMinUserId = newerConf.get('newerSkinMinUserId', 0)
            newerRandomSkins = newerConf.get('newerRandomSkins', [])
            if newerSwitch and userId >= newerSkinMinUserId:
                model.curSkin = random.choice(newerRandomSkins)
                saveMySkin(model)

                ftlog.debug('newOrOldSkinTestFunc newerSwitch=', newerSwitch, 'newerSkinMinUserId=',
                            newerSkinMinUserId, 'newerRandomSkins=', newerRandomSkins, 'model.curSkin=', model.curSkin)
    return model

def newOrOldSkinTest(userId, model):
    conf = configure.getGameJson(6, 'table.skin', {}, configure.DEFAULT_CLIENT_ID)
    if conf:
        olderConf = conf.get('changeOldUserSkin', {})
        if olderConf:
            olderSwitch = olderConf.get('switch', 0)
            changeUserSkinMinVer = olderConf.get('changeUserSkinMinVer', 0)
            userDizhuClientVer = SessionDizhuVersion.getVersionNumber(userId)
            if olderSwitch and userDizhuClientVer >= changeUserSkinMinVer:
                skin3d = olderConf.get('skin3d', {})
                skinId = skin3d.get('skinId')
                userIdList = skin3d.get('userIdList', [])
                if userId in userIdList:
                    model.curSkin = skinId
                    return model
                skin2d = olderConf.get('skin2d', {})
                skinId = skin2d.get('skinId')
                userIdList = skin2d.get('userIdList', [])
                if userId in userIdList:
                    model.curSkin = skinId
                    return model
    return model


def loadMySkin(userId):
    model = MySkinModel(userId)
    d = gamedata.getGameAttrJson(userId, DIZHU_GAMEID, 'table.skin', {})
    if d:
        model.fromDict(d)
    else:
        newUserSetRandomSkin(userId, model)

    # model = newOrOldSkinTest(userId, model)
    # if ftlog.is_debug():
    #     ftlog.debug('newOrOldSkinTest userId=', userId, 'model=', model.toDict())

    return model

# VIP特权开启全部皮肤
def loadMyVIPSkin(userId, clientId):
    model = loadMySkin(userId)
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    if vipLevel >= 3:
        skinIds = configure.getTcContentByGameId('table.skin', None, DIZHU_GAMEID, clientId, [])
        for skinId in skinIds:
            model.mySkins.add(skinId)
    return model

def saveMySkin(model):
    d = model.toDict()
    gamedata.setGameAttr(model.userId, DIZHU_GAMEID, 'table.skin', strutil.dumps(d))
    if ftlog.is_debug():
        ftlog.debug('saveMySkin userId=', model.userId, 'model=', model.toDict())

def useSkin(userId, clientId, version, skinId):
    '''
    应用皮肤
    '''
    mySkin = loadMySkin(userId)
    model = loadMyVIPSkin(userId, clientId)
    if model.curSkin != skinId:
        if skinId not in model.mySkins:
            skinVersion = loadSkinVersion(version)
            if not skinVersion:
                raise TYBizException(ErrorCode.E_UNKNOWN_VERSION, '皮肤不存在')
            
            if skinId not in skinVersion.localIds:
                # 查找是否需要购买
                skin = findSkinForClient(userId, clientId, skinVersion, skinId)
                if not skin:
                    raise TYBizException(ErrorCode.E_UNKNOWN_SKIN, '皮肤不存在')
                
                if skin.feeItem and skin.feeItem.count > 0:
                    raise TYBizException(ErrorCode.E_REQUIRED_BUY, '购买后才能使用')

                mySkin.mySkins.add(skinId)

        ftlog.info('tableskin.useSkin',
                   'userId=', userId,
                   'clientId=', clientId,
                   'version=', version,
                   'skinId=', skinId)

        mySkin.curSkin = skinId
        #model.curSkin = skinId
        saveMySkin(mySkin)
    return mySkin

def buySkin(userId, clientId, version, skinId):
    model = loadMySkin(userId)
    if skinId not in model.mySkins:
        skinVersion = loadSkinVersion(version)
        if not skinVersion:
            raise TYBizException(ErrorCode.E_UNKNOWN_VERSION, '皮肤不存在')
        skin = findSkinForClient(userId, clientId, skinVersion, skinId)
        if not skin:
            raise TYBizException(ErrorCode.E_UNKNOWN_SKIN, '皮肤不存在')
        if not skin.feeItem:
            raise TYBizException(ErrorCode.E_BUY_FREE, '购买免费皮肤')
        
        # 扣除费用
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, consumeCount, final = userAssets.consumeAsset(DIZHU_GAMEID,
                                                                 skin.feeItem.itemId,
                                                                 skin.feeItem.count,
                                                                 pktimestamp.getCurrentTimestamp(),
                                                                 'DIZHU_BUY_TABLE_SKIN',
                                                                 int(skinId))
        if consumeCount < skin.feeItem.count:
            raise TYBizException(ErrorCode.E_FEE_NOT_ENOUGH, '费用不足，无法购买')
        
        # 发送皮肤
        model.mySkins.add(skinId)
        saveMySkin(model)
        
        ftlog.info('tableskin.buySkin userId=', userId,
                   'clientId=', clientId,
                   'version=', version,
                   'skinId=', skinId,
                   'fee=', (skin.feeItem.itemId, skin.feeItem.count),
                   'counsumeCount=', consumeCount,
                   'final=', final)
        
        # 刷新客户端
        if assetKind.keyForChangeNotify:
            datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, assetKind.keyForChangeNotify)
        
    return model

skinVersionConfPrefix = 'game:6:table.skin.versions:'

def _onConfChanged(event):
    global _skinVersionMap
    if not _inited:
        return
    
    if 'all' in event.keylist:
        _skinVersionMap = {}
        return
    
    for key in event.keylist:
        if key.startswith(skinVersionConfPrefix):
            try:
                version = int(key[len(skinVersionConfPrefix):])
                _skinVersionMap.pop(version)
            except:
                pass
        
def _initialize(isCenter):
    global _inited
    if not _inited:
        _inited = True

    global _setUserSkin
    if not _setUserSkin and isCenter:
        from poker.entity.events.tyeventbus import globalEventBus
        from poker.entity.events.tyevent import EventHeartBeat
        globalEventBus.subscribe(EventHeartBeat, oldUserSetSkin)


def oldUserSetSkin(event):
    global _setUserSkin
    if _setUserSkin:
        return
    conf = configure.getGameJson(6, 'table.skin', {}, configure.DEFAULT_CLIENT_ID)
    if conf:
        olderConf = conf.get('changeOldUserSkin', {})
        olderSwitch = olderConf.get('switch', 0)
        changeUserSkinMinVer = olderConf.get('changeUserSkinMinVer', 0)
        if olderConf and olderSwitch:
            _setUserSkin = True
            skin3d = olderConf.get('skin3d', {})
            if skin3d:
                skinId = skin3d.get('skinId')
                userIdList = skin3d.get('userIdList', [])
                for userId in userIdList:
                    model = loadMySkin(userId)
                    userDizhuClientVer = SessionDizhuVersion.getVersionNumber(userId)
                    if userDizhuClientVer >= changeUserSkinMinVer:
                        model.curSkin = skinId
                        saveMySkin(model)
                ftlog.info('oldUserSetSkin userIdList=', userIdList, 'skinId=', skinId)

            skin2d = olderConf.get('skin2d', {})
            if skin2d:
                skinId = skin2d.get('skinId')
                userIdList = skin2d.get('userIdList', [])
                for userId in userIdList:
                    model = loadMySkin(userId)
                    userDizhuClientVer = SessionDizhuVersion.getVersionNumber(userId)
                    if userDizhuClientVer >= changeUserSkinMinVer:
                        model.curSkin = skinId
                        saveMySkin(model)

                ftlog.info('oldUserSetSkin userIdList=', userIdList, 'skinId=', skinId)
