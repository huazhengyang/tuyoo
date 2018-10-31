# -*- coding: utf-8 -*-
'''
Created on 2017年7月12日
@author: ljh
'''
import json
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack

from poker.entity.configure import configure, pokerconf
from poker.protocol import router
from poker.entity.dao import gamedata
from poker.util import strutil
import poker.util.timestamp as pktimestamp

from hall.entity.newcheckin import checkin
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallusercond import UserConditionAND, UserConditionOR
from hall.entity import hallitem, datachangenotify
from hall.entity.todotask import TodoTaskHelper, TodoTaskShowRewards, TodoTaskShowInfo

# 新弹窗类型
NPW_ = "npw_"
NPW_NEWCHECKIN = "newcheckin"  # 每日首次签到,不用保存redis
NPW_NOTICE = "notice"
NPW_NOTICE2 = "notice2"
NPW_MONTHCARD = "monthcard"
NPW_PAYORDER = "payorder"
NPW_VIP = "vip"
NPW_ACTIVITY = "activity"
NPW_TODOTASK = "todotask"

NPW_TYPE = (NPW_NOTICE, NPW_NOTICE2, NPW_MONTHCARD, NPW_PAYORDER, NPW_VIP, NPW_ACTIVITY, NPW_TODOTASK)


def actualTcContent(clientId, package_gameId):
    datas = configure.getTcContentByGameId('newstartflow', None, package_gameId, clientId, [])
    if datas:
        ftlog.info("newstartflow|actualTcContent|datas|", datas)
        return datas
    return {}


def getpopwndBaseData():
    return configure.getGameJson(HALL_GAMEID, "newstartflow")


def initNPWredis(userId):
    global NPW_TYPE
    for typeId in NPW_TYPE:
        gamedata.setGameAttr(userId, HALL_GAMEID, NPW_ + typeId, 0)


