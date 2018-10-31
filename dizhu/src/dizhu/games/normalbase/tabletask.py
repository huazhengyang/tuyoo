# -*- coding:utf-8 -*-
'''
Created on 2017年3月6日

@author: zhaojiangang
'''
from dizhu.games.events import UserEnterRoomEvent, UserLeaveRoomEvent
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.events import GameRoundFinishEvent
from dizhucomm.room.events import RoomConfReloadEvent
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem

from poker.util import timestamp as pktimestamp
import dizhu.entity.dizhu_giftbag as giftbag



class WinStreakTask(object):
    def __init__(self, index, reward):
        self.index = index
        self.reward = reward

class PlayerWinStreakTask(object):
    def __init__(self, player, progress=0):
        self._player = player
        self._progress = progress
        self._reward = None
        self.maxWinStreak = 0

    @property
    def player(self):
        return self._player
    
    @property
    def progress(self):
        return self._progress
    
    @property
    def reward(self):
        return self._reward

class WinStreakTaskSystem(object):
    def __init__(self, room):
        self.room = room
        self.room.on(RoomConfReloadEvent, self._onRoomConfReload)
        self.room.on(UserEnterRoomEvent, self._onUserEnterRoom)
        self.room.on(UserLeaveRoomEvent, self._onUserLeaveRoom)
        # value=WinStreakTask
        self._taskList = []
        # key=player, value=WinStreakTask
        self._playerTaskMap = {}
        self._taskPictures = []
        self._reloadTasks()
        
    @property
    def taskList(self):
        return self._taskList

    @property
    def taskPictures(self):
        return self._taskPictures
    
    def setupTable(self, table):
        table.on(GameRoundFinishEvent, self._onGameRoundFinish)
    
    def getPlayerTask(self, player):
        return self._playerTaskMap.get(player)
    
    def getNextTask(self, playerTask):
        if not self._taskList:
            return None
        if not playerTask:
            return self._taskList[0]
        index = 0 if playerTask.progress >= len(self._taskList) else playerTask.progress
        return self._taskList[index]
    
    def _onRoomConfReload(self, event):
        self._reloadTasks()

    def _reloadTasks(self):
        self._taskList = []
        winStreakTaskConf = self.room.roomConf.get('winStreakTask', {})
        for i, reward in enumerate(winStreakTaskConf.get('tasks', [])):
            TYContentItem.decodeFromDict(reward)
            self._taskList.append(WinStreakTask(i, reward))
        self._taskPictures = winStreakTaskConf.get('imgs', [])
    
    def _onUserEnterRoom(self, event):
        ftlog.info('Create WinStreakTask',
                   'roomId=', self.room.roomId,
                   'userId=', event.player.userId)


        if event.player.userId not in self._playerTaskMap:
            ret = self._getRoomMaxWinStreak(event.player.userId, self.room.roomId)
            if ret:
                ftlog.info('Init From Redis PlayerWinStreakTask',
                           'roomId=', self.room.roomId,
                           'userId=', event.player.userId,
                           'ret=', ret)
                self._playerTaskMap[event.player] = PlayerWinStreakTask(event.player)
                self._playerTaskMap[event.player].maxWinStreak = ret['maxWinStreak']
            else:
                ftlog.info('Create PlayerWinStreakTask',
                           'roomId=', self.room.roomId,
                           'userId=', event.player.userId)
                self._playerTaskMap[event.player] = PlayerWinStreakTask(event.player)

    def _onUserLeaveRoom(self, event):
        try:
            ftlog.info('Remove WinStreakTask',
                       'roomId=', self.room.roomId,
                       'userId=', event.player.userId)
            del self._playerTaskMap[event.player]
        except:
            ftlog.warn('WinStreakTaskSystem._onUserLeaveRoom',
                       'roomId=', self.room.roomId,
                       'userId=', event.player.userId)
    
    def _sendWinStreakReward(self, table, playerTask):
        assert(playerTask.reward)
        try:
            addCount, final = new_table_remote.sendWinStreakReward(playerTask.player.userId,
                                                                   self.room.roomId,
                                                                   playerTask.player.clientId,
                                                                   table.tableId,
                                                                   playerTask.reward['itemId'],
                                                                   playerTask.reward['count'])
            ftlog.info('SendWinStreakTaskReward',
                       'roomId=', self.room.roomId,
                       'tableId=', table.tableId,
                       'userId=', playerTask.player.userId,
                       'progress=', playerTask.progress,
                       'reward=', playerTask.reward,
                       'addCount=', addCount,
                       'final=', final)
        except:
            ftlog.error('WinStreakTaskSystem._sendWinStreakReward',
                        'roomId=', self.room.roomId,
                        'tableId=', table.tableId,
                        'userId=', playerTask.player.userId,
                        'progress=', playerTask.progress,
                        'reward=', playerTask.reward)
    
    def _onGameRoundFinish(self, event):
        if ftlog.is_debug():
            ftlog.debug('WinStreakTaskSystem._onGameRoundFinish',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats],
                        'result=', event.gameResult.gameRound.result,
                        'interruptWinStreakWhenAbort=', event.table.runConf.interruptWinStreakWhenAbort)
        
        for sst in event.gameResult.seatStatements:
            if sst.isWin:
                giftbag.giftBuffSettle(sst.seat.player.userId, self.room.roomId, 'user:chip', sst.delta, 'loseStreakBuff')
            elif event.gameResult.dizhuStatement:
                winStreakBuff, _ = giftbag.checkUserGiftBuff(sst.seat.player.userId)
                if winStreakBuff:
                    new_table_remote.setUserGiftBuff(sst.seat.player.userId, 'winStreakBuff', 0)

            playerTask = self.getPlayerTask(sst.seat.player)
            if playerTask:
                sst.winStreak = 0
                playerTask._reward = None
                # 流局不中断连胜
                if (sst.isWin
                    or (not event.gameResult.dizhuStatement
                        and not event.table.runConf.interruptWinStreakWhenAbort)):
                    if self._taskList and playerTask.progress >= len(self._taskList):
                        playerTask._progress = 0
                    if sst.isWin:
                        playerTask._progress += 1
                        if self._taskList:
                            playerTask._reward = self._taskList[playerTask.progress - 1].reward
                            self._sendWinStreakReward(event.table, playerTask)
                            giftbag.giftBuffSettle(playerTask.player.userId, self.room.roomId,
                                                   playerTask.reward['itemId'], playerTask.reward['count'], 'winStreakBuff')

                        if playerTask._progress > playerTask.maxWinStreak:
                            playerTask.maxWinStreak = playerTask._progress
                            ftlog.debug('mingsong WinStreakTaskSystem._onGameRoundFinish',
                                        'playerTask.maxWinStreak=', playerTask.maxWinStreak
                                        )
                            self._sendRoomMaxWinStreak(self.room.roomId,playerTask)

                else:
                    sst.stopWinStreak = playerTask._progress
                    playerTask._progress = 0
                sst.winStreak = playerTask.progress

                if ftlog.is_debug():
                    ftlog.debug('WinStreakTaskSystem._onGameRoundFinish',
                                'tableId=', event.table.tableId,
                                'userId=', sst.seat.player.userId,
                                'progress=', playerTask.progress)


    def _getRoomMaxWinStreak(self, userId, roomId):
        '''
        获取玩家room最高连胜
        '''
        return new_table_remote.getRoomMaxWinStreak(userId, roomId)

    def _sendRoomMaxWinStreak(self, roomId, playerTask):
        '''
        将玩家的room最高连胜持久化到数据库
        '''
        new_table_remote.sendRoomMaxWinStreak(playerTask.player.userId, roomId, playerTask.maxWinStreak)


