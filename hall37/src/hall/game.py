# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''

from poker.entity.configure import gdata
from poker.entity.events.tyevent import EventHeartBeat, ChargeNotifyEvent
from poker.entity.events.tyeventbus import globalEventBus
from poker.entity.game.game import TYGame
from poker.util import strutil

import freetime.util.log as ftlog
import hall.client_ver_judge as client_ver_judge
from hall.entity import hallmoduledefault, halllocalnotification, hall_third_sdk_switch, \
    halldomains, hall_game_update, hall_login_reward, hall_item_exchange, hall_friend_table, \
    hall_statics, hall_joinfriendgame, hall_jiguang_jpush, hall_robot_user
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskIssueStartChip
import poker.util.timestamp as pktimestamp


class TGHall(TYGame):

    def __init__(self):
        super(TGHall, self).__init__()

    def gameId(self):
        return HALL_GAMEID

    def initGameBefore(self):
        '''
        此方法由系统进行调用
        游戏初始化的预处理
        '''
        from hall.entity import halltask, hall_red_packet_rain, hall_red_packet_task, hall_red_packet_main
        halltask._registerClasses()
        hall_red_packet_rain._registerClasses()
        hall_red_packet_task._registerClasses()
        hall_red_packet_main._registerClasses()
        

    def initGame(self):
        from hall.entity import hallaccount
        from hall.entity import hallnewnotify
        self._account = hallaccount  # 大厅的账户处理类
        serverType = gdata.serverType()

        if serverType == gdata.SRV_TYPE_CENTER :
            centers = gdata.serverTypeMap().get(gdata.SRV_TYPE_CENTER, [])[:]
            centers.sort()
            sid = gdata.serverId()
            inits = gdata.centerServerLogics().get(sid, [])
            #轮盘开奖信息的监听
            from hall.servers.center.rpc.roulette_remote import sendReward
            globalEventBus.subscribe(EventHeartBeat, sendReward)
            if inits :
                for pkg in inits :
                    ftlog.info('init center logic of ->', pkg)
                    exec 'from %s import _initialize; _initialize(1)' % (pkg)
            
            hallnewnotify._initialize()
            globalEventBus.subscribe(EventHeartBeat, hallnewnotify.onEventHeartBeat)

            from hall.entity import hallsportlottery
            hallsportlottery._initialize()
            globalEventBus.subscribe(EventHeartBeat, hallsportlottery.onEventHeartBeat)

        from hall.entity.usercoupon import user_coupon_details
        user_coupon_details._initialize()

        if serverType == gdata.SRV_TYPE_UTIL :
            from hall.servers.util.account_handler import updateOnLineInfos
            globalEventBus.subscribe(EventHeartBeat, updateOnLineInfos)

            #充值回调
            TGHall.getEventBus().subscribe(ChargeNotifyEvent, self._ChargeNotifyEvent)
            # 在线信息初始化, ONLIE处理必须在UTIL服务
            from hall.entity import hallonline
            hallonline._initialize()
            hallnewnotify._initialize()
            globalEventBus.subscribe(EventHeartBeat, hallnewnotify.onEventHeartBeat)

        if serverType == gdata.SRV_TYPE_TABLE or  serverType == gdata.SRV_TYPE_ROOM :
            from hall.servers.room.room import reportRoomOnlineInfos
            globalEventBus.subscribe(EventHeartBeat, reportRoomOnlineInfos)
            from hall.entity import hallchatlog
            hallchatlog._initialize()

        # 注意: 各个模块间有先后初始化的顺序
        from hall.entity import hallitem, hallstore, hallvip, hallbenefits, \
            hallranking, hallshare, hallpromote, hallfree, hallgamelist, hallgamelist2, \
            halldailycheckin, hallmenulist, hallcoupon, hallmoduletip, \
            hallrename, hallads, hallflipcardluck, hallpopwnd, hallstartchip, \
            fivestarrate, match360kp, neituiguang, hallstocklimit, \
            hall_first_recharge, hallroulette, hallled, hall_exit_remind, hall_share2, \
            hall_yyb_gifts, hall_short_url, hall_red_packet_rain, hall_invite
        from hall.entity.hallactivity import activity
        from hall.entity.halltmpact import tmp_activity
        from hall.entity.hall_red_envelope import hall_red_envelope
        from hall.entity import hall_share3

        # 道具初始化
        hallitem._initialize()
        # 限购初始化
        hallstocklimit._initialize()
        # 商城初始化
        hallstore._initialize()
        # VIP系统初始化
        hallvip._initialize()
        # 救济金系统初始化
        hallbenefits._initialize()
        # 用户初始基金初始化
        hallstartchip._initialize()
        halldailycheckin._initialize()
        # 排行榜
        hallranking._initialize(0)
        # 活动系统初始化
        activity._initialize()
        hallcoupon._initialize()
        hallshare._initialize()
        hallgamelist._initialize()
        hallgamelist2._initialize()
        hallmenulist._initialize()
        hallrename._initialize()
        hallmoduletip._initialize()
        hallads._initialize()
        hallflipcardluck._initialize()
        hallpopwnd._initialize()
        hallpromote._initialize()
        hallfree._initialize()
        fivestarrate._initialize()
        match360kp._initialize()
        neituiguang._initialize()

        from hall.entity import halltask
        halltask.initialize()

        # 默认配置初始化
        hallmoduledefault._initialize()
        halllocalnotification._initialize()
        #首冲礼包配置
        hall_first_recharge._initialize()
        tmp_activity._initialize()
        #红包模块配置初始化
        hall_red_envelope._initialize()
        #钻石抽奖初始化
        hallroulette._initialize()
        #led配置初始化
        hallled._initializeConfig()
        # 退出提醒
        hall_exit_remind._initialize()
        # 三方控制模块开关
        hall_third_sdk_switch._initialize()
        # 域名配置初始化
        halldomains._initialize()
        # 插件升级模块初始化
        hall_game_update._initialize()
        # 登录奖励模块初始化
        hall_login_reward._initialize()
        # 道具转换模块初始化
        hall_item_exchange._initialize()
        # 自建桌房间号初始化
        hall_friend_table._initialize()
        from hall.entity import hallalarm
        hallalarm.initialize()
        
        from hall.entity import hall_exmall
        hall_exmall._initialize()
        # 房卡购买提示信息模块初始化
        from hall.entity import hall_fangka_buy_info
        hall_fangka_buy_info._initialize()
        
        hall_short_url._initialize()
        hall_share2._initialize()
        hall_share3._initialize()
        hall_yyb_gifts._initialize()
        hall_red_packet_rain._initialize()

        from hall.entity import hall1yuanduobao
        hall1yuanduobao._initialize()
        
        hall_invite._initialize()
        hall_statics._initialize()
        hall_joinfriendgame._initialize()
        hall_jiguang_jpush._initialize()
        hall_robot_user._initialize()

        # 红包任务初始化
        from hall.entity import hall_red_packet_task, hall_red_packet_exchange, hall_red_packet_main
        hall_red_packet_task._initialize()
        hall_red_packet_exchange._initialize()
        hall_red_packet_main._initialize()
        
        # 快速开始推荐模块初始化
        from hall.entity import hall_quick_start_recommend
        hall_quick_start_recommend._initialize()
        
        # 插件退出挽留模块初始化
        from hall.entity import hall_exit_plugin_remind
        hall_exit_plugin_remind._initialize()
        
        # 登录直接进入游戏模块初始化
        from hall.entity import hall_enter_game_after_login
        hall_enter_game_after_login._initialize()
        
        # 简单邀请功能初始化
        from hall.entity import hall_simple_invite
        hall_simple_invite.initialize()

    def initGameAfter(self):
        from hall.entity.hallactivity import activity
        activity.initAfter()

    def getInitDataKeys(self):
        '''
        取得游戏数据初始化的字段列表
        '''
        return self._account.getInitDataKeys()


    def getInitDataValues(self):
        '''
        取得游戏数据初始化的字段缺省值列表
        '''
        return self._account.getInitDataValues()


    def getGameInfo(self, userId, clientId):
        '''
        取得当前用户的游戏账户信息dict
        '''
        return self._account.getGameInfo(userId, clientId)


    def getDaShiFen(self, userId, clientId):
        '''
        取得当前用户的游戏账户的大师分信息
        '''
        return self._account.getDaShiFen(userId, clientId)


    def createGameData(self, userId, clientId):
        '''
        初始化该游戏的所有的相关游戏数据
        包括: 主游戏数据gamedata, 道具item, 勋章medal等
        返回主数据的键值和值列表
        '''
        return self._account.createGameData(userId, clientId)


    def loginGame(self, userId, gameId, clientId, iscreate, isdayfirst):
        '''
        用户登录一个游戏, 游戏自己做一些其他的业务或数据处理
        例如: 1. IOS大厅不发启动资金的补丁,
             2. 麻将的记录首次登录时间
             3. 游戏插件道具合并至大厅道具
        '''
        return self._account.loginGame(userId, gameId, clientId, iscreate, isdayfirst)

    def getTodoTasksAfterLogin(self, userId, gameId, clientId, isdayfirst):
        '''
        获取登录后的todotasks列表
        '''
        from hall.entity import hallitem, hallstartchip, hallpopwnd
        # 每日登录奖励，以前在各个游戏，现在移到大厅
        ret = []
        # 3.7以前9999没有todotask; 新大厅v4.56 9999走新的弹窗系统;
        _, clientVer, _ = strutil.parseClientId(clientId)
        if clientVer < 3.7 or clientVer >= 4.56:
            return ret
        
        if clientVer < client_ver_judge.client_ver_397:
            if hallstartchip.AlreadySendStartChip(userId, gameId)==False:
                # 需要弹启动资金领取弹框
                assetKind = hallitem.itemSystem.findAssetKind(hallitem.ASSET_ITEM_NEWER_GIFT_KIND_ID)
                pic = assetKind.pic if assetKind else ''
                if ftlog.is_debug():
                    ftlog.debug('TGHall.getTodoTasksAfterLogin userId=', userId,
                                'gameId=', gameId,
                                'clientId=', clientId,
                                'isDayFirst=', isdayfirst,
                                'assetKind=', assetKind)
                ret.append(TodoTaskIssueStartChip(hallstartchip.getCanGivestartChip(userId, gameId, clientId), 0, pic, ""))
        else:
            if hallstartchip.AlreadySendStartChip(userId, gameId)==False:
                #没有领取过启动资金
                initItems=hallitem._getInitItemsByClientId(userId, clientId)
                if (hallstartchip.newuser_startchip<=0)and (len(initItems)==0):
                    #既不发启动资金,也没有配置新手礼包
                    pass
                else:
                    pic=""
                    displayName=""
                    assetKind=None
                    for itemKind, _ in initItems:
                        pic = itemKind.pic if itemKind else ''
                        displayName= itemKind.displayName if itemKind else ''
                        assetKind=assetKind
                    if ftlog.is_debug():
                        ftlog.debug('TGHall.getTodoTasksAfterLogin userId=', userId,
                                    'gameId=', gameId,
                                    'clientId=', clientId,
                                    'isDayFirst=', isdayfirst,
                                    'assetKind=', assetKind)
                    ret.append(TodoTaskIssueStartChip(hallstartchip.newuser_startchip, 0, pic, displayName))

        timestamp = pktimestamp.getCurrentTimestamp()
        remainDays, memberBonus = hallitem.getMemberInfo(userId, timestamp)

        nsloginTodotaskList = hallpopwnd.makeTodoTaskNsloginReward(gameId, userId, clientId, remainDays, memberBonus,
                                                                   isdayfirst)

        if ftlog.is_debug():
            ftlog.debug('TGHall.getTodoTasksAfterLogin gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'nsloginTodotaskList=', nsloginTodotaskList)

        if nsloginTodotaskList:
            ret.extend(nsloginTodotaskList)

        # ios 提示更新
        iosUpgrade = hallpopwnd.makeTodoTaskByTemplate(gameId, userId, clientId, 'iosUpgrade')
        if iosUpgrade:
            ret.append(iosUpgrade)

        return ret

    def _ChargeNotifyEvent(self, event):
        from hall.entity import newcheckin
        newcheckin.deductionVipComplement(event)

TGHall = TGHall()


def getInstance():
    return TGHall

