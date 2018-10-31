# -*- coding=utf-8
'''
Created on 2015年6月12日

@author: zhaojiangang
'''

import copy

from biz import mock
from biz.mock import patch
from biz.test_base import TestMockContext, UserDBTest, TYEventBusSample
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify
from poker.entity.biz.item.dao import TYItemDataDao
from poker.entity.biz.item.exceptions import TYAssetNotEnoughException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.ranking.dao import TYRankingUserScoreInfoDao, TYRankingDao
from poker.entity.biz.store.dao import TYOrderDao
from poker.entity.biz.task.dao import TYTaskDataDao
import poker.util.timestamp as pktimestamp


class TYItemDataDaoMem(TYItemDataDao):
    def __init__(self):
        # key=userId, value=map<itemId, itemdata>
        self._userItemMap = {}
        self._nextItemId = 1
        
    def clear(self):
        self._userItemMap = {}
        self._nextItemId = 1
        
    def loadAll(self, userId):
        '''
        加载用户所有道具
        @param userId: 哪个用户
        @return: list<(itemId, ItemData)>
        '''
        print 'loadAll userId=', userId, 'self=', id(self)
        itemMap = self._userItemMap.get(userId)
        return [(itemId, itemData) for itemId, itemData in itemMap.iteritems()] if itemMap else []
    
    def saveItem(self, userId, itemId, itemData):
        '''
        保存道具
        @param userId: 哪个用户
        @param itemId: 道具ID
        @param itemData: bytes 
        '''
        print 'saveItem userId=', userId, 'itemId=', itemId
        itemMap = self._userItemMap.get(userId)
        if not itemMap:
            itemMap = {}
            self._userItemMap[userId] = itemMap
        itemMap[itemId] = itemData
    
    def removeItem(self, userId, itemId):
        '''
        删除一个道具
        @param userId: 哪个用户
        @param itemId: 道具ID
        '''
        itemMap = self._userItemMap.get(userId)
        if itemMap and itemId in itemMap:
            del itemMap[itemId]
    
    def nextItemId(self):
        '''
        获取下一个道具ID
        @param userId: 哪个用户
        @return: itemId
        '''
        ret = self._nextItemId
        self._nextItemId += 1
        return ret
    
class TYOrderDaoMem(TYOrderDao):
    def __init__(self):
        self.orderMap = {}
    
    def clear(self):
        self.orderMap = {}
        
    def addOrder(self, order):
        '''
        增加order
        '''
        found = self.orderMap.get(order.orderId)
        if found:
            raise ValueError('orderId already exists: %s' % (order.orderId))
        self.orderMap[order.orderId] = order
    
    def findOrder(self, orderId):
        return self.orderMap.get(orderId)
    
    def saveOrder(self, order):
        self.orderMap[order.orderId] = order
        
    def loadOrder(self, orderId):
        '''
        加载order
        '''
        return self.findOrder(orderId)
    
    def updateOrder(self, order, expectState):
        '''
        更新order
        '''
        found = self.findOrder(order.orderId)
        if not found:
            raise ValueError('order not exists')
        self.saveOrder(order)
       
class TYRankingUserScoreInfoDaoMem(TYRankingUserScoreInfoDao):
    def __init__(self):
        # key=userId, 
        self._userDB = UserDBTest()
        
    def clear(self):
        return self._userDB.clear()
    
    def loadScoreInfo(self, rankingId, userId):
        '''
        获取用户的scoreInfo
        '''
        field = 'ranking.info:%s' % (rankingId)
        return self._userDB.getAttr(userId, field)
    
    def saveScoreInfo(self, rankingId, userId, scoreInfo):
        '''
        保存用户的scoreInfo
        '''
        field = 'ranking.info:%s' % (rankingId)
        self._userDB.setAttr(userId, field, strutil.cloneData(scoreInfo))

