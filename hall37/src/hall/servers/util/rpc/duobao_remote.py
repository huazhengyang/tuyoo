# -*- coding: utf-8 -*-

import freetime.util.log as ftlog
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def duobaoBet(userId, duobaoId, issue, num):
    '''
    一元夺宝下注
    '''
    from poker.entity.biz.exceptions import TYBizException
    ec = 0
    info = '投注成功'
    luckyCodeList, myBetCount, totalBetCount, coupon = [], 0, 0, 0

    try:
        from hall.entity.hall1yuanduobao import duobaoBet
        luckyCodeList, myBetCount, totalBetCount, coupon = duobaoBet(userId, duobaoId, issue, num)
    except TYBizException, e:
        ec = e.errorCode
        info = e.message

        ftlog.info('doDuobaoBet failer',
                   'userId=', userId,
                   'duobaoId=', duobaoId,
                   'issue=', issue,
                   'num=', num,
                   'ec=', ec,
                   'info=', info)

    return {'ec': ec, 'info': info, 'ret': {'luckyCodeList': luckyCodeList, 'myBetCount': myBetCount, 'totalBetCount': totalBetCount, 'coupon': coupon}}

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def duobaoReward(userId, duobaoId, issue):
    '''
    一元夺宝领奖
    '''
    from poker.entity.biz.exceptions import TYBizException
    ec = 0
    info = '领取成功'

    try:
        from hall.entity.hall1yuanduobao import duobaoReward
        duobaoReward(userId, duobaoId, issue)
    except TYBizException, e:
        ec = e.errorCode
        info = e.message

        ftlog.info('doubaoReward failer',
                   'userId=', userId,
                   'duobaoId=', duobaoId,
                   'issue=', issue,
                   'ec=', ec,
                   'info=', info)

    return {'ec': ec, 'info': info}

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def duobaoProduct(userId):
    '''一元夺宝商品'''
    from hall.entity.hall1yuanduobao import duobaoProduct
    productList = duobaoProduct(userId)

    return {'productList': productList}

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def duobaoHistory(userId, duobaoId, pageId):
    '''往期得主'''
    from poker.entity.biz.exceptions import TYBizException
    ec = 0
    info = '查询成功'
    historyList = []

    try:
        from hall.entity.hall1yuanduobao import duobaoHistory
        historyList = duobaoHistory(userId, duobaoId, pageId)
    except TYBizException, e:
        ec = e.errorCode
        info = e.message

        ftlog.info('doDuobaoHistory failer',
                   'userId=', userId,
                   'duobaoId=', duobaoId,
                   'pageId=', pageId,
                   'ec=', ec,
                   'info=', info)

    return {'historyList': historyList}

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def duobaoRecord(userId, pageId):
    '''
    一元夺宝查询我的夺宝记录
    '''
    from poker.entity.biz.exceptions import TYBizException
    recordList = []
    ec = 0
    info = '查询成功'
    totalLength = 0
    try:
        from hall.entity.hall1yuanduobao import duobaoMyRecord
        recordList, totalLength = duobaoMyRecord(userId, pageId)
    except TYBizException, e:
        ec = e.errorCode
        info = e.message

        ftlog.info('doDuobaoMyRecord failer',
                   'userId=', userId,
                   'pageId=', pageId,
                   'ec=', ec,
                   'info=', info)

    return {'ec': ec, 'info': info, 'recordList': recordList, 'totalLength': totalLength}

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def duobaoRewardRecord(userId):
    '''
    一元夺宝查询我的领奖记录
    '''
    from hall.entity.hall1yuanduobao import duobaoRewardRecord
    rewardRecordList = duobaoRewardRecord(userId)

    return {'rewardRecordList': rewardRecordList, 'userId': userId}