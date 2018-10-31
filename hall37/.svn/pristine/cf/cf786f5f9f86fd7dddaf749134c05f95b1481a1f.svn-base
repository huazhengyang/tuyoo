# -*- coding: utf-8 -*-
'''
Created on 2017年4月5日

@author: zqh
'''
import time
from copy import deepcopy

import freetime.util.log as ftlog
from hall.entity import hallvip
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.dao import gamedata, sessiondata, userdata
from hall.entity.iploc import iploc
from poker.util import strutil
from poker.entity.configure import configure, pokerconf


_DEBUG = 0

# 大丰收，跑狗，百人牛牛，斗牛，红黑大战，金三顺，中发白，欢乐小丑 ，三张牌


def _getVIpLevel(userId):
    vipLevel = 0
    vipInfo = hallvip.userVipSystem.getUserVip(userId)
    if vipInfo:
        vipLevel = vipInfo.vipLevel.level
    return vipLevel


def _getPlayTimes(userId):
    totalTime = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'totaltime')
    return totalTime

def isUser2018(userId):
    try:
        createTime = userdata.getAttr(userId, 'createTime')
        if createTime and str(createTime).find('2018') == 0 :
            return 1
    except:
        ftlog.error()
    return 0

def _isPrefilterConditions(userId, clientId):
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    if not conf.get('enableIpCheck', 0):
        return 1

#     intClientId = pokerconf.clientIdToNumber(clientId)
#     if intClientId not in conf.get('filterClientIds', []):
#         return 1

    #优先过滤白名单
    if iploc.isFilterUser(userId):
        if _DEBUG:
            ftlog.debug('_isPrefilterConditions', userId, 'enableUserCheck !')
        return 1

    passHall = conf.get('passHall', [])
    if passHall:
        for ph in passHall:
            if clientId.find(ph) > 0:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, clientId, ph, 'passHall !')
                return 1

    filterHallSpecial = conf.get('filterHall_special', [])
    if filterHallSpecial:
        for ph in filterHallSpecial:
            if clientId.find(ph) > 0:
                #限制大厅的版本在3.9以上
                passClientVerSpecial = conf.get('passClientVer_special_game', 0)
                if passClientVerSpecial > 0:
                    _, cver, _ = strutil.parseClientId(clientId)
                    if cver < passClientVerSpecial:
                        if _DEBUG:
                            ftlog.debug('gamelistipfilter === filterHall_special ', userId, clientId, passClientVerSpecial, 'passClientVer_special_game !')
                        return 1
                if _DEBUG:
                    ftlog.debug('_isPrefilterConditions', userId, clientId, ph, 'filterHallSpecial !')
                return 0

    filterHall = conf.get('filterHall', [])
    if filterHall:
        for ph in filterHall:
            if clientId.find(ph) > 0:
                #限制大厅的版本在4.5以上
                passClientVer = conf.get('passClientVer', 0)
                if passClientVer > 0:
                    _, cver, _ = strutil.parseClientId(clientId)
                    if cver < passClientVer:
                        if _DEBUG:
                            ftlog.debug('gamelistipfilter === filterHall', userId, clientId, passClientVer, 'passClientVer !')
                        return 1
                if _DEBUG:
                    ftlog.debug('_isPrefilterConditions', userId, clientId, ph, 'filterHall !')
                return 0

    #other hall limit version 4.5
    passClientVer = conf.get('passClientVer', 0)
    if passClientVer > 0:
        _, cver, _ = strutil.parseClientId(clientId)
        if cver < passClientVer:
            if _DEBUG:
                ftlog.debug('gamelistipfilter === other hall', userId, clientId, passClientVer, 'passClientVer !')
            return 1

    if _DEBUG:
        ftlog.debug('in _isPrefilterConditions filtergamelist go filter !', userId)
    return 0

