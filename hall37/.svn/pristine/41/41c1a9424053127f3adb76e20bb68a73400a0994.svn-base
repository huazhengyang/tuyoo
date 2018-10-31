# -*- coding=utf-8
'''
Created on 2015年8月4日

@author: zhaojiangang
'''
import json

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from freetime.util.cache import lfu_alive_cache
from hall.entity import hallstore, hallconf, datachangenotify, hallstocklimit, neituiguang
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from hall.servers.util.rpc import neituiguang_remote, hall_yyb_gifts_remote
from poker.entity.biz.store.exceptions import TYStoreException
from poker.entity.dao import onlinedata, userdata, daobase, gamedata
from poker.protocol import runhttp, router
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from hall.servers.util.rpc import user_remote
from poker.servers.conn.rpc import onlines
from poker.entity.configure import configure
from hall.entity.hall_red_envelope.hall_red_envelope import TYRedEnvelopeMgr
import poker.util.timestamp as pktimestamp
from poker.util import strutil
from hall.servers.util.rpc import exchange_remote
from hall.servers.util.rpc import hall_exmall_remote
from poker.entity.biz.exceptions import TYBizException

_USE_FUTURE = 1

@markHttpHandler
class HttpGameHandler(BaseHttpMsgChecker):
    def _check_param_exchangeId(self, key, params):
        value = runhttp.getParamStr(key)
        if not value:
            return 'param exchangeId error', None
        return None, value

    def _check_param_result(self, key, params):
        value = runhttp.getParamInt(key, -1)
        if value < 0:
            return 'param result error', None
        return None, value

    def _check_param_isTempVipUser(self, key, params):
        value = runhttp.getParamInt(key, 0)
        if value not in (0, 1):
            return 'param needRemove error', None
        return None, value

    # 获取参数key，类型string
    def _check_param_key(self, key, params):
        value = runhttp.getParamStr("key", "gamelist2")
        if not value:
            return 'param key error', None
        ftlog.debug('HttpGameHandler._check_param_key key:', value)
        return None, value

    def _check_param_clientIdNum(self, key, params):
        value = runhttp.getParamInt("clientIdNum", 0)
        ftlog.debug('HttpGameHandler._check_param_clientIdNum clientIdNum:', value)
        return None, value

    def _check_param_reason(self, key, params):
        value = runhttp.getParamInt("reason", 0)
        ftlog.debug('HttpGameHandler._check_param_reason reason:', value)
        return None, value

    def _check_param_redEnvelopeId(self, key, params):
        value = runhttp.getParamStr("redEnvelopeId", "")
        ftlog.debug('HttpGameHandler._check_param_redEnvelopeId redEnvelopeId:', value)
        return None, value

    def _check_param_inviter(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value

    def _check_param_actname(self, key, params):
        value = runhttp.getParamStr(key)
        if not value:
            return 'no actname', None
        return None, value

    def _check_param_realGameId(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value

    def _check_param_proviceId(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value

    def _check_param_cityId(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value

    def _check_param_countyId(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value
    
    def _check_param_jdOrderId(self, key, params):
        value = runhttp.getParamStr(key)
        return None, value

    def _check_param_giftKindId(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value
    
    @markHttpMethod(httppath='/v2/game/user/forcelogout')
    def doForceLogOut(self):
        userids = runhttp.getParamStr('userids', '')
        logoutmsg = runhttp.getParamStr('logoutmsg', '')
        userids = userids.split(',')
        ulen = len(userids)
        for x in xrange(ulen):
            userids[x] = int(userids[x])
        ftlog.debug('doForceLogOut', userids)
        for uid in userids:
            userdata.clearUserCache(uid)
            onlines.forceLogOut(uid, logoutmsg)
        mo = MsgPack()
        mo.setCmd('forcelogout')
        mo.setResult('ok', 1)
        return mo

    @markHttpMethod(httppath='/v2/game/user/insertToredis')
    def doDataToRedis(self):
        ftlog.debug('doDataToRedis..is..ok')
        DataList = runhttp.getParamStr('listData', '')
        DataList = json.loads(DataList)
        ftlog.debug('DataList =', DataList)
        DataName = runhttp.getParamStr('itemList', '')
        ftlog.debug('DataName =', DataName)
        mo = MsgPack()
        mo.setCmd('insertToredis')
        daobase.executeMixCmd('del', DataName)
        for ecode in DataList:
            ftlog.debug('value =', ecode)
            daobase.executeMixCmd('lpush', DataName, ecode)
        mo.setResult('ok', 1)
        return mo

    @markHttpMethod(httppath='/v3/game/exchange/auditCallback')
    def doExchangeAudit(self, userId, exchangeId, result):
        mo = MsgPack ( )
        mo.setCmd ( 'exchange' )
        mo.setParam ( 'action', 'audit' )
        mo.setParam ( 'userId', userId )
        mo.setParam ( 'result', result )
        mo.setParam ( 'exchangeId', exchangeId )
        mo.setParam ( 'gameId', HALL_GAMEID )
        mo.setResult( '0', 'ok' )

        userdata.clearUserCache ( userId )

        if not userdata.checkUserData ( userId ):
            mo.setError ( 1, 'userId error' )
            mo.setResult ( '0', 'userId error' )
            return mo

        try:
            ec, info = exchange_remote.handleAuditResult ( HALL_GAMEID, userId, exchangeId, result )
            if ec != 0:
                mo.setError ( ec, info )
                mo.setResult ( '0', info )
        except:
            ftlog.error ( )
            mo.setError ( 1, 'audit fail' )
            mo.setResult ( '0', 'audit fail' )

        return mo

        # userdata.clearUserCache(userId)
        # if not userdata.checkUserData(userId):
        #     mo = MsgPack()
        #     mo.setError(1, 'userId error')
        #     return mo
        #
        # msg = MsgPack()
        # msg.setCmd('exchange')
        # msg.setParam('action', 'audit')
        # msg.setParam('userId', userId)
        # msg.setParam('result', result)
        # msg.setParam('exchangeId', exchangeId)
        # msg.setParam('gameId', HALL_GAMEID)
        # return router.queryUtilServer(msg, userId)

    @markHttpMethod ( httppath = '/v3/game/exchange/shippingResultCallback' )
    def doExchangeShippingResult ( self, userId, exchangeId, result ):

        mo = MsgPack ( )
        mo.setCmd ( 'exchange' )
        mo.setParam ( 'action', 'shippingResult' )
        mo.setParam ( 'userId', userId )
        mo.setParam ( 'result', result )
        mo.setParam ( 'exchangeId', exchangeId )
        mo.setParam ( 'gameId', HALL_GAMEID )
        mo.setResult ( '0', 'ok' )

        userdata.clearUserCache ( userId )

        if not userdata.checkUserData ( userId ):
            mo.setError ( 1, 'userId error' )
            mo.setResult ( '0', 'userId error' )
            return mo

        try:
            ec, info = exchange_remote.handleShippingResult ( HALL_GAMEID, userId, exchangeId, result )
            if ec != 0:
                mo.setError ( ec, info )
                mo.setResult ( '0', info )
        except:
            ftlog.error ( )
            mo.setError ( 1, 'shipping result fail' )
            mo.setResult ( '0', 'shipping result fail' )

        return mo


    @markHttpMethod(httppath='/v2/game/consume/transaction')
    def doConsumeTransaction(self, appId, realGameId, userId, prodId, clientId, prodCount, prodOrderId):
        realGameId = realGameId if realGameId else 9999
        mo = MsgPack()
        mo.setCmd('buy_prod')
        mo.setResult('appId', appId)
        mo.setResult('realGameId', realGameId)
        mo.setResult('userId', userId)
        mo.setResult('prodId', prodId)
        mo.setResult('prodCount', prodCount)
        mo.setResult('prodOrderId', prodOrderId)

        if not prodOrderId:
            mo.setError(1, 'not prodOrderId')
        else:
            try:
                hallstore.storeSystem.buyProduct(appId, realGameId, userId, clientId, prodOrderId, prodId, prodCount)
            except TYStoreException, e:
                mo.setError(e.errorCode, e.message)
            except:
                ftlog.error()
                mo.setError(1, 'doConsumeTransaction')
        return mo

    @classmethod
    def getChargeInfos(cls):
        chargeType = runhttp.getParamStr('chargeType', '')
        chargeRmbs = runhttp.getParamFloat('chargedRmbs', 0)
        chargedDiamonds = runhttp.getParamInt('chargedDiamonds', 0)
        consumeCoin = runhttp.getParamInt('consumeCoin')

        chargeMap = {}
        consumeMap = {}
        if consumeCoin > 0:
            consumeMap['coin'] = consumeCoin
        if chargeRmbs > 0:
            chargeMap['rmb'] = chargeRmbs
        if chargedDiamonds > 0:
            chargeMap['diamond'] = chargedDiamonds
        return chargeType, chargeMap, consumeMap

    @markHttpMethod(httppath='/v2/game/consume/delivery')
    def doConsumDelivery(self, appId, realGameId, userId, orderId, prodId, prodCount, platformOrder):
        ftlog.info('doConsumDelivery->', appId, realGameId, userId, orderId, prodId, prodCount, platformOrder)
        appKey = hallconf.getAppKeyInfo(appId).get('key', '')
        if not runhttp.checkHttpParamCode(appKey):
            mo = MsgPack()
            mo.setCmd('prod_delivery')
            mo.setError(1, '校验失败')
            ftlog.info('doConsumDelivery->', appId, realGameId, userId, orderId, prodId, prodCount, platformOrder,
                       'result=code verify error')
            return mo
        userdata.clearUserCache(userId)
        mo = MsgPack()
        mo.setCmd('prod_delivery')
        mo.setParam('userId', userId)
        mo.setParam('orderId', orderId)
        mo.setParam('prodCount', prodCount)
        mo.setParam('prodId', prodId)
        mo.setParam('appId', appId)
        mo.setParam('realGameId', realGameId)
        mo.setParam('orderPlatformId', platformOrder)
        mo.setParam('ok', '1')
        isSub = runhttp.getParamInt('is_monthly', 0)
        if isSub:
            mo.setParam('isSub', isSub)
        chargeType, chargeMap, consumeMap = self.getChargeInfos()
        mo.setParam('consumeMap', consumeMap)
        mo.setParam('chargeMap', chargeMap)
        mo.setParam('chargeType', chargeType)
        ret = router.queryUtilServer(mo, userId)
        ftlog.info('doConsumDelivery->', appId, realGameId, userId, orderId, prodId, prodCount, platformOrder, 'result=', ret)
        if isinstance(ret, (str, unicode)) and ret.find('error') < 0:
            return 'success'
        return 'error'

    @markHttpMethod(httppath='/v1/deliveryproduct')
    def doDeliveryProduct(self, uid, orderId, prodId, orderPrice, prodCount, platformOrder, isError, error):
        ftlog.info('doDeliveryProduct->', uid, orderId, prodId, orderPrice, prodCount, platformOrder, isError, error)
        userdata.clearUserCache(uid)
        mo = MsgPack()
        mo.setCmd('prod_delivery')
        mo.setParam('userId', uid)
        mo.setParam('orderId', orderId)
        mo.setParam('prodId', prodId)
        mo.setParam('orderPrice', orderPrice)
        mo.setParam('orderPlatformId', platformOrder)
        if isError == 'true':
            mo.setResult('ok', '0')
            mo.setResult('info', error)
            mo.setError(1, error)
            router.sendToUser(mo, uid)
            return 'success'
        else:
            mo.setParam('ok', '1')
            isSub = runhttp.getParamInt('is_monthly', 0)
            if isSub:
                mo.setParam('isSub', isSub)
            ret = router.queryUtilServer(mo, uid)
            ftlog.info('doDeliveryProduct->', uid, orderId, prodId, orderPrice, prodCount, platformOrder, isError,
                       error, 'result=', ret)
            if isinstance(ret, (str, unicode)) and ret.find('error') < 0:
                return 'success'
        return 'error'

    @markHttpMethod(httppath='/v2/game/charge/notify')
    def doChargeNotify(self, appId, userId, buttonId, rmbs, diamonds, clientId):
        userdata.clearUserCache(userId)
        try:
            ftlog.info('HttpGameHandler.doChargeNotify',
                       'appId=', appId,
                       'userId=', userId,
                       'buttonId=', buttonId,
                       'rmbs=', rmbs,
                       'diamonds=', diamonds,
                       'clientId=', clientId)
        except:
            pass
        mo = MsgPack()
        mo.setCmd('charge_notify')
        mo.setParam('gameId', appId)
        mo.setParam('userId', userId)
        mo.setParam('prodId', buttonId)
        mo.setParam('rmbs', rmbs)
        mo.setParam('diamonds', diamonds)
        mo.setParam('clientId', clientId)
        router.sendUtilServer(mo, userId)
        return 'success'

    @markHttpMethod(httppath='/v2/game/clearcache')
    def doClearUserCache(self, userId):
        return userdata.clearUserCache(userId)

    @markHttpMethod(httppath='/v2/game/charge/qipainotify')
    def doQiPaiNotify(self, appId, userId, buttonId, rmbs, diamonds):
        userdata.clearUserCache(userId)
        if appId > 0 and userId > 0:
            datachangenotify.sendDataChangeNotify(appId, userId, ['chip', 'diamonds'])
        msg = MsgPack()
        msg.setResult('ec', 0)
        return msg

    #     兑换码
    @markHttpMethod(httppath='/v1/activity/generateExcode')
    def doGenerateExcode(self):
        paramsDict = runhttp.getDict()
        ftlog.debug("doGenerateExcode:", paramsDict)
        from hall.entity.hallactivity.activity_exchange_code import TYActivityExchangeCode
        mo = TYActivityExchangeCode.doGenerateCode(paramsDict)
        return mo

    @markHttpMethod(httppath='/v1/activity/queryCode')
    def doQueryExcode(self):
        paramsDict = runhttp.getDict()
        ftlog.debug("doQueryExcode:", paramsDict)
        from hall.entity.hallactivity.activity_exchange_code import TYActivityExchangeCode
        mo = TYActivityExchangeCode.doQueryCode(paramsDict)
        return mo

    @markHttpMethod(httppath='/v1/activity/getExcodeForUser')
    def doExcodeForUser(self):
        paramsDict = runhttp.getDict()
        ftlog.debug("doExcodeForUser:", paramsDict)
        from hall.entity.hallactivity.activity_exchange_code import TYActivityExchangeCode
        mo = TYActivityExchangeCode.doExcodeForUser(paramsDict)
        return mo

    @markHttpMethod(httppath='/v1/activity/queryTimeCode')
    def doQueryForTime(self):
        """
        废弃，目前的生成规则已不再依赖时间，原因不明，人员已离职
        """
        paramsDict = runhttp.getDict()
        ftlog.debug("doQueryForTime:", paramsDict)
        from hall.entity.hallactivity.activity_exchange_code import TYActivityExchangeCode
        mo = TYActivityExchangeCode.doQueryTimeCode(paramsDict)
        return mo

    @markHttpMethod(httppath='/v2/game/sdk/notify')
    def doReceiveSdkNotify(self):
        """
        action: add_friend accept_friend
        """
        paramsDict = runhttp.getDict()
        ftlog.debug("doReceiveSdkNotify:", paramsDict)

        appId = paramsDict.get('appId', 0)
        userId = int(paramsDict.get('userId', 0))
        actionType = paramsDict.get('type', '')
        ext = paramsDict.get('ext', None)
        msg = paramsDict.get('message', '')
        mo = MsgPack()
        mo.setCmd('friend_notify')
        mo.setResult('gameId', appId)
        mo.setResult('userId', userId)
        mo.setResult('action', actionType)
        mo.setResult('info', msg)
        if ext != None:
            try:
                extjson = json.loads(ext)
                for k in extjson:
                    mo.setResult(k, extjson[k])
            except:
                pass
        userdata.clearUserCache(userId)
        router.sendToUser(mo, userId)
#         if actionType == 'add_friend':
#             from poker.entity.biz.message import message
#             message.send(int(appId), message.MESSAGE_TYPE_SYSTEM, int(userId), msg)
        return 'success'

    @markHttpMethod(httppath='/v2/game/sdk/getRecommendFriends')
    def doGetRecommendFriends(self):
        paramsDict = runhttp.getDict()
        ftlog.debug("doGetRecommendFriends:", paramsDict)
        count = int(paramsDict.get('count', 0))
        friend_uids = paramsDict.get('friend_uids', '')
        userId = paramsDict.get('userId', '')

        friend_uid_list = []
        if friend_uids and friend_uids != '':
            friend_uid_list = friend_uids.split(',')

        count_all = len(friend_uid_list) + count * 3  # 适当扩大范围,优先推荐女性
        uids = onlinedata.getOnlineRandUserIds(count_all)
        ftlog.debug("doGetRecommendFriends uids:", uids)

        recommend_uids = set()
        for uid in uids:
            if uid <= 10000 or uid == int(userId) or str(uid) in friend_uid_list:
                continue
            recommend_uids.add(uid)
        return json.dumps(list(recommend_uids))

    @markHttpMethod(httppath='/v2/game/sdk/getGameInfo')
    def doGetGameInfoForSdk(self):
        paramsDict = runhttp.getDict()
        ftlog.debug("doGetGameInfoForSdk:", paramsDict)
        uidlist = paramsDict.get('uids', '').split(',')
        for_winchip = paramsDict.get('for_winchip', 0)
        for_level_info = paramsDict.get('for_level_info', 0)
        for_online_info = paramsDict.get('for_online_info', 1)
        gameIds = paramsDict.get('gameids', '').split(',')
        for x in xrange(len(gameIds)):
            gameIds[x] = strutil.parseInts(gameIds[x])
        for x in xrange(len(uidlist)):
            uidlist[x] = strutil.parseInts(uidlist[x])
        return self._doGetGameInfoForSdk(uidlist, gameIds, for_level_info, for_winchip, for_online_info)
    

    def _doGetGameInfoForSdk(self, uidlist, gameIds, for_level_info, for_winchip, for_online_info):
        users = []
# TODO HALL51 异常临时屏蔽
#         if _USE_FUTURE :
#             fulist = []
#             for userId in uidlist:
#                 if userId:
#                     fu = user_remote.getFriendGameInfoFuture(userId, gameIds, for_level_info,  for_winchip ,  for_online_info)
#                     fulist.append(fu)
#             for fu in fulist :
#                 ret = fu.getResult()
#                 if ret != None :
#                     users.append(ret)
#                 else:
#                     users.append({})
#         else:
#             for userId in uidlist:
#                 if userId:
#                     try:
#                         data = user_remote.getFriendGameInfo(userId, gameIds, for_level_info,  for_winchip ,  for_online_info)
#                     except:
#                         data = {}
#                         ftlog.error()
#                     users.append(data)
        return json.dumps(users)


    @markHttpMethod(httppath='/v2/game/sdk/youyifuVip/unsubscribe')
    def doSdkUnsubscribeMember(self, userId, isTempVipUser):
        userdata.clearUserCache(userId)
        mo = MsgPack()
        mo.setCmd('sub_member')
        mo.setParam('userId', userId)
        mo.setParam('action', 'unsub')
        mo.setParam('isTempVipUser', isTempVipUser)
        router.queryUtilServer(mo, userId)
        return 'success'

    @markHttpMethod(httppath='/v2/game/sdk/sns_callback')
    def doSdkSnsCallback(self):
        paramsDict = runhttp.getDict()
        # ftlog.debug("doGetGameInfoForSdk:", paramsDict)
        sdk_result = paramsDict.get('sdk_result')
        tcp_params = paramsDict.get('tcp_params')

        # from urllib import unquote
        # ftlog.debug("tcp_params:", tcp_params)
        try:
            tcp_params = json.loads(tcp_params)
        except:
            tcp_params = None

        if not tcp_params or not sdk_result:
            return ''

        try:
            sdk_result = strutil.loads(sdk_result)
            sdk_result = sdk_result['result']
        except:
            ftlog.error()
            return ''

        action = tcp_params['action']

        userId = tcp_params.get('userId')
        gameId = tcp_params.get('gameId')
        clientId = tcp_params.get('clientId')

        ftlog.debug('sdk_result', sdk_result)

        # if sdk_result is None or 'ec' in sdk_result:
        #     return False, -1, u'请求失败'

        mo = MsgPack()
        mo.setCmd('friend_call')
        mo._ht['result'] = tcp_params
        # mo.setResult('action', 'query')
        for k in sdk_result:
            mo.setResult(k, sdk_result[k])

        userdata.clearUserCache(userId)

        try:
            if action == 'praise_friend':
                self.on_praise_friend(gameId, userId, clientId, mo)
            elif action == 'ready_invite_friend':
                self.on_ready_invite_friend(gameId, userId, clientId, mo)
                code = mo.getResult('code', 0)
                if code > 0:
                    return ''
            elif action == 'add_friend':
                self.on_add_friend(gameId, userId, clientId, mo)
            elif action == 'accept_friend':
                self.on_accept_friend(gameId, userId, clientId, mo)
            elif action == 'get_friends_rank':
                self.on_get_friends_rank(gameId, mo)
            elif action == 'get_friend_list':
                self.on_get_friend_list(userId, mo)
        except:
            import traceback
            traceback.print_exc()
        router.sendToUser(mo, userId)
        return ''

    @classmethod
    def on_add_friend(cls, gameId, uid, clientId, mo):
        code = mo.getResult('code', 0)
        if code != 0:
            return
        from hall.entity import hallmoduletip
        friend_uid = mo.getResult('friend_uid', None)
        friend_uids = friend_uid.split(',')
        ftlog.debug('add_friend', friend_uid)
        for fid in friend_uids:
            hallmoduletip.sendModuleTipEvent(int(fid), gameId, "friends", 1)

    @classmethod
    def on_accept_friend(cls, gameId, uid, clientId, mo):
        code = mo.getResult('code', 0)
        if code != 0:
            return
        # red dot
        friend_uid = mo.getResult('friend_uid', None)
        if not friend_uid:
            return
        friend_uids = friend_uid.split(',')

        nick_name = mo.getResult('nick_name', '')
        is_agree = int(mo.getResult('is_agree', 0))
        if is_agree == 0:
            return
        msg = '恭喜您和"' + nick_name + '"成为好友'
        ftlog.debug('on_accept_friend.... ' + msg)
        from poker.entity.biz.message import message
        message.send(gameId, message.MESSAGE_TYPE_SYSTEM, int(friend_uid), msg)

        from hall.entity import hallmoduletip
        ftlog.debug('on_accept_friend', friend_uids)
        for fid in friend_uids:
            hallmoduletip.sendModuleTipEvent(int(fid), gameId, "friends", 1)

    @classmethod
    def on_ready_invite_friend(cls, gameId, uid, clientId, mo):
        from hall.entity.todotask import TodoTaskHelper
        code = mo.getResult('code', 0)
        if code != 1:
            return
        from hall.entity.todotask import TodoTaskBindPhoneFriend
        info_ = '请绑定手机，成为正式账号即可与朋友一起玩！'
        task = TodoTaskBindPhoneFriend(info_, 0)
        task.setSubText('绑定手机')
        TodoTaskHelper.sendTodoTask(gameId, uid, [task])

    @classmethod
    def on_praise_friend(cls, gameId, uid, clientId, mo):
        code = mo.getResult('code', 0)
        # vip = mo.getResult('vip')
        if code == 0:
            friend_uid = int(mo.getResult('friend_uid'))
            nick_name = mo.getResult('nick_name')
            friend_nick_name = mo.getResult('friend_nick_name')
            my_add_charm = mo.getResult('my_add_charm')
            friend_add_charm = mo.getResult('friend_add_charm')
            my_charm = mo.getResult('my_charm')
            friend_charm = mo.getResult('friend_charm')

            msg1 = '给"' + friend_nick_name + '"点赞获得' + str(my_add_charm) + '个魅力值'
            msg2 = '"' + nick_name + '"给您点赞获得' + str(friend_add_charm) + '个魅力值'
            from poker.entity.biz.message import message
            message.send(gameId, message.MESSAGE_TYPE_SYSTEM, int(uid), msg1)
            message.send(gameId, message.MESSAGE_TYPE_SYSTEM, int(friend_uid), msg2)
            ftlog.debug('on praise friend.... ' + msg1)
            ftlog.debug('on praise friend.... ' + msg2)

            datachangenotify.sendDataChangeNotify(gameId, uid, 'charm')

            from hall.entity.hallranking import rankingSystem, TYRankingInputTypes
            timestamp = pktimestamp.getCurrentTimestamp()
            rankingSystem.setUserByInputType(gameId, TYRankingInputTypes.CHARM,
                                             uid, my_charm, timestamp)
            rankingSystem.setUserByInputType(gameId, TYRankingInputTypes.CHARM,
                                             friend_uid, friend_charm, timestamp)
            # 历史获赞次数
            history_praised_num = gamedata.incrGameAttr(friend_uid, gameId, 'history_praised_num', 1)
            mo.setResult('friend_history_praised_num', history_praised_num)

        if code != 2:
            return

        from hall.entity.todotask import TodoTaskPayOrder, TodoTaskShowInfo
        from hall.entity.todotask import TodoTaskHelper
        from hall.entity import hallvip, hallitem

        user_vip = hallvip.userVipSystem.getUserVip(uid)
        delta_exp = user_vip.deltaExpToNextLevel()

        product, _ = hallstore.findProductByContains(gameId, uid, clientId,
                                                     ['coin'], None,
                                                     hallitem.ASSET_CHIP_KIND_ID,
                                                     delta_exp * 1000)

        pay_order = TodoTaskPayOrder(product)
        if user_vip == 0:
            msg = '点赞次数已达今日上限，开通VIP可提高点赞次数上限获得更多福利哦~'
            btnTxt = '开通VIP'
        else:
            msg = '点赞次数已达今日上限，升级VIP等级可提高点赞次数上限获得更多福利哦~'
            btnTxt = '升级VIP'
        dialog_task = TodoTaskShowInfo(msg, True)
        dialog_task.setSubCmd(pay_order)
        dialog_task.setSubText(btnTxt)
        TodoTaskHelper.sendTodoTask(gameId, uid, [dialog_task])

    @classmethod
    def on_get_friends_rank(cls, gameid, mo):
        friend_list = mo.getResult('data')
        for friend in friend_list:
            # 填充历史获赞次数
            uid = int(friend['uid'])
            num = gamedata.getGameAttr(uid, gameid, 'history_praised_num')
            friend['history_praised_num'] = num if num else 0

    @staticmethod
    def _friend_list_order(friend_info):
        request = friend_info.get('is_request', 0)
        online = friend_info.get('online', 1)
        close = friend_info.get('close', 0)
        chip = friend_info.get('chip', 0)
        offline_time = friend_info.get('offline_time', 1)
        return -request, -online, -close, -chip, offline_time, friend_info['uid']

    @classmethod
    def on_get_friend_list(cls, uid, mo):
        page = max(1, mo.getResult('page', 1))  # 分页请求,数据太大,超63k了
        friend_requests = mo.getResult('friend_list')
        begin_idx = (page - 1) * 100
        total = len(friend_requests)
        mo.setResult('friend_cnt', total)
        if total <= begin_idx:
            mo.setResult('friend_list', [])
            return

        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(uid, timestamp)
        for info in friend_requests:
            if info.get('is_request', 0):
                continue
            # 填充密友
            fid = int(info['uid'])
            # if status.inviter == fid or fid in status.inviteeMap else 0
            info['close'] = 1 if fid in status.inviteeMap else 0
        friend_requests.sort(key=cls._friend_list_order)
        mo.setResult('friend_list', friend_requests[begin_idx:begin_idx + 100])

    @markHttpMethod(httppath='/v2/game/info/getConfigOnline')
    def doGetConfigOnline(self, gameId, clientIdNum, key):
        conf = configure.getGameJson(gameId, key, None, clientIdNum)
        return conf

    @markHttpMethod(httppath='/v2/game/info/getConfigOnline2')
    def doGetConfigOnline2(self, key):
        conf = configure.getJson(key, {}, None)
        return conf

    @markHttpMethod(httppath='/v2/game/info/inWhichGames')
    def doInWhichGames(self, uid):
        # 获取当前用户在哪个游戏下，用于确认用户游戏状态及检验bind_game/leave_game的调用
        gameIdList = onlinedata.getGameEnterIds(uid)
        return gameIdList

    @markHttpMethod(httppath='/v2/game/info/getStoreLimit')
    def getStoreLimit(self, prodId):
        return hallstocklimit.stockSystem.loadStock(prodId)

    @markHttpMethod(httppath='/v2/game/info/setStoreLimit')
    def setStoreLimit(self, prodId, prodCount):
        return hallstocklimit.stockSystem.setStock(prodId, prodCount)

    @markHttpMethod(httppath='/v2/game/red_envelope/generateRedEnvelope')
    def generateRedEnvelope(self, reason, gameId, userId):
        contents = [{"itemId": "chip", "value": 10000, "count": 2}, {"itemId": "coupon", "value": 10, "count": 3},
                    {"itemId": "1001", "value": 1, "count": 5}]
        return TYRedEnvelopeMgr.buildEnvelope(reason, userId, gameId, contents, None)

    @markHttpMethod(httppath='/v2/game/red_envelope/queryRedEnvelope')
    def queryRedEnvelope(self, redEnvelopeId):
        return TYRedEnvelopeMgr.queryEnvelope(redEnvelopeId)

    @markHttpMethod(httppath='/v2/game/red_envelope/queryRedEnvelopeID')
    def queryRedEnvelopeID(self, redEnvelopeId):
        return TYRedEnvelopeMgr.queryEnvelopeID(redEnvelopeId)

    # openRedEnvelope
    @markHttpMethod(httppath='/v2/game/red_envelope/openRedEnvelope')
    def openRedEnvelope(self, redEnvelopeId, userId):
        return TYRedEnvelopeMgr.openRedEnvelope(redEnvelopeId, userId)

    @markHttpMethod(httppath='/v2/game/neituiguang/addInviterTemp')
    def doNeituiguangCheckCode(self, userId, inviter, clientId):
        msg = MsgPack()
        msg.setCmd('promote_info')
        msg.setParam('action', 'code_check')
        msg.setParam('gameId', 9999)
        msg.setParam('userId', userId)
        msg.setParam('promoteCode', inviter)
        if clientId:
            msg.setParam('clientId', clientId)
        result = router.queryUtilServer(msg, userId)
        return {'result':result}

    @markHttpMethod(httppath='/v2/game/neituiguang/setinviter')
    def neituiguang_set_inviter(self, userId, inviter):
        return neituiguang_remote.set_inviter(userId, inviter)

    @markHttpMethod(httppath='/v2/game/neituiguang/getinvitee')
    def neituiguang_get_invitee(self, userId):
        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(userId, timestamp)
        return status.encodeInvitee()
    
    @markHttpMethod(httppath='/v2/game/getUserInfo')
    def doGetUserInfo(self, userId):
        uInfo = user_remote.getThirdPartyUserInfo(userId) 
        return json.dumps(uInfo)

    @markHttpMethod(httppath='/v2/game/activity/shareClick')
    def do_share_click(self, userId, actname):
        if userId <= 0 or not userdata.checkUserData(userId):
            return 'user not exsit'
        return user_remote.activity_share_click(userId, actname)

    JD_ADDRESS_RET_CODE_OK = 1
    JD_ADDRESS_RET_CODE_NO_DATA = 0
    JD_ADDRESS_RET_CODE_HANDLE = {
        JD_ADDRESS_RET_CODE_OK: lambda addrs: addrs,
        JD_ADDRESS_RET_CODE_NO_DATA: lambda addrs: {},
    }

    @markHttpMethod(httppath='/v2/game/getJdAddress')
    def getJdAddress(self, proviceId, cityId, countyId):
        try:
            if proviceId:
                addrs = self._getJdAddress('http://gdss.touch4.me/?act=api.getJdCity', ('proviceId', proviceId),
                                           self.JD_ADDRESS_RET_CODE_OK)
            elif cityId:
                addrs = self._getJdAddress('http://gdss.touch4.me/?act=api.getJdCounty', ('cityId', cityId),
                                           self.JD_ADDRESS_RET_CODE_OK)
            elif countyId:
                addrs = self._getJdAddress('http://gdss.touch4.me/?act=api.getJdTown', ('townId', countyId),  # gdss接口参数名字起错了,将错就错
                                           self.JD_ADDRESS_RET_CODE_OK, self.JD_ADDRESS_RET_CODE_NO_DATA)  # 四级地址可能是没有的
            else:
                addrs = self._getJdAddress('http://gdss.touch4.me/?act=api.getJdProvice', ('', 0),  # 无需参数,硬造个key
                                           self.JD_ADDRESS_RET_CODE_OK)
            return {'retcode': 0, 'retmsg': addrs}
        except Exception, e:
            ftlog.warn('HttpGameHandler.getJdAddress failed', e)
            return {'retcode': -1}

    @lfu_alive_cache(maxsize=10240, cache_key_args_index=2, alive_second=3600)
    def _getJdAddress(self, url, keyTuple, *retfilters):
        from poker.util import webpage
        resp, _ = webpage.webget(url, {keyTuple[0]: keyTuple[1]} if keyTuple[0] else {},
                                 connect_timeout=6, timeout=6, retrydata={'max': 3})
        if resp:
            resp = strutil.loads(resp)
            retcode = resp.get('retcode', -1)
            if retcode in retfilters:
                return self.JD_ADDRESS_RET_CODE_HANDLE[retcode](resp['retmsg'])
        raise Exception('ret error', resp)  # 抛出异常,从而不缓存



    @markHttpMethod(httppath='/v3/game/hall_exmall/auditCallback')
    def doHallExmallAudit(self, userId, exchangeId, result):
        mo = MsgPack ( )
        mo.setCmd ( 'exchange' )
        mo.setParam ( 'action', 'audit' )
        mo.setParam ( 'userId', userId )
        mo.setParam ( 'result', result )
        mo.setParam ( 'exchangeId', exchangeId )
        mo.setParam ( 'gameId', HALL_GAMEID )
        mo.setResult( '0', 'ok' )

        userdata.clearUserCache ( userId )

        if not userdata.checkUserData ( userId ):
            mo.setError ( 1, 'userId error' )
            mo.setResult ( '0', 'userId error' )
            return mo

        try:
            ec, info = hall_exmall_remote.handleAuditResult ( HALL_GAMEID, userId, exchangeId, result )
            if ec != 0:
                mo.setError ( ec, info )
                mo.setResult ( '0', info )
        except:
            ftlog.error ( )
            mo.setError ( 1, 'audit fail' )
            mo.setResult ( '0', 'audit fail' )

        return mo


    @markHttpMethod (httppath='/v3/game/hall_exmall/shippingResultCallback')
    def doHallExmallShippingResult(self, userId, exchangeId, result, jdOrderId):
        mo = MsgPack()
        mo.setCmd('exchange')
        mo.setParam('action', 'shippingResult')
        mo.setParam('userId', userId)
        mo.setParam('result', result)
        mo.setParam('exchangeId', exchangeId)
        mo.setParam('gameId', HALL_GAMEID)
        mo.setResult('0', 'ok')

        userdata.clearUserCache (userId)

        if not userdata.checkUserData (userId):
            mo.setError(1, 'userId error')
            mo.setResult('0', 'userId error')
            return mo

        try:
            ec, info = hall_exmall_remote.handleShippingResult(HALL_GAMEID, userId, exchangeId, result, jdOrderId)
            if ec != 0:
                mo.setError(ec, info)
                mo.setResult('0', info)
        except:
            ftlog.error()
            mo.setError(1, 'shipping result fail')
            mo.setResult('0', 'shipping result fail')

        return mo
    
    @markHttpMethod (httppath='/v3/game/yyb/gift/gain')
    def doGainYYBGift(self, userId, giftKindId):
        ec, result = hall_yyb_gifts_remote.gainYYBGift(userId, giftKindId, pktimestamp.getCurrentTimestamp())
        if ec == 0:
            return {'code':result}
        return {'code':-1, 'info':result}


