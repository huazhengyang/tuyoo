# -*- coding=utf-8
'''
Created on 2015年9月7日

@author: zhaojiangang
'''
from datetime import datetime
import json
import time

from dateutil.relativedelta import relativedelta

import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.item.item import TYAssetKind, TYItemAction, \
    TYAssetKindRegister, TYItemActionRegister
from poker.entity.dao import userdata, gamedata
from poker.util import strutil
from hall.entity import datachangenotify


class SubMemberStatus(object):
    def __init__(self, isSub, subDT=None, deliveryDT=None, unsubDesc=None, expiresDT=None):
        self.isSub = isSub
        self.subDT = subDT
        self.deliveryDT = deliveryDT
        self.unsubDesc = unsubDesc
        self.expiresDT = expiresDT
    
    @classmethod
    def calcSubExpiresDT(self, subDT, nowDT):
        '''
        计算nowDT所在订阅周期的到期时间
        @param subDT: 订阅时间
        @param param: 当前时间
        @return: 到期时间
        '''
        years = nowDT.year - subDT.year
        months = nowDT.month - subDT.month
        ret = subDT + relativedelta(years=years, months=months)
        if nowDT.date() >= ret.date():
            ret = subDT + relativedelta(years=years, months=months+1)
        return ret.replace(hour=0, minute=0, second=0, microsecond=0)

    def isSubExpires(self, nowDT):
        return not self.expiresDT or nowDT >= self.expiresDT
    
    def calcDeliveryDays(self, nowDT):
        '''
        计算需要发几天货
        '''
        if self.subDT and self.expiresDT:
            # 本次订阅周期到期时间
            if (not self.deliveryDT
                or self.expiresDT > self.calcSubExpiresDT(self.subDT, self.deliveryDT)):
                return max(0, (self.expiresDT.date() - nowDT.date()).days)
        return 0
    
def _decodeDT(timestamp):
    return datetime.fromtimestamp(timestamp) if timestamp >= 0 else None

def _loadSubMemberStatus(userId):
    try:
        d = gamedata.getGameAttrJson(userId, HALL_GAMEID, 'submember', {})
        subDT = _decodeDT(d.get('subTime', -1))
        deliveryDT = _decodeDT(d.get('deliveryTime', -1))
        expiresDT = _decodeDT(d.get('expiresTime', -1))
        return SubMemberStatus(False, subDT, deliveryDT, None, expiresDT)
    except:
        ftlog.error()
        return SubMemberStatus(False, None, None, None, None)
        
def _adjustExpiresDT(status, nowDT):
    if status.subDT:
        # 本次订阅周期到期时间
        expiresDT = SubMemberStatus.calcSubExpiresDT(status.subDT, nowDT)
        if expiresDT != status.expiresDT:
            status.expiresDT = expiresDT
            return True
    return False
    
def loadSubMemberStatus(userId):
    isYouyifuVipUser, youyifuVipMsg = userdata.getAttrs(userId, ['isYouyifuVipUser', 'youyifuVipMsg'])
    isSub = isYouyifuVipUser == 1
    if ftlog.is_debug():
        ftlog.debug('hallsubmember.loadSubMemberStatus userId=', userId,
                    'isYouyifuVipUser=', (isYouyifuVipUser, type(isYouyifuVipUser)),
                    'youyifuVipMsg=', youyifuVipMsg)
    youyifuVipMsg = str(youyifuVipMsg) if youyifuVipMsg is not None else None
    nowDT = datetime.now()
    status = _loadSubMemberStatus(userId)
    status.isSub = isSub
    status.unsubDesc = youyifuVipMsg
    if status.isSub and not status.subDT:
        status.subDT = nowDT
    _adjustExpiresDT(status, nowDT)
    return status

def _saveSubMemberStatus(userId, status):
    d = {}
    if status.subDT:
        d['subTime'] = int(time.mktime(status.subDT.timetuple()))
    if status.deliveryDT:
        d['deliveryTime'] = int(time.mktime(status.deliveryDT.timetuple()))
    if status.expiresDT:
        d['expiresTime'] = int(time.mktime(status.expiresDT.timetuple()))
    jstr = json.dumps(d)
    gamedata.setGameAttr(userId, HALL_GAMEID, 'submember', jstr)
    
def checkSubMember(gameId, userId, timestamp, eventId, intEventParam, userAssets=None):
    status = loadSubMemberStatus(userId)
    _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam, userAssets)
    return status