def _isfilterConditions_group1(userId, clientId):
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('_isfilterConditions_group1', userId, ipstr, 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group1_passVipLevel = conf.get('group1_passVipLevel', 0)
        if group1_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group1_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group1', userId, vipLevel, group1_passVipLevel, 'group1_passVipLevel !')
                adjustVIP = 1

        group1_passTotalPlayTime = conf.get('group1_passTotalPlayTime', 0)
        if group1_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group1_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group1_passTotalPlayTime, 'group1_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1
    else:
        if _DEBUG:
                ftlog.debug('_isfilterConditions_group1 is in beijing or shenzhe!! userId = ', userId , 'enableIpCheck !')
        return 0

def _isfilterConditions_group2(userId, clientId):
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('_isfilterConditions_group2', userId, ipstr, 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group2_passVipLevel = conf.get('group2_passVipLevel', 0)
        if group2_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group2_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group2', userId, vipLevel, group2_passVipLevel, 'group2_passVipLevel !')
                adjustVIP = 1

        group2_passTotalPlayTime = conf.get('group2_passTotalPlayTime', 0)
        if group2_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group2_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group2_passTotalPlayTime, 'group2_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1
    else:
        if _DEBUG:
                ftlog.debug('_isfilterConditions_group2 is in beijing or shenzhe!! userId = ', userId , 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group2_passVipLevel = conf.get('group2_key_area_passVipLevel', 0)
        if group2_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group2_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group2', userId, vipLevel, group2_passVipLevel, 'group2_passVipLevel !')
                adjustVIP = 1

        group2_passTotalPlayTime = conf.get('group2_passTotalPlayTime', 0)
        if group2_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group2_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group2_passTotalPlayTime, 'group2_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1


def _isfilterConditions_group3(userId, clientId):
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('_isfilterConditions_group3', userId, ipstr, 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group3_passVipLevel = conf.get('group3_passVipLevel', 0)
        if group3_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group3_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group3', userId, vipLevel, group3_passVipLevel, '_isfilterConditions_group3 !')
                adjustVIP = 1

        group3_passTotalPlayTime = conf.get('group3_passTotalPlayTime', 0)
        if group3_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group3_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group3_passTotalPlayTime, '_isfilterConditions_group3 !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1
    else:
        if _DEBUG:
                ftlog.debug('_isfilterConditions_group3 is in beijing or shenzhe!! userId = ', userId , 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group3_passVipLevel = conf.get('group3_key_area_passVipLevel', 0)
        if group3_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group3_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group3', userId, vipLevel, group3_passVipLevel, 'group3_passVipLevel !')
                adjustVIP = 1

        group3_passTotalPlayTime = conf.get('group3_key_area_passTotalPlayTime', 0)
        if group3_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group3_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group3_passTotalPlayTime, 'group3_key_area_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1


def _isOutOfBeijingIp(userId, clientId):
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    if not conf.get('enableIpCheck', 0):
        return 1

#     intClientId = pokerconf.clientIdToNumber(clientId)
#     if intClientId not in conf.get('filterClientIds', []):
#         return 1

    passHall = conf.get('passHall', [])
    if passHall:
        for ph in passHall:
            if clientId.find(ph) > 0:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, clientId, ph, 'passHall !')
                return 1

    passClientVer = conf.get('passClientVer', 0)
    if passClientVer > 0:
        _, cver, _ = strutil.parseClientId(clientId)
        if cver < passClientVer:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, clientId, passClientVer, 'passClientVer !')
            return 1

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBeijingIp(ipstr):
        if _DEBUG:
            ftlog.debug('gamelistipfilter', userId, ipstr, 'enableIpCheck !')
        return 1

    passTotalPlayTime = conf.get('passTotalPlayTime', 0)
    if passTotalPlayTime > 0:
        totalTime = _getPlayTimes(userId)
        if totalTime >= passTotalPlayTime:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, totalTime, passTotalPlayTime, 'passTotalPlayTime !')
            return 1
    
    passVipLevel = conf.get('passVipLevel', 0)
    if passVipLevel > 0:
        vipLevel = _getVIpLevel(userId)
        if vipLevel >= passVipLevel:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, vipLevel, passVipLevel, 'passVipLevel !')
            return 1

    if _DEBUG:
        ftlog.debug('filtergamelist go filter !', userId, ipstr)
    return 0


def notifyUserGameWillShutDown(userId, clientId, isNeedPopShutDownGameWnd):
    #过期不弹窗
    nowStamp = int(time.time())
    if nowStamp >= 1524326400:
        return
    if not isNeedPopShutDownGameWnd:
        return
    from hall.entity.todotask import TodoTaskHelper
    from hall.entity.todotask import TodoTaskShowInfo
    TodoTaskHelper.sendTodoTask(9999, userId, TodoTaskShowInfo('因运营需要,4月19日起暂停发财扑克(含天地麻将)等功能模块,恢复时间请关注官网,感谢理解!', True))


def filtergamelist(version, games, pages, innerGames, userId, clientId, isNeedPopShutDownGameWnd = False):
    try:
        return _filtergamelist(version, games, pages, innerGames, userId, clientId, isNeedPopShutDownGameWnd)
    except:
        ftlog.error()
        return games, pages, innerGames


def _filtergamelist(version, games, pages, innerGames, userId, clientId, isNeedPopShutDownGameWnd):

    # if _isOutOfBeijingIp(userId, clientId):
    #     return games, pages, innerGames
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    # 优先过滤2018用户, 2018年用户不可见放在了第一优先级
    is2018 = isUser2018(userId)
    if _DEBUG:
        ftlog.debug('filtergamelist rm filterGameIds =====> is2018', userId, is2018)
    
    if not is2018 :
        if _isPrefilterConditions(userId, clientId):
            # 符合过滤条件玩家通知游戏即将下线,需要满足两个条件：gamelist里如果没有下线的游戏是不弹窗的，不符合看到小游戏的玩家也是不弹窗
            containGames = []
            for x in xrange(len(games) - 1, -1, -1):
                gameId = games[x].get('gameId')
                containGames.append(gameId)
            for x in xrange(len(innerGames) - 1, -1, -1):
                gameId = innerGames[x].get('params', {}).get('gameId')
                containGames.append(gameId)
            for x in xrange(len(pages) - 1, -1, -1):
                nodes = pages[x].get('nodes', [])
                for y in xrange(len(nodes) - 1, -1, -1):
                    gameId = nodes[y].get('params', {}).get('gameId')
                    containGames.append(gameId)
            gg1 = conf.get('group1_games', [])
            gg2 = conf.get('group2_games', [])
            gg3 = conf.get('group3_games', [])
            totalFilterGames = gg1 + gg2 + gg3
            canPop = False
            for fId in totalFilterGames:
                if fId in containGames:
                    canPop = True
                    break

            if canPop:
                notifyUserGameWillShutDown(userId, clientId, isNeedPopShutDownGameWnd)
            if ftlog.is_debug():
                ftlog.debug('filtergamelist containGames:', containGames, 'gg1:', gg1, 'gg2:', gg2, 'gg3:', gg3,
                            'userId:', userId)

            return games, pages, innerGames


    # filterGameIds = conf.get('filterGameIds', [])
    
    if version <= 0:
        games = deepcopy(games)
        pages = deepcopy(pages)
        innerGames = deepcopy(innerGames)

    filterGameIds = []
    containGames = []
    
    if is2018 :
        group2018 = conf.get('group2018_games', [])
        filterGameIds.extend(group2018)

    group1_games = conf.get('group1_games', [])
    if not _isfilterConditions_group1(userId, clientId):
        for game in group1_games:
            filterGameIds.append(game)


    group2_games = conf.get('group2_games', [])
    if not _isfilterConditions_group2(userId, clientId):
        for game in group2_games:
            filterGameIds.append(game)

    group3_games = conf.get('group3_games', [])
    if not _isfilterConditions_group3(userId, clientId):
        for game in group3_games:
            filterGameIds.append(game)

    if _DEBUG:
        ftlog.debug('filtergamelist rm filterGameIds =====> ', userId, filterGameIds)

    for x in xrange(len(innerGames) - 1, -1, -1):
        gameId = innerGames[x].get('params', {}).get('gameId')
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm innerGames', userId, gameId, innerGames[x])
            del innerGames[x]
        else:
            containGames.append(gameId)

    adjustPage = 0
    for x in xrange(len(pages) - 1, -1, -1):
        nodes = pages[x].get('nodes', [])
        for y in xrange(len(nodes) - 1, -1, -1):
            gameId = nodes[y].get('params', {}).get('gameId')
            if gameId in filterGameIds:
                if _DEBUG:
                    ftlog.debug('filtergamelist rm pages', userId, gameId, nodes[y])
                del nodes[y]
                adjustPage = 1
            else:
                containGames.append(gameId)
                subnodes = nodes[y].get('nodes', [])
                if subnodes:
                    for z in xrange(len(subnodes) - 1, -1, -1):
                        gameId = subnodes[z].get('params', {}).get('gameId')
                        if gameId in filterGameIds:
                            if _DEBUG:
                                ftlog.debug('filtergamelist rm sub pages', userId, gameId, subnodes[z])
                            del subnodes[z]
                            adjustPage = 1
                        else:
                            containGames.append(gameId)
                    if len(subnodes) <= 0:
                        if _DEBUG:
                            ftlog.debug('filtergamelist rm pages', userId, 'zero list', nodes[y])
                        del nodes[y]
                        adjustPage = 1


    if adjustPage:
        allnodes = []
        for x in xrange(len(pages)):
            nodes = pages[x].get('nodes', [])
            allnodes.extend(nodes)
            pages[x]['nodes'] = []

        x = 0
        while len(allnodes) > 0:
            pages[x]['nodes'] = allnodes[0:6]
            allnodes = allnodes[6:]
            x += 1

        for x in xrange(len(pages) - 1, -1, -1):
            nodes = pages[x].get('nodes', [])
            if not nodes:
                del pages[x]

    for x in xrange(len(games) - 1, -1, -1):
        gameId = games[x].get('gameId')
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm games', userId, gameId, games[x])
            del games[x]
        else:
            containGames.append(gameId)

    # 符合过滤条件玩家通知游戏即将下线,需要满足两个条件：gamelist里如果没有下线的游戏是不弹窗的，不符合看到小游戏的玩家也是不弹窗

    totalFilterGames = group1_games + group2_games + group3_games
    canPop = False
    for fId in containGames:
        if fId in totalFilterGames:
            canPop = True
            break
    if canPop:
        notifyUserGameWillShutDown(userId, clientId, isNeedPopShutDownGameWnd)
        if ftlog.is_debug():
            ftlog.debug('filtergamelist filterGameIds:', filterGameIds, 'containGames:', containGames, 'userId:',
                        userId)

    return games, pages, innerGames
