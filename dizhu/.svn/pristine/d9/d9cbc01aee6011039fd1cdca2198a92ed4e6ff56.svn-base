# -*- coding:utf-8 -*-
'''
Created on 2016年9月28日

@author: zhaojiangang
'''
from collections import OrderedDict

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.table.rpc import ft_table_remote
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.util.rpc import user_remote
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
import poker.util.timestamp as pktimestamp


class Player(object):
    '''
    比赛中的用户
    '''
    def __init__(self, userId):
        super(Player, self).__init__()
        # 用户ID
        self.userId = userId
        # 玩家坐的座位
        self._seat = None
    
    @property
    def state(self):
        return self._state
        
    @property
    def table(self):
        return self._seat.table if self._seat else None
    
    @property
    def seat(self):
        return self._seat
    
    @property
    def ftId(self):
        return self.table.ftId if self.table else None
        
class Seat(object):
    def __init__(self, table, seatId):
        self._table = table
        self._seatId = seatId
        self._location = '%s.%s.%s.%s' % (table.gameId, table.roomId, table.tableId, seatId)
        self._player = None
        
    @property
    def gameId(self):
        return self.table.gameId
    
    @property
    def table(self):
        return self._table
    
    @property
    def seatId(self):
        return self._seatId
    
    @property
    def roomId(self):
        return self.table.roomId
    
    @property
    def tableId(self):
        return self.table.tableId
    
    @property
    def location(self):
        return self._location
    
    @property
    def player(self):
        return self._player

class Table(object):
    def __init__(self, gameId, roomId, tableId, seatCount):
        # 游戏ID
        self._gameId = gameId
        # 房间ID
        self._roomId = roomId
        # 座位ID
        self._tableId = tableId
        # 所有座位
        self._seats = self._makeSeats(seatCount)
        # 空闲座位
        self._idleSeats = self._seats[:]
        # 当前牌局开始时间
        self.playTime = None
        # 桌子Location
        self._location = '%s.%s.%s' % (self.gameId, self.roomId, self.tableId)
        # 本桌相关的ftTable
        self._ftTable = None
        
    @property
    def gameId(self):
        return self._gameId
    
    @property
    def roomId(self):
        return self._roomId
    
    @property
    def tableId(self):
        return self._tableId
    
    @property
    def seats(self):
        return self._seats
    
    @property
    def location(self):
        return self._location
    
    @property
    def seatCount(self):
        return len(self._seats)
    
    @property
    def idleSeatCount(self):
        '''
        空闲座位的数量
        '''
        return len(self._idleSeats)
    
    @property
    def ftTable(self):
        return self._ftTable
    
    @property
    def ftId(self):
        return self._ftTable.ftId if self._ftTable else None
    
    def getPlayerList(self):
        '''
        获取本桌的所有player
        '''
        return [seat.player for seat in self.seats if seat.player]
        
    def getUserIdList(self):
        '''
        获取本桌所有userId
        '''
        ret = []
        for seat in self.seats:
            ret.append(seat.player.userId if seat.player else 0)
        return ret
    
    def sitdown(self, player):
        '''
        玩家坐下
        '''
        assert(player._seat is None)
        assert(len(self._idleSeats) > 0)
        seat = self._idleSeats[-1]
        del self._idleSeats[-1]
        seat._player = player
        player._table = self
        player._seat = seat
        
    def standup(self, player):
        '''
        玩家离开桌子
        '''
        assert(player._seat is not None
               and player._seat.table == self)
        self._clearSeat(player._seat)
        
    def clear(self):
        '''
        清理桌子上的所有玩家
        '''
        for seat in self._seats:
            if seat._player:
                self.standup(seat._player)
                
    def _clearSeat(self, seat):
        seat._player._seat = None
        seat._player = None
        self._idleSeats.append(seat)
        
    def _makeSeats(self, count):
        assert(count > 0)
        seats = []
        for i in xrange(count):
            seats.append(Seat(self, i + 1))
        return seats
    
