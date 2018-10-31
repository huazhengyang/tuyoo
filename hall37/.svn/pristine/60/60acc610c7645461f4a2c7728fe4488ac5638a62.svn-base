# -*- coding: utf-8 -*-
'''
Created on 2017年6月26日
@author: ljh
'''
import datetime
import json
import random

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify, hallvip, hallconf
from hall.entity.hallconf import HALL_GAMEID, getNewCheckinTCConf
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper,\
    TodoTaskPopTip
from poker.entity.biz import bireport
import poker.entity.biz.message.message as pkmessage
from poker.entity.configure import configure, pokerconf
from poker.entity.dao import userdata, gamedata, userchip
from poker.entity.dao.userchip import ChipNotEnoughOpMode
from poker.protocol import router
import poker.util.timestamp as pktimestamp
import poker.entity.dao.gamedata as pkgamedata


WHERE_NPW = 2
WHERE_REQ = 1
NCI_TYPE_3 = 3
NCI_TYPE_7 = 7


def sendMsg2client(gameId, userId, type, context, isDisplay=True, npwId='', where=WHERE_REQ):
    if isDisplay == False:
        ftlog.hinfo("newcheckin|sendmsg2client|isDisplay", gameId, userId, type, context, where)
        return

    results = {}
    results['type'] = type  # '3','7'
    results['context'] = context

    mp = MsgPack()
    if where == WHERE_NPW:
        mp.setCmd('game_popwinodws')
        results['action'] = 'newpop_checkin'
        results['npwId'] = npwId
    else:
        mp.setCmd('new_checkin')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.debug("newcheckin|sendmsg2client|", gameId, userId, type, context, where, results)


def actualTcContent(clientId):
    datas = configure.getTcContentByGameId('newcheckin', None, HALL_GAMEID, clientId, [])
    if datas:
        ftlog.debug("actualTcContent|datas|", datas)
        return datas
    return {}


# 利用每日游戏时长反作弊
def antiCheatWithTodayTime(userId):
    todoayTime = pkgamedata.getGameAttrJson(userId, HALL_GAMEID, 'todaytime', {})
    dayCount = 0
    totalTime = 0
    for (_, value) in todoayTime.items():
        totalTime += value
        dayCount += 1

    if ftlog.is_debug():
        ftlog.debug('antiCheatWithTodayTime userId =', userId, ' daysWithRecord = ', dayCount,
                    ' gameTimeInDaysWithRecord = ', totalTime)

    cheatDays = hallconf._getHallPublic('cheatDays')
    cheatGameTime = hallconf._getHallPublic('gameTime')
    ret = dayCount >= cheatDays and totalTime < cheatGameTime
    
    if ftlog.is_debug():
        ftlog.debug('antiCheatWithTodayTime cheatDays=', cheatDays, 'cheatGameTime=', cheatGameTime, 'ret=', ret)

    return ret


# 是否充值，首充标记
def isFirstRecharged(userId):
    return pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'first_recharge') > 0


def isScriptDoGetReward(userId):
    isRecharged = isFirstRecharged(userId)
    return antiCheatWithTodayTime(userId) and not isRecharged