class TYRankingDaoMem(TYRankingDao):
    def __init__(self):
        # key=rankingId, value=statusData
        self._statusMap = {}
        # key=rankingId.issueNumber, value=list<(userId, score)>
        self._rankingListMap = {}
        
    def clear(self):
        self._statusMap = {}
        self._rankingListMap = {}
        
    def loadRankingStatusData(self, rankingId):
        '''
        加载ranking信息
        '''
        return self._statusMap.get(rankingId)
    
    def removeRankingStatus(self, rankingId):
        '''
        删除ranking信息
        '''
        if rankingId in self._statusMap:
            del self._statusMap[rankingId]
    
    def saveRankingStatusData(self, rankingId, data):
        '''
        保存ranking信息
        '''
        self._statusMap[rankingId] = data
    
    def removeRankingList(self, rankingId, issueNumber):
        '''
        删除raking榜单
        '''
        raise NotImplemented()
    
    def setUserScore(self, rankingId, issueNumber, userId, score, totalN):
        '''
        设置用户积分
        @return: rank
        '''
        key = '%s.%s' % (rankingId, issueNumber)
        index = self._findUser(key, userId)
        if index >= 0:
            l = self._rankingListMap[key]
            del l[index]
            l.append((userId, score))
            # 排序
            l.sort(key=lambda x:x[1])
        else:
            l = self._rankingListMap.get(key)
            if l is None:
                l = []
                self._rankingListMap[key] = l
            l.append((userId, score))
            l.sort(key=lambda x:x[1])
        if len(l) > totalN:
            del l[totalN:]
        return self._findUser(key, userId)
    
    def removeUser(self, rankingId, issueNumber, userId):
        '''
        删除用户
        '''
        key = '%s.%s' % (rankingId, issueNumber)
        index = self._findUser(key, userId)
        if index >= 0:
            l = self._rankingListMap[key]
            del l[index]
            return True
        return False
    
    def getUserRankWithScore(self, rankingId, issueNumber, userId):
        '''
        获取用户排名和积分
        @return: (rank, score)
        '''
        key = '%s.%s' % (rankingId, issueNumber)
        index = self._findUser(key, userId)
        if index >= 0:
            return index, self._rankingListMap[key][index][1]
        return -1, 0
    
    def getTopN(self, rankingId, issueNumber, topN):
        '''
        获取topN
        @return: [userId1, score1, userId2, score2,...] 
        '''
        ret = []
        key = '%s.%s' % (rankingId, issueNumber)
        l = self._rankingListMap.get(key)
        if l:
            for userId, score in l:
                ret.append(userId)
                ret.append(score)
        return ret
    
    def _findUser(self, key, userId):
        l = self._rankingListMap.get(key)
        if l:
            for i in xrange(len(l)):
                if l[i][0] == userId:
                    return i 
        return -1
    
class TYTaskDataDaoTest(TYTaskDataDao):
    def __init__(self):
        # key=gameId, value=UserDBTest
        self._gameUserDBMap = {}
        
    def _ensureGameDBExists(self, gameId):
        gameDB = self._gameUserDBMap.get(gameId)
        if not gameDB:
            gameDB = UserDBTest()
            self._gameUserDBMap[gameId] = gameDB
        return gameDB
    
    def clear(self):
        self._gameUserDBMap = {}
        
    def loadAll(self, gameId, userId):
        '''
        加载用户所有任务
        @return: map<kindId, bytes>
        '''
        gameDB = self._ensureGameDBExists(gameId)
        attrlist = gameDB.getAllAttrs(userId)
        ret = []
        if attrlist:
            for i in xrange(len(attrlist)/2):
                ret.append((attrlist[i*2], attrlist[i*2+1]))
        return ret
    
    def saveTask(self, gameId, userId, kindId, taskDataBytes):
        '''
        保存一个用户的task
        @param kindId: kindId
        @param taskDataBytes: bytes
        '''
        gameDB = self._ensureGameDBExists(gameId)
        gameDB.setAttr(userId, kindId, taskDataBytes)
    
    def removeTask(self, gameId, userId, kindId):
        '''
        删除一个用户的task
        @param kindId: kindId
        '''
        gameDB = self._ensureGameDBExists(gameId)
        gameDB.removeAttr(userId, kindId)
    