class TableManager(object):
    def __init__(self, room):
        self._room = room
        self._idleTables = []
        self._allTableMap = {}
        
    @property
    def allTableCount(self):
        return len(self._allTableMap)
    
    @property
    def idleTableCount(self):
        return len(self._idleTables)
    
    @property    
    def busyTableCount(self):
        return max(0, self.allTableCount - self.idleTableCount)
    
    def addTable(self, table):
        assert(not table.tableId in self._allTableMap)
        self._idleTables.append(table)
        self._allTableMap[table.tableId] = table

    def borrowTable(self):
        assert(self.idleTableCount > 0)
        table = self._idleTables.pop(0)
        ftlog.info('TableManager.borrowTable',
                   'roomId=', self._room.roomId,
                   'idleTableCount=', self.idleTableCount,
                   'allTableCount=', self.allTableCount,
                   'tableId=', table.tableId)
        return table
    
    def returnTable(self, table):
        assert(self._allTableMap.get(table.tableId, None) == table)
        assert(not table.getPlayerList())
        self._idleTables.append(table)
        ftlog.info('TableManager.returnTable',
                   'roomId=', self._room.roomId,
                   'idleTableCount=', self.idleTableCount,
                   'allTableCount=', self.allTableCount,
                   'tableId=', table.tableId)
        
    def findTable(self, roomId, tableId):
        return self._allTableMap.get(tableId, None)
    
class FTConf(object):
    def __init__(self, nRound=None, fee=None,
                 canDouble=None, playMode=None,
                 goodCard=None):
        self.nRound = nRound
        self.fee = fee
        self.canDouble = canDouble
        self.playMode = playMode
        self.goodCard = goodCard
        
class FTTable(object):
    def __init__(self, userId, ftId, ftConf, createTime, expires, table=None):
        # 谁创建的
        self.userId = userId
        # 自建桌ID
        self.ftId = ftId
        # 配置
        self.ftConf = ftConf
        # 到期时间
        self.expires = expires
        # 绑定的桌子
        self.table = None
        # 是否开始了
        self.started = False
        # 所有局的结算信息
        self.results = []
        # 创建时间
        self.createTime = createTime
    
class TableController(object):
    @classmethod
    def buildFTTableDetails(cls, ftTable):
        ret = {
            'ftId':ftTable.ftId,
            'userId':ftTable.userId,
            'nRound':ftTable.ftConf.nRound,
            'canDouble':ftTable.ftConf.canDouble,
            'playMode':ftTable.ftConf.playMode,
            'expires':ftTable.expires,
            'goodCard':ftTable.ftConf.goodCard
        }
        if ftTable.ftConf.fee:
            ret['fee'] = ftTable.ftConf.fee.toDict()
        return ret
    
    def bindTable(self, table):
        msg = MsgPack()
        msg.setCmd('table_manage')
        msg.setAction('ft_bind')
        msg.setParam('roomId', table.roomId)
        msg.setParam('tableId', table.tableId)
        msg.setParam('ftTable', self.buildFTTableDetails(table.ftTable))
        router.sendTableServer(msg, table.roomId)
        
    def unbindTable(self, table):
        msg = MsgPack()
        msg.setCmd('table_manage')
        msg.setAction('ft_unbind')
        msg.setParam('roomId', table.roomId)
        msg.setParam('tableId', table.tableId)
        msg.setParam('ftId', table.ftTable.ftId)
        router.sendTableServer(msg, table.roomId)
        
    def continueTable(self, table):
        msg = MsgPack()
        msg.setCmd('table_manage')
        msg.setAction('ft_continue')
        msg.setParam('roomId', table.roomId)
        msg.setParam('tableId', table.tableId)
        msg.setParam('ftId', table.ftTable.ftId)
        msg.setParam('expires', table.ftTable.expires)
        router.sendTableServer(msg, table.roomId)
        
    def sitdown(self, table, userId):
        return ft_table_remote.ftEnter(DIZHU_GAMEID, userId, table.roomId, table.tableId, table.ftTable.ftId)
#         msg = MsgPack()
#         msg.setCmd('table')
#         msg.setParam('action', 'sit')
#         msg.setParam('userId', userId)
#         msg.setParam('roomId', table.roomId)
#         msg.setParam('tableId', table.tableId)
#         msg.setParam('clientId', sessiondata.getClientId(userId))
#         router.sendTableServer(msg, table.roomId)

