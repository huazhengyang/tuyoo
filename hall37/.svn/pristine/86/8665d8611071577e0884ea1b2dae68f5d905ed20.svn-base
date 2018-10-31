# -*- coding: utf-8 -*-
'''
Created on 2017-6-29
@author: ljh
'''
import time

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallconf, newpopwnd
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.localservice import localServiceConfig
from hall.entity.newcheckin import getCheckinId
from hall.servers.util.store_handler import StoreHelper
from poker.entity.configure import configure
from poker.protocol import router
from poker.util import strutil


def getPriceList(gameId, userId, clientId):
    priceList = []
    datas = StoreHelper.getStoreTabByName(gameId, userId, 'coin', clientId)
    if 'items' not in datas:
        return priceList
    for item in datas['items']:
        priceList.append({'price': item['price'], 'name': item['name'], 'id': item['id']})

    priceList.sort(key=lambda product: (float(product['price'])))

    ftlog.debug("getPriceList|", priceList, datas)
    return priceList

def sendPriceList2client(gameId, userId, clientId, pricelist):
    results = {}
    results['pricelist'] = pricelist

    mp = MsgPack()
    mp.setCmd('game_pricelist')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.debug("localservice|sendPriceList2client|", gameId, userId, clientId, pricelist)


def sendCheckinId2client(gameId, userId, checkinId):
    results = {}
    results['clientId'] = checkinId

    mp = MsgPack()
    mp.setCmd('game_clientId')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.info("localservice|sendCheckinId2client|", gameId, userId, checkinId)

#新大厅v4.56功能入口
def loginGame_v456(userId, gameId, clientId, loginsum, isdayfirst, daylogin):
    ftlog.info("loginGame_v456|", userId, gameId, clientId, loginsum, isdayfirst, daylogin)

    # 是否是登录大厅
    if gameId != HALL_GAMEID:
        ftlog.debug("loginGame_v456|isnotloginHall", gameId)
        return

    if isdayfirst:  #每日首次登陆vip补足,全放开不做版本限制2017.8.2
        # from hall.entity.newcheckin import complementByVip
        # complementByVip(userId, gameId, clientId)

        from hall.entity import hallitem
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()
        if ftlog.is_debug():
            ftlog.debug('isdayfirst=', userId, gameId, clientId, loginsum, isdayfirst, daylogin)
        for itemKindId in [hallitem.ITEM_CROWN_MONTHCARD_KIND_ID, hallitem.ITEM_HONOR_MONTHCARD_KIND_ID]:
            item = userBag.getItemByKindId(itemKindId)
            if ftlog.is_debug():
                ftlog.debug('honor monthcard itemKindId', userId, itemKindId, item)
            if item:
                timestamp = int(time.time())
                deltatime = item.expiresTime - timestamp
                if deltatime > 0 and deltatime < 48 * 3600:
                    msg = u"亲，您的月卡即将到期，明天以后就不能享受尊贵权益了，请及时续费吧~"
                    from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
                    infoTodoTask = TodoTaskShowInfo(msg, True)
                    TodoTaskHelper.sendTodoTask(gameId, userId, infoTodoTask)
                    if ftlog.is_debug():
                        ftlog.debug('honor monthcard expiresTime', userId, itemKindId)
        from poker.entity.dao import gamedata, userdata
        import json
        gamedata.setGameAttr(userId, HALL_GAMEID, "honormonthcardreward", 0)
        gamedata.setGameAttr(userId, HALL_GAMEID, 'todaynotifylist', json.dumps([]))
        item = userBag.getItemByKindId(hallitem.ITEM_HONOR_MONTHCARD_KIND_ID)
        if item and item.expiresTime - (time.time()) > 24 * 3600:
            name = userdata.getAttr(userId, 'name')
            COLOR_DEFAULT = "F0F8FF"
            COLOR_SPECIAL = "FFFF00"
            content = [
                [COLOR_DEFAULT, u'热烈欢迎尊贵的星耀月卡用户'],
                [COLOR_SPECIAL, name],
                [COLOR_DEFAULT, u'登录游戏，祝愿您手气长虹~']
            ]
            from hall.servers.util.rpc import user_remote as SendLed
            SendLed.sendHallLed(gameId,
                                json.dumps({'text': [{'color': color, 'text': text} for color, text in content]}),
                                ismgr=1)
            if ftlog.is_debug():
                ftlog.debug('honor monthcard led', userId, content)
    #是否是v4.56
    if not checkClientVer(userId, gameId, clientId):
        ftlog.info("loginGame_v456|failer|clientVer|isnotMatch|", userId, gameId, clientId)
        return

    # checkinId客户端自己查找本地数据index
    checkinId = getCheckinId(clientId)
    sendCheckinId2client(gameId, userId, checkinId)

    # 价格列表
    pricelist = getPriceList(gameId, userId, clientId)
    sendPriceList2client(gameId, userId, clientId, pricelist)

    # 推送配置数据2c
    pushGameConfig(userId, gameId, clientId)

    # 新弹窗入口
    newpopwnd.enterpopwnd(userId, gameId, clientId, loginsum, isdayfirst, daylogin)

    download_guide(userId, gameId, clientId)