class PlayerDailyPlayTimesWinTask(object):
    
    def __init__(self, userId, dailyPlayTimes=0):
        self.userId = userId
        self.dailyPlayTimes = dailyPlayTimes
        self.reward = None
        self.timestamp = pktimestamp.getCurrentTimestamp()

class DailyPlayTimesWinTaskSystem(object):
    '''
    每日打牌次数任务
    '''
    
    def __init__(self, room):
        self.room = room
        self.room.on(RoomConfReloadEvent, self._onRoomConfReload)
        self.room.on(UserEnterRoomEvent, self._onUserEnterRoom)
        self.room.on(UserLeaveRoomEvent, self._onUserLeaveRoom)
        # 配置中的json
        self._taskList = []
        # key: player    value: PlayerDailyPlayTimeskTask
        self._playerTaskMap = {}
        self._reloadTasks()
    
    def getPlayerTask(self, userId):
        return self._playerTaskMap.get(userId)
        
    def setupTable(self, table):
        table.on(GameRoundFinishEvent, self._onGameRoundFinish)
    
    def _reloadTasks(self):
        self._taskList = []
        dailyPlayTimesWinTaskConf = self.room.roomConf.get('dailyPlayTimesWinTask', {})
        for reward in dailyPlayTimesWinTaskConf.get('tasks', []):
            self._taskList.append(reward)
    
    def _onRoomConfReload(self, event):
        self._reloadTasks()
    
    def _onUserEnterRoom(self, event):

        if not self._taskList:
            return 
        
        if event.player.userId not in self._playerTaskMap:
            ret = self._getUserDailyPlayTimes(event.player.userId, self.room.roomId)
            if ret:
                ftlog.info('Init From Redis PlayerDailyPlayTimesTask',
                           'roomId=', self.room.roomId,
                           'userId=', event.player.userId,
                           'ret=', ret)
                self._playerTaskMap[event.player.userId] = PlayerDailyPlayTimesWinTask(event.player.userId)
                self._playerTaskMap[event.player.userId].dailyPlayTimes = ret['dailyplaytimes']
                self._playerTaskMap[event.player.userId].timestamp = ret['timestamp']
            else:
                ftlog.info('Create PlayerDailyPlayTimesTask',
                           'roomId=', self.room.roomId,
                           'userId=', event.player.userId)
                self._playerTaskMap[event.player.userId] = PlayerDailyPlayTimesWinTask(event.player.userId)

    def _onUserLeaveRoom(self, event):
        ftlog.info('PlayerDailyPlayTimesTaskSystem._onUserLeaveRoom',
                   'roomId=', self.room.roomId,
                   'userId=', event.player.userId)
    
    def _onGameRoundFinish(self, event):
        if ftlog.is_debug():
            ftlog.debug('DailyPlayTimesTaskSystem._onGameRoundFinish',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])

        if not self._taskList:
            return
        for sst in event.gameResult.seatStatements:
            playerTask = self.getPlayerTask(sst.seat.player.userId)
            if playerTask:
                playerTask.reward = None
                
                # 判断是否为当天, 不是归1， 是加1
                current_timestamp = pktimestamp.getCurrentTimestamp()
                if not pktimestamp.is_same_day(playerTask.timestamp, current_timestamp):
                    playerTask.dailyPlayTimes = 1
                else:
                    playerTask.dailyPlayTimes += 1
                playerTask.timestamp = current_timestamp
                    
                self._sendUserDailyPlayTimes(self.room.roomId, playerTask)
                
                # 奖励金币逻辑
                if sst.isWin:
                    for reward in self._taskList:
                        if (playerTask.dailyPlayTimes >= reward['times'][0]) and (reward['times'][1] == -1 or playerTask.dailyPlayTimes <= reward['times'][1]):
                            playerTask.reward = {'itemId': reward['itemId'],
                                                 'count': reward['count']['dizhu'] if sst.isDizhu else reward['count']['nongmin']}
                            self._sendDailyPlayTimesWinRewardsIfNeed(event.table, playerTask, sst.seat.player.clientId)
                            break

    def _sendUserDailyPlayTimes(self, roomId, playerTask):
        '''
        将玩家的玩的次数和时间持久化到数据库
        '''
        new_table_remote.sendUserDailyPlayTimes(playerTask.userId, roomId, playerTask.timestamp, playerTask.dailyPlayTimes)
    
    def _getUserDailyPlayTimes(self, userId, roomId):
        '''
        获取玩家玩的次数和时间
        '''
        return new_table_remote.getUserDailyPlayTimes(userId, roomId)
    
    def _sendDailyPlayTimesWinRewardsIfNeed(self, table, playerTask, clientId):
        '''
        获取金币入库
        '''
        assert(playerTask.dailyPlayTimes > 0)
        reward = playerTask.reward
        if reward['count']:
            addCount, final = new_table_remote.sendDailyPlayTimesWinReward(playerTask.userId,
                                                                           self.room.roomId,
                                                                           clientId,
                                                                           table.tableId,
                                                                           reward['itemId'],
                                                                           reward['count'])

            ftlog.info('SendDailyPlayTimesReward',
                       'roomId=', self.room.roomId,
                       'tableId=', table.tableId,
                       'userId=', playerTask.userId,
                       'dailyPlayTimes=', playerTask.dailyPlayTimes,
                       'reward=', reward,
                       'addCount=', addCount,
                       'final=', final)
        
