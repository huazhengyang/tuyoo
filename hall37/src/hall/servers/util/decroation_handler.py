# -*- coding=utf-8
'''
Created on 2015年7月3日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from hall.entity import hallitem, hallvip
from hall.entity.hallitem import TYDecroationItem, TYDecroationItemKind
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
import poker.util.timestamp as pktimestamp
from hall.servers.util.rpc import user_remote
from freetime.util.cache import lfu_alive_cache

@markCmdActionHandler
class DecroationHelper(object):
    @classmethod
    def encodeDecroationItemKind(cls, itemKind):
        assert(isinstance(itemKind, TYDecroationItemKind))
        ret = {
            'id':itemKind.kindId,
        }
        if itemKind.localRes:
            ret['localRes'] = itemKind.localRes
        if itemKind.remoteRes:
            ret['remoteRes'] = itemKind.remoteRes
        if itemKind.pos:
            ret['pos'] = itemKind.pos
        return ret
    
    @classmethod
    def encodeDecroationItemKindList(cls, gameId, userId, itemKindList):
        ret = []
        for itemKind in itemKindList:
            if isinstance(itemKind, TYDecroationItemKind):
                ret.append(cls.encodeDecroationItemKind(itemKind))
        return ret
    
    @classmethod
    def makeDecoroationConfigResponse(cls, gameId, userId):
        itemKindList = hallitem.itemSystem.getAllItemKindByType(TYDecroationItemKind)
        mo = MsgPack()
        mo.setCmd('decoration')
        mo.setResult('action', 'config')
        mo.setResult('decroations', cls.encodeDecroationItemKindList(gameId, userId, itemKindList))
        return mo
    
    @classmethod
    def queryUserWeardItemKindIds(cls, gameId, userId):
        return _queryUserWeardItemKindIds(userId)
        
    @classmethod
    def makeDecroationQueryResponse(cls, gameId, userIds):
        mo = MsgPack()
        mo.setCmd('decoration')
        mo.setResult('action', 'query')
        users = []
        for userId in userIds:
            if isinstance(userId, int) and userId > 0: # 客户端发送的userId是一个dict？确保一下有效值
                itemIds = user_remote.queryUserWeardItemKindIds(gameId, userId)
                users.append({
                    'userId':userId,
                    'itemIds':itemIds
                })
        mo.setResult('users', users)
        return mo
    
    @classmethod
    def makeDecroationQueryResponseV3_7(cls, gameId, userId):
        mo = MsgPack()
        mo.setCmd('decoration')
        mo.setResult('action', 'query')
        mo.setResult('userId', userId)
        mo.setResult('itemIds', cls.queryUserWeardItemKindIds(gameId, userId))
        return mo
    
@markCmdActionHandler
class DecroationTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        pass
    
    def _check_param_users(self, msg, key, params):
        users = msg.getParam(key)
        if isinstance(users, list) :
            return None, users
        return 'ERROR of users !' + str(users), None
    
    @markCmdActionMethod(cmd='decoration', action="config", clientIdVer=0)
    def doDecroationConfig(self, gameId, userId):
        mo = DecroationHelper.makeDecoroationConfigResponse(gameId, userId)
        router.sendToUser(mo, userId)
    
    @markCmdActionMethod(cmd='decoration', action="query", lockParamName = '', clientIdVer=0)
    def doDecroationQuery(self, gameId, userId, users):
        if len(users) <= 0:
            users.append(userId)
        mo = DecroationHelper.makeDecroationQueryResponse(gameId, users)
        router.sendToUser(mo, userId)
    
#     @markCmdActionMethod(cmd='decoration', action="query", clientIdVer=3.7)
#     def doDecroationQueryV3_7(self, gameId, userId):
#         mo = DecroationHelper.makeDecroationQueryResponseV3_7(gameId, userId)
#         router.sendToUser(mo, userId)

@lfu_alive_cache(maxsize=300, cache_key_args_index=0, alive_second=60)
def _queryUserWeardItemKindIds(userId):
    # 此方法仅为A用户的界面显示B的信息而进行的查询，查询比较频繁，
    # 但是，不要求精确，因此限定进行缓存，60秒内查到的结果完全一致
    wearedItemKindIdList = []
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    decroationItemList = userBag.getAllTypeItem(TYDecroationItem)
    for decroationItem in decroationItemList:
        if decroationItem.isWore:
            wearedItemKindIdList.append(decroationItem.itemKind.kindId)
    
    # 增加VIP增值位
    userVip = hallvip.userVipSystem.getUserVip(userId)
    if userVip and userVip.vipLevel.level > 0:
        itemId = userVip.vipLevel.level - 1 + hallitem.ITEM_VIP_LABEL_1
        wearedItemKindIdList.append(itemId)
        
    # 增加会员框道具
    remainDays, _ = hallitem.getMemberInfo(userId, pktimestamp.getCurrentTimestamp())
    if remainDays > 0:
        wearedItemKindIdList.append(hallitem.ITEM_MEMBER_BORDER_SILVER_KIND_ID)
    return wearedItemKindIdList