# 玩家每日首次登陆,请求签到[s-s]
def checkin(userId, gameId, clientId, loginsum, isDisplay, npwId, where=WHERE_NPW):
    ftlog.info("|newcheckin|login|", userId, gameId, loginsum, clientId)

    #complementByVip(userId, gameId, clientId)

    # info = {'type': 3, 'checkDay': 2, 'isCheckIn': True, 'checkDate': '2017-06-23'}
    ftlog.debug("|newcheckin|login|2", userId, gameId, loginsum, clientId)
    info = gamedata.getGameAttr(userId, HALL_GAMEID, 'checkin_new')
    if not info:
        # loginDays = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'loginDays')
        # if not loginDays:
        #     ftlog.error("newcheckin|user|havenot|loginDays|",userId,gameId,clientId,loginsum)
        #     return

        # 新用户人生第一次登陆
        ftlog.debug("|newcheckin|login|3", userId, gameId, loginsum, clientId)
        if loginsum == 1:
            type = NCI_TYPE_3
            checkDay = 0  # 0,1,2   3,4,5,6
            info = {'type': type, 'checkDay': checkDay, 'isCheckIn': True,
                    'checkDate': datetime.datetime.now().strftime('%Y-%m-%d')}
            gamedata.setGameAttr(userId, HALL_GAMEID, 'checkin_new', json.dumps(info))

            checkinId, rewards = reward(userId, clientId, type, checkDay)

            clientMsg = {'isCheckIn': False, 'checkDay': checkDay, 'checkinId': checkinId, 'rewards': rewards}
            sendMsg2client(gameId, userId, type, clientMsg, isDisplay, npwId, where)

            ftlog.debug("newcheckin|firstreward|newavatar|ok|", userId, info, checkinId, rewards)
        else:
            type = NCI_TYPE_7
            if isScriptDoGetReward(userId):
                TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskPopTip('亲，签到奖励准备中，请玩几把再来领取吧！'))
                return
            checkDay = 0  # 0,1,2   3,4,5,6
            info = {'type': type, 'checkDay': checkDay, 'isCheckIn': True,
                    'checkDate': datetime.datetime.now().strftime('%Y-%m-%d')}
            gamedata.setGameAttr(userId, HALL_GAMEID, 'checkin_new', json.dumps(info))

            checkinId, rewards = reward(userId, clientId, type, checkDay)

            clientMsg = {'isCheckIn': False, 'checkDay': checkDay, 'checkinId': checkinId, 'rewards': rewards}
            sendMsg2client(gameId, userId, type, clientMsg, isDisplay, npwId, where)

            ftlog.debug("newcheckin|firstreward|oldavatar|ok|", userId, info, checkinId, rewards)

    else:
        info = json.loads(info)
        checkinImpl(userId, info, clientId, gameId, isDisplay, npwId, where)


# 玩家进入签到领取界面,请求签到[c-s]
def clientReqCheckin(userId, clientId, gameId):
    from hall.entity.localservice import localservice
    ftlog.debug("|clientReqCheckin|freeItemId|", userId, gameId, clientId)
    if not localservice.checkClientVer(userId, gameId, clientId):
        if ftlog.is_debug():
            ftlog.debug("clientReqCheckin|less|clientVer", userId, gameId, clientId, clientId)
        return

    info = gamedata.getGameAttr(userId, HALL_GAMEID, 'checkin_new')
    if not info:
        ftlog.hinfo("clientReqCheckin|redis|havenot|checkin_new|", userId, gameId, clientId)
        return
    checkinImpl(userId, json.loads(info), clientId, gameId, True, '', WHERE_REQ)


