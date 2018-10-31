# -*- coding:utf-8 -*-

####################################################################################
#
# Copyright © 2017 TU. All Rights Reserved.
#
####################################################################################

"""

@File: dizhu_util.py

@Description: 地主工具设施

@Author: leiyunfei(leiyunfei@tuyoogame.com)

@Depart: 棋牌中心-斗地主项目组

@Create: 2017-05-22 15:23:57

"""

import random

import datetime

from freetime.util import log as ftlog

from poker.util import strutil
from poker.util import timestamp as pktimestamp
from poker.entity.biz.message import message
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.item.item import TYAssetUtils
from hall.entity import hallitem, datachangenotify

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.segment.dizhu_segment_match import SegmentMatchHelper


def getItemByWeight(items):
    """
    根据配置的权重概率获取数据
    param: items 候选列表
    格式：[
        {'item': {用户自定义数据字典}, 'weight': 1000},
        {'item': {用户自定义数据字典}, 'weight': 2000},
        {'item': {用户自定义数据字典}, 'weight': 3000},
        ...
    ]
    其中用户数据字典由用户自己定义并在应用程序中自解释

    return: {用户自定义数据字典}
    """
    assert (isinstance(items, list))

    total = sum([item.get('weight', 0) for item in items])
    base = random.randint(1, int(total))
    curtotal = 0
    index = None
    for i, item in enumerate(items):
        curtotal = curtotal + item.get('weight', 0)
        if base <= curtotal:
            index = i
            break
    pickedItem = items[index]
    if ftlog.is_debug():
        ftlog.debug('getItemByWeight',
                    'base=', base,
                    'tatal=', total,
                    'curtotal=', curtotal,
                    'index=', index,
                    'pickedItem=', pickedItem)
    return pickedItem.get('item', {})

def sendRewardItems(userId, items, mail, eventId, eventParam, **kwargs):
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetList = userAssets.sendContentItemList(
        DIZHU_GAMEID,
        items,
        1,
        True,
        pktimestamp.getCurrentTimestamp(),
        eventId,
        eventParam
    )
    changeNames = TYAssetUtils.getChangeDataNames(assetList)
    contents = TYAssetUtils.buildContentsString(assetList)
    if mail:
        replaceDict = {'rewardContent': contents}
        replaceDict.update(kwargs)
        mailstr = strutil.replaceParams(mail, replaceDict)
        mailstr = mailstr.replace('红包券', '元红包')
        message.send(DIZHU_GAMEID, message.MESSAGE_TYPE_SYSTEM, userId, mailstr)
        changeNames.add('message')
    datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, changeNames)
    return assetList

def sendReward(userId, rewardConf, mailstr, eventId, eventParam):
    """
    通用发货
    param: rewardConf 奖励配置
    格式：
    {
        'typeId': 'FixedContent',
        'items': [{'itemId': 'user:chip', 'count': 100}]
    }
    param: mailstr 邮件内容文本字符串，其中包含子串\\${rewardContent}
    eventId: 哪个事件触发的
    eventParam: 事件参数 
    return: list<(TYAssetKind, consumeCount, final)>
    """
    rewardContent = TYContentRegister.decodeFromDict(rewardConf)
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetList = userAssets.sendContent(
        DIZHU_GAMEID,
        rewardContent,
        1,
        True,
        pktimestamp.getCurrentTimestamp(),
        eventId,
        eventParam
    )
    changeNames = TYAssetUtils.getChangeDataNames(assetList)
    contents = TYAssetUtils.buildContentsString(assetList)
    if mailstr:
        mailstr = strutil.replaceParams(mailstr, {'rewardContent': contents})
        message.send(DIZHU_GAMEID, message.MESSAGE_TYPE_SYSTEM, userId, mailstr)
        changeNames.add('message')
    datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, changeNames)
    return assetList


def checkRoomOpenTime(roomConfig, nowTime):
    openTimeList = roomConfig.get('openTimeList')
    if not openTimeList:
        return True
    timeZeroStr = '00:00:00'
    for timeRange in openTimeList:
        try:
            beginTime = datetime.datetime.strptime(timeRange.get('begin', timeZeroStr), '%H:%M:%S').time()
            endTime = datetime.datetime.strptime(timeRange.get('end', timeZeroStr), '%H:%M:%S').time()
            if beginTime == endTime:
                return True
            elif beginTime < endTime:
                if nowTime >= beginTime and nowTime < endTime:
                    return True
            else:
                if nowTime >= beginTime or nowTime < endTime:
                    return True
        except:
            ftlog.error('checkRoomOpenTime',
                        'openTimeList=', openTimeList,
                        'timeRange=', timeRange)
    return False

def calcWeekBeginIssueNum(timestamp=None):
    '''
    返回timestamp时间戳时的周一日期 如：20170611
    :return: 返回格式为str
    '''
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    timestamp = pktimestamp.getWeekStartTimestamp(timestamp)
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')


def calcTodayIssueNum(timestamp=None):
    '''
    返回timestamp时间戳时的日期 如：20170611
    :return: 返回格式为str
    '''
    timestamp = pktimestamp.getCurrentTimestamp() if not timestamp else timestamp
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')


def get_user_segment(uid):
    issue = SegmentMatchHelper.getCurrentIssue()
    userSegmentIssue = SegmentMatchHelper.getUserSegmentDataIssue(uid, issue)
    if not userSegmentIssue:
        return 0
    return userSegmentIssue.segment