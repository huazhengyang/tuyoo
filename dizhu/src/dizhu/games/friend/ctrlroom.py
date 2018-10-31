# -*- coding:utf-8 -*-
'''
Created on 2017年1月20日

@author: zhaojiangang
'''
from collections import OrderedDict

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.room.base import DizhuRoom
from dizhu.servers.table.rpc import ft_table_remote
from dizhucomm.utils.msghandler import MsgHandler
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from hall.servers.util.rpc import user_remote
from poker.entity.biz.exceptions import TYBizException
import poker.util.timestamp as pktimestamp


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

class Table(object):
    def __init__(self, gameId, roomId, tableId):
        # 游戏ID
        self._gameId = gameId
        # 房间ID
        self._roomId = roomId
        # 座位ID
        self._tableId = tableId
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
    def ftTable(self):
        return self._ftTable
    
    @property
    def ftId(self):
        return self._ftTable.ftId if self._ftTable else None
    
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
        ftDetails = self.buildFTTableDetails(table.ftTable)
        return ft_table_remote.ftBind(DIZHU_GAMEID, table.roomId, table.tableId, ftDetails)
        
    def sitdown(self, table, userId):
        return ft_table_remote.ftEnter(DIZHU_GAMEID, userId, table.roomId, table.tableId, table.ftTable.ftId)

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
        self._idleTables.append(table)
        ftlog.info('TableManager.returnTable',
                   'roomId=', self._room.roomId,
                   'idleTableCount=', self.idleTableCount,
                   'allTableCount=', self.allTableCount,
                   'tableId=', table.tableId)
        
    def findTable(self, roomId, tableId):
        return self._allTableMap.get(tableId, None)
            
class DizhuCtrlRoomFriend(DizhuRoom, MsgHandler):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomFriend, self).__init__(roomDefine)
        self._ftMap = OrderedDict()
        self._tableCtrl = TableController()
        self._tableManager = self._buildTableManager()
        self._idleFTTimer = FTLoopTimer(60, -1, self._releaseIdleFT)
        self._idleFTTimer.start()
        ftlog.info('DizhuCtrlRoomFriend.DizhuCtrlRoomFriend Succ',
                   'roomId=', self.roomId,
                   'tableCount=', self._tableManager.allTableCount)
        
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
            ftTable = FTTable(userId, ftId, ftConf, pktimestamp.getCurrentTimestamp(), pktimestamp.getCurrentTimestamp() + ft_service.getCreatorConf(userId).tableExpires)
            self._ftMap[ftId] = ftTable
            ftlog.info('DizhuCtrlRoomFriend.createFT Succ',
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
        # 收费
        ftTable = self.findFT(ftId)
        if not ftTable:
            raise TYBizException(-2, '没有找到该牌桌')
        if ftTable.userId != userId:
            raise TYBizException(-3, '只有桌子主人才能继续')
        self._collectFee(userId, ftTable.ftId, ftTable.ftConf)
        from dizhu.friendtable import ft_service
        ftTable.expires = pktimestamp.getCurrentTimestamp() + ft_service.getCreatorConf(userId).tableExpires
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
        if ftTable.table:
            self._tableManager.returnTable(ftTable.table)
        ft_service.releaseFTId(ftId)
        
        ftlog.info('DizhuCtrlRoomFriend.disbindFT Succ',
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
            ftlog.info('DizhuCtrlRoomFriend.enterFT BindTable',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'ftId=', ftTable.ftId,
                       'tableId=', ftTable.table.tableId)
            # 通知桌子绑定了朋友桌
            self._tableCtrl.bindTable(ftTable.table)
            
        ec, info = self._tableCtrl.sitdown(ftTable.table, userId)
        if ec != 0:
            raise TYBizException(ec, info)
        
        ftlog.info('DizhuCtrlRoomFriend.enterFT Succ',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'ftId=', ftTable.ftId,
                   'tableId=', ftTable.table.tableId)
        return ftTable

    def _releaseIdleFT(self):
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomFriend._releaseIdleFT',
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
                    ftlog.info('DizhuCtrlRoomFriend._releaseIdleFT',
                               'roomId=', self.roomId,
                               'ftId=', ftId,
                               'reason=', 'idleExpires')
                except:
                    pass
        except:
            ftlog.error('DizhuCtrlRoomFriend._releaseIdleFT',
                        'roomId=', self.roomId)
        
        ftlog.info('DizhuCtrlRoomFriend._releaseIdleFT',
                   'roomId=', self.roomId,
                   'ftCount=', len(self._ftMap))
        
    def _buildTableManager(self):
        shadowRoomIds = self.roomDefine.shadowRoomIds
        seatCount = self.tableConf.get('maxSeatN')
        ftlog.info('DizhuCtrlRoomFriend._buildTableManager',
                   'roomId=', self.roomId,
                   'shadowRoomIds=', list(shadowRoomIds),
                   'seatCount=', seatCount)
        
        tableManager = TableManager(self)
        for roomId in self.roomDefine.shadowRoomIds:
            count = self.roomDefine.configure['gameTableCount']
            baseId = roomId * 10000 + 1
            ftlog.info('DizhuCtrlRoomFriend._buildTableManager addTables',
                       'roomId=', self.roomId,
                       'shadowRoomId=', roomId,
                       'baseId=', baseId,
                       'tableCount=', count)
            for i in xrange(count):
                table = Table(DIZHU_GAMEID, roomId, baseId + i)
                tableManager.addTable(table)
        ftlog.info('FTRoom._buildTableManager Succ',
                   'roomId=', self.roomId,
                   'shadowRoomIds=', list(shadowRoomIds),
                   'seatCount=', seatCount,
                   'tableCount=', tableManager.allTableCount)
        return tableManager

    def _returnFee(self, userId, ftId, ftConf):
        if not ftConf.fee:
            return
        try:
            addCount, final = user_remote.addAsset(DIZHU_GAMEID,
                                                   userId,
                                                   ftConf.fee.assetKindId,
                                                   ftConf.fee.count,
                                                   'FT_FEE', int(ftId))
            ftlog.info('DizhuCtrlRoomFriend._returnFee',
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
            ftlog.error('DizhuCtrlRoomFriend._returnFee',
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
    
            ftlog.info('DizhuCtrlRoomFriend._collectFee',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'nRound=', ftConf.nRound,
                       'playMode=', ftConf.playMode,
                       'canDouble=', ftConf.canDouble,
                       'fee=', ftConf.fee.toDict(),
                       'cousumeCount=', ftConf.fee.count,
                       'final=', final)

    def _genFTId(self):
        from dizhu.friendtable import ft_service
        for _ in xrange(10):
            ftId = ft_service.genFTId()
            if not self.findFT(ftId):
                return ftId
        return None
        
    def _do_room__leave(self, msg):
        ftlog.info('DizhuCtrlRoomFriend._do_room__leave',
                   'roomId=', self.roomId,
                   'msg=', msg)
        userId = msg.getParam('userId')
        reason = msg.getParam('reason')
        clientRoomId = msg.getParam('clientRoomId')
        ft_table_remote.leaveRoom(self.gameId, userId, clientRoomId, reason)