bieventmap = {
  "ACTIVITY_CONSUME" : 10001,
  "ACTIVITY_EXCHANGE" : 10067,
  "ACTIVITY_FAN_PAI" : 10087,
  "ACTIVITY_REWARD" : 10002,
  "BEAUTYCERT_INSURANCE" : 10003,
  "BEAUTYCERT_RETURN_INSURANCE" : 10044,
  "BEAUTYCERT_REWARDS" : 10045,
  "BENE_SEND" : 10004,
  "BENE_SEND_VIP_EXT" : 10075,
  "BENE_SEND_VIP_EXT_TIMES" : 10076,
  "BIG_WIN_FEE" : 10046,
  "BIND_GAME" : 14003,
  "BIND_USER" : 14002,
  "BUY_IN" : 10055,
  "BUY_PRODUCT" : 10005,
  "COIN_HALL_USER_CREATE" : 15004,
  "COUPON_ADD_ITEM" : 13023,
  "COUPON_BANK_UNKNOW" : 13025,
  "COUPON_BUY_BY_COIN" : 13022,
  "COUPON_DIZHU_ACT_NEWYEAR" : 13037,
  "COUPON_DIZHU_ACT_OLDUSER" : 13035,
  "COUPON_DIZHU_CHRISTMAS" : 13040,
  "COUPON_DIZHU_GAME_WIN" : 13013,
  "COUPON_DIZHU_MONTHER_DAY" : 13039,
  "COUPON_DIZHU_MOONBOX" : 13016,
  "COUPON_DIZHU_NEI_TUI_GUANG" : 13038,
  "COUPON_DIZHU_NEWER_GIFTS" : 13018,
  "COUPON_DIZHU_NEWR_RAFFLE" : 13017,
  "COUPON_DIZHU_NOVICE_REWARD" : 13036,
  "COUPON_DIZHU_PAY" : 13019,
  "COUPON_DIZHU_PAY100" : 13014,
  "COUPON_DIZHU_TURN_TABLE" : 13034,
  "COUPON_DIZHU_UNKNOW" : 13015,
  "COUPON_DOUNIU_ACTIVITY" : 13033,
  "COUPON_DOUNIU_BAOSHI" : 13032,
  "COUPON_DOUNIU_UNKNOW" : 13012,
  "COUPON_HALL_USER_CREATE" : 13011,
  "COUPON_MAJIANG_MATCH" : 13010,
  "COUPON_MAJIANG_TASK" : 13009,
  "COUPON_MEDAL_REWARD" : 13020,
  "COUPON_RAFFLE" : 13021,
  "COUPON_T3CARD_DOUBLE_ELEVEN" : 13028,
  "COUPON_T3CARD_MEDAL" : 13007,
  "COUPON_T3CARD_MONTHCHARGE" : 13006,
  "COUPON_T3CARD_NEWYEAR" : 13027,
  "COUPON_T3CARD_TURNTABLE" : 13026,
  "COUPON_T3CARD_UNKNOW" : 13008,
  "COUPON_T3CARD_XMAS13_5WINS" : 13031,
  "COUPON_T3CARD_XMAS13_CHIPS" : 13029,
  "COUPON_T3CARD_XMAS13_POKER" : 13030,
  "COUPON_T3FLUSH_BOX" : 13046,
  "COUPON_TEST_ADJUST" : 13001,
  "COUPON_TEXAS_ADMIN" : 13003,
  "COUPON_TEXAS_LINER_MATCH" : 13005,
  "COUPON_TEXAS_MATCH_REWARD" : 13004,
  "COUPON_TEXAS_NEW_USER" : 13003,
  "COUPON_TEXAS_PURPLE" : 13002,
  "COUPON_TEXAS_REWARD_CODE" : 13005,
  "COUPON_TEXAS_SNG_MATCH" : 13004,
  "COUPON_TEXAS_TBOX" : 13002,
  "COUPON_USE" : 13024,
  "CREATE_GAME_DATA" : 14001,
  "DATA_FROM_MYSQL_2_REDIS_CHIP" : 10078,
  "DATA_FROM_MYSQL_2_REDIS_COIN" : 15002,
  "DATA_FROM_MYSQL_2_REDIS_COUPON" : 13041,
  "DATA_FROM_MYSQL_2_REDIS_DIAMOND" : 15102,
  "DATA_FROM_REDIS_2_MYSQL_CHIP" : 10082,
  "DATA_FROM_REDIS_2_MYSQL_COIN" : 15003,
  "DATA_FROM_REDIS_2_MYSQL_COUPON" : 13042,
  "DATA_FROM_REDIS_2_MYSQL_DIAMOND" : 15103,
  "DIAMOND_HALL_USER_CREATE" : 15104,
  "DO_BET" : 10058,
  "DTASK_CHANGE" : 10006,
  "DTASK_REWARD" : 10007,
  "DTASK_REWARD_CHIP" : 10089,
  "DTASK_REWARD_COUPON" : 13044,
  "EMOTICON_BOMB_CONSUME" : 10049,
  "EMOTICON_CONSUME" : 10008,
  "EMOTICON_DIAMOND_CONSUME" : 10050,
  "EMOTICON_EGG_CONSUME" : 10047,
  "EMOTICON_FLOWER_CONSUME" : 10048,
  "EXCHANGE_COUPON" : 10009,
  "EXCHANGE_PURPLE_CARD" : 10010,
  "FIREWORK_BASEFEE" : 10064,
  "FIREWORK_BUY" : 10063,
  "FIREWORK_OTHERFEE" : 10065,
  "FIREWORK_PRIZE" : 10066,
  "FIRST_RECHARGE" : 10070,
  "FIRST_RECHARGE_REWARD" : 10086,
  "FRUIT_BETS" : 10042,
  "FRUIT_REWARDS" : 10043,
  "GAME_BANKER_ABDICATE" : 10011,
  "GAME_COMPLAIN_INSURANCE" : 10012,
  "GAME_WINLOSE" : 10013,
  "GAME_WINLOSE_BR" : 10014,
  "GAOBEI_SERVER_FEE" : 10071,
  "GDSS_ADJUST_CHIP" : 10060,
  "GIFT_PAWN_REWARD" : 10053,
  "GIFT_SEND_CONSUME" : 10052,
  "GM_ADJUST" : 3,
  "GM_ADJUST_CHIP" : 10088,
  "GM_ADJUST_COIN" : 15001,
  "GM_ADJUST_COUPON" : 13043,
  "GM_ADJUST_DIAMOND" : 15101,
  "ITEM_USE" : 10015,
  "ITEM_USER_CREATE" : 15201,
  "LED_PUBLIC" : 10016,
  "LOTTERYPOOL_REWARD" : 10017,
  "LOTTERYPOOL_REWARD_BR" : 10072,
  "MATCH_FINISH" : 14010,
  "MATCH_RETURN_FEE" : 10041,
  "MATCH_REWARD" : 10018,
  "MATCH_SIGNIN_FEE" : 10019,
  "MATCH_SIGN_OUT" : 14008,
  "MATCH_SIGN_UP" : 14007,
  "MATCH_START" : 14009,
  "MEDAL2_REWARD" : 10020,
  "MEDAL2_REWARD_CHIP" : 10099,
  "MEDAL2_REWARD_COUPON" : 13045,
  "MEDAL_REWARD" : 10021,
  "MEMBER_DAY_REWARD" : 10022,
  "MEMBER_LOGIN_REWARD" : 10023,
  "MERGE_TO_HALL" : 10024,
  "NSLOGIN_REWARD" : 10025,
  "NSLOGIN_REWARD2" : 10026,
  "PK_FEE" : 10059,
  "PRESENT_MATCH_TICKET" : 10102,
  "RANDOM_LOTTERY_PRIZE" : 10098,
  "RANK_REWARD" : 10103,
  "REFERRER_REWARD" : 10038,
  "RETURN_TABLECHIP" : 10061,
  "ROOM_BAICAISHEN" : 10054,
  "ROOM_GAME_FEE" : 10027,
  "SDK_BUY_CALLBACK_FAIL" : 12007,
  "SDK_BUY_CALLBACK_OK" : 12006,
  "SDK_BUY_CLIENT_CANCELED" : 12002,
  "SDK_BUY_CLIENT_FINISHED" : 12001,
  "SDK_BUY_CREATE" : 12000,
  "SDK_BUY_DELIVER_FAIL" : 12009,
  "SDK_BUY_DELIVER_OK" : 12008,
  "SDK_BUY_INTERNAL_ERR" : 12010,
  "SDK_BUY_REQUEST_ERROR" : 12005,
  "SDK_BUY_REQUEST_OK" : 12003,
  "SDK_BUY_REQUEST_RETRY" : 12004,
  "SDK_CREATE_BY_DEVID_FAIL" : 11011,
  "SDK_CREATE_BY_DEVID_SUCC" : 11008,
  "SDK_CREATE_BY_MAIL_FAIL" : 11015,
  "SDK_CREATE_BY_MAIL_SUCC" : 11014,
  "SDK_CREATE_BY_MOBILE_FAIL" : 11013,
  "SDK_CREATE_BY_MOBILE_SUCC" : 11010,
  "SDK_CREATE_BY_SNSID_FAIL" : 11012,
  "SDK_CREATE_BY_SNSID_SUCC" : 11009,
  "SDK_LOGIN_BY_DEVID_FAIL" : 11005,
  "SDK_LOGIN_BY_DEVID_SUCC" : 11001,
  "SDK_LOGIN_BY_MAIL_FAIL" : 11004,
  "SDK_LOGIN_BY_MAIL_SUCC" : 11000,
  "SDK_LOGIN_BY_MOBILE_FAIL" : 11006,
  "SDK_LOGIN_BY_MOBILE_SUCC" : 11002,
  "SDK_LOGIN_BY_SNSID_FAIL" : 11007,
  "SDK_LOGIN_BY_SNSID_SUCC" : 11003,
  "SLOT_MACHINE" : 10062,
  "SYSTEM_ADJUST_ROBOT_CHIP" : 10028,
  "SYSTEM_REPAIR" : 1,
  "TABLE_CARD" : 14005,
  "TABLE_SITDOWN_SET_TCHIP" : 10029,
  "TABLE_STANDUP_TCHIP_TO_CHIP" : 10030,
  "TABLE_START" : 14004,
  "TABLE_SUPPLIES" : 10031,
  "TABLE_TCHIP_TO_CHIP" : 10032,
  "TABLE_WIN" : 14006,
  "TASK_MASTER_SCORE_UP_LEVEL_REWARD" : 10033,
  "TASK_ONLINE_REWARD" : 10034,
  "TASK_OPEN_TBOX_REWARD" : 10035,
  "TASK_REWARD" : 10036,
  "TEST_ADJUST" : 2,
  "TEXAS_FLIP_CARD_GAME_IN" : 10068,
  "TEXAS_FLIP_CARD_GAME_OUT" : 10069,
  "TE_HUI_LI_BAO" : 10090,
  "TUTORIAL_AWARD" : 10101,
  "UNKNOWN" : 0,
  "USER_CREATE" : 10051,
  "USER_STARTUP" : 10037,
  "VIP_GIFT_REWARD" : 10074,
  "VIP_GOT_ASSISTANCE" : 10077,
  "VIP_REWARD" : 10073,
  "WINNER_TAX" : 10100,
  "XIJIN_IN" : 10057,
  "XIJIN_OUT" : 10056,
  "REPAIRE_ITEM":10057,
  "ASSEMBLE_ITEM":10058,
  "SALE_ITEM":10059
}