# 执行签到领取
def checkinImpl(userId, info, clientId, gameId, isDisplay, npwId, where):
    ftlog.debug("checkinImpl|enter|", userId, info, clientId, gameId)
    type = info['type']
    checkDay = info['checkDay']
    checkDate = info['checkDate']
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if today == info['checkDate']:
        clientMsg = {'isCheckIn': True, 'checkDay': info['checkDay'], 'checkinId': getCheckinId(clientId)}
        sendMsg2client(gameId, userId, type, clientMsg, isDisplay, npwId, where)

        ftlog.debug("checkinImpl|already|reward|", userId, info, clientId, gameId)
        return

    if type == NCI_TYPE_3 and checkDay < 2:
        ncheckDay = checkDay + 1
        info = {'type': type, 'checkDay': ncheckDay, 'isCheckIn': True,
                'checkDate': datetime.datetime.now().strftime('%Y-%m-%d')}
        gamedata.setGameAttr(userId, HALL_GAMEID, 'checkin_new', json.dumps(info))

        checkinId, rewards = reward(userId, clientId, type, ncheckDay)

        clientMsg = {'isCheckIn': False, 'checkDay': ncheckDay, 'checkinId': checkinId, 'rewards': rewards}
        sendMsg2client(gameId, userId, type, clientMsg, isDisplay, npwId, where)

        ftlog.debug("checkinImpl|3Day|ok|", userId, info, checkinId, rewards)
    elif type == NCI_TYPE_3 and checkDay == 2:
        ntype = NCI_TYPE_7
        ncheckDay = 0
        info = {'type': ntype, 'checkDay': ncheckDay, 'isCheckIn': True,
                'checkDate': datetime.datetime.now().strftime('%Y-%m-%d')}
        gamedata.setGameAttr(userId, HALL_GAMEID, 'checkin_new', json.dumps(info))

        checkinId, rewards = reward(userId, clientId, ntype, ncheckDay)

        clientMsg = {'isCheckIn': False, 'checkDay': ncheckDay, 'checkinId': checkinId, 'rewards': rewards}
        sendMsg2client(gameId, userId, ntype, clientMsg, isDisplay, npwId, where)

        ftlog.debug("checkinImpl|7Day|init|ok|", userId, info, checkinId, rewards)
    elif type == NCI_TYPE_7:
        if isScriptDoGetReward(userId):
            TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskPopTip('亲，签到奖励准备中，请玩几把再来领取吧！'))
            return
        delta = datetime.timedelta(days=1)
        checkDate_dt = datetime.datetime.strptime(checkDate, '%Y-%m-%d')
        add1Day = checkDate_dt + delta
        add1Day_str = add1Day.strftime('%Y-%m-%d')

        ftlog.debug("checkinImpl|7day", userId, info, add1Day_str, today)
        if add1Day_str == today:
            if checkDay < 6:
                ncheckDay = checkDay + 1
            elif checkDay == 6:
                ncheckDay = 0

            info = {'type': type, 'checkDay': ncheckDay, 'isCheckIn': True,
                    'checkDate': datetime.datetime.now().strftime('%Y-%m-%d')}
            gamedata.setGameAttr(userId, HALL_GAMEID, 'checkin_new', json.dumps(info))

            checkinId, rewards = reward(userId, clientId, type, ncheckDay)

            clientMsg = {'isCheckIn': False, 'checkDay': ncheckDay, 'checkinId': checkinId, 'rewards': rewards}
            sendMsg2client(gameId, userId, type, clientMsg, isDisplay, npwId, where)

            ftlog.debug("checkinImpl|7Day|ok|", userId, info, checkinId, rewards)
        else:
            ncheckDay = 0
            info = {'type': type, 'checkDay': ncheckDay, 'isCheckIn': True,
                    'checkDate': datetime.datetime.now().strftime('%Y-%m-%d')}
            gamedata.setGameAttr(userId, HALL_GAMEID, 'checkin_new', json.dumps(info))

            checkinId, rewards = reward(userId, clientId, type, ncheckDay)

            clientMsg = {'isCheckIn': False, 'checkDay': ncheckDay, 'checkinId': checkinId, 'rewards': rewards}
            sendMsg2client(gameId, userId, type, clientMsg, isDisplay, npwId, where)

            ftlog.debug("checkinImpl|7Day|reset|ok|", userId, info, checkinId, rewards)


def addAsset(userId, itemId, count):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)

    assetKind, consumecount, finalcount = userAssets.addAsset(HALL_GAMEID, itemId,
                                                              count, timestamp,
                                                              pokerconf.biEventIdToNumber("HALL_NEWCHECKIN"),
                                                              0)

    ftlog.hinfo("newcheckin|reward|addAsset|", userId, itemId, count)
    # 通知用户道具和消息存在改变
    if assetKind.keyForChangeNotify:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId,
                                              [assetKind.keyForChangeNotify, 'message'])


def getDatasKey(type, dataskeyList):
    for key in dataskeyList:
        if str(type) in key:
            return key  # u'default_3'


def getVipLevel(userId):
    userVip = hallvip.userVipSystem.getUserVip(userId)
    if userVip:
        return userVip.vipLevel.level
    return 0


# 获取节点key 比如'default'
def getCheckinIdKey(soncheckinId):
    assert (isinstance(soncheckinId, basestring))

    sidlist = soncheckinId.split('_')
    assert len(sidlist) > 1
    return sidlist[0]


