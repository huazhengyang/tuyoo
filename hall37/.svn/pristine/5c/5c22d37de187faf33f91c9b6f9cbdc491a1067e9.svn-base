# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''

from datetime import datetime
import random
from string import strip

import freetime.util.log as ftlog
from hall.entity import hallvip, hallconf, datachangenotify, hallitem
from poker.entity.biz import bireport
from poker.entity.biz.message import message
from poker.entity.configure import configure, gdata
from poker.entity.dao import daobase, userdata, userchip, gamedata, day1st
from poker.entity.events.tyevent import EventUserLogin
from poker.entity.game.game import TYGame
from poker.util import strutil, timestamp

HALL_ID = 9999


def getRegisterDay(userId):
    """
    获取玩家注册的天数
    """
    registerTimeStr = userdata.getAttr(userId, 'createTime')
    nowTime = datetime.now()
    try:
        registerTime = datetime.strptime(registerTimeStr, '%Y-%m-%d %H:%M:%S.%f')
    except:
        registerTime = nowTime
    ct = nowTime.time()
    dt1 = datetime.combine(nowTime.date(), ct)
    dt2 = datetime.combine(registerTime.date(), ct)
    past = dt1 - dt2
    return int(past.days)


def isForceLogout(userId):
    '''
    检查该用户是否已经禁止登录
    '''
    isForbidden = daobase.executeForbiddenCmd('EXISTS', 'forbidden:uid:' + str(userId))
    if isForbidden:
        return  1
    return 0


def getUserInfo(userId, gameId, clientId):
    '''
    取得用户的基本账户的信息
    '''
    ukeys = ['email', 'pdevid', 'mdevid', 'isbind', 'snsId', 'name',
             'source', 'diamond', 'address', 'sex', 'state',
             'payCount', 'snsinfo', 'vip', 'dayang', 'idcardno',
             'phonenumber', 'truename', 'detect_phonenumber',
             'lang', 'country', "signature", "set_name_sum", "coupon", "exchangedCoupon",
             'purl', 'beauty', 'charm', 'password', 'bindMobile', 'chip_exp', 'chip_level',
             'myCardNo', 'myRealName']

    udataDb = userdata.getAttrs(userId, ukeys)

    udata = dict(zip(ukeys, udataDb))
    udata['coin'] = udata['diamond']  # 数据补丁: 再把diamond转换到coin返回, 老版本用的是coin
    udata['chip'] = userchip.getChip(userId)
    myCardNo = udata.get('myCardNo')
    myRealName = udata.get('myRealName')
    udata['myCardNo'] = str(myCardNo) if myCardNo else ''
    udata['myRealName'] = str(myRealName) if myRealName else ''
    
    # 头像相关
    purl, isbeauty = getUserHeadUrl(userId, clientId, udata['purl'], udata['beauty'])
    udata['purl'] = purl
    udata['isBeauty'] = isbeauty

    # vip信息
    udata['vipInfo'] = hallvip.userVipSystem.getVipInfo(userId)

    # 等级系统 2017-05-25增加
    udata['chip_exp'] = udata.get('chip_exp') or 0
    udata['chip_level'] = udata.get('chip_level') or 0
    chip_level = udata['chip_level']
    try:
        maxlevel = configure.getGameJson(HALL_ID, 'chiplevel')['max']['maxlevel']
        maxexp = configure.getGameJson(HALL_ID, 'chiplevel')['max']['maxexp']
    except:
        maxlevel = 0
        maxexp = 0

    try:
        if chip_level == maxlevel:
            next_level_exp = maxexp
        else:
            chip_level_ = configure.getGameJson(HALL_ID, 'chiplevel')['level']
            next_level = str(chip_level + 1)
            next_level_exp = chip_level_[next_level]
        udata['next_level_exp'] = next_level_exp
    except:
        udata['next_level_exp'] = 0


    # 江湖救急次数
    udata['assistance'] = {
        'count': hallvip.userVipSystem.getAssistanceCount(gameId, userId),
        'limit':hallvip.vipSystem.getAssistanceChipUpperLimit()
    }
    # 推荐人
    from hall.entity import hall_invite
    inviteStatus = hall_invite.loadUserInviteStatus(userId)
    if inviteStatus.inviter >= 0:
        udata['inviter'] = inviteStatus.inviter
    
    assetRateMap = {}
    for assetKind in hallitem.itemSystem.getAllRateAssetKind():
        assetRateMap[assetKind.kindId] = assetKind.displayRate
    udata['assetRate'] = assetRateMap
    userdata.updateUserGameDataAuthorTime(userId, gameId)
    return udata