class RemoteUserRpcTest(object):
    def consumeAssets(self, gameId, userId, contentItems, eventId, params):
        if ftlog.is_debug():
            ftlog.debug('user_remote.consumeAssets gameId=', gameId,
                       'userId=', userId,
                       'contentItems=', contentItems,
                       'eventId=', eventId,
                       'params=', params)
        try:
            contentItems = self.decodeContentItems(contentItems)
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            assetList = userAssets.consumeContentItemList(gameId, contentItems, True, pktimestamp.getCurrentTimestamp(), eventId, 0)
            datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
            return None, 0
        except TYAssetNotEnoughException, e:
            ftlog.error()
            return e.assetKind.kindId, e.required - e.actually
        
    def addAssets(self, gameId, userId, contentItems, eventId, params):
        if ftlog.is_debug():
            ftlog.debug('user_remote.addAssets gameId=', gameId,
                       'userId=', userId,
                       'contentItems=', contentItems,
                       'eventId=', eventId,
                       'params=', params)
        try:
            contentItems = self.decodeContentItems(contentItems)
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            #def sendContentItemList(self, gameId, contentItemList, count, ignoreUnknown, timestamp, eventId, **kwargs):
            # TODO set eventId
            assetList = userAssets.sendContentItemList(gameId, contentItems, 1, True, pktimestamp.getCurrentTimestamp(), 0)
            datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
            return True
        except:
            ftlog.error()
            return False
    
    def queryUserWeardItemKindIds(self, gameId, userId):
        from hall.servers.util.decroation_handler import DecroationHelper
        return DecroationHelper.queryUserWeardItemKindIds(gameId, userId)
    
    def presentItemByUnitsCount(self, gameId, userId, fromUserId, kindId, count):
        itemKind = hallitem.itemSystem.findItemKind(kindId)
        if not itemKind:
            return False
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        userBag.addItemUnitsByKind(gameId, itemKind, count,
                                   pktimestamp.getCurrentTimestamp(), fromUserId,
                                   'ITEM_PRESENT', fromUserId)
        return True
    
    def presentItem(self, gameId, userId, fromUserId, itemDataDict):
        kindId = itemDataDict['itemKindId']
        itemKind = hallitem.itemSystem.findItemKind(kindId)
        if not itemKind:
            return False
        itemData = itemKind.newItemData()
        itemData = itemData.fromDict(itemDataDict)
        item = hallitem.itemSystem.newItemFromItemData(itemData)
        if not item:
            return False
        item.fromUserId = fromUserId
        item.giftHandCount += 1
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        userBag.addItem(gameId, item, 'ITEM_PRESENT', fromUserId)
        return True

