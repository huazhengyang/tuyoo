# -*- coding:utf-8 -*-
'''
Created on 2017年2月9日

@author: zhaojiangang
'''
from hall.entity import hallshare, hallitem
from poker.entity.configure import configure
from poker.util import strutil
import freetime.util.log as ftlog


def getChangeNickNameLevel(gameId):
    return configure.getGameJson(gameId, 'public', {}).get('change_nickname_level')

def getAdNotifyPlayCount(gameId):
    return configure.getGameJson(gameId, 'public', {}).get('ad_notify_play_count')

def getRoomComplainConf(gameId, bigRoomId):
    conf = configure.getGameJson(gameId, 'complain', {}, configure.DEFAULT_CLIENT_ID)
    tips = conf.get('tips', {})
    clientIdLimit = conf.get('clientIdLimit', 3.72)
    template = conf.get('rooms', {}).get(str(bigRoomId), '')
    if template:
        return conf.get('complains', {}).get(template, {}), tips, clientIdLimit
    else:
        return {}, tips, clientIdLimit

def getGamewinShareinfo(gameId, clientId):
    '''
    获取结算分享所需的
    '''
    templateName = configure.getVcTemplate('share.gamewin', clientId, gameId)
    shareConf = configure.getGameJson(gameId, 'share.gamewin', {}, configure.CLIENT_ID_TEMPLATE)
    templateMap = shareConf.get('templates', {})
    retConf = templateMap.get(templateName, {}).get('default', {})
    return retConf

def getNewShareInfoByCondiction(gameId, clientId, condiction=None):
    '''
    新分享 根据 牌桌连胜、牌桌赢金币、红包赛、实物赛 4种情况区分shareId和发奖
    '''
    condiction = condiction if condiction else 'default'
    templateName = configure.getVcTemplate('share.gamewin', clientId, gameId)
    shareConf = configure.getGameJson(gameId, 'share.gamewin', {}, configure.CLIENT_ID_TEMPLATE)
    templateMapCond = shareConf.get('templates', {}).get(templateName, {})
    shareConf = templateMapCond.get(str(condiction), {})

    if shareConf:
        itemId = shareConf.get('rewardInfo', {}).get('itemId')
        if itemId:
            assetKind = hallitem.itemSystem.findAssetKind(itemId)
            shareConf['rewardInfo']['img'] = assetKind.pic if assetKind else ''
    else:
        shareConf = templateMapCond.get('default', {})

    if ftlog.is_debug():
        ftlog.debug('getNewShareInfoByCondiction condiction=', condiction, 'conf=', shareConf)

    return shareConf if shareConf else getGamewinShareinfo(gameId, clientId)

def getMatchShareInfo(userName, raceName, rank, reward, userId, condiction, clientId):
    DIZHU_GAMEID = 6
    shareIds = getNewShareInfoByCondiction(DIZHU_GAMEID, clientId, condiction).get('shareIds', {})
    rewardInfo = getNewShareInfoByCondiction(DIZHU_GAMEID, clientId, condiction).get('rewardInfo', {})
    shareId = shareIds.get('weixin', 0) if shareIds else None
    if not shareId:
        return None

    share = hallshare.findShare(shareId)
    params = {'userName': userName, 'raceName': raceName, 'rank': rank, 'reward': reward}

    todotask = share.buildTodotask(DIZHU_GAMEID, userId, 'diploma_share')
    desc = todotask.getParam('des', '')
    todotask.setParam('des', strutil.replaceParams(desc, params))

    todotaskDict = todotask.toDict()
    todotaskDict['rewardInfo'] = rewardInfo if rewardInfo else None

    if ftlog.is_debug():
        ftlog.debug('getMatchShareInfo userId=', userId,
                    'shareId=', shareId,
                    'userName=', userName,
                    'raceName=', raceName,
                    'rank=', rank,
                    'reward=', reward,
                    'condiction=', condiction)

    return todotaskDict



