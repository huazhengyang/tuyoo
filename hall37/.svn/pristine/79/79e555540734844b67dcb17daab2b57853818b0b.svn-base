# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import gdata
from poker.entity.dao import daobase, userdata, onlinedata, userchip, gamedata
from poker.entity.events.tyevent import OnLineGameChangedEvent
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.servers.conn.rpc import onlines
from poker.servers.rpc import roommgr
from poker.util import strutil
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf, halluser, halldailycheckin, datachangenotify, \
    hallitem, hallrename, hallstore, hallstartchip, hallled, fivestarrate, \
    hallsubmember, hallversionmgr, hallexchange
from hall.entity.hall_clipboardhaner import Clipboard
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import EventAfterUserLogin
from hall.entity.todotask import TodoTaskHelper, TodoTaskShowInfo, \
    TodoTaskRename, TodoTaskPayOrder, TodoTaskPopTip
from hall.game import TGHall
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.util_helper import UtilHelper
import poker.util.timestamp as pktimestamp
from poker.entity.biz.exceptions import TYBizException


_ONLINES = {}

@markCmdActionHandler
class AccountTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        self.helper = UtilHelper()

    def _check_param_newName(self, msg, key, params):
        newName = msg.getParam(key)
        if not newName or not isstring(newName):
            return 'Error param newName', None
        return None, newName
    
    def _check_param_msg(self, msg, key, params):
        msgstr = msg.getParam(key)
        if not msgstr or not isstring(msgstr):
            return 'Error param msg', None
        return None, msgstr
    
    def _check_param_ismgr(self, msg, key, params):
        ismgr = msg.getParam(key)
        if ismgr in (0, 1):
            return None, ismgr
        return 'Error param ismgr', None

    def _check_param_scope(self, msg, key, params):
        scope = msg.getParam(key)
        if not scope or not isstring(scope):
            return None, 'hall'
        return None, scope
    
    def _check_param_clientIds(self, msg, key, params):
        clientIds = msg.getParam(key)
        if not clientIds:
            return None, []
        return None, clientIds
    
    def _check_param_isTempVipUser(self, msg, key, params):
        isTempVipUser = msg.getParam(key, 0)
        if isTempVipUser in (0, 1):
            return None, isTempVipUser
        return 'Error param isTempVipUser', None
    
    def _check_param_clipboardContent(self, msg, key, params):
        value = msg.getParam(key, '')
        return None, value
    
    def _check_param_isStopServer(self, msg, key, params):
        isStopServer = msg.getParam(key)
        if not isinstance(isStopServer, bool):
            return 'Error param isStopServer', None
        return None, isStopServer
    
    def checkForceLogout(self, userId):
        '''
        检查是否运行登录
        '''
        if halluser.isForceLogout(userId) :
            onlines.forceLogOut(userId, '')
            return 1
        return 0


    def recoverUserTableChips(self, userId, clientId):
        try:
            tableChips = userchip.getTableChipsAll(userId)
            ftlog.debug('recoverUserTableChips->', tableChips)
            datas = None
            if isinstance(tableChips, dict):
                datas = tableChips
            elif isinstance(tableChips, list):
                datas = {}
                for x in xrange(len(tableChips) / 2):
                    datas[tableChips[x * 2]] = tableChips[x * 2 + 1]
            delTablesIds = []
            for tableId, tchip in datas.items():
                tableId, tchip = strutil.parseInts(tableId, tchip)
                troomId = strutil.getTableRoomId(tableId)
                if not troomId or troomId <= 0:
                    delTablesIds.append(tableId)
                    continue
                gameId, _, _, _ = strutil.parseInstanceRoomId(troomId)
                if not gameId or gameId <= 0:
                    delTablesIds.append(tableId)
                    continue
                seatId = 0
                try:
                    seatId, _ = roommgr.doCheckUserLoc(userId, gameId, troomId, tableId, clientId)
                except:
                    delTablesIds.append(tableId)
                    ftlog.error()
                    continue
    
                if not seatId:
                    userchip.moveAllTableChipToChip(userId, gameId, 'TABLE_TCHIP_TO_CHIP', troomId, clientId, tableId)
                    delTablesIds.append(tableId)
                else:
                    # the user is on the table , do not clear
                    pass
    
            if delTablesIds:
                userchip.delTableChips(userId, delTablesIds)
        except:
            ftlog.error()


    @markCmdActionMethod(cmd='user', action='info', clientIdVer=0)
    def doUserInfo_0(self, userId):
        '''
        低版本不允许登录了
        '''
        onlines.forceLogOut(userId, '')


    @markCmdActionMethod(cmd='user', action='info', clientIdVer=3.0)
    def doUserInfo_3(self, userId, gameId, clientId, isFirstuserInfo):
        # 检查是否禁止登录
        if self.checkForceLogout(userId) :
            return
        
        self.updateBiggestHallVersion(userId, gameId, clientId)
        
        loc = ''
        if isFirstuserInfo :
            self._sendLocalStaticInfo(userId)
            loc = onlinedata.checkUserLoc(userId, clientId, 0)
            self.recoverUserTableChips(userId, clientId)
        # 发送udata和gdata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 1, 1)

    def _sendLocalStaticInfo(self, userId):
        mo = hallversionmgr.makeStaticMessage()
        router.sendToUser(mo, userId)


    @markCmdActionMethod(cmd='user', action='info', clientIdVer=3.3)
    def doUserInfo_3_3(self, userId, gameId, clientId, isFirstuserInfo):
        # 检查是否禁止登录
        if self.checkForceLogout(userId) :
            return
        
        self.updateBiggestHallVersion(userId, gameId, clientId)

        loc = ''
        if isFirstuserInfo :
            loc = onlinedata.checkUserLoc(userId, clientId, 0)
            self.recoverUserTableChips(userId, clientId)
        # 发送udata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 1, 0)
        
    def updateBiggestHallVersion(self, userId, gameId, clientId):
        '''
        记录更新该用户最高的版本号
        '''
        if gameId != HALL_GAMEID:
            return 
        
        _, clientVer, _ = strutil.parseClientId(clientId)
        if not clientVer:
            return
        
        bVer = 1.0
        biggestClientIdStr = gamedata.getGameAttr(userId, gameId, 'biggestHallVer')
        if biggestClientIdStr:
            bVer = float(biggestClientIdStr)
        
        if clientVer > bVer:
            gamedata.setGameAttr(userId, gameId, 'biggestHallVer', str(clientVer))
            ftlog.debug('update user biggest hallVersion:', clientVer)
        

    @markCmdActionMethod(cmd='user', action='bind', clientIdVer=0)
    def doUserBind_0(self, userId, gameId, clientId, isFirstuserInfo, clipboardContent):
        if ftlog.is_debug():
            ftlog.debug('AccountTcpHandler.doUserBind_0',
                        'userId=', userId,
                        'clipboard=', clipboardContent)
        
        # 检查是否禁止登录
        if self.checkForceLogout(userId) :
            return
        
        self.updateBiggestHallVersion(userId, gameId, clientId)
        
        loc = ''
        if isFirstuserInfo :
            loc = onlinedata.checkUserLoc(userId, clientId, 0)
            self.recoverUserTableChips(userId, clientId)
