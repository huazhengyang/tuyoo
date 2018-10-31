# -*- coding:utf-8 -*-
'''
Created on 2018年5月13日

@author: wangyonghui
'''
import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from poker.util import timestamp as pktimestamp, strutil

# ****************************************
#           用户红包券明细来源常量
# ****************************************
from hall.entity.usercoupon.events import UserCouponReceiveEvent
from poker.entity.dao import sessiondata, daobase, userchip

USER_COUPON_SOURCE_SEGMENT_TASK = 'segment.task'
USER_COUPON_SOURCE_SEGMENT_REWARDS_POOL= 'segment.rewards.pool'
USER_COUPON_SOURCE_MATCH_ARENA = 'match.arena'
USER_COUPON_SOURCE_SEGMENT_WINSTREAK_TASK = 'segment.task.winstreak'
USER_COUPON_TABLE_TBBOX = 'table.tbbox'
USER_COUPON_SHARE3 = 'share3'
USER_COUPON_SHARE_CHARM = 'share.charm'
USER_COUPON_WX_FOLLOW = 'wx.follow'
USER_COUPON_INVITE = 'invite'
USER_AUTH_SHARE = 'auth'



USER_COUPON_NAME_MAP = {
    USER_COUPON_SOURCE_SEGMENT_TASK: '任务奖励',
    USER_COUPON_SOURCE_SEGMENT_REWARDS_POOL: '奖池瓜分',
    USER_COUPON_SOURCE_MATCH_ARENA: '红包赛',
    USER_COUPON_SOURCE_SEGMENT_WINSTREAK_TASK: '闯关连胜',
    USER_COUPON_TABLE_TBBOX: '金币桌返奖',
    USER_COUPON_SHARE3: '新手礼红包',
    USER_COUPON_SHARE_CHARM: '分享排行',
    USER_COUPON_WX_FOLLOW: '收藏有礼',
    USER_COUPON_INVITE: '福利来了',
    USER_AUTH_SHARE: '授权红包'
}

USER_COUPON_NAME_OTHER = '其它'


def getSourceName(source):
    return USER_COUPON_NAME_MAP.get(source, USER_COUPON_NAME_OTHER)


MAX_RECEIVED_ITEMS = 50



# ****************************************
#           用户红包券明细数据存储
# ****************************************
class ReceivedItem(object):
    def __init__(self, count=0, source=None, timestamp=0):
        # 数量
        self.count = count
        # 来源
        self.source = source
        # 领取时间
        self.timestamp = timestamp

    def toDict(self):
        return {
            'count': self.count,
            'source': self.source,
            'time': self.timestamp
        }

    def fromDict(self, d):
        self.count = d['count']
        self.source = d['source']
        self.timestamp = d['time']
        return self


class UserStatus(object):
    def __init__(self, userId, couponCount):
        self.userId = userId
        # 用户奖券数量
        self.couponCount = couponCount
        # 收到的红包券
        self.receivedItems = []

    def addReceivedItem(self, count, source, timestamp):
        item = ReceivedItem(count, source, timestamp)
        self.receivedItems.append(item)
        self.trimReceivedItems()
        return item

    def trimReceivedItems(self):
        trimCount = len(self.receivedItems) - MAX_RECEIVED_ITEMS
        trimCount = max(0, trimCount)
        if trimCount > 0:
            self.receivedItems = self.receivedItems[trimCount:]


def saveUserStatus(status):
    ritems = []
    for ritem in status.receivedItems:
        ritems.append({'count': ritem.count, 'source': ritem.source, 'time': ritem.timestamp})

    jstr = strutil.dumps(ritems)
    daobase.executeUserCmd(status.userId, 'hset', 'couponDetails:%s:%s' % (HALL_GAMEID, status.userId), 'status', jstr)
    ftlog.info('user_coupon_details.saveUserStatus',
               'userId=', status.userId,
               'jstr=', jstr)


def loadUserStatus(userId, clientId):
    coupon = userchip.getCoupon(userId)
    jstr = daobase.executeUserCmd(userId, 'hget', 'couponDetails:%s:%s' % (HALL_GAMEID, userId), 'status')
    ftlog.info('user_coupon_details.loadUserStatus',
               'userId=', userId,
               'clientId=', clientId,
               'jstr=', jstr)
    try:
        d = strutil.loads(jstr or '[]')
        status = UserStatus(userId, coupon)
        for ritem in d:
            status.addReceivedItem(ritem['count'], ritem['source'], ritem['time'])
        return status
    except:
        ftlog.warn('user_coupon_details.loadUserStatus BadData',
                   'userId=', userId,
                   'clientId=', clientId,
                   'jstr=', jstr)


# ****************************************
#           用户红包券明细事件监听处理
# ****************************************
def _onUserCouponReceiveEvent(evt):
    if ftlog.is_debug():
        ftlog.debug('user_coupon_details._onUserCouponReceiveEvent userId=', evt.userId,
                    'gameId=', evt.gameId,
                    'source=', evt.source,
                    'sourceDesc=', getSourceName(evt.source))
    if evt.count > 0:
        clientId = sessiondata.getClientId(evt.userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        status = loadUserStatus(evt.userId, clientId)
        status.addReceivedItem(evt.count, evt.source, timestamp)
        saveUserStatus(status)


def _initialize():
    from hall.game import TGHall
    TGHall.getEventBus().subscribe(UserCouponReceiveEvent, _onUserCouponReceiveEvent)
    ftlog.info('user_coupon_details._initialized ok')

