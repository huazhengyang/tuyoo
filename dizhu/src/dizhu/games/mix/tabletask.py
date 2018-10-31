# -*- coding:utf-8 -*-
'''
Created on 2017年6月15日

@author: wangyonghui
'''
from dizhu.games.normalbase.tabletask import WinStreakTaskSystem, WinStreakTask
from poker.entity.biz.content import TYContentItem
import freetime.util.log as ftlog


class WinStreakTaskSystemMix(WinStreakTaskSystem):
    def __init__(self, room):
        super(WinStreakTaskSystemMix, self).__init__(room)
        self._taskListMap = {}
        self._reloadTasks()

    @property
    def taskListMap(self):
        return self._taskListMap

    def getPlayerTask(self, player):
        return self._playerTaskMap.get(player)

    def getNextTask(self, playerTask, player=None):
        if not self._taskListMap:
            return None
        mixTaskList = self._taskListMap.get(player.mixId)
        if not mixTaskList:
            return None
        if not playerTask:
            return mixTaskList[0]
        index = 0 if playerTask.progress >= len(mixTaskList) else playerTask.progress
        return mixTaskList[index]

    def _onRoomConfReload(self, event):
        self._reloadTasks()

    def _reloadTasks(self):
        self._taskListMap = {}
        for mixConf in self.room.roomConf.get('mixConf', []):
            mixId = mixConf.get('mixId')
            winStreakTaskList = []
            winStreakTaskConf = mixConf.get('winStreakTask', {})
            for i, reward in enumerate(winStreakTaskConf.get('tasks', [])):
                TYContentItem.decodeFromDict(reward)
                winStreakTaskList.append(WinStreakTask(i, reward))
            self._taskListMap[mixId] = winStreakTaskList

    def _onGameRoundFinish(self, event):
        if ftlog.is_debug():
            ftlog.debug('WinStreakTaskSystemMix._onGameRoundFinish',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats],
                        'result=', event.gameResult.gameRound.result,
                        'interruptWinStreakWhenAbort=', event.table.runConf.interruptWinStreakWhenAbort)

        for sst in event.gameResult.seatStatements:
            playerTask = self.getPlayerTask(sst.seat.player)
            mixTaskList = self._taskListMap.get(sst.seat.player.mixId)
            if playerTask:
                sst.winStreak = 0
                playerTask._reward = None
                # 流局不中断连胜
                if (sst.isWin
                    or (not event.gameResult.dizhuStatement
                        and not sst.seat.player.mixConf.get('tableConf').get('interruptWinStreakWhenAbort'))):
                    if self._taskListMap and playerTask.progress >= len(mixTaskList):
                        playerTask._progress = 0
                    if sst.isWin:
                        playerTask._progress += 1
                        if mixTaskList:
                            playerTask._reward = mixTaskList[playerTask.progress - 1].reward
                            self._sendWinStreakReward(event.table, playerTask)

                        if playerTask._progress > playerTask.maxWinStreak:
                            playerTask.maxWinStreak = playerTask._progress
                            ftlog.debug('mingsong WinStreakTaskSystem._onGameRoundFinish',
                                        'playerTask.maxWinStreak=', playerTask.maxWinStreak
                                        )
                            self._sendRoomMaxWinStreak(self.room.roomId,playerTask)
                else:
                    playerTask._progress = 0
                sst.winStreak = playerTask.progress

                if ftlog.is_debug():
                    ftlog.debug('WinStreakTaskSystemMix._onGameRoundFinish',
                                'tableId=', event.table.tableId,
                                'userId=', sst.seat.player.userId,
                                'progress=', playerTask.progress)