#         # 更新基本信息
        #halluser.updateUserBaseInfo(userId, clientId, runcmd.getMsgPack())
        clipboard = Clipboard.parse(clipboardContent)
        # 登录游戏处理
        isdayfirst, isCreate = halluser.loginGame(userId, gameId, clientId, clipboard)
        # 发送udata和gdata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 1, 1)
        # 发送TodoTask消息
        self.helper.sendTodoTaskResponse(userId, gameId, clientId, isdayfirst)
        
        # 分析clipboardConent内容，根据分析结果 功能 
        TGHall.getEventBus().publishEvent(EventAfterUserLogin(userId, gameId, isdayfirst, isCreate, clientId, loc, clipboard))

        # 标记游戏时长开始
        gamedata.incrPlayTime(userId, 0, gameId)
        # BI日志统计
        bireport.userBindUser(gameId, userId, clientId)
        bireport.reportGameEvent('BIND_USER',
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)
        evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
        TGHall.getEventBus().publishEvent(evt)


    def _isReconnect(self, userId, gameId, clientId, loc):
        if loc:
            locList = loc.split(':')
            for subLoc in locList:
                if subLoc != '0.0.0.0':
                    return True
        return False
        
    @markCmdActionMethod(cmd='user', action='bind', clientIdVer=3.3)
    def doUserBind_3_3(self, userId, gameId, clientId, isFirstuserInfo, clipboardContent):
        # 检查是否禁止登录
        if self.checkForceLogout(userId) :
            return

        self.updateBiggestHallVersion(userId, gameId, clientId)
        
        loc = ''
        isReconnect = False
        if isFirstuserInfo :
            loc = onlinedata.checkUserLoc(userId, clientId, 0)
            self.recoverUserTableChips(userId, clientId)
            isReconnect = self._isReconnect(userId, gameId, clientId, loc)
