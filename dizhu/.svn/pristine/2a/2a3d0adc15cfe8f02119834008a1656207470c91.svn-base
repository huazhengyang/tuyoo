# -*- coding:utf-8 -*-
'''
Created on 2017年4月10日

@author: wangyonghui
@目的： 特殊牌型有动画效果， 要延迟。由于配置在game的public中，所以抽象出一个game6 下 的共有层，起到灵活配置作用
'''
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.util.rpc import task_remote, new_table_remote
from dizhucomm.entity import commconf
from dizhucomm.table.proto import DizhuTableProto
from dizhu.entity import dizhuconf
import freetime.util.log as ftlog
from freetime.core.tasklet import FTTasklet
from poker.protocol import router


class DizhuTableProtoCommonBase(DizhuTableProto):
    def _onOutCard(self, event):
        cards = event.validCards.cards if event.validCards else []
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoCommonBase._onOutCard',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'cards=', cards)
        try:
            # 炸弹红包事件
            if event.validCards and (event.validCards.isHuoJian() or event.validCards.isZhaDan()):
                mixRoomId = None
                roomName = event.table.room.roomConf.get('name', '')
                if hasattr(event.seat.player, 'mixConf') and event.seat.player.mixConf.get('roomId'):
                    mixRoomId = event.seat.player.mixConf.get('roomId')
                    roomName = event.seat.player.mixConf.get('name')
                # 红包赛混房
                if hasattr(event.seat.player, 'mixId') and event.seat.player.mixId and event.seat.player.mixId.isdigit():
                    mixRoomId = int(event.seat.player.mixId)
                    for fr in event.table.room.roomConf.get('matchConf', {}).get('feeRewardList', []):
                        if fr.get('mixId') == str(mixRoomId):
                            roomName = fr.get('roomName')
                new_table_remote.publishUserTableBomb(event.seat.userId, event.table.roomId, event.table.tableId, [(s.userId, s.seatId) for s in event.table.seats], mixRoomId=mixRoomId, roomName=roomName)
        except Exception, e:
            ftlog.error('DizhuTableProtoCommonBase._onOutCard',
                        'userId=', event.seat.userId,
                        'roomId=', event.table.roomId,
                        'err=', e.message)
        self.sendOutCardsRes(event.seat, cards, event.prevCards, event.oper)
        # 判断牌型，增加延迟
        delayNextStep = False
        if event.validCards and (
                                event.validCards.isSanShun() or event.validCards.isFeiJiDai1() or event.validCards.isFeiJiDai2() or event.validCards.isHuoJian() or event.validCards.isZhaDan()):
            delayNextStep = True

        if delayNextStep:
            interval = dizhuconf.getPublic().get('bombNextDelay', 0)
            if interval > 0:
                FTTasklet.getCurrentFTTasklet().sleepNb(interval)

    def sendTableInfoRes(self, seat):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoCommonBase.sendTableInfoRes',
                        'userId=', seat.userId,
                        caller=self)
        
        logUserIds = [66706022]
        if seat.player and seat.userId in logUserIds:
            ftlog.info('DizhuTableProtoCommonBase.sendTableInfoRes beforeSentMsg',
                       'tableId=', self.tableId,
                       'userId=', seat.userId,
                       'gameClientVer=', seat.player.gameClientVer,
                       'isGiveup=', seat.isGiveup,
                       'isQuit=', seat.player.isQuit,
                       'seats=', [(s.userId, s.seatId) for s in self.table.seats])
            
        if seat.player and not seat.isGiveup and not seat.player.isQuit:
            mp = self.buildTableInfoResp(seat, 0)
            taskInfo = task_remote.getNewbieTaskInfo(DIZHU_GAMEID, seat.userId, seat.player.playShare.totalCount)
            if taskInfo is not None and not self.table.room.isMatch:
                mp.setResult('newertask', taskInfo)
            router.sendToUser(mp, seat.userId)
            if seat.userId in logUserIds:
                ftlog.info('DizhuTableProtoCommonBase.sendTableInfoRes sentMsg',
                           'tableId=', self.tableId,
                           'userId=', seat.userId,
                           'gameClientVer=', seat.player.gameClientVer,
                           'seats=', [(seat.userId, seat.seatId) for seat in self.table.seats],
                           'mp=', mp.pack())

    def sendWinloseRes(self, result):
        '''
         新手任务奖励发奖必须在结算时
         重写这个方法的原因：
         dizhucomm不能调用dizhu的方法，所以在dizhu里重写dizhucomm的方法
        '''
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoCommonBase.sendWinloseRes, result=', result)
        details = self.buildResultDetails(result)
        mp = self.buildWinloseRes(result, details, 1)
        for _, seat in enumerate(self.table.seats):
            # 新手任务
            status = task_remote.getTaskProgress(DIZHU_GAMEID, seat.userId)
            if seat.player and not seat.isGiveup:
                mp.rmResult('newertask')
                if status and not self.table.room.isMatch:
                    mp.setResult('newertask', status)
                # 分享时的二维码等信息
                mp.setResult('share', commconf.getNewShareInfoByCondiction(self.gameId, seat.player.clientId, 'winstreak'))
                router.sendToUser(mp, seat.userId)
