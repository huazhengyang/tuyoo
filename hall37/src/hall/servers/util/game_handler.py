# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''

from hall.entity import halluser, hallitem, datachangenotify, hall_game_update,\
    hall_friend_table, hall_fangka, hall_fangka_buy_info,\
    hall_enter_resume_background, hall_quick_start_recommend,\
    hall_exit_plugin_remind, hallgamelist2, hall_enter_game_after_login,\
    hallconf
from hall.entity.todotask import TodoTaskHelper, TodoTaskGoldRain
from hall.game import TGHall
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.util_helper import UtilHelper
from poker.entity.biz import bireport
from poker.entity.events.tyevent import OnLineGameChangedEvent
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from poker.entity.dao import gamedata
from hall.entity.hallevent import UserBindPhoneEvent
from hall.entity import hall_exit_remind
from hall.servers.util.hall_handler import HallHelper
from poker.protocol import router
from freetime.entity.msg import MsgPack
from sre_compile import isstring

@markCmdActionHandler
class GameTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        self.helper = UtilHelper()
        
    def _check_param_configKey(self, msg, key, params):
        configKey = msg.getParam(key)
        if not configKey or not isstring(configKey):
            return None, None
        return None, configKey

    @markCmdActionMethod(cmd='game', action="data", clientIdVer=0)
    def doGameData(self, userId, gameId, clientId):
        self.helper.sendUserInfoResponse(userId, gameId, clientId, '', 0, 1)

    @markCmdActionMethod(cmd='game', action="bindPhone", clientIdVer=0)
    def dosendChipToUser(self, userId, gameId, clientId):
        # 添加绑定
        nowBindPone = gamedata.getGameAttr(userId, gameId, 'bindReward1')
        if not nowBindPone or nowBindPone < 1:
            gamedata.setGameAttr(userId, gameId, 'bindReward1', 1)
        else:
            from poker.entity.biz.exceptions import TYBizException
            raise TYBizException(-1, '重复绑定')
        # 发金币
        ftlog.info('cmd game action bindPhone userId =', userId)
        from poker.entity.dao import userchip, daoconst
        userchip.incrChip(userId, gameId, 5000, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'BIND_PHONE', 0, clientId)
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
        # 消息推送
        from poker.entity.biz.message import message
        msg = '恭喜您绑定手机成功，赠送您5000金币'
        message.send(gameId, message.MESSAGE_TYPE_PRIVATE, userId, msg)
        # 更新小红点
        datachangenotify.sendDataChangeNotify(gameId, userId, ['free', 'promotion_loc'])
        TGHall.getEventBus().publishEvent(UserBindPhoneEvent(userId, gameId))
        
    @markCmdActionMethod(cmd='game', action="bindIDCard", clientIdVer=0)
    def dosendBindIDChipToUser(self, userId, gameId, clientId):
        # 添加绑定
        nowBindID = gamedata.getGameAttr(userId, gameId, 'bindIDReward')
        if not nowBindID or nowBindID < 1:
            gamedata.setGameAttr(userId, gameId, 'bindIDReward', 1)
        else:
            from poker.entity.biz.exceptions import TYBizException
            raise TYBizException(-1, '重复绑定')
        
        ftlog.info('cmd game action bindIDCard userId =', userId)
        day2Kind = hallitem.itemSystem.findItemKind(hallitem.ITEM_HERO_KIND_ID)
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        timestamp = pktimestamp.getCurrentTimestamp()
        userBag.addItemUnitsByKind(gameId, day2Kind, 1, timestamp, 0, 'BIND_PHONE', 0)
        datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
        # 消息推送
        from poker.entity.biz.message import message
        msg = '恭喜您绑定身份证成功，赠送您1张英雄帖'
        message.send(gameId, message.MESSAGE_TYPE_PRIVATE, userId, msg)

    @markCmdActionMethod(cmd='game', action="enter", clientIdVer=0)
    def doGameEnter(self, userId, gameId, clientId):
        isdayfirst, iscreate = halluser.loginGame(userId, gameId, clientId)
        self.helper.sendUserInfoResponse(userId, gameId, clientId, '', 0, 1)
        self.helper.sendTodoTaskResponse(userId, gameId, clientId, isdayfirst)
        # BI日志统计
        bireport.userGameEnter(gameId, userId, clientId)
        bireport.reportGameEvent('BIND_GAME',
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId, iscreate)
        evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
        TGHall.getEventBus().publishEvent(evt)

    @markCmdActionMethod(cmd='game', action="leave", clientIdVer=0)
    def doGameLeave(self, userId, gameId, clientId):
        evt = OnLineGameChangedEvent(userId, gameId, 0, clientId)
        TGHall.getEventBus().publishEvent(evt)

    @markCmdActionMethod(cmd='game', action='get_member_reward', clientIdVer=0)
    def doGameGetMemberReward(self, userId, gameId, clientId):
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()
        memberCardItem = userBag.getItemByKindId(hallitem.ITEM_MEMBER_NEW_KIND_ID)
        timestamp = pktimestamp.getCurrentTimestamp()
        if memberCardItem and memberCardItem.canCheckin(timestamp):
            checkinAction = memberCardItem.itemKind.findActionByName('checkin')
            checkinAction.doAction(gameId, userAssets, memberCardItem, timestamp, {})
            datachangenotify.sendDataChangeNotify(gameId, userId, 'free')
            TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskGoldRain('恭喜您领取了今天的会员福利'))

    @markCmdActionMethod(cmd='game', action='get_exit_remind', clientIdVer=0)
    def doGameGetExitRemind(self, userId, gameId, clientId):
        hall_exit_remind.queryExitRemind(gameId, userId, clientId)
        
    @markCmdActionMethod(cmd='game', action='get_quick_start_recommend', clientIdVer=0)
    def doGetQuickStartRecommend(self, userId, gameId, clientId):
        '''
        获取快速开始推荐
        '''
        hall_quick_start_recommend.queryQuickStartRecommend(userId, gameId, clientId)
        
    @markCmdActionMethod(cmd='game', action='get_exit_plugin_remind', clientIdVer=0)
    def doGetExitPluginRemind(self, userId, gameId, clientId):
        '''
        获取插件退出挽留推荐
        '''
        gameIds = self.getGamesUserCanEnter(userId, gameId, clientId)
        hall_exit_plugin_remind.queryExitPluginRemind(userId, gameId, clientId, gameIds)
        
    @markCmdActionMethod(cmd='game', action='enter_game_after_login', clientIdVer=0)
    def doEnterGameAfterLogin(self, userId, gameId, clientId):
        '''
        获取快速开始推荐
        '''
        gameIds = self.getGamesUserCanEnter(userId, gameId, clientId)
        hall_enter_game_after_login.queryEnterGameAfterLogin(userId, gameId, clientId, gameIds)
       
    @markCmdActionMethod(cmd='game', action='common_config', clientIdVer=0)
    def doGetCommonConfig(self, userId, gameId, clientId, configKey):
        '''
        获取透传给前端的通用配置
        '''
        config = hallconf.getCommonConfig(clientId, configKey)
        msg = MsgPack()
        msg.setCmd('game')
        msg.setResult('action', 'common_config')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('configKey', configKey)
        msg.setResult('config', config)
        router.sendToUser(msg, userId)
         
    def getGamesUserCanEnter(self, userId, gameId, clientId):
        '''
        获取用户可以进入那些游戏
        '''
        gameIds = []
        template = hallgamelist2.getUITemplate(gameId, userId, clientId)
        if template is None:
            return gameIds
        _games, pages, innerGames = HallHelper.encodeHallUITemplage2(gameId, userId, clientId, template)
        from hall.servers.util import gamelistipfilter
        _games, _, _ = gamelistipfilter.filtergamelist(3.81, _games, pages, innerGames, userId, clientId)
        
        for game in _games:
            gameId = game.get('gameId', 0)
            if (0 != gameId) and (gameId not in gameIds):
                gameIds.append(gameId)
        
        return gameIds
        
    @markCmdActionMethod(cmd='game', action='get_fangka_item', clientIdVer=0)
    def doGetFangKaItem(self, userId, gameId, clientId):
        hall_fangka.sendFangKaItemToClient(gameId, userId, clientId)
        
    @markCmdActionMethod(cmd='game', action='require_fangka_buy_info', clientIdVer=0)
    def doRequireFangBuyInfo(self, userId, gameId, clientId):
        hall_fangka_buy_info.queryFangKaBuyInfo(gameId, userId, clientId)

    @markCmdActionMethod(cmd='game', action='get_game_update_info', clientIdVer=0)
    def doGameGetUpdateInfo(self, userId, gameId, clientId, version, updateVersion):
        hall_game_update.getUpdateInfo(gameId, userId, clientId, version, updateVersion)

    @markCmdActionMethod(cmd='game', action='update_notify', clientIdVer=0)
    def doGameUpdateNotify(self, userId, gameId, clientId, module):
        '''
        通知前端更新消息
        '''
        from hall.entity.hallconf import HALL_GAMEID
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, module)
        
    @markCmdActionMethod(cmd='game', action='enter_friend_table', clientIdVer=0)
    def doEnterFriendTable(self, userId, gameId, clientId, ftId):
        '''
        通知前端更新消息
        '''
        hall_friend_table.enterFriendTable(userId, gameId, clientId, ftId)
        
    @markCmdActionMethod(cmd='game', action='enter_back_ground', clientIdVer=0)
    def doEnterBackground(self, userId, gameId, clientId):
        '''
        用户退回后台
        '''
        hall_enter_resume_background.enterBackGround(userId, gameId, clientId)
    
    @markCmdActionMethod(cmd='game', action='resume_fore_ground', clientIdVer=0)
    def doResumeForeground(self, userId, gameId, clientId):
        '''
        用户返回前台
        '''
        hall_enter_resume_background.resumeForeGround(userId, gameId, clientId)

    @markCmdActionMethod(cmd='game', action="get_assign_reward", clientIdVer=0)
    def doHallNoticeReward(self, userId, gameId, clientId):
        ftlog.debug("doHallNoticeReward:", userId, gameId, clientId)
        from hall.entity.newpopwnd import noticeReward
        from poker.protocol import runcmd
        msg = runcmd.getMsgPack()
        noticeReward(userId, gameId, clientId, msg)
        if ftlog.is_debug():
            ftlog.debug("hall_notice_reward:", userId, gameId, clientId)