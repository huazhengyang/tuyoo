# -*- coding:utf-8 -*-
'''
Created on 2018-04-21

@author: wangyonghui
'''
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from hall.entity import hall_share2, hallitem
from hall.entity.hall_share2 import ParsedClientId
from poker.entity.configure import configure
import freetime.util.log as ftlog
from poker.util import strutil
import poker.util.timestamp as pktimestamp


def getWxShareTcContentByKey(userId, key, clientId):
    ''' 获取微信小游戏分享配置, 已clientId 进行区分 '''
    temp = configure.getTcContentByGameId('share.wx', None, DIZHU_GAMEID, clientId, defaultVal={})
    if ftlog.is_debug():
        ftlog.debug('dizhu_wx_share.getWxShareTcContent',
                    'userId=', userId,
                    'clientId=', clientId,
                    'temp=', temp)
    return temp.get(key, [])


# -------------------------------------------------------------------------------
# 以下是具体业务相关的配置获取函数, 目前为通用函数， 有业务区分时，可以根据kwargs参数，分拆N个函数
# -------------------------------------------------------------------------------

def getWxShareInfo(userId, key, clientId, **kwargs):
    shareInfoList = getWxShareTcContentByKey(userId, key, clientId)
    for shareInfo in shareInfoList:
        condition = shareInfo.get('condition')
        if not condition:
            continue

        if condition.get('type') in kwargs or condition.get('type') == 'default':
            start = condition.get('compare', {}).get('start', -1)
            stop = condition.get('compare', {}).get('stop', -1)
            if (start == -1 or (kwargs.get(condition.get('type'), {}).get('start', -1) >= start)) and (stop == -1 or (kwargs.get(condition.get('type'), {}).get('stop', -1) <= stop)):
                text = strutil.replaceParams(shareInfo.get('text', ''), kwargs.get(condition.get('type'), {}))
                parsedClientId = ParsedClientId.parseClientId(clientId)
                sharePoint = hall_share2.getSharePoint(DIZHU_GAMEID, parsedClientId, kwargs.get('pointId') or shareInfo.get('pointId'))
                rewards = []
                totalShareCount = 0
                rewardCount = 0
                if sharePoint and sharePoint.reward.content:
                    assetKindTupleList = hallitem.getAssetKindTupleList(sharePoint.reward.content)
                    for atup in assetKindTupleList:
                        rewards.append({'itemId': atup[0].kindId,
                                        'name': atup[0].displayName,
                                        'url': atup[0].pic,
                                        'count': atup[1]})
                    totalShareCount = sharePoint.reward.cycle.count
                    _, rewardCount = hall_share2.loadShareStatus(DIZHU_GAMEID, userId, sharePoint, pktimestamp.getCurrentTimestamp())
                return {
                    'pointId': kwargs.get('pointId') or shareInfo.get('pointId'),
                    'totalShareCount':  totalShareCount,
                    'leftShareCount': totalShareCount - rewardCount,
                    'img': shareInfo.get('img'),
                    'text': text,
                    'rewards': rewards
                }
    return None