class FTRoom(TYRoom):
    def __init__(self, roomdefine):
        super(FTRoom, self).__init__(roomdefine)
        if gdata.serverType() == gdata.SRV_TYPE_ROOM :
            self._initGR()

    def findFT(self, ftId):
        return self._ftMap.get(ftId)
    
    def createFT(self, userId, ftConf):
        from dizhu.friendtable import ft_service
        ftId = self._genFTId()
        if not ftId:
            raise TYBizException(-1, '资源不足')
        
        collectedFee = False
        # 收费
        try:
            self._collectFee(userId, ftId, ftConf)
            collectedFee = True
            ft_service.ftBindRoomId(ftId, self.roomId)
            timestamp = pktimestamp.getCurrentTimestamp()
            ftTable = FTTable(userId, ftId, ftConf, timestamp, timestamp + ft_service.getCreatorConf(userId).tableExpires)
            self._ftMap[ftId] = ftTable
            ftlog.info('FTRoom.createFT Succ',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'ftId=', ftId,
                       'nRound=', ftConf.nRound,
                       'canDouble=', ftConf.canDouble,
                       'playMode=', ftConf.playMode,
                       'expires=', ftTable.expires,
                       'goodCard=', ftConf.goodCard,
                       'fee=', ftConf.fee.toDict() if ftConf.fee else None)
            return ftTable
        except:
            if collectedFee:
                self._returnFee(userId, ftId, ftConf)
            ft_service.releaseFTId(ftId)
            raise
    
    def continueFT(self, userId, ftId):
        from dizhu.friendtable import ft_service
        # 收费
        ftTable = self.findFT(ftId)
        if not ftTable:
            raise TYBizException(-1, '没有找到该牌桌')
        if ftTable.userId != userId:
            raise TYBizException(-1, '只有桌子主人才能继续')
        self._collectFee(userId, ftTable.ftId, ftTable.ftConf)
        ftTable.expires = pktimestamp.getCurrentTimestamp() + ft_service.getCreatorConf(userId).tableExpires
        self._tableCtrl.continueTable(ftTable.table)
        ftlog.info('FTRoom.continueFT Succ',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'ftId=', ftId,
                   'nRound=', ftTable.ftConf.nRound,
                   'canDouble=', ftTable.ftConf.canDouble,
                   'playMode=', ftTable.ftConf.playMode,
                   'expires=', ftTable.expires,
                   'fee=', ftTable.ftConf.fee.toDict() if ftTable.ftConf.fee else None)
        return ftTable
    
    def disbindFT(self, ftId, returnFee):
        from dizhu.friendtable import ft_service
        ftTable = self.findFT(ftId)
        if not ftTable:
            raise TYBizException(-1, '没有找到该牌桌')
        
        # 没有开始则退费
        if not ftTable.table or returnFee:
            self._returnFee(ftTable.userId, ftId, ftTable.ftConf)
        
        del self._ftMap[ftId]
        ftTable.table.clear()
        self._tableManager.returnTable(ftTable.table)
        ft_service.releaseFTId(ftId)
        
        ftlog.info('FTRoom.disbindFT Succ',
                   'roomId=', self.roomId,
                   'userId=', ftTable.userId,
                   'ftId=', ftTable.ftId,
                   'nRound=', ftTable.ftConf.nRound,
                   'canDouble=', ftTable.ftConf.canDouble,
                   'playMode=', ftTable.ftConf.playMode,
                   'fee=', ftTable.ftConf.fee.toDict() if ftTable.ftConf.fee else None)
        
    def enterFT(self, userId, ftId):
        ftTable = self.findFT(ftId)
        if not ftTable:
            raise TYBizException(-1, '没有找到该牌桌')
        
        # 绑定桌子
        if not ftTable.table:
            if self._tableManager.idleTableCount < 1:
                raise TYBizException(-1, '桌子资源不足')
            table = self._tableManager.borrowTable()
            ftTable.table = table
            table._ftTable = ftTable
            ftlog.info('FTRoom.enterFT BindTable',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'ftId=', ftTable.ftId,
                       'tableId=', ftTable.table.tableId)
            # 通知桌子绑定了朋友桌
            self._tableCtrl.bindTable(ftTable.table)
            
        ec, info = self._tableCtrl.sitdown(ftTable.table, userId)
        if ec != 0:
            raise TYBizException(ec, info)
        
        ftlog.info('FTRoom.enterFT Succ',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'ftId=', ftTable.ftId,
                   'tableId=', ftTable.table.tableId)
        return ftTable
    
    def _returnFee(self, userId, ftId, ftConf):
        if not ftConf.fee:
            return
        try:
            addCount, final = user_remote.addAsset(DIZHU_GAMEID,
                                                   userId,
                                                   ftConf.fee.assetKindId,
                                                   ftConf.fee.count,
                                                   'FT_FEE', int(ftId))
            ftlog.info('FTRoom._returnFee',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'ftId=', ftId,
                       'nRound=', ftConf.nRound,
                       'playMode=', ftConf.playMode,
                       'canDouble=', ftConf.canDouble,
                       'fee=', ftConf.fee.toDict(),
                       'addCount=', addCount,
                       'final=', final)
        except:
            ftlog.error('FTRoom._returnFee',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'ftId=', ftId,
                        'nRound=', ftConf.nRound,
                        'playMode=', ftConf.playMode,
                        'canDouble=', ftConf.canDouble,
                        'fee=', ftConf.fee.toDict())
    
    def _collectFee(self, userId, ftId, ftConf):
        if ftConf.fee:
            consumeCount, final = user_remote.consumeAsset(DIZHU_GAMEID,
                                                           userId,
                                                           ftConf.fee.assetKindId,
                                                           ftConf.fee.count,
                                                           'FT_FEE', int(ftId))
            if consumeCount != ftConf.fee.count:
                raise TYBizException(-1, '房卡不足')
    
            ftlog.info('FTRoom._collectFee',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'nRound=', ftConf.nRound,
                       'playMode=', ftConf.playMode,
                       'canDouble=', ftConf.canDouble,
                       'fee=', ftConf.fee.toDict(),
                       'cousumeCount=', ftConf.fee.count,
                       'final=', final)
            
    def _initGR(self):
        # 获取所有的bigRoomId
        self._ftMap = OrderedDict()
        self._tableCtrl = TableController()
        self._tableManager = self._buildTableManager()
        self._idleFTTimer = FTLoopTimer(60, -1, self._releaseIdleFT)
        self._idleFTTimer.start()
        ftlog.info('FTRoom._initGR Succ',
                   'roomId=', self.roomId,
                   'tableCount=', self._tableManager.allTableCount)
        
    def _releaseIdleFT(self):
        if ftlog.is_debug():
            ftlog.debug('FTRoom._releaseIdleFT',
                        'roomId=', self.roomId)
        try:
            ftIds = []
            timestamp = pktimestamp.getCurrentTimestamp()
            for ftId, ftTable in self._ftMap.iteritems():
                if (timestamp - ftTable.createTime) >= 60:
                    if not ftTable.table:
                        ftIds.append(ftId)
                else:
                    break
            for ftId in ftIds:
                try:
                    self._ftMap.pop(ftId)
                    ftlog.info('FTRoom._releaseIdleFT',
                               'roomId=', self.roomId,
                               'ftId=', ftId,
                               'reason=', 'idleExpires')
                except:
                    pass
        except:
            ftlog.error('FTRoom._releaseIdleFT',
                        'roomId=', self.roomId)
        
        ftlog.info('FTRoom._releaseIdleFT',
                   'roomId=', self.roomId,
                   'ftCount=', len(self._ftMap))
        
    def _buildTableManager(self):
        shadowRoomIds = self.roomDefine.shadowRoomIds
        seatCount = self.tableConf.get('maxSeatN')
        ftlog.info('FTRoom._buildTableManager',
                   'roomId=', self.roomId,
                   'shadowRoomIds=', list(shadowRoomIds),
                   'seatCount=', seatCount)
        
        tableManager = TableManager(self)
        for roomId in self.roomDefine.shadowRoomIds:
            count = self.roomDefine.configure['gameTableCount']
            baseId = roomId * 10000 + 1
            ftlog.info('FTRoom._buildTableManager addTables',
                       'roomId=', self.roomId,
                       'shadowRoomId=', roomId,
                       'baseId=', baseId,
                       'tableCount=', count)
            for i in xrange(count):
                table = Table(DIZHU_GAMEID, roomId, baseId + i, seatCount)
                tableManager.addTable(table)
        ftlog.info('FTRoom._buildTableManager Succ',
                   'roomId=', self.roomId,
                   'shadowRoomIds=', list(shadowRoomIds),
                   'seatCount=', seatCount,
                   'tableCount=', tableManager.allTableCount)
        return tableManager
    
    def _genFTId(self):
        from dizhu.friendtable import ft_service
        for _ in xrange(10):
            ftId = ft_service.genFTId()
            if not self.findFT(ftId):
                return ftId
        return None
    

    
    