def subscribeMember(gameId, userId, timestamp, eventId, intEventParam,
                    roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    status = loadSubMemberStatus(userId)
    deliveryDays = _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam,
                                   roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)
    if deliveryDays > 0:
        datachangenotify.sendDataChangeNotify(gameId, userId, ['promotion_loc'])
    return status

def unsubscribeMember(gameId, userId, isTempVipUser, timestamp, eventId, intEventParam):
    from hall.entity import hallitem
    status = loadSubMemberStatus(userId)
    _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam)
    if status.subDT:
        subDT = status.subDT
        nowDT = datetime.fromtimestamp(timestamp)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        balance = userAssets.balance(gameId, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID, timestamp)
        removeDays = 0
        if isTempVipUser:
            # 用户首次购买72小时之内如果退订则扣除剩余会员天数
            removeDays = max(0, (status.expiresDT.date() - nowDT.date()).days)
            status.deliveryDT = None
            status.subDT = None
            status.expiresDT = None
#         # 退订会员权益不消失
#         else:
#             # 根据平台中心建议新增：用户退订后会员有效期最长维持到当月最后一天
#             limitDT = datetime.fromtimestamp(pktimestamp.getDeltaMonthStartTimestamp(timestamp, 1))
#             # 最多剩余多少天
#             maxKeep = max(0, (limitDT.date() - nowDT.date()).days)
#             status.subDT = None
#             status.deliveryDT = None
#             status.expiresDT = (nowDT + timedelta(days=maxKeep)).replace(hour=0, minute=0, second=0, microsecond=0)
#             removeDays = max(0, balance - maxKeep)
        
        _saveSubMemberStatus(userId, status)
        removeDays = min(balance, removeDays)
        
        if removeDays > 0:
            changed = []
            _assetKind, _consumeCount, final = userAssets.consumeAsset(gameId, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID,
                                                                       removeDays, timestamp, eventId, intEventParam)
            if final <= 0:
                changed.append('promotion_loc')
            changed.append('item')
            datachangenotify.sendDataChangeNotify(gameId, userId, changed)
        ftlog.info('hallsubmember.unsubscribeMember gameId=', gameId,
                   'userId=', userId,
                   'isTempVipUser=', isTempVipUser,
                   'isSub=', status.isSub,
                   'unsubDesc=', status.unsubDesc,
                   'expiresDT=', status.expiresDT.strftime('%Y-%m-%d %H:%M:%S') if status.expiresDT else None,
                   'eventId=', eventId,
                   'intEventParam=', intEventParam,
                   'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                   'subTime=', subDT.strftime('%Y-%m-%d %H:%M:%S') if subDT else None,
                   'balance=', balance,
                   'removeDays=', removeDays)
        
def _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam, userAssets=None,
                    roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    from hall.entity import hallitem
    nowDT = datetime.fromtimestamp(timestamp)
    prevDeliveryDT = status.deliveryDT
    deliveryDays = 0
    if status.isSub:
        deliveryDays = status.calcDeliveryDays(nowDT)
        if deliveryDays > 0:
            status.deliveryDT = nowDT
            _saveSubMemberStatus(userId, status)
            if not userAssets:
                userAssets = hallitem.itemSystem.loadUserAssets(userId)
            userAssets.addAsset(gameId, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID,
                                deliveryDays, timestamp, eventId, intEventParam, param01=param01, param02=param02)
        
    ftlog.debug('hallsubmember._checkSubMember gameId=', gameId,
               'userId=', userId,
               'isSub=', status.isSub,
               'unsubDesc=', status.unsubDesc,
               'deliveryDays=', deliveryDays,
               'expiresDT=', status.expiresDT.strftime('%Y-%m-%d %H:%M:%S') if status.expiresDT else None,
               'eventId=', eventId,
               'intEventParam=', intEventParam,
               'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
               'subTime=', status.subDT.strftime('%Y-%m-%d %H:%M:%S') if status.subDT else None,
               'prevDeliveryTime=', prevDeliveryDT.strftime('%Y-%m-%d %H:%M:%S') if prevDeliveryDT else None)
    return deliveryDays

