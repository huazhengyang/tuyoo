# -*- coding=utf-8
'''
Created on 2015年10月23日

@author: zhaojiangang
'''
import time

from freetime.entity.msg import MsgPack
from hall.entity import hallads, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallitem import TYItemActionExchange
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from hall.servers.util.ads_handler import AdsHelper
from hall.servers.util.rpc import item_remote, user_remote, message_remote
from hall.servers.util.store_handler import StoreHelper
from poker.entity.biz.item.item import TYAssetKindItem
from poker.entity.biz.message.message import MESSAGE_TYPE_SYSTEM
from poker.entity.configure import configure
from poker.entity.dao import onlinedata, userchip, daoconst, userdata
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.util import strutil


@markHttpHandler
class HttpGameHandler(BaseHttpMsgChecker):
    def _check_param_itemId(self, key, params):
        value = runhttp.getParamInt(key, -1)
        if value < 0:
            return 'param itemId error', None
        return None, value

    def _check_param_kindId(self, key, params):
        value = runhttp.getParamInt(key, -1)
        if value < 0:
            return 'param kindId error', None
        return None, value

    def _check_param_count(self, key, params):
        value = runhttp.getParamInt(key, -1)
        if value <= 0:
            return 'param count error', None
        return None, value

    def _check_param_toAddExp(self, key, params):
        value = runhttp.getParamInt(key, -1)
        if value <= 0:
            return 'param toAddExp error', None
        return None, value

    def _check_param_deltaCount(self, key, params):
        value = runhttp.getParamInt(key, 0)
        if value == 0:
            return 'param deltaCount error', None
        return None, value

    def _check_param_intEventParam(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value

    def checkCode(self):
        code = ''
        datas = runhttp.getDict()
        if 'code' in datas:
            code = datas['code']
            del datas['code']
        keys = sorted(datas.keys())
        checkstr = ''
        for k in keys:
            checkstr += k + '=' + datas[k] + '&'
        checkstr = checkstr[:-1]

        apikey = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'
        checkstr = checkstr + apikey
        if code != strutil.md5digest(checkstr):
            return -1, 'Verify code error'

#         acttime = int(datas.get('time', 0))
#         if abs(time.time() - acttime) > 10:
#             return -1, 'verify time error'
        return 0, None

    @markHttpMethod(httppath='/_gdss/item/list')
    def doGdssListItem(self):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            ec, result = item_remote.listItem()
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult('items', result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/item/list')
    def doGdssListUserItem(self, userId):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            if userdata.checkUserData(userId):
                ec, result = item_remote.listUserItem(userId)
            else:
                ec, result = 2, 'userId error !!'
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult('items', result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/item/remove')
    def doGdssRemoveUserItem(self, userId, itemId, intEventParam):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            if userdata.checkUserData(userId):
                ec, result = item_remote.removeUserItem(HALL_GAMEID, userId, itemId, "GM_ADJUST", intEventParam)
            else:
                ec, result = 2, 'userId error !!'
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/item/add')
    def doGdssAddUserItem(self, userId, kindId, count, intEventParam):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            if count >= 1000:
                ec = 1
                result = 'item count to much !!'
            else:
                if userdata.checkUserData(userId):
                    ec, result = item_remote.addUserItem(HALL_GAMEID, userId, kindId, count, "GM_ADJUST", intEventParam)
                else:
                    ec, result = 2, 'userId error !!'
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/addchip')
    def doGdssAddUserChip(self, userId, gameId, deltaCount, intEventParam):
        mo = MsgPack()
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('adjustDelta', deltaCount)
        mo.setResult('trueDelta', 0)
        mo.setResult('final', 0)
        ec, result = self.checkCode()
        if ec == 0:
            if deltaCount > 100000000:
                mo.setError(1, 'chip deltaCount to much !!')
            else:
                if userdata.checkUserData(userId):
                    trueDelta, final = userchip.incrChip(userId, gameId, deltaCount,
                                                         daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                         'GM_ADJUST', intEventParam, configure.CLIENTID_SYSCMD)
                    mo.setResult('trueDelta', trueDelta)
                    mo.setResult('final', final)
                else:
                    mo.setError(2, 'userId error !!')
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/addcoupon')
    def doGdssAddUserCoupon(self, userId, gameId, deltaCount, intEventParam):
        mo = MsgPack()
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('adjustDelta', deltaCount)
        mo.setResult('trueDelta', 0)
        mo.setResult('final', 0)
        ec, result = self.checkCode()
        if ec == 0:
            if deltaCount > 100000:
                mo.setError(1, 'coupon deltaCount to much !!')
            else:
                if userdata.checkUserData(userId):
                    trueDelta, final = userchip.incrCoupon(userId, gameId, deltaCount,
                                                           daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                           'GM_ADJUST', intEventParam, configure.CLIENTID_SYSCMD)
                    mo.setResult('trueDelta', trueDelta)
                    mo.setResult('final', final)
                else:
                    mo.setError(2, 'userId error !!')
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/adddiamond')
    def doGdssAddUserDiamond(self, userId, gameId, deltaCount, intEventParam):
        mo = MsgPack()
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('adjustDelta', deltaCount)
        mo.setResult('trueDelta', 0)
        mo.setResult('final', 0)
        ec, result = self.checkCode()
        if ec == 0:
            if deltaCount > 100000:
                mo.setError(1, 'coupon deltaCount to much !!')
            else:
                if userdata.checkUserData(userId):
                    trueDelta, final = userchip.incrDiamond(userId, gameId, deltaCount,
                                                            daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                            'GM_ADJUST', intEventParam, configure.CLIENTID_SYSCMD)
                    mo.setResult('trueDelta', trueDelta)
                    mo.setResult('final', final)
                else:
                    mo.setError(2, 'userId error !!')
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/item/consume')
    def doGdssConsumeUserItem(self, userId, kindId, count, intEventParam):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            if userdata.checkUserData(userId):
                ec, result = item_remote.consumeUserItemByKind(HALL_GAMEID, userId, kindId, count, "GM_ADJUST",
                                                               intEventParam)
            else:
                ec, result = 2, 'userId error !!'
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/vip/addExp')
    def doGdssAddVipExp(self, userId, toAddExp):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            if userdata.checkUserData(userId):
                ec, result = user_remote.addVipExp(HALL_GAMEID, userId, toAddExp, 'GM_ADJUST', 0)
            else:
                ec, result = 2, 'userId error !!'
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult('vipExp', result)
        return mo

    @markHttpMethod(httppath='/_gdss/user/ads/query')
    def doGdssQueryAds(self, userId, clientId):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec != 0:
            mo.setError(ec, result)
        else:
            adsTemplate = hallads.queryAds(HALL_GAMEID, 10001, clientId)
            if adsTemplate:
                mo.setResult('name', adsTemplate.name)
                mo = AdsHelper.encodeAdsTemplate(HALL_GAMEID, 10001, clientId, adsTemplate)
            else:
                mo.setResult('name', None)
        return mo

    @markHttpMethod(httppath='/_gdss/user/store/query')
    def doGdssQueryStore(self, userId, clientId):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec != 0:
            mo.setError(ec, result)
        else:
            if userdata.checkUserData(userId):
                tabs = StoreHelper.getStoreTabs(HALL_GAMEID, userId, clientId)
                mo.setResult('tabs', tabs)
            else:
                mo.setError(2, 'userId error !!')
        return mo

    @markHttpMethod(httppath='/_gdss/assets/query')
    def doGdssQueryAssets(self):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            items = []
            assetKinds = hallitem.itemSystem.getAllAssetKind()
            for assetKind in assetKinds:
                exchangeType = None
                if isinstance(assetKind, TYAssetKindItem):
                    for action in assetKind.itemKind.actionList:
                        if isinstance(action, TYItemActionExchange):
                            exchangeType = action.auditParams.get('type')
                data = {
                    'itemId': assetKind.kindId,
                    'displayName': assetKind.displayName,
                    'units': assetKind.units
                }
                if exchangeType is not None:
                    data['exchangeType'] = exchangeType
                items.append(data)
            mo.setResult('items', items)
        if ec != 0:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/clena/onlineloc')
    def doGdssCleanOnLineLoc(self):
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            uids = []
            userIds = runhttp.getParamStr('userIds', '')
            userIds = userIds.split(',')
            for userId in userIds:
                try:
                    userId = int(userId)
                except:
                    pass
                if userId > 0:
                    onlinedata.cleanOnlineLoc(userId)
                    uids.append(userId)
            mo.setResult('clean', uids)
        if ec != 0:
            mo.setError(ec, result)
        return mo

    def _check_param_text(self, key, params):
        text = runhttp.getParamStr(key, '')
        return None, text

    @markHttpMethod(httppath='/_gdss/user/message/send')
    def do_gdss_user_msg_send(self, gameId, userId, text):
        """
        发送站内消息
        @param text: 消息文本内容
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if not ec:
            if userdata.checkUserData(userId):
                message_remote.send(gameId, MESSAGE_TYPE_SYSTEM, userId, text)
            else:
                mo.setError(2, "userId error !!")
        else:
            mo.setError(ec, result)
        return mo

    def _check_param_assets(self, key, params):
        assets = runhttp.getParamStr(key, '')
        if not assets:
            return 'param assets is empty!!', None
        try:
            assets = strutil.loads(assets)
        except:
            return 'param assets must be json-dump string!!', None
        return None, assets

    @markHttpMethod(httppath='/_gdss/user/message/sendasset')
    def do_gdss_user_msg_sendasset(self, gameId, userId, text, assets, intEventParam):
        """
        发送带物品或者货币的站内消息
        @param text: 消息文本内容
        @param assets: 附件内容,格式必须是：[{'itemId':'item:0011', 'count':1}, ...]
        @param intEventParam: 发奖事件的附带参数
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if not ec:
            if userdata.checkUserData(userId):
                d = {'eventid': "GM_ADJUST", 'eventparam': intEventParam, 'assets': assets}
                message_remote.send_asset(gameId, MESSAGE_TYPE_SYSTEM, userId, text, d)
            else:
                mo.setError(2, "userId error !!")
        else:
            mo.setError(ec, result)
        return mo

    def _check_param_duration(self, key, params):
        value = runhttp.getParamInt(key)
        return None, value

    def _check_param_todotask(self, key, params):
        todotask = runhttp.getParamStr(key, '')
        if not todotask:
            return 'param todotask is empty!!', None
        try:
            todotask = strutil.loads(todotask)
        except:
            return 'param todotask must be json-dump string!!', None
        return None, todotask

    def _check_param_todotask_kwarg(self, key, params):
        todotask_kwarg = runhttp.getParamStr(key, '')
        if not todotask_kwarg:
            return 'param todotask_kwarg is empty!!', None
        try:
            todotask_kwarg = strutil.loads(todotask_kwarg)
        except:
            return 'param todotask_kwarg must be json-dump string!!', None
        return None, todotask_kwarg

    @markHttpMethod(httppath='/_gdss/user/message/sendtodotask')
    def do_gdss_user_msg_sendtodotask(self, gameId, clientId, userId, text, duration, todotask, todotask_kwarg):
        """
        发送带查看的站内消息
        @param text: 消息文本内容
        @param duration: 展示有效期,分钟,<=0就是永久有效
        @param todotask: 模板参数,支持两种todotask:
        1.hall.entity.hallpopwnd,见各game下popwnd的配置,这种情况只需要一个参数'templateName',但要保证clientid有效
        2.不走模板的hall.entity.todotask,配置散落的到处都是。。。,这种情况需要传入详细的模板参数,其中必须含有'typeId'
        @param todotask_kwarg: 实例化todotask需要的参数,多数情况都不需要
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if not ec:
            if userdata.checkUserData(userId):
                message_remote.send_todotask(gameId, MESSAGE_TYPE_SYSTEM, clientId, userId, text,
                                             todotask, duration, None, **todotask_kwarg)
            else:
                mo.setError(2, "userId error !!")
        else:
            mo.setError(ec, result)
        return mo

    @markHttpMethod(httppath='/_gdss/game/clear_table')
    def do_gdss_clear_table(self, gameId, roomId0, tableId0):
        moCheck = MsgPack()
        ec, result = self.checkCode()
        if ec:
            moCheck.setError(ec, result)
            return
            
        from freetime.util import log as ftlog
        ftlog.debug('HALLAdmin.clearTable gameId:', gameId
            , ' roomId:', roomId0
            , ' tableId:', tableId0)
        
        mo = MsgPack()
        mo.setCmd('table_manage')
        mo.setAction('clear_table')
        mo.setParam('gameId', gameId)
        mo.setParam('roomId', roomId0)
        mo.setParam('tableId', tableId0)
        from poker.protocol import router
        router.sendTableServer(mo, roomId0)
        
        return moCheck
    
    @markHttpMethod(httppath='/_gdss/game/query_friend_table')
    def do_gdss_query_FriendTable_Info(self, tableId0):
        moCheck = MsgPack()
        ec, result = self.checkCode()
        if ec:
            moCheck.setError(ec, result)
            return
            
        from freetime.util import log as ftlog
        ftlog.debug('HALLAdmin.queryFriendTableInfo tableId:', tableId0)
        from hall.entity import hall_friend_table
        params = hall_friend_table.getFriendTableInfo(str(tableId0))
        return params


    @markHttpMethod(httppath='/_gdss/hall/send_hall_notify_info')
    def do_gdss_send_HallNotify_Info(self):
        '''
        typeId 发送类型 1公告通知 2消息通知 3系统推送 必须选一个,没有默认
        ntimeId 发送时间 -2立即、-1定时、0每天、1周一、2周二、3周三、4周四、5周五、6周六、7周日 必须选一个,没有默认
        ntime 时间12:35 如果是ntimeId-2立即 可以不填 ,ntimeId-1定时 20170822|12:35,其他的 ntimeId,必须填一个时间,没有默认
        iconAddr 路径 必须填,没有默认
        context 文本内容 存文本 不超过50字 必须填,没有默认
        passthrough 透传消息,json{todotask} 可以不填,默认为空字符串
        platform 1 ios、2 android 必须选一个,没有默认
        buttonType 按钮类型 1确定 2忽略+前往  不选 默认确定
        hall 不需要手动填写的,根据用户权限给分配, 例如:'hall6', 'hall30'
        gameId 插件gameId  比如斗地主大厅的'30'插件,  不选发送所有插件,不填就是空字符串
        package 多个clientId,以 | 分割 'clientId1|clientId2|' 例如'Android_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu|
        Ios_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu' 不填就是空字符串
        userId 不填发送给所有的用户 'userId1|userId2|' 例如 '123456|78923' 不填就是空字符串
        '''
        typeId = runhttp.getParamStr('typeId', '')
        ntimeId = runhttp.getParamStr('ntimeId', '')
        ntime = runhttp.getParamStr('ntime', '')
        iconAddr = runhttp.getParamStr('iconAddr', '')
        context = runhttp.getParamStr('context', '')
        passthrough = runhttp.getParamStr('passthrough', '')
        platform = runhttp.getParamStr('platform', '')
        buttonType = runhttp.getParamStr('buttonType', '')
        hall = runhttp.getParamStr('hall', '')
        gameId = runhttp.getParamStr('gameId', '')
        package = runhttp.getParamStr('package', '')
        userId = runhttp.getParamStr('userId', '')
        timelimit = runhttp.getParamStr('timelimit', '')
        import freetime.util.log as ftlog
        try:
            ftlog.hinfo('HttpGameHandler.do_gdss_send_HallNotify_Info enter', 'typeId:', typeId,'ntimeId:', ntimeId,'ntime:', ntime,'iconAddr:',
                        iconAddr,'context:', context,'passthrough:', passthrough,'platform:', platform,'buttonType:', buttonType,'hall:', hall,
                        'gameId:', gameId,'package:', package,'userId:', userId,'timelimit:', timelimit)
            from hall.servers.center.rpc import newnotify_remote
            ok = newnotify_remote.addHallNotifyInfo(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform,
                                                    buttonType, hall, gameId, package, userId, timelimit)
            if ok:
                ftlog.hinfo('HttpGameHandler.do_gdss_send_HallNotify_Info ok', typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType,
                            hall, gameId, package, userId, timelimit)
                return {'retmsg': 1}
            else:
                ftlog.hinfo('HttpGameHandler.do_gdss_send_HallNotify_Info failed', typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType,
                            hall, gameId, package, userId, timelimit)
                return {'retmsg': 0}
        except:
            ftlog.hinfo('HttpGameHandler.do_gdss_send_HallNotify_Info error', typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType,
                        hall, gameId, package, userId, timelimit)
            return {'error': 404}


    @markHttpMethod(httppath='/_gdss/hall/get_hall_notify_info')
    def do_gdss_get_HallNotify_Info(self):
        hall = runhttp.getParamStr('hall', '')
        import freetime.util.log as ftlog
        try:
            ftlog.hinfo('HttpGameHandler.do_gdss_get_HallNotify_Info enter',hall)
            from hall.servers.center.rpc import newnotify_remote
            notifyList = newnotify_remote.getHallNotifyInfo(hall)
            ftlog.hinfo("HttpGameHandler.do_gdss_get_HallNotify_Info ok", notifyList)
            return {'retmsg': notifyList}
        except:
            ftlog.hinfo('HttpGameHandler.do_gdss_get_HallNotify_Info error', hall)
            return {'error': 404}


    @markHttpMethod(httppath='/_gdss/hall/del_hall_notify_info')
    def do_gdss_del_HallNotify_Info(self):
        ntimeId = runhttp.getParamStr('ntimeId', '')
        uuid = runhttp.getParamStr('uuid', '')
        hall = runhttp.getParamStr('hall', '')
        ntime = runhttp.getParamStr('ntime', '')
        import freetime.util.log as ftlog
        try:
            ftlog.hinfo('HttpGameHandler.do_gdss_del_HallNotify_Info enter', ntimeId, uuid, hall, ntime)
            from hall.servers.center.rpc import newnotify_remote
            ok = newnotify_remote.delHallNotifyInfo(ntimeId, uuid, hall, ntime)
            if ok:
                ftlog.hinfo('HttpGameHandler.do_gdss_del_HallNotify_Info ok', ntimeId, uuid, hall, ntime)
                return {'retmsg': 1}
            else:
                ftlog.hinfo('HttpGameHandler.do_gdss_del_HallNotify_Info failed', ntimeId, uuid, hall, ntime)
                return {'retmsg': 0}
        except:
            ftlog.hinfo('HttpGameHandler.do_gdss_del_HallNotify_Info error', ntimeId, uuid, hall, ntime)
            return {'error': 404}
        
    @markHttpMethod(httppath='/_gdss/hall/sport/end')
    def do_gdss_sport_end(self):
        matchId = runhttp.getParamInt('matchId', 0)
        leagueId = runhttp.getParamInt('leagueId', 0)
        homeTeamId = runhttp.getParamInt('homeTeamId', 0)
        awayTeamId = runhttp.getParamInt('awayTeamId', 0)
        timestamp = runhttp.getParamInt('timestamp', 0)
        scoreh = runhttp.getParamInt('scoreh', 0)
        scorea = runhttp.getParamInt('scorea', 0)
        oddsw = runhttp.getParamStr('oddsw', 0)
        oddsa = runhttp.getParamStr('oddsa', 0)
        oddsl = runhttp.getParamStr('oddsl', 0)
        status = runhttp.getParamInt('status', 0)
        try:
            import freetime.util.log as ftlog
            ftlog.hinfo('HttpGameHandler.do_gdss_sport_end enter', matchId, leagueId, homeTeamId, \
                        awayTeamId, timestamp, scoreh, scorea, oddsw, oddsa, oddsl, status)
            from hall.servers.center.rpc import newnotify_remote
            ret = newnotify_remote.doSportEnd(matchId, leagueId, homeTeamId, awayTeamId, timestamp, [scoreh, scorea], [oddsw, oddsa, oddsl], status)

            if ret == 0:
                ftlog.hinfo('HttpGameHandler.do_gdss_sport_end ok')
                return {'retmsg': 1}
            else:
                ftlog.hinfo('HttpGameHandler.do_gdss_sport_end failed')
                return {'retmsg': 0}

        except:
            ftlog.hinfo('HttpGameHandler.do_gdss_sport_end error')
            return {'error': 404}

