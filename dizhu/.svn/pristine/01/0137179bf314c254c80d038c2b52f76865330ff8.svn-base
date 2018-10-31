# -*- coding:utf-8 -*-
'''
Created on 2015年12月1日

@author: zhaojiangang
'''
import time

from dizhu.gametable.dizhu_arena_sender import DizhuArenaSender
from dizhu.gametable.dizhu_table import DizhuTable
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.dao import sessiondata, onlinedata
from poker.entity.game.rooms.big_match_ctrl.const import AnimationType
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from dizhu.entity import dizhuconf
from freetime.core.tasklet import FTTasklet
from poker.util import strutil

class DizhuArenaMatchTable(DizhuTable):
    MSTART_SLEEP = 3
    
    def __init__(self, room, tableId):
        super(DizhuArenaMatchTable, self).__init__(room, tableId)
        self._match_table_info = None
        self.gamePlay.sender = DizhuArenaSender(self)
        self._doMatchTableClear()

    def _doTableManage(self, msg, action):
        '''
        处理来arena比赛的table_manage命令
        '''
        if action == 'm_table_start' :
            self.doMatchTableStart(msg)
            return

        if action == 'm_table_clear' :
            self.doMatchTableClear(msg)
            return
        
    def _doSit(self, msg, userId, seatId, clientId): 
        '''
        玩家操作, 尝试再当前的某个座位上坐下
        '''
        if not self._match_table_info:
            self.gamePlay.sender.sendQuickStartRes(userId, clientId, {'isOK':False, 'reason':TYRoom.LEAVE_ROOM_REASON_MATCH_END})
            return
        super(DizhuArenaMatchTable, self)._doSit(msg, userId, seatId, clientId)
        
    def checkMatchTableInfo(self, matchTableInfo):
        return True
    
    def doMatchTableStart(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuArenaMatchTable.doMatchTableStart gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'matchId=', self.room.bigmatchId,
                        'msg=', msg)
        startTime = time.time()
        tableInfo = msg.getKey('params')
        if self.checkMatchTableInfo(tableInfo):
            self._doUpdateTableInfo(tableInfo)
            self._doMatchQuickStart()
        if ftlog.is_debug():
            ftlog.debug('DizhuArenaMatchTable.doMatchTableStart gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'matchId=', self.room.bigmatchId,
                        'msg=', msg,
                        'usedTime=', (time.time() - startTime))
            
    def doMatchTableClear(self, msg):
        params = msg.getKey('params')
        matchId = params.get('matchId', -1)
        ccrc = params.get('ccrc', -1)
        
        if ftlog.is_debug():
            ftlog.debug('DizhuArenaMatchTable.doMatchTableClear gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'matchId=', self.room.bigmatchId,
                        'paramsMatchId=', matchId,
                        'paramsCCRC=', ccrc)
            
        if matchId != self.room.bigmatchId:
            ftlog.error('DizhuArenaMatchTable.doMatchTableClear gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'matchId=', self.room.bigmatchId,
                        'paramsMatchId=', matchId,
                        'paramsCCRC=', ccrc,
                        'msg=', msg,
                        'err=', 'DiffMatchId')
            return
         
        if not self._match_table_info:
            ftlog.error('DizhuArenaMatchTable.doMatchTableClear gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'matchId=', self.room.bigmatchId,
                        'paramsMatchId=', matchId,
                        'paramsCCRC=', ccrc,
                        'msg=', msg,
                        'err=', 'AlreadyClear')
            return
         
        if ccrc != self._match_table_info['ccrc']:
            ftlog.error('DizhuArenaMatchTable.doMatchTableClear gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'matchId=', self.room.bigmatchId,
                        'paramsMatchId=', matchId,
                        'paramsCCRC=', ccrc,
                        'msg=', msg,
                        'err=', 'DiffCCRC')
            return
         
        self._doMatchTableClear()
        
    def _doMatchTableClear(self):
        for seatIndex in xrange(len(self.seats)):
            uid = self.seats[seatIndex].userId
            if uid > 0:
                clientId = sessiondata.getClientId(uid)
                #比赛阶段清理牌桌时无需刷新客户端
                self.gamePlay.doStandUp(uid, seatIndex+1, TYRoom.LEAVE_ROOM_REASON_MATCH_END, clientId)
        self.clear(None)
        self._match_table_info = None
    
    def _doUpdateTableInfo(self, tableInfo):
        self._match_table_info = tableInfo
        
    def _doMatchQuickStart(self):
        tableInfo = self._match_table_info
        
        userInfos = tableInfo['userInfos']
        userIds = []
        userSeatList = []
         
        for i, userInfo in enumerate(userInfos):
            this_seat = self.seats[i]
            userIds.append(userInfo['userId'])
            this_seat.userId = userInfo['userId']
            this_seat.state = TYSeat.SEAT_STATE_WAIT
            this_seat.call123 = -1
            userSeatList.append((userInfo['userId'], i + 1))
        
        # 初始化用户数据
        for x in xrange(len(self.players)):
            self.players[x].initUser(0, 1)

        ctrlRoomId = self.room.ctrlRoomId
        ctrlRoomTableId = ctrlRoomId * 10000
        for userId, seatId in userSeatList :
            onlinedata.removeOnlineLoc(userId, ctrlRoomId, ctrlRoomTableId)
            onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
            if ftlog.is_debug() :
                ftlog.debug("|locList:", onlinedata.getOnlineLocList(userId), caller=self)
                
        # 做一个延迟
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        inter = delayConf.get('waitToNextMatch', 3)
        FTTasklet.getCurrentFTTasklet().sleepNb(inter)
    
        for x in xrange(len(self.seats)) :
            this_seat = self.seats[x]
            if this_seat.userId > 0:
                mq = MsgPack()
                mq.setCmd('quick_start')
                mq.setResult('userId', this_seat.userId)
                mq.setResult('gameId', self.gameId)
                mq.setResult('roomId', self.roomId)
                mq.setResult('tableId', self.tableId)
                mq.setResult('seatId', x + 1)
                # 发送用户的quick_start
                router.sendToUser(mq, this_seat.userId)

        # 发送table_info
        self.gamePlay.sender.sendTableInfoResAll()
         
        delay = self._playAnimation(userInfos)
        
        if delay > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(delay)
        
        for x in xrange(len(self.players)):
            self.gamePlay.doReady(self.players[x], False)
            
        self._sendRanks(userInfos)

    def _playAnimation(self, userInfos):
        delay = 0
        for _, userInfo in enumerate(userInfos):
            animationType = userInfo['stage'].get('animationType')
            if ftlog.is_debug():
                ftlog.debug('DizhuArenaMatchTable._playAnimation userId=', userInfo['userId'],
                            'stage=', userInfo['stage'])
            if animationType is not None and animationType != AnimationType.UNKNOWN: 
                msg = MsgPack()
                msg.setCmd('m_play_animation')
                msg.setResult('gameId', self.gameId)
                msg.setResult('roomId', self.roomId)
                msg.setResult('tableId', self.tableId)
                msg.setResult('type', userInfo['stage']['animationType'])
                isStartStep = userInfo['stage'].get('index') == 0
                if isStartStep:
                    msg.setResult('isStartStep', 1)
                router.sendToUser(msg, userInfo['userId'])
                delay = max(delay, self._getAnimationDelay(animationType, isStartStep, userInfo['clientId']))
        return delay
    
    def _getAnimationDelay(self, animationType, isStartStep, clientId):
        _, clientVer, _ = strutil.parseClientId(clientId)
        if str(clientVer) < 3.77:
            return self.MSTART_SLEEP
        
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay')
        if not delayConf:
            return 3
        valKey = 'startStep'
        if not isStartStep:
            valKey = 'type' + str(animationType)
        return delayConf.get(valKey, 3)
    
    def _sendRanks(self, userInfos):
        for _, userInfo in enumerate(userInfos):
            mrank = MsgPack()
            mrank.setCmd('m_rank')
            ranktops = []
            ranktops.append({'userId':userInfo['userId'],
                             'name':userInfo['userName'],
                             'score':userInfo['score'],
                             'rank':userInfo['rank']})
            mrank.setResult('mranks', ranktops)
            router.sendToUser(mrank, userInfo['userId'])
    
    def _buildNote(self, userId, tableInfo):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        for userInfo in tableInfo['userInfos']:
            if userInfo['userId'] == userId:
                return u'%s人晋级，第%s副（共%s副）' % (userInfo['stage']['riseCount'],
                                                    userInfo['cardCount'],
                                                    userInfo['stage']['cardCount'])
    
    
