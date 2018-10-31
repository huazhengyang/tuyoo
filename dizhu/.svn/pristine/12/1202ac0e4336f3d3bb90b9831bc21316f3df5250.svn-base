# -*- coding=utf-8
'''
Created on 2015年8月6日

@author: zhaojiangang
'''
import json

from dizhu.activities.toolbox import UserInfo
from dizhu.entity import dizhuconf, dizhutodotask
from dizhucomm.core.const import UserReportReason
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.table.rpc import normal_table_room_remote
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import halldailycheckin, datachangenotify, hallitem, \
    hallstartchip
from hall.entity.todotask import TodoTaskHelper, TodoTaskIssueStartChip, \
    TodoTaskQuickStartTip
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz import bireport
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.dao import userchip, gamedata, daoconst
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil, webpage
import poker.util.timestamp as pktimestamp
from poker.util.constants import CLIENT_SYS_H5
from poker.entity.configure import gdata
import poker.entity.biz.message.message as pkmessage

@markCmdActionHandler
class AccountTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(AccountTcpHandler, self).__init__()

    def _check_param_actionType(self, msg, key, params):
        value = msg.getParam(key, 0)
        if not isinstance(value, int):
            return 'Bad gameNum param', None
        return None, value

    def _check_param_gameNum(self, msg, key, params):
        value = msg.getParam(key)
        if not isinstance(value, (str, unicode)):
            return 'Bad gameNum param', None
        return None, value
    
    def _check_param_otherPlayerId1(self, msg, key, params):
        value = msg.getParam(key)
        if not isinstance(value, int):
            return 'Bad otherPlayerId1 param', None
        return None, value
    
    def _check_param_otherPlayerId2(self, msg, key, params):
        value = msg.getParam(key)
        if not isinstance(value, int):
            return 'Bad otherPlayerId1 param', None
        return None, value

    def _check_param_otherPlayerId(self, msg, key, params):
        value = msg.getParam(key)
        if not isinstance(value, int):
            return 'Bad otherPlayerId param', None
        return None, value

    def _check_param_reasons(self, msg, key, params):
        value = msg.getParam(key)
        if not isinstance(value, list):
            return 'Bad reasons param', None
        return None, value

    @markCmdActionMethod(cmd='complain', action='complain', clientIdVer=0, scope='game')
    def doComplain(self, userId, gameId, clientId, roomId0, tableId0,
                   gameNum, otherPlayerId1, otherPlayerId2):
        '''
        牌局投诉
        '''
        self._do_complain(userId, gameId, clientId, roomId0, tableId0,
                          gameNum, otherPlayerId1, otherPlayerId2)

    def _do_complain(self, userId, gameId, clientId, roomId0, tableId0,
                     gameNum, otherPlayerId1, otherPlayerId2):
        mo = MsgPack()
        mo.setCmd('complain')
        roomId = roomId0
        roomId0 = gdata.getBigRoomId(roomId0)
        complainConf, tips = dizhuconf.getComplainInfo(roomId0)
        if not complainConf:
            mo.setError(1, '本房间不支持投诉')
            router.sendToUser(mo, userId)
            return mo

        comMoney = complainConf['fee']
        currentUserChip = userchip.getChip(userId)
        if complainConf['fee'] <= (currentUserChip):
            trueDelta, _chip = userchip.incrChip(userId, gameId, -complainConf['fee'],
                                                 daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                 'GAME_COMPLAIN_INSURANCE', roomId0, clientId)
            # 金币不足支付举报的，返回错误。现改为'﻿金币不足扔可继续举报'所以注释掉
            if trueDelta != -complainConf['fee']:
                comMoney = trueDelta
                # mo.setError(2, tips.get("error", ""))
                # router.sendToUser(mo, userId)
                # return mo
        else:
            comMoney = 0
        if ftlog.is_debug():
            ftlog.debug('AccountTcpHandler.doComplain userId=', userId,
                        'userchip=', currentUserChip,
                        'fee=', complainConf['fee'],
                        'comMoney=', comMoney)

        complain_time = pktimestamp.getCurrentTimestamp()
        params = {
            'act': 'api.getComplaintDetailInfo',
            'gameid': gameId,
            'playerId': userId,
            'comtTime': complain_time,
            'roomId': roomId0,
            'PlayerOneId': otherPlayerId1,
            'PlayerTwoId': otherPlayerId2,
            'tableId': tableId0,
            'gameSign': gameNum,
            'comMoney': complainConf['fee']
        }
        try:
            roundNum = int(gameNum.split('_')[-1])
        except Exception:
            roundNum = 0

        try:
            ret, complainCodec = normal_table_room_remote.getComplainContent(gameId, userId, roomId, tableId0, gameNum)
            if ret != 0:
                mo.setError(3, complainCodec)
                router.sendToUser(mo, userId)
                if comMoney > 0:
                    userchip.incrChip(userId, gameId, comMoney,
                                      daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                      'GAME_COMPLAIN_INSURANCE', roomId0, clientId)
                    datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
                ftlog.error('doComplain userId=', userId, 'gameId=', gameId, 'clientId=', clientId, 'err=',
                            complainCodec)
            else:
                mo.setResult('success', {"code": 1, 'info': tips.get("succ", "")})
                pkmessage.sendPrivate(9999, userId, 0, tips.get("succ", ""))
                router.sendToUser(mo, userId)
                datachangenotify.sendDataChangeNotify(gameId, userId, ['chip', 'message'])
                bireport.reportGameEvent('GAME_COMPLAIN_INSURANCE', userId, DIZHU_GAMEID, params['roomId'],
                                         params['tableId'], roundNum, params['comMoney'], 0, 0, [
                                             params['PlayerOneId'], params['PlayerTwoId'], params['comtTime'],
                                             strutil.dumps(complainCodec)
                                         ], clientId, 0, 0)
                ftlog.info('report_bi_game_event', 'eventId=GAME_COMPLAIN_INSURANCE', 'userId=', userId, 'gameId=',
                           DIZHU_GAMEID, 'params=', params)
        except Exception, e:
            mo.setError(4, '操作失败')
            router.sendToUser(mo, userId)
            if comMoney > 0:
                userchip.incrChip(userId, gameId, comMoney,
                                  daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                  'GAME_COMPLAIN_INSURANCE', roomId0, clientId)
                datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
            ftlog.error('doComplain userId=', userId, 'gameId=', gameId, 'clientId=', clientId, 'err=', e.message)
            
    @markCmdActionMethod(cmd='gain_nslogin_reward', clientIdVer=0, scope='game')
    def doGainNSLoginReward(self, userId, gameId, clientId, actionType):
        checkinOk, rewardAssetList, _checkinDays = \
            halldailycheckin.dailyCheckin.gainCheckinReward(gameId, userId, None, actionType)
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
        self._doAfterGainNsLoginReward(gameId, userId, clientId)
        
    def _doAfterGainNsLoginReward(self, gameId, userId, clientId):
        # todo task
        # 如果是3.3的新用户则需要发送启动资金 并发送启动资金todotask
        # 如果是老用户并没有玩过游戏 发送快速游戏提示的todotask
        # 如果是老用户并且玩过游戏 发送活动弹窗
        if ftlog.is_debug():
            ftlog.debug('AccountTcpHandler._doAfterGainNsLoginReward gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId)
        
        clientsys, clientVer, _ = strutil.parseClientId(clientId)
        if clientVer > 3.32 and clientVer < 3.7 or clientsys == CLIENT_SYS_H5:
#             clist = gamedata.getGameAttr(userId, gameId, 'history_clientids')
#             try:
#                 clist = json.loads(clist) if clist else []
#             except:
#                 clist = []
            
            send, startChip, final = hallstartchip.sendStartChip(userId, gameId, clientId)
            if send:
                if ftlog.is_debug():
                    ftlog.debug('AccountTcpHandler._doAfterGainNsLoginReward gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'sendStartChip=', (send, startChip, final))
                assetKind = hallitem.itemSystem.findAssetKind(hallitem.ASSET_ITEM_NEWER_GIFT_KIND_ID)
                pic = assetKind.pic if assetKind else ''
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskIssueStartChip(startChip, final, pic, '您有一个新手礼包在‘我的道具’里'))
            else:
                winrate = gamedata.getGameAttr(userId, gameId, 'winrate')
                try:
                    winrate = json.loads(winrate)
                    play_count = winrate['pt']
                except:
                    return 
                
                if ftlog.is_debug():
                    ftlog.debug('AccountTcpHandler._doAfterGainNsLoginReward gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'winrate=', winrate,
                                'playCount=', play_count)
                    
                if play_count <= 0:
                    mo = TodoTaskHelper.makeTodoTaskMsg(gameId, userId, TodoTaskQuickStartTip())
                    router.sendToUser(mo, userId)
                else:
                    conf = dizhuconf.getPopActivityTemplate(clientId)
                    if ftlog.is_debug():
                        ftlog.debug('AccountTcpHandler._doAfterGainNsLoginReward gameId=', gameId,
                                    'userId=', userId,
                                    'clientId=', clientId,
                                    'winrate=', winrate,
                                    'popActivityTemplate=', conf)
                    if conf:
                        todotask = dizhutodotask.makeTodoTaskPopActivity(gameId, userId, clientId, conf)
                        if todotask:
                            TodoTaskHelper.sendTodoTask(gameId, userId, todotask)

    @markCmdActionMethod(cmd='dizhu', action='user_report', clientIdVer=0, scope='game')
    def doReport(self, gameId, userId, otherPlayerId, reasons):
        '''
        举报用户, reportDetail  '{"count":1,"timestamp":1435345}'   reportedDetail '{'1':5,'2':5,'count':100,'timestamp':34534}
        '''
        self._doReport(gameId, userId, otherPlayerId, reasons)

    @classmethod
    def _doReport(cls, gameId, userId, otherPlayerId, reasons):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'user_report')
        # 检测举报条件
        reportDetail = gamedata.getGameAttr(userId, gameId, 'report')
        reportDetail = strutil.loads(reportDetail) if reportDetail else {}
        reportCount = reportDetail.setdefault('count', 0)
        reportTimestamp = reportDetail.setdefault('timestamp', 1356969600)
        currentTimestamp = pktimestamp.getCurrentTimestamp()

        if not pktimestamp.is_same_day(currentTimestamp, reportTimestamp):
            reportDetail['count'] = 0
        else:
            if reportCount >= 10:
                mo.setError(1, '举报过于频繁，系统正在核实举报信息')
                router.sendToUser(mo, userId)
                return

            if currentTimestamp - reportTimestamp < 180:
                mo.setError(2, '举报过于频繁，系统正在核实举报信息')
                mo.setResult('remaining', 180 - (currentTimestamp - reportTimestamp))
                router.sendToUser(mo, userId)
                return

        # 发送消息给举报者, 增加举报者举报次数
        reportDetail['count'] += 1
        reportDetail['timestamp'] = currentTimestamp
        gamedata.setGameAttr(userId, gameId, 'report', strutil.dumps(reportDetail))
        reportStr = ''
        for reason in reasons:
            reportStr += cls._getTipByReason(reason)
        tip = '举报反馈：\n  您举报了玩家【%s】。\n  我们会核实原因，进行相应处理。' % (UserInfo.getNickname(otherPlayerId))
        mo.setResult('success', 1)
        mo.setResult('tip', tip)
        router.sendToUser(mo, userId)
        pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, tip)

        # 发送消息给被举报者，只有在原因①/③的情况下，被举报玩家才会收到信息，若被举报玩家同时因①③被举报，则优先使用①的被举报文本。
        # 增加被举报者举报次数
        reportedDetail = gamedata.getGameAttr(otherPlayerId, gameId, 'reported')
        reportedDetail = strutil.loads(reportedDetail) if reportedDetail else {}
        reportedDetail.setdefault('count', 0)

        for r in reasons:
            if r in [UserReportReason.NEGATIVE, UserReportReason.OFFLINE]:
                reportedDetail['count'] += 1
                if not pktimestamp.is_same_day(currentTimestamp, reportTimestamp):
                    reportedDetail.setdefault(str(r), 0)
                    reportedDetail[str(r)] = 0
                else:
                    reportedDetail.setdefault(str(r), 0)
                    reportedDetail[str(r)] += 1
        gamedata.setGameAttr(otherPlayerId, gameId, 'reported', strutil.dumps(reportedDetail))

        tip = ''
        if UserReportReason.NEGATIVE in reasons:
            tip = '举报信息：\n  您因<%s>被玩家举报。\n  系统已记录，下次要认真一些喔~' % cls._getTipByReason(UserReportReason.NEGATIVE)
            if reportedDetail.setdefault(str(UserReportReason.NEGATIVE), 0) > 5:
                tip = ''

        if UserReportReason.OFFLINE in reasons:
            if reportedDetail.setdefault(str(UserReportReason.OFFLINE), 0) > 5:
                tip = tip
            else:
                tip = '举报信息：\n  您因<%s>被玩家举报。\n  快去找一个好的网络环境吧~' % cls._getTipByReason(UserReportReason.OFFLINE)

        if tip:
            pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, otherPlayerId, tip)

    @classmethod
    def _getTipByReason(cls, reason):
        if reason == UserReportReason.OFFLINE:
            return '频繁托管'
        elif reason == UserReportReason.NEGATIVE:
            return '态度消极'
        elif reason == UserReportReason.LOW_LEVEL:
            return '水平过低'
        elif reason == UserReportReason.ILLEGAL_AVATAR:
            return '违规头像'
        elif reason == UserReportReason.ILLEGAL_NICKNAME:
            return '违规昵称'
        else:
            return ''