class TYAssetKindSubMember(TYAssetKind):
    TYPE_ID = 'common.subMember'
    def __init__(self):
        super(TYAssetKindSubMember, self).__init__()
        
    def buildContentForDelivery(self, count):
        return self.displayName
    
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        status = subscribeMember(gameId, userAssets.userId, timestamp, eventId, intEventParam,
                                 roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)
        return 1 if status.isSub else 0
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        return 0, self.balance(userAssets, timestamp)
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        return 0, self.balance(userAssets, timestamp)
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        status = loadSubMemberStatus(userAssets.userId)
        return 1 if status.isSub else 0
    
class TYItemActionSubMemberInfo(TYItemAction):
    TYPE_ID = 'common.subMemberInfo'
    def __init__(self):
        super(TYItemActionSubMemberInfo, self).__init__()
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        status = loadSubMemberStatus(userBag.userId)
        return status.isSub
    
    def getInputParams(self, gameId, userBag, item, timestamp):
        ret = strutil.cloneData(self._inputParams)
        desc = ret.get('desc', '')
        status = loadSubMemberStatus(userBag.userId)
        unsubDesc = status.unsubDesc or ''
        ret['desc'] = strutil.replaceParams(desc, {'unsubDesc':unsubDesc})
        return ret
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        pass
        
    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        if not self._inputParams:
            self._inputParams = {
                'type':'detail',
                'desc':''
            }
    
def _registerClasses():
    ftlog.debug('hallsubmember._registerClasses')
    TYAssetKindRegister.registerClass(TYAssetKindSubMember.TYPE_ID, TYAssetKindSubMember)
    TYItemActionRegister.registerClass(TYItemActionSubMemberInfo.TYPE_ID, TYItemActionSubMemberInfo)
    
if '__main__' == __name__:
    testcases = [
        # subDT, deliveryDT, nowDT, expiresDT, deliveryDays
        (datetime.strptime('2000-01-29', '%Y-%m-%d'),
         datetime.strptime('2000-01-29', '%Y-%m-%d'),
         datetime.strptime('2000-02-28', '%Y-%m-%d'),
         datetime.strptime('2000-02-29', '%Y-%m-%d'),
         0),
        
        (datetime.strptime('2000-01-29', '%Y-%m-%d'),
         datetime.strptime('2000-01-28', '%Y-%m-%d'),
         datetime.strptime('2000-02-28', '%Y-%m-%d'),
         datetime.strptime('2000-02-29', '%Y-%m-%d'),
         1),
         
        (datetime.strptime('2001-02-28', '%Y-%m-%d'),
         datetime.strptime('2001-02-27', '%Y-%m-%d'),
         datetime.strptime('2001-02-28', '%Y-%m-%d'),
         datetime.strptime('2001-03-28', '%Y-%m-%d'),
         27+1),
#                  
#         (datetime.strptime('2000-01-29', '%Y-%m-%d'),
#          datetime.strptime('2000-02-29', '%Y-%m-%d'),
#          datetime.strptime('2000-03-29', '%Y-%m-%d'),
#          28+1),
#                  
#         (datetime.strptime('2000-02-29', '%Y-%m-%d'),
#          datetime.strptime('2001-02-28', '%Y-%m-%d'),
#          datetime.strptime('2001-03-29', '%Y-%m-%d'),
#          28+1),
#                  
#         (datetime.strptime('2000-02-29', '%Y-%m-%d'),
#          datetime.strptime('2001-02-28', '%Y-%m-%d'),
#          datetime.strptime('2001-03-29', '%Y-%m-%d'),
#          28+1),
#                  
#         (datetime.strptime('2000-03-29', '%Y-%m-%d'),
#          datetime.strptime('2001-03-29', '%Y-%m-%d'),
#          datetime.strptime('2001-04-29', '%Y-%m-%d'),
#          28+3),
#                  
#         (datetime.strptime('2000-04-29', '%Y-%m-%d'),
#          datetime.strptime('2001-05-30', '%Y-%m-%d'),
#          datetime.strptime('2001-06-29', '%Y-%m-%d'),
#          28+2),
    ]
    for subDT, deliveryDT, nowDT, expectExpiresDT, expectNDays in testcases:
        status = SubMemberStatus(True, subDT, deliveryDT, '')
        nDays, expriesDT = status.calcDeliveryDays(nowDT)
        print (expectNDays, expectExpiresDT.date().strftime('%Y-%m-%d')), (nDays, expriesDT.date().strftime('%Y-%m-%d'))
        assert(expriesDT == expectExpiresDT and nDays == expectNDays)
    
    