class ExchangeTester(object):
    def __init__(self):
        self._exchangeId = 0
        self._userDB = UserDBTest()
    
    def clear(self):
        self._userDB.clear()
    def makeExchangeId(self):
        ret = self._exchangeId
        self._exchangeId += 1
        return ret
    
    def saveRecordData(self, userId, exchangeId, recordData):
        self._userDB.setAttr(userId, exchangeId, recordData)
    
    def loadRecordData(self, userId, exchangeId):
        return self._userDB.getAttr(userId, exchangeId)
    
    def loadRecordDatas(self, userId, exchangeId):
        return self._userDB.getAllAttrs(userId)
    
# def _makeExchangeId():
#     ct = datetime.now()
#     exchangeId = 'EO%s%s' % (ct.strftime('%Y%m%d%H%M%S'), exchangeId)
#     return exchangeId
#     
# def _buildExchangeKey(userId):
#     return 'eo:9999:%s' % (userId)
# 
# def _saveRecordData(userId, exchangeId, recordData):
#     daobase.executeUserCmd(userId, 'hset', _buildExchangeKey(userId), exchangeId, recordData)
# 
# def _loadRecordData(userId, exchangeId):
#     return daobase.executeUserCmd(userId, 'hget', _buildExchangeKey(userId, exchangeId))
# 
# def _loadRecordDatas(userId):
#     return daobase.executeUserCmd(userId, 'hgetall', _buildExchangeKey(userId))