# 获取渠道 "huawei"
def getCheckinId(clientId, typeId=NCI_TYPE_3):
    datas = actualTcContent(clientId)
    soncheckinId = getDatasKey(typeId, datas.keys())  # u'default_3'
    checkinId = getCheckinIdKey(soncheckinId)  # u'default'
    return checkinId


# 计算vip翻倍
def getVipRatio(userId, vipKeyConf):
    if vipKeyConf == None:
        return 1
    vip = vipKeyConf[0]
    ratio = vipKeyConf[1]
    vipL = getVipLevel(userId)
    if vipL >= vip:
        return ratio
    return 1


def reward(userId, clientId, type, checkDay):
    datas = actualTcContent(clientId)
    soncheckinId = getDatasKey(type, datas.keys())  # u'default_3'
    checkinId = getCheckinIdKey(soncheckinId)  # u'default'

    rewards = []
    tcConf = getNewCheckinTCConf()
    rewardList = tcConf['templates'][checkinId][soncheckinId]['days'][checkDay]['rewards']
    for rewardd in rewardList:
        ratio = getVipRatio(userId, rewardd.get('vip'))
        if rewardd['start'] == rewardd['stop']:
            addAsset(userId, rewardd['itemId'], rewardd['start'] * ratio)
            rewards.append(rewardd['start'] * ratio)
        else:
            count = random.randint(rewardd['start'], rewardd['stop'])
            addAsset(userId, rewardd['itemId'], count * ratio)
            rewards.append(count * ratio)

    ftlog.debug("newcheckin|reward|", userId, clientId, type, checkDay, soncheckinId, checkinId, rewards)
    return checkinId, rewards


def addChip(userId, gameId, clientId, chip):
    trueDelta, final = userchip.incrChip(userId, gameId, chip,
                                         ChipNotEnoughOpMode.NOOP,
                                         pokerconf.biEventIdToNumber("HALL_VIPCOMPLEMENT"),
                                         0, clientId)
    ftlog.hinfo("newcheckin|complementByVip|", gameId, userId, chip, trueDelta, final)

    if ftlog.is_debug():
        ftlog.debug('complementByVip.add gameId=', gameId,
                    'userId=', userId,
                    'count=', chip,
                    'trueDelta=', trueDelta,
                    'final=', final)

    return final


# 充值抵扣补偿
def deductionVipComplement(event):
    userId = event.userId

    ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|enter", userId, event.rmbs)
    if event.rmbs and event.rmbs > 0:
        gamedata.setGameAttr(userId, HALL_GAMEID, 'vip_complement_msg', 0)
        vip_complement = configure.getGameJson(HALL_GAMEID, "misc").get("vip_complement")
        vip_complement_max = configure.getGameJson(HALL_GAMEID, "misc").get("vip_complement_max")
        vipL = getVipLevel(userId)
        vipKey = "vip_" + str(vipL)
        max = 0
        if vipKey in vip_complement:
            max = vip_complement_max[vipKey]
        chargeDate = datetime.datetime.now().strftime('%Y-%m-%d')
        gamedata.setGameAttr(userId, HALL_GAMEID, 'chargeDate', chargeDate)
        vipcominfo = gamedata.getGameAttr(userId, HALL_GAMEID, 'vip_complement')
        ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|vipcominfo", userId, event.rmbs, vipcominfo)
        if vipcominfo:
            vipcominfo = json.loads(vipcominfo)
            vipcom = vipcominfo['vipcom']
            if vipcom == 0:
                ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|vipcom|zero", userId, event.rmbs, vipcominfo)
                return

            vip_complement_deduction = configure.getGameJson(HALL_GAMEID, "misc").get("vip_complement_deduction", 10000)
            deduction = int(event.rmbs) * vip_complement_deduction
            delta = vipcom - deduction
            ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement|vip_complement_deduction", userId, event.rmbs, vipcominfo, vip_complement_deduction, deduction, vipcom, delta)
            if delta < 0:
                delta = 0

            gamedata.setGameAttr(userId, HALL_GAMEID, 'vip_complement',
                                 json.dumps({'vipLevel': vipcominfo['vipLevel'], 'vipcom': int(delta)}))
            final = userchip.getChip(userId)
            bireport.reportGameEvent('HALL_VIPCOMPLEMENT', userId, event.gameId, 0, 0, 0, 0, 0, 0,
                                     [vipL, 0, deduction, int(max - delta), final],
                                     event.clientId,
                                     0, 0)

            ftlog.hinfo("ChargeNotifyEvent|deductionVipComplement", userId, event.rmbs, vipcominfo['vipLevel'], vipcom, delta)