def getGameInfo(userId, gameId, clientId):
    '''
    取得当前用户的游戏账户信息dict
    '''
    # 获取插件游戏的信息
    infos = TYGame(gameId).getGameInfo(userId, clientId)
    # 数据补丁, 避免客户端崩溃
    if 'headUrl' not in infos :
        infos['headUrl'] = ''
    return infos


def _filter360QihuImage(userId, clientId, headurl):
    '''
    过滤360SNS账户的恶心的头像图标
    '''
    headurl = unicode(headurl)
    if headurl.find('qhimg.com') > 0 :
        heads = getUserHeadPics(clientId)
        purl = random.choice(heads)
        userdata.setAttr(userId, 'purl', purl)
        return purl
    return headurl


def getUserHeadUrl(userId, clientId, purl=None, beauty=None):
    '''
    取得当前的用户的头像
    取得当前的用户是否是美女认证账户
    '''
    # 自定义头像, 美女认证
    if purl == None :
        purl, beauty = userdata.getAttrs(userId, ['purl', 'beauty'])
        if purl :
            purl = unicode(purl)
        else:
            purl = ''
    purl = _filter360QihuImage(userId, clientId, purl)
    if isinstance(purl, (str, unicode)):
        if (purl.find('http://') < 0) and (purl.find('https://') < 0):
            purl = ''
    if purl == '' or purl == None:
        heads = getUserHeadPics(clientId)
        purl = random.choice(heads)
        userdata.setAttr(userId, 'purl', purl)

    isBeauty = False
    if beauty:
        isBeauty = True if (beauty & 1) != 0 else False

    return purl, isBeauty


def _getMsgParam(atts, values, msg , checkType, msgkey, attname=None):
    '''
    重MsgPack实例中取得一个参数的值, 并使用checkType进行检查
    将结果追加到atts和values中
    '''
    value = msg.getParam(msgkey)
    if value == None :
        return
    value = checkType(value)
    if value != None :
        if attname == None :
            atts.append(msgkey)
        else:
            atts.append(attname)
        values.append(value)


def _checkStr(val):
    '''
    检查用户的一个字符串属性的数据格式
    '''
    val = strip(unicode(val))
    if len(val) > 0 :
        return val
    return None


def _checkSex(val):
    '''
    检查用户的性别的数据格式
    '''
    try:
        val = int(val)
        if val == 1 or val == 0 :
            return val
    except:
        pass
    return None


def _checkHeadUrl(val):
    '''
    检查用户的头像的数据格式
    '''
    val = _checkStr(val)
    if val :
        if val.find('http://') < 0:
            val = gdata.httpAvatar() + '/' + val
    return None

# HALL51 数据补丁，如果服务回滚，需要将移动到gamedta的几个数据返还至user中
# 补丁在 08年9月6日5：~9：40登陆并退出过hall51大厅的玩家金币数据
# HALL51 暂时不进行chip数据的转移
def _moveHall51DataBack(userId, gameId, clientId):
    try:
        gameId = HALL_ID
        flag = gamedata.getGameAttrInt(userId, gameId, 'userChipMoveGame')
        ftlog.info('_moveHall51DataBack', userId, gameId, flag)
        if flag > 0 :
            # 当前用户登录过HALL51
            chip, exp, charm, coupon = gamedata.getGameAttrs(userId, gameId, ['chip', 'exp', 'charm', 'coupon'])
            chip, exp, charm, coupon = strutil.parseInts(chip, exp, charm, coupon)
            ftlog.info('_moveHall51DataBack data->', userId, gameId, chip, exp, charm, coupon)
            if charm > 0 :
                userdata.incrCharm(userId, charm)
            if exp > 0 :
                userdata.incrExp(userId, exp)
            if coupon > 0 :
                trueDelta, finalCount = userchip.incrCoupon(userId, gameId, coupon, userchip.ChipNotEnoughOpMode.NOOP, userchip.EVENT_NAME_SYSTEM_REPAIR, 0, clientId)
                ftlog.info('_moveHall51DataBack data coupon->', userId, gameId, coupon, trueDelta, finalCount)
            if chip > 0 :
                trueDelta, finalCount = userchip.incrChip(userId, gameId, chip, userchip.ChipNotEnoughOpMode.NOOP, userchip.EVENT_NAME_SYSTEM_REPAIR, 0, clientId)
                ftlog.info('_moveHall51DataBack data chip->', userId, gameId, chip, trueDelta, finalCount)
            gamedata.delGameAttrs(userId, gameId, ['chip', 'exp', 'charm', 'coupon', 'userChipMoveGame'])
            datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
    except:
        ftlog.error()

def getHistoryClientIds(userId, gameId):
    '''
    获取历史clientId
    '''
    jstr = gamedata.getGameAttr(userId, gameId, 'hisClientIds')
    if jstr:
        try:
            ret = strutil.loads(jstr)
            if isinstance(ret, list):
                return ret
        except:
            pass
    return []
    