#         # 更新基本信息
#         halluser.updateUserBaseInfo(userId, clientId, runcmd.getMsgPack())
        clipboard = Clipboard.parse(clipboardContent)
        # 登录游戏处理
        isdayfirst, isCreate = halluser.loginGame(userId, gameId, clientId, clipboard)
        # 发送udata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 1, 0)
        # 发送gdata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 0, 1)
        # 发送响应消息
        if not isReconnect:
            self.helper.sendTodoTaskResponse(userId, gameId, clientId, isdayfirst)
        
        # 分析clipboardConent内容，根据分析结果 功能 
        TGHall.getEventBus().publishEvent(EventAfterUserLogin(userId, gameId, isdayfirst, isCreate, clientId, loc, clipboard))    
            
        # 标记游戏时长开始
        gamedata.incrPlayTime(userId, 0, gameId)
        # BI日志统计
        bireport.userBindUser(gameId, userId, clientId)
        bireport.reportGameEvent('BIND_USER',
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)

        evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
        TGHall.getEventBus().publishEvent(evt)


    @markCmdActionMethod(cmd='user', action='heart_beat', clientIdVer=0)
    def doUserHeartBeat(self, userId, gameId, clientId, isMust):
        hallled.doSendLedToUser(userId)
        clientIdVer = strutil.parseClientId(clientId)[1]
        if clientIdVer < 3.0:  # c++老版本斗地主才需要在heart_beat时下发m_signs 
            self._sendMatchSignsToUser(userId, gameId, clientId)
        self._sendOnLineInfoToUser(userId, gameId, clientId)

        if ftlog.is_debug():
            ftlog.debug("user|heart_beat", userId, gameId, clientId)
        from hall.entity import hallnewnotify
        hallnewnotify.pushNotify(userId, gameId, clientId)
        
    @markCmdActionMethod(cmd='user', action='sync_timestamp', clientIdVer=0)
    def doUserTimestamp(self, userId, gameId, clientId, isMust):
        '''
        同步服务器时间
        '''
        msg = MsgPack()
        msg.setCmd('user')
        msg.setResult('action', 'sync_timestamp')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('current_ts', pktimestamp.getCurrentTimestamp())
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='send_led', clientIdVer=0, lockParamName='send_led')
    def doSendLed(self, gameId, msg, ismgr, scope='hall', clientIds=[], isStopServer=False):
        hallled.sendLed(gameId, msg, ismgr, scope, clientIds, isStopServer)
        
    @markCmdActionMethod(cmd='gain_nslogin_reward', clientIdVer=0)
    def doGainNSLoginReward(self, userId, gameId, clientId):
        checkinOk, rewardAssetList, _checkinDays = \
            halldailycheckin.dailyCheckin.gainCheckinReward(gameId, userId)
        rewardChipCount = 0
        if checkinOk:
            datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(rewardAssetList))
            rewardChipCount = TYAssetUtils.getAssetCount(rewardAssetList, hallitem.ASSET_CHIP_KIND_ID)
        states = halldailycheckin.dailyCheckin.getStates(gameId, userId, pktimestamp.getCurrentTimestamp())
        mo = MsgPack()
        mo.setCmd('gain_nslogin_reward')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('rewardstate', TodoTaskHelper.translateDailyCheckinStates(states))
        mo.setResult('success', True)
        mo.setResult('chip', userchip.getChip(userId))
        mo.setResult('rewardchip', rewardChipCount)
        router.sendToUser(mo, userId)
        
    def _sendMatchSignsToUser(self, userId, gameId, clientId):
        signs = {}
        for roomdef in gdata.roomIdDefineMap().values() :
            if roomdef.shadowId == 0 and roomdef.configure.get('ismatch') :
                roomId = roomdef.roomId
                issignin = daobase.executeTableCmd(roomId, 0, 'SISMEMBER', 'signs:' + str(roomId), userId)
                if issignin :
                    signs[roomdef.bigRoomId] = 1
        if signs :
            mo = MsgPack()
            mo.setCmd('m_signs')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('signs', signs)
            router.sendToUser(mo, userId)


    def _sendOnLineInfoToUser(self, userId, gameId, clientId):
        all_count = _ONLINES.get(gameId, 30000)
        if all_count <= 0 :
            all_count = 30000
        rate = hallconf.getOnlineUserCountRate(clientId)
        mo = MsgPack()
        mo.setCmd('room_online_info')
        mo.setResult('gameId', gameId)
        mo.setResult('free_count', int(all_count * 0.5 * rate))
        mo.setResult('high_count', int(all_count * 0.3 * rate))
        mo.setResult('match_count', int(all_count * 0.2 * rate))
        mo.setResult('rooms', [])
        # 兼容
        mo.setParam('gameId', gameId)
        mo.setParam('free_count', int(all_count * 0.5 * rate))
        mo.setParam('high_count', int(all_count * 0.3 * rate))
        mo.setParam('match_count', int(all_count * 0.2 * rate))
        mo.setParam('rooms', [])
        router.sendToUser(mo, userId)


    @markCmdActionMethod(cmd='user', action='get_head_pics', clientIdVer=0)
    def doUserGetHeadPics(self, userId, gameId, clientId):
        mo = MsgPack()
        mo.setCmd('get_head_pics')
        mo.setResult('heads', halluser.getUserHeadPics(clientId))
        router.sendToUser(mo, userId)


    @markCmdActionMethod(cmd='user', action='set_star_id', clientIdVer=0)
    def doUserSetStarId(self, userId, gameId, clientId, starId):
        userdata.setAttr(userId, 'starid', starId)
        mo = MsgPack()
        mo.setCmd('set_star_id')
        mo.setResult('gameId', gameId)
        mo.setResult('starId', starId)
        router.sendToUser(mo, userId)


    @markCmdActionMethod(cmd='user', action='todo_task', clientIdVer=0)
    def doUserToDoTask(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doUserToDoTask, msg=', msg)
        return runcmd.newOkMsgPack(code=1)

    @markCmdActionMethod(cmd='new_user_reward', action='receive', clientIdVer=0)
    def doNewUserRewardReceive(self, userId, gameId, clientId):
        '''
        领取新手启动资金
        '''
        isSend, startChip, _final = hallstartchip.sendStartChip(userId, gameId, clientId)
        mo = MsgPack()
        mo.setCmd('new_user_reward')
        mo.setResult('action', 'receive')
        mo.setResult('coin', startChip if isSend else 0)
        router.sendToUser(mo, userId)
    
    @markCmdActionMethod(cmd='sub_member', action='unsub', clientIdVer=0)
    def doUnsubMember(self, userId, isTempVipUser):
        ftlog.info('AccountTcpHandler.doUnsubMember userId=', userId,
                   'isTempVipUser=', isTempVipUser)
        timestamp = pktimestamp.getCurrentTimestamp()
        hallsubmember.unsubscribeMember(HALL_GAMEID, userId, isTempVipUser, timestamp, 'UNSUB_MEMBER', 0)
    
    @classmethod
    def _doChangeNameCheck(self, userId, clientId):
        canRename, desc = hallrename.checkRename(HALL_GAMEID, userId)
        if canRename:
            return TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskRename(desc))
        else:
            info = TodoTaskShowInfo(desc, True)
            if hallrename.payOrder:
                product, _ = hallstore.findProductByPayOrder(HALL_GAMEID, userId, clientId, hallrename.payOrder)
                if product:
                    info.setSubCmd(TodoTaskPayOrder(product))
            return TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, info)
            
    @markCmdActionMethod(cmd='change_name', action='check', clientIdVer=0)
    def doChangeNameCheck(self, userId, clientId):
        self._doChangeNameCheck(userId, clientId)
    
    @classmethod
    def _doChangeNameTry(self, userId, clientId, newName):
