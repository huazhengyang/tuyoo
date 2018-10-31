# -*- coding:utf-8 -*-
'''
Created on 2017年2月15日

@author: zhaojiangang
'''
from dizhu.entity import dizhupopwnd, dizhu_score_ranking, dizhu_giftbag
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games.tablecommonproto import DizhuTableProtoCommonBase
from dizhu.servers.util.rpc import new_table_remote, task_remote
from dizhucomm.core.const import StandupReason
from dizhucomm.entity import commconf
from dizhucomm.servers.util.rpc import comm_table_remote
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router


class DizhuTableProtoNormalBase(DizhuTableProtoCommonBase):
    def __init__(self, tableCtrl):
        super(DizhuTableProtoNormalBase, self).__init__(tableCtrl)
    
    def _fillWinsTask(self, mp, seat):
        playerTask = self.room.winStreakTask.getPlayerTask(seat.player)
        if playerTask and playerTask.progress > 0:
            winstask = {}
            winstask['wins'] = playerTask.progress if playerTask else 0
            winstask['reward'] = playerTask.reward
            mp.setResult('winstask', winstask)
        else:
            mp.rmResult('winstask')

    def _fillDailyPlayTimesWinsTask(self, mp, seat, index):
        '''
        每日局数胜利奖励任务
        '''
        seatInfos = mp.getResult('seats')
        if not seatInfos:
            return

        # 是否返回奖励任务标志
        if not self.room.roomConf.get('dailyPlayTimesWinTaskFlag', 0):
            return

        playerTimesWinTask = self.room.dailyPlayTimesWinTask.getPlayerTask(seat.player.userId)
        if playerTimesWinTask and playerTimesWinTask.dailyPlayTimes > 0 and playerTimesWinTask.reward:
            reward = playerTimesWinTask.reward
            winreward = {
                'count': reward['count'],
                'itemId': reward['itemId'],
            }
            seatInfos[index].update({"winreward": winreward})

    def sendWinloseRes(self, result):
        details = self.buildResultDetails(result)
        mp = self.buildWinloseRes(result, details, 1)
        for index, seat in enumerate(self.table.seats):
            # 新手任务
            status = task_remote.getTaskProgress(DIZHU_GAMEID, seat.userId)
            if seat.player and not seat.isGiveup:
                mp.rmResult('newertask')
                if status:
                    mp.setResult('newertask', status)
                # 分享时的二维码等信息
                mp.setResult('share', commconf.getNewShareInfoByCondiction(self.gameId, seat.player.clientId, 'winstreak'))

                self._fillWinsTask(mp, seat)
                self._fillDailyPlayTimesWinsTask(mp, seat, index)
                router.sendToUser(mp, seat.userId)

    def buildTableInfoResp(self, seat, isRobot):
        mp = DizhuTableProtoCommonBase.buildTableInfoResp(self, seat, isRobot)
        winstreak = {}
        playerTask = self.room.winStreakTask.getPlayerTask(seat.player)
        cur = playerTask.progress if playerTask else 0
        if cur >= len(self.room.winStreakTask.taskList):
            cur = 0
        winstreak['cur'] = cur
        winstreak['maxWinStreak'] = playerTask.maxWinStreak if playerTask else 0
        rewards = []
        for task in self.room.winStreakTask.taskList:
            rewards.append(task.reward)
        winstreak['rewards'] = rewards
        winstreak['imgs'] = self.room.winStreakTask.taskPictures
        mp.setResult('winstreak', winstreak)

        # 房间属于哪个积分榜
        scoreRankingConf = dizhu_score_ranking.getConf()
        bigRoomId = gdata.getBigRoomId(self.roomId)
        rankDef = scoreRankingConf.rankDefineForRoomId(bigRoomId)
        if not scoreRankingConf.closed and rankDef and rankDef.switch == 1:
            mp.setResult('scoreboardFlag', rankDef.rankId)

        taskInfo = task_remote.getNewbieTaskInfo(DIZHU_GAMEID, seat.userId, seat.player.playShare.totalCount)
        if taskInfo is not None:
            mp.setResult('newertask', taskInfo)

        winSteakBuff, loseStreakBuff = dizhu_giftbag.checkUserGiftBuff(seat.player.userId)
        if winSteakBuff:
            mp.setResult('buff', 'winSteakBuff')
        elif loseStreakBuff:
            mp.setResult('buff', 'loseStreakBuff')

        dailyPlayCount = new_table_remote.doGetUserDailyPlayCount(seat.userId, DIZHU_GAMEID)
        mp.setResult('dailyPlay', dailyPlayCount)
        if ftlog.is_debug():
            ftlog.debug('normalbase.tableproto.buildTableInfoResp.checkUserGiftBuff',
                        'bigRoomId=', bigRoomId,
                        'winSteakBuff=', winSteakBuff,
                        'loseStreakBuff=', loseStreakBuff,
                        'mp=', mp)
        return mp
    
    def _do_table__replay_save(self, msg):
        mo = MsgPack()
        mo.setCmd('table')
        mo.setResult('action', 'replay_save')
        userId = msg.getParam('userId')
        roundId = msg.getParam('roundId')
        try:
            self.tableCtrl.saveReplay(userId, roundId)
        except TYBizException, e:
            mo.setResult('code', e.errorCode)
            mo.setResult('info', e.message)
        router.sendToUser(mo, userId)
        return mo
    
    def _do_table__leave(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoNormalBase._do_table__leave',
                        'msg=', msg)
        userId = msg.getParam('userId')
        tableId = msg.getParam('tableId')
        reason = msg.getParam('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
        result = {
            'gameId':self.gameId,
            'userId':userId,
            'roomId':self.roomId,
            'tableId':tableId,
            'reason':reason
        }
        if not self.tableCtrl.leaveTable(userId, reason):
            result['reason'] = TYRoom.LEAVE_ROOM_REASON_FORBIT
        clientId = sessiondata.getClientId(userId)
        self.sendTableLeaveRes(userId, clientId, result)

    def _onGameStart(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onGameStart',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendGameStartResAll()
        self.sendLuckyBoxToAll()

    def _onStandup(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onStandup',
                        'tableId=', event.table.tableId,
                        'seatId=', event.seat.seatId,
                        'userId=', event.player.userId,
                        'reason=', event.reason)
        if event.reason == StandupReason.GAME_OVER:
            try:
                new_table_remote.sendUserBenefitsIfNeed(DIZHU_GAMEID, event.player.userId, event.table.room.roomId)
            except Exception, e:
                ftlog.warn('DizhuTableProtoNormalBase._onStandup sendUserBenefitsIfNeed err=', e.message)

        if event.reason not in (StandupReason.GAME_OVER,
                                StandupReason.GAME_ABORT,
                                StandupReason.FORCE_CLEAR):
            self.sendTableInfoResAll()

        if event.reason != StandupReason.FORCE_CLEAR:
            self.sendRobotNotifyShutDown(None)

    def sendLuckyBoxToAll(self):
        luckyBox = self.table.room.roomConf.get('luckyBox', None)
        if not luckyBox:
            return
        for seat in self.table.seats:
            if seat.player.isRobotUser:
                continue
            task = dizhupopwnd.generateDizhuLuckyBoxTodoTask(seat.player.userId, seat.player.clientId)
            if not task:
                continue
            mo = self.buildTableMsgRes('table_call', 'lucky_box')
            mo.setResult('task', task.toDict())
            self.sendToSeat(mo, seat)

    def _do_table__tbox(self, msg):
        # 开宝箱需要判断是否是发送宝箱还是直接发奖
        userId = msg.getParam('userId')
        try:
            data = comm_table_remote.doTableTreasureBox(self.gameId, userId, self.bigRoomId)
            mo = self.buildTableMsgRes('table_call', 'tbox')
            mo.setResult('userId', userId)
            mo.updateResult(data)

            # if TreasureChestHelper.isValidUser(userId):
            #     rewards = data.get('items', [])
            #     rw = []
            #     for r in rewards:
            #         itemId = r['item']
            #         if itemId == 'CHIP':
            #             itemId = 'user:chip'
            #         elif itemId == 'COUPON':
            #             itemId = 'user:coupon'
            #         rw.append({'itemId': itemId, 'count': r['count']})
            #     # 广播事件
            #     event_remote.publishTreasureChestEvent(userId, DIZHU_GAMEID, TREASURE_CHEST_TYPE_AS_TREASUREBOX, rw)
            #     mo.setResult('treasureChest', 1)

            router.sendToUser(mo, userId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table__tbox',
                       'msg=', msg,
                       'e=', e)
