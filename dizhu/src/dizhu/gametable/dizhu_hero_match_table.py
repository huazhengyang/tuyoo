# -*- coding:utf-8 -*-
'''
Created on 2015年12月1日

@author: zhaoliang

地主百万英雄闯关赛的房间

'''
import time
from dizhu.gametable.dizhu_table import DizhuTable
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.dao import sessiondata, onlinedata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from dizhu.entity import dizhuconf
from freetime.core.tasklet import FTTasklet
from dizhu.gametable.dizhu_hero_match_sender import DizhuMillionHeroMatchSender
from poker.entity.game.tables.table_player import TYPlayer
from dizhu.gametable.dizhu_player import DizhuPlayer
from poker.entity.game.tables.table_timer import TYTableTimer
from dizhu.gametable.dizhu_erdayi_match_table import AIPlayer
import random

class DizhuPlayerHeroMatch(DizhuPlayer):
    def __init__(self, table, seatIndex, copyData=None):
        super(DizhuPlayerHeroMatch, self).__init__(table, seatIndex, copyData)
        self.ai = AIPlayer(self)
        
    def doActiveOutCard(self):
        if not self.ai:
            ftlog.error('ai object is null, userId:', self.userId)
            return []
            
        return self.ai.doActiveOutCard()
        
    def doPassiveOutCard(self):
        if not self.ai:
            ftlog.error('ai object is null, userId:', self.userId)
            return []
            
        return self.ai.doPassiveOutCard()
    
    def initUser(self, isNextBuyin, isUsingScore, randomIndex = 0):
        '''
        从redis里获取并初始化player数据, 远程操作
        '''
        ret = super(DizhuPlayerHeroMatch, self).initUser(isNextBuyin, isUsingScore)
        if TYPlayer.isRobot(self.userId):
            from dizhu.wx_resource import wx_resource
            wx_resource.initRobotSetting()
            wxUserInfo = wx_resource.getRobot(randomIndex)
            self.datas['sex'] = wxUserInfo['sex']
            self.datas['name'] = wxUserInfo['name']
            self.datas['purl'] = wxUserInfo['purl']
            self.clientId = 'robot_3.7_-hall6-robot'
        return ret
    
class DizhuMillionHeroMatchTable(DizhuTable):
    MSTART_SLEEP = 3
    
    '''
    {
        'cmd': 'table_manage',
        'params': {
            'action': 'm_table_start',
            'gameId': 6,
            'roomId': 67891001,
            'tableId': 678910010075,
            'matchId': 6789,
            'baseChip': 1,
            'cardCount': 1,
            'users': [{
                'userId': 10007,
                'stageIndex': 1,
                'state': 3,
                'type': 'player'
            }, {
                'type': 'robot'
            }, {
                'type': 'robot'
            }]
        }
    }
    '''
    
    def __init__(self, room, tableId):
        self.seatOpTimers = []
        super(DizhuMillionHeroMatchTable, self).__init__(room, tableId)
        self._match_table_info = None
        self.gamePlay.sender = DizhuMillionHeroMatchSender(self)
        for _ in xrange(self.maxSeatN):
            self.seatOpTimers.append(TYTableTimer(self))
            
        self._doMatchTableClear()
        
    def clear(self, userids):
        '''
        完全清理桌子数据和状态, 恢复到初始化的状态
        '''
        super(DizhuMillionHeroMatchTable, self).clear(userids)
        self.cancelAllSeatOpTimers()
        
    def cancelAllSeatOpTimers(self):
        for timer in self.seatOpTimers:
            timer.cancel()
        
    def _doOtherAction(self, msg, player, seatId, action, clientId):
        if action == 'AI_OUTCARD_TIMEUP':
            self.seatOpTimers[player.seatIndex].cancel()
            ccrc = msg.getParam('ccrc')
            self.gamePlay.doAIOutCard(player, ccrc)

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
        
    def _makePlayer(self, seatIndex):
        return DizhuPlayerHeroMatch(self, seatIndex)
        
    def _doSit(self, msg, userId, seatId, clientId): 
        '''
        玩家操作, 尝试再当前的某个座位上坐下
        '''
        if not self._match_table_info:
            self.gamePlay.sender.sendQuickStartRes(userId, clientId, {'isOK':False, 'reason':TYRoom.LEAVE_ROOM_REASON_MATCH_END})
            return
        super(DizhuMillionHeroMatchTable, self)._doSit(msg, userId, seatId, clientId)
        
    def doMatchTableStart(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuMillionHeroMatchTable.doMatchTableStart gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'msg=', msg)
            
        # 牌桌清理    
        self._doMatchTableClear()
        
        startTime = time.time()
        tableInfo = msg.getKey('params')
        self._doUpdateTableInfo(tableInfo)
        if ftlog.is_debug():
            ftlog.debug('DizhuMillionHeroMatchTable.doMatchTableStart gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'msg=', msg,
                        'usedTime=', (time.time() - startTime))

        argd = {'handler':self._doMatchQuickStart}
        FTTasklet.create([], argd)
            
    def doMatchTableClear(self, msg):
        if not self._match_table_info:
            ftlog.error('DizhuMillionHeroMatchTable.doMatchTableClear gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'msg=', msg,
                        'err=', 'AlreadyClear')
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
        '''
        牌桌开始
        初始化牌桌玩家
        
        如果是机器人，根据需求初始化机器人信息
        '''
        robots = [1,2]
        tableInfo = self._match_table_info
        userInfos = tableInfo['users']
        userIds = []
        userSeatList = []
         
        for i, userInfo in enumerate(userInfos):
            if userInfo['type'] == 'robot':
                userInfo['userId'] = robots.pop()
            
            this_seat = self.seats[i]
            userIds.append(userInfo['userId'])
            this_seat.userId = userInfo['userId']
            this_seat.state = TYSeat.SEAT_STATE_WAIT
            this_seat.call123 = -1
            userSeatList.append((userInfo['userId'], i + 1))
        
        # 初始化用户数据
        from dizhu.wx_resource import wx_resource
        wx_resource.initRobotSetting()
        robotCount = wx_resource.getRobotCount()
        robotRange = range(0, robotCount)
        robots = random.sample(robotRange, 3)
        for x in xrange(len(self.players)):
            self.players[x].initUser(0, 1, robots[x])

        for userId, seatId in userSeatList :
            if TYPlayer.isRobot(userId):
                continue
            
            onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
            if ftlog.is_debug() :
                ftlog.debug("|locList:", onlinedata.getOnlineLocList(userId), caller=self)
                
        # 做一个延迟
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        inter = delayConf.get('waitToNextMatch', 3)
        FTTasklet.getCurrentFTTasklet().sleepNb(inter)
    
        for x in xrange(len(self.seats)) :
            this_seat = self.seats[x]
            if TYPlayer.isHuman(this_seat.userId):
                mq = MsgPack()
                mq.setCmd('quick_start')
                mq.setResult('userId', this_seat.userId)
                mq.setResult('gameId', self.gameId)
                mq.setResult('roomId', self.roomId)
                mq.setResult('tableId', self.tableId)
                mq.setResult('seatId', x + 1)
                mq.setResult('isOK', True)
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
        return 3
    
    def _sendRanks(self, userInfos):
        pass
    
    def _buildNote(self, userId, tableInfo):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        pass