# 近1月内充值金额为0的玩家该权益冻结
def checkChargeDate(userId):
    chargeDate = gamedata.getGameAttr(userId, HALL_GAMEID, 'chargeDate')
    if not chargeDate:
        return True

    delta = datetime.timedelta(days=30)
    chargeDate = datetime.datetime.strptime(chargeDate, '%Y-%m-%d')
    add30Day = chargeDate + delta
    if add30Day < datetime.datetime.now():
        return False

    return True


# 每日首次登陆金币补足
def complementByVip(userId, gameId, clientId):
    if not checkChargeDate(userId):
        ftlog.info("complementByVip|charge|surpass|30days", userId)
        return
    vip_complement = configure.getGameJson(HALL_GAMEID, "misc").get("vip_complement")
    vip_complement_max = configure.getGameJson(HALL_GAMEID, "misc").get("vip_complement_max")
    vipL = getVipLevel(userId)
    vipKey = "vip_" + str(vipL)
    ftlog.info("complementByVip|enter", userId, gameId, vipL, vipKey, vip_complement, clientId)
    if vipKey in vip_complement:
        once = vip_complement[vipKey]
        max = vip_complement_max[vipKey]
        coin = userdata.getAttr(userId, 'chip')
        vipcominfo = gamedata.getGameAttr(userId, HALL_GAMEID, 'vip_complement')
        if not vipcominfo:
            vipcom = 0
        else:
            vipcominfo = json.loads(vipcominfo)
            vipLevel = vipcominfo['vipLevel']
            if vipL != vipLevel:
                vipcom = 0
                ftlog.info("complementByVip|vip|up", userId, vipL, vipLevel)
            else:
                vipcom = vipcominfo['vipcom']

        mostchip = max - vipcom
        ftlog.info("complementByVip|go", userId, gameId, clientId, once, max, coin, vipcom, mostchip, vipcominfo)
        if vipcom >= max:
            vip_complement_msg = gamedata.getGameAttr(userId, HALL_GAMEID, 'vip_complement_msg')
            if not vip_complement_msg:
                vip_complement_msg = 0
            else:
                if int(vip_complement_msg) >= 3:
                    return
            gamedata.setGameAttr(userId, HALL_GAMEID, 'vip_complement_msg', int(vip_complement_msg) + 1)
            ftlog.info("complementByVip|reach|max", userId ,gameId, clientId, vipcom, max)
            msg = u"今日您的VIP金币补足权益已停止，充值可恢复权益，充值越多，额度越高。客服电话：4008-098-000"
            infoTodoTask = TodoTaskShowInfo(msg, True)
            TodoTaskHelper.sendTodoTask(gameId, userId, infoTodoTask)

            return

        if coin >= once:
            ftlog.info("complementByVip|once|is|ok", userId, coin, once)
            return
        else:
            delta = once - coin
            if delta > mostchip:
                delta = mostchip
            final = addChip(userId, gameId, clientId, delta)
            if final:
                gamedata.setGameAttr(userId, HALL_GAMEID, 'vip_complement',
                                     json.dumps({'vipLevel': vipL, 'vipcom': vipcom + delta}))
                mail = "您当前是VIP%d，今日首次登录为您补足到%d金币"%(vipL, final)
                pkmessage.sendPrivate(9999, userId, 0, mail)

                bireport.reportGameEvent('HALL_VIPCOMPLEMENT', userId, gameId, 0, 0, 0, 0, 0, 0,
                                         [vipL, delta, -delta, max - vipcom - delta, final],
                                         clientId,
                                         0, 0)
                ftlog.info("complementByVip|", userId, vipL, delta, final)