class HallTestMockContext(TestMockContext):
    
    def __init__(self):
        super(HallTestMockContext, self).__init__()
        self.orderDao = TYOrderDaoMem()
        self.itemDataDao = TYItemDataDaoMem()
        self.scoreInfoDao = TYRankingUserScoreInfoDaoMem()
        self.rankingDao = TYRankingDaoMem()
        self.eventBus = TYEventBusSample()
        self.taskDataDao = TYTaskDataDaoTest()
        self.exchangeTest = ExchangeTester()
        self.userRemote = RemoteUserRpcTest()
        self.itemDataDaoPatcher = patch('hall.entity.hallitem.TYItemDataDaoImpl', self._makeItemDataDao)
        self.orderDaoPatcher = patch('hall.entity.hallstore.TYOrderDaoImpl', self._makeOrderDao)
        self.scoreInfoDaoPatcher = patch('hall.entity.hallranking.TYRankingUserScoreInfoDaoImpl', self._makeScoreInfoDao)
        self.rankingDaoPatcher = patch('hall.entity.hallranking.TYRankingDaoImpl', self._makeRankingDao)
        self.TGHallEventBusPatcher = patch('hall.game.TGHall.getEventBus', self._getEventBus)
        self.taskDaoPatacher = patch('hall.entity.halltask.TYTaskDataDaoImpl', self._makeTaskDataDao)
        self.userRemotePatcher = mock._patch_multiple('hall.servers.util.rpc.user_remote',
                                                      consumeAssets=self.userRemote.consumeAssets,
                                                      addAssets=self.userRemote.addAssets,
                                                      queryUserWeardItemKindIds=self.userRemote.queryUserWeardItemKindIds,
                                                      presentItemByUnitsCount=self.userRemote.presentItemByUnitsCount,
                                                      presentItem=self.userRemote.presentItem)
        
        self.exchangePatcher = mock._patch_multiple('hall.entity.hallexchange',
                                                    _makeExchangeId=self.exchangeTest.makeExchangeId,
                                                    _saveRecordData=self.exchangeTest.saveRecordData,
                                                    _loadRecordData=self.exchangeTest.loadRecordData,
                                                    _loadRecordDatas=self.exchangeTest.loadRecordDatas)
        
        #gdatas['tygame.instance.ids'] = [9999]
        #gdatas['tygame.instance.dict'] = {9999:TGHall}
        
    def _startMockImpl(self):
        self.configure.setJson('poker:map.bieventid', bieventmap, None)
        self.itemDataDaoPatcher.start()
        self.orderDaoPatcher.start()
        self.scoreInfoDaoPatcher.start()
        self.rankingDaoPatcher.start()
        self.TGHallEventBusPatcher.start()
        self.taskDaoPatacher.start()
        self.userRemotePatcher.start()
        self.exchangePatcher.start()
        
    def _stopMockImpl(self):
        self.itemDataDaoPatcher.stop()
        self.orderDaoPatcher.stop()
        self.scoreInfoDaoPatcher.stop()
        self.rankingDaoPatcher.stop()
        self.TGHallEventBusPatcher.stop()
        self.taskDaoPatacher.stop()
        self.userRemotePatcher.stop()
        self.exchangePatcher.stop()
        
        self.itemDataDao.clear()
        self.orderDao.clear()
        self.scoreInfoDao.clear()
        self.rankingDao.clear()
        self.taskDataDao.clear()
        self.exchangeTest.clear()
        
    def _getEventBus(self):
        return self.eventBus
    
    def _makeOrderDao(self):
        return self.orderDao
    def _makeItemDataDao(self):
        return self.itemDataDao
    def _makeScoreInfoDao(self):
        return self.scoreInfoDao
    def _makeRankingDao(self):
        return self.rankingDao
    def _makeTaskDataDao(self):
        return self.taskDataDao
    
    
    