def download_guide(userId, gameId, clientId):
    datas = configure.getTcContentByGameId('download_guide', None, HALL_GAMEID, clientId, {})
    if not datas:
        datas = {}
    msg = MsgPack()
    msg.setCmd('game_config')
    msg.setResult('action', 'download_guide')
    msg.setResult('gameId', gameId)
    msg.setResult('userId', userId)
    msg.setResult('datas', datas.get('list', []))
    router.sendToUser(msg, userId)
    if ftlog.is_debug():
        ftlog.debug('doGetdownload_guide',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'datas=', datas)

# user loginGame的时候给客户端推送配置数据
def pushGameConfig(userId, gameId, clientId, tag="all"):
    ftlog.debug("pushGameConfig|", userId, gameId, clientId, tag)

    if tag == 'all':
        doConfigData(gameId, userId, clientId, "checkin_config")
        doConfigData(gameId, userId, clientId, "vip_config")


def checkClientVer(userId, gameId, clientId):
    _, clientVer, _ = strutil.parseClientId(clientId)
    if clientId in localServiceConfig.SPECIAL_CLIENTIDS:
        return True
    if clientVer < localServiceConfig.CLIENT_VER:
        return False
    return True

def sendConfigData2client(gameId, userId, action, configData):
    results = {}
    results['action'] = action
    results['configData'] = configData

    mp = MsgPack()
    mp.setCmd('game_config')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.info("localservice|sendConfigJson2client|", gameId, userId, action, configData)

def getXXTcConf(action):
    if action == "checkin_config":
        return hallconf.getNewCheckinTCConf()
    elif action == "vip_config":
        return hallconf.getNewVipTCConf()

def actualTcContent(clientId, keystr):
    datas = configure.getTcContentByGameId(keystr, None, HALL_GAMEID, clientId, [])
    if datas:
        ftlog.debug("actualTcContent|datas|ls|", clientId, keystr, datas)
        return datas
    return {}

def getDatasKey(typestr, dataskeyList):
    for key in dataskeyList:
        if str(typestr) in key:
            return key  # u'default_vipLevel'
def getConfIdKey(soncheckinId):
    ftlog.debug("doConfigData|getConfIdKey", soncheckinId, type(soncheckinId))
    assert (isinstance(soncheckinId, basestring))
    sidlist = soncheckinId.split('_')
    assert len(sidlist) > 1
    ftlog.debug("doConfigData|getConfIdKey", soncheckinId, sidlist)
    return sidlist[0]
def getConfKeyVip(clientId, confKey, typestr):
    datas = actualTcContent(clientId, confKey)
    if len(datas) == 0:
        return 'default'
    ftlog.debug("doConfigData|getDatasKey", typestr, datas.keys())
    sonId = getDatasKey(typestr, datas.keys())  # u'default_vipLevel'
    if sonId is None:
        return 'default'
    vipidkey = getConfIdKey(sonId)  # u'default'
    ftlog.debug("doConfigData|getConfKeyVip", clientId, confKey, sonId, vipidkey, typestr, datas.keys())
    return vipidkey
def sendVipClientId2client(gameId, userId, keyId):
    results = {}
    results['vip_clientId'] = keyId
    mp = MsgPack()
    mp.setCmd('game_vipclientId')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.info("localservice|sendVipClientId2client|", gameId, userId, keyId)
# configJson
def doConfigData(gameId, userId, clientId, action):
    keyId = 'default'
    configData = getXXTcConf(action)
    if action == 'vip_config':
        keyId = getConfKeyVip(clientId, 'newvip', 'vipLevel')
        sendVipClientId2client(gameId,userId,keyId)
        ftlog.info("doConfigData|vip_config", userId, clientId, keyId)
    sendConfigData2client(gameId, userId, action, configData)
    ftlog.info("localservice|doConfigData|action", gameId, userId, action, keyId)


# 客户端获取配置数据本地化-调度
def doGetConfigJsonData(action, gameId, userId, version, msg):
    if action == "vip":
        doGetConfigJsonData_vip(gameId, userId, version, msg)
    elif action == "item":
        doGetConfigJsonData_item(gameId, userId, version, msg)


# 客户端获取vip配置数据本地化[这个机制暂时没有启用]
def doGetConfigJsonData_vip(gameId, userId, version, msg):
    conf = hallconf.getVipConf()
    conf_version = conf.get("version", 1)
    if version >= conf_version:
        ftlog.debug("doGetConfigJsonData|vip|version|already|new", gameId, userId, version, conf_version, msg)
        return

    mo = MsgPack()
    mo.setCmd('localservice')
    mo.setResult('action', 'vip')
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('conf_version', conf_version)
    mo.setResult('confJsonData', conf)
    router.sendToUser(mo, userId)

    ftlog.debug("doGetConfigJsonData|vip|version|conf_version|send2client|ok", gameId, userId, version, conf_version,
                msg)


# 客户端获取item配置数据本地化[这个机制暂时没有启用]
def doGetConfigJsonData_item(gameId, userId, version, msg):
    conf = hallconf.getVipConf()
    conf_version = conf.get("version", 1)
    if version >= conf_version:
        ftlog.debug("doGetConfigJsonData|item|version|already|new", gameId, userId, version, conf_version, msg)
        return

    mo = MsgPack()
    mo.setCmd('localservice')
    mo.setResult('action', 'vip')
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('conf_version', conf_version)
    mo.setResult('confJsonData', conf)
    router.sendToUser(mo, userId)

    ftlog.debug("doGetConfigJsonData|item|version|conf_version|send2client|ok", gameId, userId, version, conf_version,
                msg)