def updateHistoryClientIdsIfNeed(userId, gameId, numClientId):
    clientIds = getHistoryClientIds(userId, gameId)
    if not clientIds or clientIds[-1] != numClientId:
        clientIds.append(numClientId)
        if len(clientIds) > 2:
            clientIds = clientIds[-2:]
        jstr = strutil.dumps(clientIds)
        gamedata.setGameAttr(userId, gameId, 'hisClientIds', jstr)

def loginGame(userId, gameId, clientId, clipboard=None):
    """
    用户登录一个游戏, 检查用户的游戏数据是否存在(创建用户数据)
    """
    # 确认用户的游戏数据是否存在
    iscreate = ensureGameDataExists(userId, gameId, clientId)

    if not iscreate:
        _moveHall51DataBack(userId, gameId, clientId)

    # 游戏登录次数加1，每次bind_user都会加1，包括断线重连
    loginsum = gamedata.incrGameAttr(userId, gameId, 'loginsum', 1)

    # 确认是否是今日第一次登录
    isdayfirst = False
    datas = day1st.getDay1stDatas(userId, gameId)
    if 'daylogin' not in datas:
        isdayfirst = True
        datas['daylogin'] = 1
        datas['iscreate'] = 1
    else:
        datas['daylogin'] += 1
        datas['iscreate'] = 0
    day1st.setDay1stDatas(userId, gameId, datas)

    if isdayfirst:
        # 消息的数据结构新旧转换
        message.convertOldData(gameId, userId)
       
    # 插件的登录补充处理
    TYGame(gameId).loginGame(userId, gameId, clientId, iscreate, isdayfirst)

    try:
        from poker.entity.configure import pokerconf
        numClientId = pokerconf.clientIdToNumber(clientId)
        updateHistoryClientIdsIfNeed(userId, gameId, numClientId)
    except:
        pass
    
    evt = EventUserLogin(userId, gameId, isdayfirst, iscreate, clientId)
    evt.clipboard = clipboard
    TYGame(gameId).getEventBus().publishEvent(evt)

    userdata.updateUserGameDataAuthorTime(userId, gameId)

    # 新大厅v4.56功能入口
    # from hall.entity.localservice import localservice
    # localservice.loginGame_v456(userId, gameId, clientId, loginsum, isdayfirst, datas['daylogin'])

    return isdayfirst, iscreate


def ensureGameDataExists(userId, gameId, clientId):
    '''
    判定用户游戏数据是否存在, 若不存在则初始化该游戏的所有的相关游戏数据
    包括: 主游戏数据gamedata, 道具, 勋章等
    '''
    isCreate = False
    gaccount = TYGame(gameId)
    # 以游戏主数据的前2个字段为判定条件
    ukeys = gaccount.getInitDataKeys()[0:2]
    d1, d2 = gamedata.getGameAttrs(userId, gameId, ukeys)
    if d1 is None or d2 is None:
        gdkeys, gdata = gaccount.createGameData(userId, gameId)
        gdkeys.append('createTime')
        gdata.append(timestamp.formatTimeMs())
        bireport.creatGameData(gameId, userId, clientId, gdkeys, gdata)
        bireport.reportGameEvent('CREATE_GAME_DATA',
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)
        isCreate = True
    return isCreate


# def updateHistoryClientIds(userId, gameId, clientId):
#     '''
#     更新当前游戏数据中, 客户端的历史版本记录
#     即详细记录当前用户再每个游戏中,使用过的客户端
#     '''
#     intClientId = pokerconf.clientIdToNumber(clientId)
#     if intClientId <= 0 :
#         ftlog.error('updateGameDataHistoryClientIds not know clientid ! [', clientId, ']')
#         return
# 
#     changed = False
#     found = False
#     clist = gamedata.getGameAttrJson(userId, gameId, 'history_clientids', [])
#     for x in xrange(len(clist)) :
#         c = clist[x]
#         if not isinstance(c, int) :  # 老数据的补丁, 转换字符格式到数字格式
#             c = pokerconf.clientIdToNumber(c)
#             if c <= 0 :
#                 ftlog.error('updateGameDataHistoryClientIds not know clientid ! [', clist[x], ']')
#             clist[x] = c
#             changed = True
#         if c == intClientId :
#             found = True
# 
#     if not found :
#         clist.append(intClientId)
#         changed = True
#     
#     if changed :
#         gamedata.setGameAttr(userId, gameId, 'history_clientids', strutil.dumps(clist))


# def getHistoryClientIds(userId, gameId):
#     return gamedata.getGameAttrJson(userId, gameId, 'history_clientids', [])


def getUserHeadPics(clientId):
    return hallconf.getUserHeadPics(clientId)