#         renameConf = hallconf.getClientRenameConf(clientId)
#         if (renameConf
#             and not renameConf.get('containsSensitive', 1)
#             and keywords.isContains(newName)):
#             info = TodoTaskShowInfo(hallrename.stringRenameContainsSensitive)
#             return TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, info)
        code, info = hallrename.tryRename(HALL_GAMEID, userId, newName)
        if ftlog.is_debug():
            ftlog.debug('hallrename._doChangeNameTry->', code, info)

        CLIENT_VER = 4.57
        _, clientVer, _ = strutil.parseClientId(clientId)

        if ftlog.is_debug():
            ftlog.debug("_doChangeNameTry clientVer", userId, clientId, newName, code, info, clientVer)

        reInfo = ""
        if code == -3 :
            reInfo = "昵称没有变化"
        elif code == -2 :
            # 没有改名卡
            info = TodoTaskShowInfo(hallrename.stringRenameCardRequired, True)
            if hallrename.payOrder:
                product, _ = hallstore.findProductByPayOrder(HALL_GAMEID, userId, clientId, hallrename.payOrder)
                if product:
                    info.setSubCmd(TodoTaskPayOrder(product))
            return TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, info)
        elif code == 0 :
            reInfo = "昵称修改成功"
            # 改名成功
            if clientVer < CLIENT_VER:
                if ftlog.is_debug():
                    ftlog.debug("_doChangeNameTry ok", userId, clientId, newName, code, info, clientVer)
                return TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskPopTip(hallrename.stringRenameSuccessed))
        else:
            #reInfo = "修改昵称失败,请重试"
            reInfo = info
            # SDK改名失败
            if clientVer < CLIENT_VER:
                if ftlog.is_debug():
                    ftlog.debug("_doChangeNameTry fail", userId, clientId, newName, code, info, clientVer)
                return TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskPopTip(info))
                    
        mo = MsgPack()
        mo.setCmd('change_name')
        mo.setResult('action', 'try')
        mo.setResult('userId', userId)
        mo.setResult('code', code)
        mo.setResult('reInfo', reInfo)
        router.sendToUser(mo, userId)
        if ftlog.is_debug():
            ftlog.debug("_doChangeNameTry result",userId, clientId, newName, code, reInfo)
    @markCmdActionMethod(cmd='change_name', action='try', clientIdVer=0)
    def doChangeNameTry(self, userId, clientId, newName):
        self._doChangeNameTry(userId, clientId, newName)
    
    @markCmdActionMethod(cmd='five_star_rating', clientIdVer=0)
    def doFiveStarRating(self, userId, clientId):
        fivestarrate.onFiveStarRated(userId, clientId, pktimestamp.getCurrentTimestamp())
    
    def _doCashGetCash(self, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('cash')
        mo.setResult('action', 'get_cash')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        msg = runcmd.getMsgPack()
        try:
            wxappId = msg.getParam('wxappId')
            value = msg.getParam('value')
            if not isstring(wxappId):
                raise TYBizException(-1, 'wxappId参数错误')
            if not isinstance(value, int) or value <= 0:
                raise TYBizException(-1, 'value参数错误')
            mo.setResult('value', value)
            hallexchange.requestExchangeCash(userId, value, wxappId, pktimestamp.getCurrentTimestamp())
        except TYBizException, e:
            ftlog.error('AccountTcpHandler._doCashGetCash',
                        'userId=', userId,
                        'clientId=', clientId,
                        'msg=', msg.pack())
            mo.setResult('code', e.errorCode)
            mo.setResult('info', e.message)
        router.sendToUser(mo, userId)
            
    @markCmdActionMethod(cmd='cash', action='get_cash', clientIdVer=0)
    def doCashGetCash(self, userId, clientId):
        self._doCashGetCash(HALL_GAMEID, userId, clientId)
    
def updateOnLineInfos(event):
    if event.count % 10 != 0 :
        return

    allcount = 0
    ucounts = {}
    for gameId in gdata.gameIds():
        count, _, _ = bireport.getRoomOnLineUserCount(gameId)
        allcount += count
        ucounts[gameId] = count
    ucounts[HALL_GAMEID] = allcount

    _ONLINES.clear()
    _ONLINES.update(ucounts)
    ftlog.debug('updateOnLineInfos->', _ONLINES)
   


