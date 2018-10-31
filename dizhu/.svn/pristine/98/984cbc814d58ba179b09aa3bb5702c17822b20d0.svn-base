# -*- coding:utf-8 -*-
'''
Created on 2018年9月20日

@author: wangyonghui
'''
from dizhu.ai_player.ai import DizhuAIPlayer
from dizhu.games.normal_ai import dealer
from dizhu.games.normal_ai.table import DizhuTableCtrlNormalAI
from dizhu.games.normalbase.tableroom import DizhuPlayerNormalBase, DizhuTableRoomNormalBase
from dizhu.servers.room.rpc import normal_room_remote
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.exceptions import ChipNotEnoughException, NoIdleSeatException
import freetime.util.log as ftlog
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer


class DizhuPlayerNormalAI(DizhuPlayerNormalBase):
    def __init__(self, room, userId):
        super(DizhuPlayerNormalAI, self).__init__(room, userId)
        self.segment = 0
        self.currentStar = 0
        self.isAI = False

    def updateDatas(self, datas):
        self._datas = datas
        self.clientId = datas.get('clientId', '')
        self.name = datas.get('name', '')
        self.chip = datas.get('chip', 0)
        self.gameClientVer = datas.get('gameClientVer', 0)

        segment, currentStar = new_table_remote.doGetUserSegment(self.userId)
        self.segment = segment
        self.currentStar = currentStar
        self.updateSegmentDatas()

    def updateSegmentDatas(self):
        self._datas.update({'segment': self.segment, 'currentStar': self.currentStar})

    def isFirstLose(self, isWin):
        if isWin:
            return False
        if self._datas['registerDays'] < 3:
            wins = self._datas.get('winrate2', {}).get('wt', 0)
            plays = self._datas.get('winrate2', {}).get('pt', 0)
            return wins == plays

    def isFirstWin(self, isWin):
        if not isWin:
            return False
        import poker.util.timestamp as pktimestamp
        today = pktimestamp.formatTimeDayInt()
        isFirstWin = self._datas.get('firstWin', {}).get(str(today), 0)
        if not isFirstWin:
            return True
        return False


class DizhuTableRoomNormalAI(DizhuTableRoomNormalBase):
    def __init__(self, roomDefine):
        super(DizhuTableRoomNormalAI, self).__init__(roomDefine)
        # 桌子列表
        self._tableList = []
        self._dealer = dealer.DIZHU_DEALER_DICT[self.roomConf['playMode']]
        # 初始化定时器循环定时检测
        if self.roomConf.get('occupyIntervalSeconds'):
            # 启动定时器
            self._timer = FTLoopTimer(self.roomConf['occupyIntervalSeconds'], -1, self._processRoomUserOccupy)
            self._timer.start()

    def newTable(self, tableId):
        tableCtrl = self._makeTableCtrl(tableId, self._dealer)
        self._addTable(tableCtrl.table)
        tableCtrl.setupTable()
        return tableCtrl

    def _enterRoomCheck(self, player, continueBuyin):
        '''
        检查用户是否可以进入该房间
        '''
        # 检查location
        roomMinCoin = self.roomConf.get('minCoin', 0)
        if player.chip < roomMinCoin:
            raise ChipNotEnoughException()

    def _getTable(self, player):
        '''
        查找一张合适的桌子
        '''
        found = None
        if ftlog.is_debug():
            ftlog.debug('DizhuTableRoomNormalAI._getTable Enter',
                        'roomId=', self.roomId,
                        'userId=', player.userId,
                        'tableCount=', len(self._tableList))

        for table in self._tableList:
            if table.processing:
                continue

            if table.state.name != 'idle':
                if ftlog.is_debug():
                    ftlog.debug('DizhuTableRoomNormalAI._getTable BadTableState',
                                'roomId=', self.roomId,
                                'userId=', player.userId,
                                'tableId=', table.tableId,
                                'tableState=', table.state.name)
                continue

            idleSeatCount = table.idleSeatCount
            if idleSeatCount == table.seatCount:
                found = table
                break

            if 1 <= idleSeatCount <= table.seatCount - 1:
                ftlog.warn('DizhuTableRoomNormalAI._getTable UserHasInTable',
                           'roomId=', self.roomId,
                           'userId=', player.userId,
                           'tableId=', table.tableId,
                           'tableState=', table.state.name,
                           'idleSeatCount=', idleSeatCount)
                continue

        if not found:
            ftlog.warn('DizhuTableRoomNormalAI._getTable notFound',
                       'roomId=', self.roomId,
                       'userId=', player.userId,
                       'table=', None)

        if ftlog.is_debug():
            ftlog.debug('DizhuTableRoomNormalAI._getTable finally',
                        'roomId=', self.roomId,
                        'userId=', player.userId,
                        'tableCount=', len(self._tableList),
                        'found=', found)
        return found

    def _trySitdown(self, player, continueBuyin):
        for _ in xrange(3):
            table = self._getTable(player)
            if table:
                table.processing = True
                try:
                    if table.sitdown(player, continueBuyin):
                        # 机器人立即坐下
                        DizhuAIPlayer.addRobot(table)
                        return True
                except NoIdleSeatException:
                    pass
                finally:
                    table.processing = False
            FTTasklet.getCurrentFTTasklet().sleepNb(0.5)
        return False

    def _makeTableCtrl(self, tableId, dealer):
        return DizhuTableCtrlNormalAI(self, tableId, dealer)

    def _makePlayer(self, userId):
        return DizhuPlayerNormalAI(self, userId)

    def _processRoomUserOccupy(self):
        """获取当前进程容量"""
        if not self.roomConf.get('occupySwitch', 0):
            return
        playerCount = len(self._playerMap)
        tableCount = len(self._tableList)
        tableSeatCount = self.tableConf['maxSeatN']
        totalCount = tableSeatCount * tableCount
        occupy = round(playerCount * 1.0 / totalCount, 3)
        if ftlog.is_debug():
            ftlog.debug('DizhuTableRoomNormalBase._processRoomUserOccupy',
                        'roomId=', self.roomId,
                        'playerCount=', playerCount,
                        'tableCount=', tableCount,
                        'tableSeatCount=', tableSeatCount,
                        'totalCount=', totalCount,
                        'roomUserOccupy=', occupy)
        normal_room_remote.reportRoomUserOccupy(self.ctrlRoomId, self.roomId, occupy)

    def getRoomOnlineInfo(self):
        ucount, pcount, ocount = 0, 0, 0
        for t in self.maptable.values():
            players = t.table.getPlayers()
            if players:
                pcount += 1
                ucount += 1
            if ftlog.is_debug():
                ftlog.debug('DizhuTableRoomNormalAI.getRoomOnlineInfo Single',
                            'roomId=', self.roomId, 'tableId=', t.tableId, 'players=', [p.userId for p in players])
        if ftlog.is_debug():
            ftlog.debug('DizhuTableRoomNormalAI.getRoomOnlineInfo Final',
                        'roomId=', self.roomId,
                        'ucount=', ucount, 'pcount=', pcount, 'ocount=', ocount, 'allTables=', len(self.maptable.values()))
        return ucount, pcount, ocount
