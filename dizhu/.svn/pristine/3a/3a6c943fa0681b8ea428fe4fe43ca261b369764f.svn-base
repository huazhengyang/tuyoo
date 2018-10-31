# -*- coding:utf-8 -*-
'''
Created on 2017年12月5日

@author: wangyonghui

@function: 比赛报名折扣
'''
import json

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from poker.entity.configure import configure
from poker.entity.dao import daobase
import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp


def buildUserMatchDiscountKey(userId):
    return "signinDiscount:%s:%s" % (DIZHU_GAMEID, userId)


def getRoomDiscountConf(bigRoomId):
    matchDiscountConf = configure.getGameJson(DIZHU_GAMEID, 'match.discount', {})
    opened = matchDiscountConf.get('open')
    if not opened:
        return
    roomDiscountConf = matchDiscountConf.get(str(bigRoomId), {})
    if not roomDiscountConf:
        return
    return roomDiscountConf


def saveUserMatchDiscountCount(userId, bigRoomId, itemId):
    """保存用户针对特定房间特定itemId的折扣次数"""
    try:
        key = buildUserMatchDiscountKey(userId)
        ret = daobase.executeUserCmd(userId, 'HGET', key, bigRoomId)
        if not ret:
            v = {itemId: {'count': 1, 'timestamp': pktimestamp.getCurrentTimestamp()}}
        else:
            v = json.loads(ret)
            if itemId in v:
                v[itemId]['count'] += 1
            else:
                v.setdefault(itemId, {'count': 1, 'timestamp': pktimestamp.getCurrentTimestamp()})
        daobase.executeUserCmd(userId, 'HSET', key, bigRoomId, json.dumps(v))
        if ftlog.is_debug():
            ftlog.debug('match_signin_discount.saveUserMatchDiscountCount',
                        'userId=', userId,
                        'bigRoomId=', bigRoomId,
                        'itemId=', itemId,
                        'data=', v)

    except Exception, e:
        ftlog.error('match_signin_discount.saveUserMatchSiginDiscountCount',
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'itemId=', itemId,
                    'err=', e.message)

def getUserMatchDiscountCount(userId, bigRoomId, itemId):
    """获取用户针对特定房间特定itemId的折扣次数, 每天清零"""
    try:
        key = buildUserMatchDiscountKey(userId)
        ret = daobase.executeUserCmd(userId, 'HGET', key, bigRoomId)
        if ret:
            ret = json.loads(ret)
            if itemId in ret:
                timestamp = ret[itemId]['timestamp']
                currentTimestamp = pktimestamp.getCurrentTimestamp()
                if not pktimestamp.is_same_day(timestamp, currentTimestamp):
                    ret[itemId]['timestamp'] = currentTimestamp
                    ret[itemId]['count'] = 0
                    daobase.executeUserCmd(userId, 'HSET', key, bigRoomId, json.dumps(ret))
                if ftlog.is_debug():
                    ftlog.debug('match_signin_discount.getUserMatchDiscountCount',
                                'userId=', userId,
                                'bigRoomId=', bigRoomId,
                                'itemId=', itemId,
                                'count=', ret[itemId]['count'])
                return ret[itemId]['count']
        return 0
    except Exception, e:
        ftlog.error('match_signin_discount.getUserMatchSiginDiscountCount',
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'itemId=', itemId,
                    'err=', e.message)
        return 0


def changeItemToDiscount(userId, bigRoomId, contentItem):
    """改变价格"""
    if ftlog.is_debug():
        ftlog.debug('match_signin_discount.changeItemsToDiscount',
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'contentItem=', contentItem)
    itemId = contentItem['itemId']
    ret, disConf, _ = canMatchDiscount(userId, bigRoomId, itemId)
    if not ret:
        return contentItem
    contentItem['count'] = int(disConf.get('discount', 1) * contentItem['count'])
    if ftlog.is_debug():
        ftlog.debug('match_signin_discount.changeItemsToDiscount new',
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'new_item=', contentItem)
    return contentItem

def canMatchDiscount(userId, bigRoomId, itemId):
    """判断是否可以在折扣"""

    # 判断用户此ItemId下的折扣次数
    roomDiscountConf = getRoomDiscountConf(bigRoomId)
    dizhuVersion = SessionDizhuVersion.getVersionNumber(userId)
    if not roomDiscountConf or dizhuVersion < roomDiscountConf.get('minVersion', 0):
        return False, None, 0

    disConf = roomDiscountConf.get(itemId, {})
    disCount = getUserMatchDiscountCount(userId, bigRoomId, itemId)
    for oroomid in disConf.get('actOn', []):
        disCount += getUserMatchDiscountCount(userId, oroomid, itemId)
    if disConf.get('count', -1) > 0 and disCount < disConf.get('count', -1):
        if ftlog.is_debug():
            ftlog.debug('match_signin_discount.canMatchDiscount',
                        'userId=', userId,
                        'bigRoomId=', bigRoomId,
                        'disCount=', disCount,
                        'disConf=', disConf)
        return True, disConf, disConf.get('count', -1) - disCount
    return False, None, 0