# 逻辑入口
def enterpopwnd(userId, gameId, clientId, loginsum, isdayfirst, daylogin):
    ftlog.info("newstartflow|enterpopwnd1", userId, gameId, clientId, loginsum, isdayfirst, daylogin)
    package_gameId = strutil.getGameIdFromHallClientId(clientId)

    if isdayfirst:
        initNPWredis(userId)

    datas = actualTcContent(clientId, package_gameId)
    if len(datas) == 0:
        ftlog.info("newstartflow|package_gameId|noTc.json", userId, gameId, package_gameId)
        return

    popwndBaseData = getpopwndBaseData()

    npwsList = []
    for data in datas['list']:
        npwId = data['npwId']
        if npwId in popwndBaseData:
            npwsList.append((popwndBaseData[npwId], data))
        else:
            ftlog.info("npwId[%s] not in newstartflow" % npwId)

    npwsList.sort(key=lambda d: d[0]['sortId'])

    for npws_data in npwsList:
        dispatcher(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
        # ftlog.info("npws_data", userId, gameId, clientId, loginsum, isdayfirst, daylogin)

    ftlog.info("newstartflow|enterpopwnd2", userId, gameId, clientId, package_gameId, npwsList)


def dispatcher(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    global NPW_NEWCHECKIN, NPW_NOTICE, NPW_NOTICE2, NPW_MONTHCARD, NPW_PAYORDER, NPW_VIP, NPW_TODOTASK
    npws = npws_data[0]
    typeId = npws['typeId']
    # 这个地方之所以这么写,就是为了以后扩展考虑,没有把它们抽象在一起
    ftlog.info("dispatcher", typeId, userId, gameId, clientId, loginsum, isdayfirst, daylogin)
    if typeId == NPW_NEWCHECKIN:
        if isdayfirst:  # 每日首次登陆签到
            ftlog.info("dispatcher|checkin", userId, gameId, clientId, loginsum, isdayfirst, daylogin)
            npw_newcheckin(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    elif typeId in [NPW_NOTICE, NPW_NOTICE2]:
        npw_notice(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    elif typeId == NPW_MONTHCARD:
        npw_monthcard(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    elif typeId == NPW_PAYORDER:
        npw_payorder(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    elif typeId == NPW_VIP:
        npw_vip(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    elif typeId == NPW_ACTIVITY:
        npw_activity(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    elif typeId == NPW_TODOTASK:
        npw_todotask(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)


def gettimestamp():
    return pktimestamp.getCurrentTimestamp()


def checkConditionsAND(userId, gameId, clientId, condition):
    cond = UserConditionAND()
    cond.decodeFromDict(condition)
    ftlog.debug("checkConditionsAND||", userId, condition)
    for c in cond.conditions:
        r = c.check(gameId, userId, clientId, gettimestamp())
        ftlog.debug("checkConditionsAND|TYPE_ID|", userId, c.TYPE_ID, r)

    return cond.check(gameId, userId, clientId, gettimestamp())


def checkConditionsOR(userId, gameId, clientId, condition):
    cond = UserConditionOR()
    cond.decodeFromDict(condition)
    ftlog.debug("UserConditionOR||", userId, condition)
    for c in cond.conditions:
        r = c.check(gameId, userId, clientId, gettimestamp())
        ftlog.debug("UserConditionOR|TYPE_ID|", userId, c.TYPE_ID, r)

    return cond.check(gameId, userId, clientId, gettimestamp())


def npw_newcheckin(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']

    ftlog.debug("npw_newcheckin|user.cond.and|enter", userId, condition)

    isDisplay = False
    if enable and condition['typeId'] == "user.cond.and":
        isDisplay = checkConditionsAND(userId, gameId, clientId, condition)
        ftlog.debug("npw_newcheckin|user.cond.and", enable, userId, isDisplay)
    elif enable and condition['typeId'] == "user.cond.or":
        isDisplay = checkConditionsOR(userId, gameId, clientId, condition)
        ftlog.debug("npw_newcheckin|user.cond.or", userId)

    ftlog.info("npw_newcheckin", userId, condition['typeId'], isDisplay)
    checkin(userId, gameId, clientId, loginsum, isDisplay, data['npwId'])


def checkConditionsTimes(userId, daylogin, npws):
    dailyTimes = npws['dailyTimes']
    dailyStartLoginTimes = npws['dailyStartLoginTimes']
    typeId = npws['typeId']

    # 从每日第几次开始弹
    if daylogin < dailyStartLoginTimes:
        ftlog.debug("checkConditionsTimes|dailyStartLoginTimes", userId, daylogin, dailyStartLoginTimes)
        return False
    # 每日弹窗的次数
    poptimes = gamedata.getGameAttr(userId, HALL_GAMEID, NPW_ + typeId)
    if poptimes >= dailyTimes:
        ftlog.debug("checkConditionsTimes|dailyTimes", userId, poptimes, dailyTimes)
        return False

    return True


def sendMsg2client(gameId, userId, action, params):
    results = {}
    results.update(params)
    # results['params'] = params
    results['action'] = action

    mp = MsgPack()
    mp.setCmd('game_popwinodws')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.debug("npw_|sendmsg2client|", gameId, userId, action, results)


def npw_notice(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    ftlog.debug("npw_notice|enter", userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']
    if not enable or not checkConditionsTimes(userId, daylogin, npws):
        ftlog.debug("npw_notice|timesNotMatch", enable, userId, daylogin)
        return

    if condition['typeId'] == "user.cond.and":
        if not checkConditionsAND(userId, gameId, clientId, condition):
            ftlog.debug("npw_notice|user.cond.and", userId)
            return
    elif condition['typeId'] == "user.cond.or":
        if not checkConditionsOR(userId, gameId, clientId, condition):
            ftlog.debug("npw_notice|user.cond.or", userId)
            return

    # 查看noticereward
    buttonText = data['buttonText']
    if "sub_action" in data:
        if "noticereward" in data["sub_action"]:
            info = gamedata.getGameAttr(userId, HALL_GAMEID, NPW_ + "noticereward")
            if info:
                info = json.loads(info)
            if not info or info != data["sub_action"]["noticereward"]:
                data['buttonText'] = "领 取"
                ftlog.debug("noticereward|buttonText", userId, info, data["sub_action"]["noticereward"])

    ftlog.debug("noticereward|buttonText2", userId, data["buttonText"])
    sendMsg2client(gameId, userId, "newpop_notice", data)
    gamedata.incrGameAttr(userId, HALL_GAMEID, NPW_ + NPW_NOTICE, 1)
    data['buttonText'] = buttonText


def npw_monthcard(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    ftlog.debug("npw_monthcard|enter", userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']
    if not enable or not checkConditionsTimes(userId, daylogin, npws):
        ftlog.debug("npw_monthcard|timesNotMatch", enable, userId, daylogin)
        return

    if condition['typeId'] == "user.cond.and":
        if not checkConditionsAND(userId, gameId, clientId, condition):
            ftlog.debug("npw_monthcard|user.cond.and", userId)
            return
    elif condition['typeId'] == "user.cond.or":
        if not checkConditionsOR(userId, gameId, clientId, condition):
            ftlog.debug("npw_monthcard|user.cond.or", userId)
            return

    sendMsg2client(gameId, userId, "newpop_member_buy", data)
    gamedata.incrGameAttr(userId, HALL_GAMEID, NPW_ + NPW_MONTHCARD, 1)


def npw_payorder(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    ftlog.debug("npw_payorder|enter", userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']
    if not enable or not checkConditionsTimes(userId, daylogin, npws):
        ftlog.debug("npw_payorder|timesNotMatch", enable, userId, daylogin)
        return

    if condition['typeId'] == "user.cond.and":
        if not checkConditionsAND(userId, gameId, clientId, condition):
            ftlog.debug("npw_payorder|user.cond.and", userId)
            return
    elif condition['typeId'] == "user.cond.or":
        if not checkConditionsOR(userId, gameId, clientId, condition):
            ftlog.debug("npw_payorder|user.cond.or", userId)
            return

    sendMsg2client(gameId, userId, "newpop_first_recharge", data)
    gamedata.incrGameAttr(userId, HALL_GAMEID, NPW_ + NPW_PAYORDER, 1)


def npw_vip(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    ftlog.debug("npw_vip|enter", userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']
    if not enable or not checkConditionsTimes(userId, daylogin, npws):
        ftlog.debug("npw_vip|timesNotMatch", enable, userId, daylogin)
        return

    if condition['typeId'] == "user.cond.and":
        if not checkConditionsAND(userId, gameId, clientId, condition):
            ftlog.debug("npw_vip|user.cond.and", userId)
            return
    elif condition['typeId'] == "user.cond.or":
        if not checkConditionsOR(userId, gameId, clientId, condition):
            ftlog.debug("npw_vip|user.cond.or", userId)
            return

    sendMsg2client(gameId, userId, "newpop_sence_vip", {'npwId': data['npwId']})
    gamedata.incrGameAttr(userId, HALL_GAMEID, NPW_ + NPW_VIP, 1)

def npw_activity(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    ftlog.debug("npw_activity|enter", userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']
    if not enable or not checkConditionsTimes(userId, daylogin, npws):
        ftlog.debug("npw_activity|timesNotMatch", enable, userId, daylogin)
        return
    if condition['typeId'] == "user.cond.and":
        if not checkConditionsAND(userId, gameId, clientId, condition):
            ftlog.debug("npw_activity|user.cond.and", userId)
            return
    elif condition['typeId'] == "user.cond.or":
        if not checkConditionsOR(userId, gameId, clientId, condition):
            ftlog.debug("npw_activity|user.cond.or", userId)
            return
    sendMsg2client(gameId, userId, "newpop_act", {'npwId': data['npwId']})
    gamedata.incrGameAttr(userId, HALL_GAMEID, NPW_ + NPW_ACTIVITY, 1)

def npw_todotask(userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data):
    ftlog.debug("npw_todotask|enter", userId, gameId, clientId, loginsum, isdayfirst, daylogin, npws_data)
    npws = npws_data[0]
    data = npws_data[1]
    enable = data['enable']
    condition = npws['condition']
    if not enable or not checkConditionsTimes(userId, daylogin, npws):
        ftlog.debug("npw_todotask|timesNotMatch", enable, userId, daylogin)
        return
    if condition['typeId'] == "user.cond.and":
        if not checkConditionsAND(userId, gameId, clientId, condition):
            ftlog.debug("npw_todotask|user.cond.and", userId)
            return
    elif condition['typeId'] == "user.cond.or":
        if not checkConditionsOR(userId, gameId, clientId, condition):
            ftlog.debug("npw_todotask|user.cond.or", userId)
            return
    sendMsg2client(gameId, userId, "newpop_todotask", data)
    gamedata.incrGameAttr(userId, HALL_GAMEID, NPW_ + NPW_TODOTASK, 1)

def addAssetnpw(userId, itemId, count, biEventId):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)

    assetKind, _consumecount, _finalcount = userAssets.addAsset(HALL_GAMEID, itemId,
                                                                count, timestamp,
                                                                pokerconf.biEventIdToNumber(biEventId),
                                                                0)

    ftlog.hinfo("addAssetnpw|reward|addAsset|", biEventId, userId, itemId, count)
    # 通知用户道具和消息存在改变
    if assetKind.keyForChangeNotify:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId,
                                              [assetKind.keyForChangeNotify, 'message'])


def getNoticeRewardData(userId, gameId, clientId):
    package_gameId = strutil.getGameIdFromHallClientId(clientId)
    datas = actualTcContent(clientId, package_gameId)
    if len(datas) == 0:
        ftlog.warn("getNoticeRewardData|newstartflow|package_gameId|noTc.json", userId, gameId, package_gameId)
        return

    for data in datas['list']:
        if "notice" == data['npwId']:
            return data


# 公告奖励领取并弹窗
def noticeReward(userId, gameId, clientId, msg):
    from hall.entity.localservice import localservice
    ftlog.debug("noticeReward:", userId, gameId, clientId, msg)
    # 是否是登录大厅
    if gameId != HALL_GAMEID:
        ftlog.debug("noticeReward|isnotloginHall", gameId)
        return

    # 是否是v4.56
    if not localservice.checkClientVer(userId, gameId, clientId):
        ftlog.debug("noticeReward|failer|clientVer|isnotMatch|", userId, gameId, clientId)
        return

    data = getNoticeRewardData(userId, gameId, clientId)
    if not data:
        ftlog.warn("noticeReward|haveNotConfig", userId, gameId, clientId)
        return

    ftlog.debug("noticeReward|data|", userId, "sub_action" in data, data)

    if "sub_action" in data:
        if "noticereward" in data["sub_action"]["params"]:
            info = gamedata.getGameAttr(userId, HALL_GAMEID, NPW_ + "noticereward")
            ftlog.debug("noticereward|redis", userId, info, type(info), data["sub_action"]["params"]["noticereward"],
                        type(data["sub_action"]["params"]["noticereward"]),
                        info == data["sub_action"]["params"]["noticereward"])
            if info:
                info = json.loads(info)
            if not info or info != data["sub_action"]["params"]["noticereward"]:
                if "params" not in data["sub_action"] or "reward" not in data["sub_action"]["params"]:
                    ftlog.warn("noticeReward|ConfigError!", userId, gameId, clientId)
                    return
                rewardList = []
                rewardds = data["sub_action"]["params"]["reward"]
                for rewardd in rewardds:
                    addAssetnpw(userId, rewardd['itemId'], rewardd['count'], "HALL_NEWNOTICEREWARD")
                    rewardList.append({'name': rewardd['name'], 'pic': rewardd['pic'], 'count': rewardd['count']})

                gamedata.setGameAttr(userId, HALL_GAMEID, NPW_ + "noticereward",
                                     json.dumps(data["sub_action"]["params"]["noticereward"]))

                rewardTodotask = TodoTaskShowRewards(rewardList)
                TodoTaskHelper.sendTodoTask(gameId, userId, rewardTodotask)

                ftlog.debug("noticereward|addAssetnpw。", userId)
            else:
                ftlog.debug("noticereward|alreadydone。", userId)
                msg = u"对不起，您已经领过该奖励了。"
                infoTodoTask = TodoTaskShowInfo(msg, True)
                TodoTaskHelper.sendTodoTask(gameId, userId, infoTodoTask)
