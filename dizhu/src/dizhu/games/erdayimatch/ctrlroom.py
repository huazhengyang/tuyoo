# -*- coding:utf-8 -*-
'''
Created on 2017年01月19日

@author: luwei
'''
from datetime import datetime
import random

from dizhu.entity import dizhuhallinfo, dizhumatchcond
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhu.entity.matchrecord import MatchRecord
from dizhu.games import matchutil
from dizhu.games.erdayimatch import erdayi3api
from dizhu.games.erdayimatch.interfacedizhu import ErdayiMatchFactory, \
    TableControllerErdayi, PlayerNotifierErday, MatchRewardsErdayi, \
    MatchUserIFErdayi, SignerInfoLoaderErdayi, SigninFeeErdayi
from dizhu.servers.table.rpc import match_table_room_remote
from dizhucomm.room.base import DizhuRoom
from dizhucomm.utils.msghandler import MsgHandler
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallstore, hallitem, hallpopwnd
from hall.entity.todotask import TodoTaskOrderShow, TodoTaskHelper, \
    TodoTaskShowInfo
from poker.entity.biz import bireport
from poker.entity.configure import gdata, configure
from poker.entity.dao import sessiondata, userdata, userchip, onlinedata, \
    daobase
from poker.entity.game.rooms.erdayi_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.erdayi_match_ctrl.const import WaitReason
from poker.entity.game.rooms.erdayi_match_ctrl.exceptions import MatchException, \
    SigninFeeNotEnoughException, SigninException, SigninConditionNotEnoughException, AleadyInMatchException
from poker.entity.game.rooms.erdayi_match_ctrl.interfaceimpl import \
    MatchStatusDaoRedis, SigninRecordDaoRedis
from poker.entity.game.rooms.erdayi_match_ctrl.match import MatchAreaLocal, \
    MatchInst, MatchMaster
from poker.entity.game.rooms.erdayi_match_ctrl.models import TableManager
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router, runcmd
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class DizhuCtrlRoomErdayiMatch(DizhuRoom, MsgHandler):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomErdayiMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self.conf = None
        self._initMatch()

    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        if tableId == self.roomId * 10000:
            player = self.match.findPlayer(userId)
            if player:
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomErdayiMatch.doCheckUserLoc',
                                'gameId=', gameId,
                                'userId=', userId,
                                'tableId=', tableId,
                                'clientId=', clientId,
                                'ret=', (self.conf.seatId, 0))
                return self.conf.seatId, 0
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomErdayiMatch.doCheckUserLoc',
                        'gameId=', gameId,
                        'userId=', userId,
                        'tableId=', tableId,
                        'clientId=', clientId,
                        'ret=', (-1, 0))
        return -1, 0
    
    def getMasterRoomId(self):
        if self.conf.start.isUserCountType():
            return self.roomId
        ctrlRoomIdList = sorted(gdata.bigRoomidsMap().get(self.bigRoomId, []))
        return ctrlRoomIdList[0]
     
    def buildMatch(self):
        ctrlRoomIdList = gdata.bigRoomidsMap().get(self.bigRoomId, [])
        if self.conf.start.isUserCountType():
            self.conf.start.userMaxCountPerMatch = self.conf.start.userMaxCount
            self.conf.start.signinMaxCount = self.conf.start.signinMaxCount
        else:
            self.conf.start.userMaxCountPerMatch = int(self.conf.start.userMaxCount / max(len(ctrlRoomIdList), 1))
            self.conf.start.signinMaxCountPerMatch = int(self.conf.start.signinMaxCount / max(len(ctrlRoomIdList), 1))
             
        master = MatchMaster(self, self.conf)
        master.matchStatusDao = MatchStatusDaoRedis(self)
        master.matchFactory = ErdayiMatchFactory()
        area = MatchAreaLocal(master, self, self.conf)
        master.addArea(area)
        
        if self.conf.matchId3:
            self.checkMatchingSequence(self, self.conf.matchId3)

        ftlog.info('DizhuErdayiMatchCtrlRoom.buildMatch roomId=', self.roomId,
                   'ctrlRoomIdList=', ctrlRoomIdList,
                   'ctrlRoomCount=', len(ctrlRoomIdList),
                   'userMaxCount=', self.conf.start.userMaxCount,
                   'userMaxCountPerMatch=', self.conf.start.userMaxCountPerMatch,
                   'signinMaxCount=', self.conf.start.signinMaxCount,
                   'signinMaxCountPerMatch=', self.conf.start.signinMaxCountPerMatch)
        
        area.signinRecordDao = SigninRecordDaoRedis(self.gameId)
        area.tableController = TableControllerErdayi(area)
        area.playerNotifier = PlayerNotifierErday(self)
        area.matchRewards = MatchRewardsErdayi(self)
        area.matchUserIF = MatchUserIFErdayi(self, self.conf.tableId, self.conf.seatId)
        area.signerInfoLoader = SignerInfoLoaderErdayi()
        area.matchFactory = ErdayiMatchFactory()
        area.signinFee = SigninFeeErdayi(self)

        return area, master
    
    def checkMatchingSequence(self, room, matchId):
        key = 'matchingId:%s' % (room.gameId)
        sequence = daobase.executeMixCmd('hget', key, matchId)
        if not sequence:
            sequence = daobase.executeMixCmd('hget', key, '%s01' % (matchId))
            if sequence:
                daobase.executeMixCmd('hset', key, matchId, sequence)
            ftlog.info('DizhuCtrlRoomErdayiMatch.checkMatchingSequence',
                       'matchId=', matchId,
                       'key=', key,
                       'moveSequence=', sequence)
        else:
            ftlog.info('DizhuCtrlRoomErdayiMatch.checkMatchingSequence',
                       'matchId=', matchId,
                       'key=', key,
                       'seq=', sequence)
            
    def _initMatch(self):
        ftlog.info('DizhuCtrlRoomErdayiMatch._initMatch',
                   'roomId=', self.roomId,
                   'bigmatchId=', self.bigmatchId)
        self.conf = MatchConfig.parse(self.gameId,
                                      self.roomId,
                                      self.bigmatchId,
                                      self.roomConf['name'],
                                      self.matchConf)
        self.conf.tableId = self.roomId * 10000  # 用来表示玩家在房间队列的特殊tableId
        self.conf.seatId = 1
        self.masterRoomId = self.getMasterRoomId()
        self.isMaster = self.masterRoomId == self.roomId
        tableManager = TableManager(self, self.conf.tableSeatCount)
        shadowRoomIds = self.roomDefine.shadowRoomIds
         
        ftlog.info('DizhuCtrlRoomErdayiMatch.initMatch',
                   'roomId=', self.roomId,
                   'masterRoomId=', self.masterRoomId,
                   'isMaster=', self.isMaster,
                   'bigmatchId=', self.bigmatchId,
                   'shadowRoomIds=', list(shadowRoomIds))
         
        for roomId in shadowRoomIds:
            count = self.roomDefine.configure['gameTableCount']
            baseid = roomId * 10000
            ftlog.info('DizhuErdayiMatchCtrlRoom._initMatch',
                       'roomId=', self.roomId,
                       'masterRoomId=', self.masterRoomId,
                       'isMaster=', self.isMaster,
                       'bigmatchId=', self.bigmatchId,
                       'shadowRoomId=', roomId,
                       'tableCount=', count,
                       'baseid=', baseid)
            tableManager.addTables(roomId, baseid, count)
        random.shuffle(tableManager._idleTables)
         
        match, master = self.buildMatch()
        match.tableManager = tableManager
         
        if gdata.mode() == gdata.RUN_MODE_ONLINE :
            playerCapacity = int(tableManager.allTableCount * tableManager.tableSeatCount * 0.9)
            if playerCapacity <= self.conf.start.userMaxCountPerMatch:
                ftlog.error('DizhuErdayiMatchCtrlRoom._initMatch',
                            'roomId=', self.roomId,
                            'masterRoomId=', self.masterRoomId,
                            'isMaster=', self.isMaster,
                            'bigmatchId=', self.bigmatchId,
                            'allTableCount=', tableManager.allTableCount,
                            'tableSeatCount=', tableManager.tableSeatCount,
                            'playerCapacity=', playerCapacity,
                            'userMaxCount=', self.conf.start.userMaxCount,
                            'confUserMaxCountPerMatch=', self.conf.start.userMaxCountPerMatch,
                            'err=', 'NotEnoughTable')
            assert(playerCapacity >= self.conf.start.userMaxCountPerMatch)
         
        self.match = match
        self.matchMaster = master
        if master:
            master.startHeart()

    def _do_room__leave(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__leave', msg)

        userId = msg.getParam('userId')
        reason = msg.getParam('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
        roomId = msg.getParam('roomId')
        clientRoomId = msg.getParam('clientRoomId', 0)

        if self.match.curInst:
            signer = self.match.curInst.findSigner(userId)
            if signer:
                self.match.curInst.leave(signer)
            room = gdata.rooms()[roomId]
            player = room.match.findPlayer(userId)

            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomErdayiMatch.leaveRoom',
                            'roomId=', self.roomId,
                            'player=', player,
                            'reason=', reason,
                            'userId=', userId)
            self.match.leave(userId)
            if reason == TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:  # 断线不离开房间
                return
            bigRoomId = gdata.getBigRoomId(roomId)
            if clientRoomId and bigRoomId == clientRoomId:
                mp = MsgPack()
                mp.setCmd('room_leave')
                mp.setResult('reason', reason)
                mp.setResult('gameId', self.gameId)
                mp.setResult('roomId', clientRoomId)  # 处理结果返回给客户端时，部分游戏（例如德州、三顺）需要判断返回的roomId是否与本地一致
                mp.setResult('userId', userId)
                router.sendToUser(mp, userId)
                return

            # 已经开始比赛了
            canQuit = room.roomConf.get('canQuit', 0)
            tableId = player.table.tableId if player and player.table else 0
            realRoomId = player.table.roomId if player and player.table else 0
            # 解决由于时差导致的用户换桌后房间与桌子对不上
            if tableId and clientRoomId and clientRoomId != realRoomId:
                return
            if not canQuit or not self.leaveRoom(userId, clientRoomId, tableId, reason):
                reason = TYRoom.LEAVE_ROOM_REASON_FORBIT
            else:
                if player and clientRoomId:
                    player.isQuit = 1

            ftlog.info('DizhuCtrlRoomErdayiMatch._do_room__leave userId=', player.userId if player else -1,
                       'isQuit=', player.isQuit if player else -1,
                       'roomId=', roomId,
                       'clientRoomId=', clientRoomId,
                       'reason=', reason)

            mp = MsgPack()
            mp.setCmd('room_leave')
            mp.setResult('reason', reason)
            mp.setResult('gameId', self.gameId)
            mp.setResult('roomId', clientRoomId)  # 处理结果返回给客户端时，部分游戏（例如德州、三顺）需要判断返回的roomId是否与本地一致
            mp.setResult('userId', userId)
            router.sendToUser(mp, userId)

    def _do_room__update(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__update', msg)
        userId = msg.getParam('userId')
        self.sendMatchStatas(userId)
        self.sendMatchRanks(userId)
         
    def _do_room__enter(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__enter', msg)
        userId = msg.getParam('userId')
        mo = MsgPack()
        mo.setCmd('m_enter')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.roomId)
        mo.setResult('userId', userId)
         
        try:
            self.match.enter(userId)
        except MatchException, e:
            self._handleMatchException(e, userId, mo)
        router.sendToUser(mo, userId)
         
    def _do_room__signin(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__signin', msg)
        userId = msg.getParam('userId')
        signinParams = msg.getParam('signinParams', {})
        feeIndex = msg.getParam('feeIndex', 0)
         
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__signin',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'signinParams=', signinParams,
                        'feeIndex=', feeIndex)
 
        try:
            mp = MsgPack()
            mp.setCmd('m_signin')
            self._ensureCanSignInMatch(userId, mp)
            signer = self.match.signin(userId, feeIndex)
            clientId = signer.clientId if signer else sessiondata.getClientId(userId)
            finalUserChip = userchip.getChip(userId)
            bireport.reportGameEvent('MATCH_SIGN_UP', userId, DIZHU_GAMEID, self.roomId, 0, 0, 0,
                                     0, 0, [], clientId, 0, finalUserChip)
        except MatchException, e:
            self._handleMatchException(e, userId, mp)
 
        self.sendMatchStatas(userId)
        self.sendMatchSigns(userId)
         
    def _do_room__signout(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__signout', msg)
        userId = msg.getParam('userId')
        mo = MsgPack()
        mo.setCmd('m_signout')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.bigRoomId)
        mo.setResult('userId', userId)
        try:
            signer = self.match.signout(userId)
            if signer:
                finalUserChip = userchip.getChip(userId)
                bireport.reportGameEvent('MATCH_SIGN_OUT', userId, DIZHU_GAMEID, self.roomId,
                                         0, 0, 0, 0, 0, [], signer.clientId, 0, finalUserChip)
        except MatchException, e:
            self._handleMatchException(e, userId, mo)
        router.sendToUser(mo, userId)
     
    def _do_room__m_winlose(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__m_winlose', msg)
        matchId = msg.getParam('matchId', 0)
        tableId = msg.getParam('tableId', 0)
        ccrc = msg.getParam('ccrc', -1)

        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__m_winlose',
                        'matchId=', matchId,
                        'tableId=', tableId,
                        'ccrc=', ccrc)
     
        userWinloseList = msg.getParam('users')
        assert(isinstance(userWinloseList, list))

        for userWinlose in userWinloseList:
            userId = userWinlose.get('userId', 0)
            seatId = userWinlose.get('seatId', 0)
            deltaScore = userWinlose.get('deltaScore', 0)
            if userId > 0:
                if ftlog.is_debug():
                    ftlog.debug('DizhuErdayiMatchCtrlRoom.doWinlose',
                                'matchId=', matchId,
                                'tableId=', tableId,
                                'ccrc=', ccrc,
                                'userId=', userId,
                                'seatId=', seatId,
                                'deltaScore=', deltaScore)
                player = self.match.findPlayer(userId)
                if player:
                    player.group.stage.winlose(player, deltaScore, deltaScore >= 0, False)
     
    def _do_room__giveup(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__giveup', msg)
        userId = msg.getParam('userId')
        mo = MsgPack()
        mo.setCmd('room')
        mo.setError(-1, '不能退出比赛')
        router.sendToUser(mo, userId)

    def _do_room__des(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__des', msg)
        userId = msg.getParam('userId')
        mp = MsgPack()
        mp.setCmd('m_des')
        mp.setResult('gameId', self.gameId)
        self.getMatchInfo(userId, mp)
        router.sendToUser(mp, userId)
 
    def _do_room__quick_start(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__quick_start', msg)
        assert(self.roomId == msg.getParam('roomId'))
        userId = msg.getParam('userId')
        tableId = msg.getParam('tableId')
        shadowRoomId = msg.getParam('shadowRoomId')
        clientId = msg.getParam('clientId')
         
        ftlog.info('DizhuErdayiMatchCtrlRoom._do_room__quick_start',
                   'userId=', userId,
                   'tableId=', tableId,
                   'shadowRoomId=', shadowRoomId,
                   'clientId=', clientId)
    
        if tableId == self.roomId * 10000:
            isOk = True  # 玩家在队列里时断线重连
            player = self.match.findPlayer(userId)
            if player is None:
                ftlog.warn('DizhuErdayiMatchCtrlRoom._do_room__quick_start',
                           'userId=', userId,
                           'tableId=', tableId,
                           'shadowRoomId=', shadowRoomId,
                           'clientId=', clientId,
                           'err=', 'NotFoundPlayer')
                try:
                    onlinedata.removeOnlineLoc(userId, self.roomId, tableId)
                except:
                    ftlog.error('DizhuErdayiMatchCtrlRoom._do_room__quick_start',
                                'userId=', userId,
                                'tableId=', tableId,
                                'shadowRoomId=', shadowRoomId,
                                'clientId=', clientId)
                isOk = False
        else :
            isOk = False

        if isOk:
            reason = TYRoom.ENTER_ROOM_REASON_OK
            self.sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, self.match.tableId)
            # 如果用户已经被分组则发送等待信息
            if player.group:
                self.match.playerNotifier.notifyMatchWait(player, player.group)
        else:
            reason = TYRoom.ENTER_ROOM_REASON_INNER_ERROR
            info = u'在线状态错误或其他系统内部错误'
            self.sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, 0, info)

    def _do_room__myCardRecords(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__myCardRecords', msg)
        
        userId = msg.getParam('userId')
        player = self.match.findPlayer(userId)
        if not player:
            ftlog.warn('DizhuErdayiMatchCtrlRoom._do_room__myCardRecords NoPlayer msg=', msg)
            return

        mo = MsgPack()
        mo.setCmd('room')
        mo.setResult('action', 'myCardRecords')
        records = []
        for i, cardResult in enumerate(player.cardResults):
            records.append({
                'cardNo':str(i + 1),
                'score':erdayi3api.fmtScore(cardResult.score),
                'rate':'%s%s' % (erdayi3api.fmtScore(cardResult.mpRate * 100), '%'),
                'mscore':erdayi3api.fmtScore(cardResult.mpRatioScore)
            })
        mo.setResult('records', records)
        router.sendToUser(mo, player.userId)
    
    def _do_room__cardRank(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._do_room__cardRank', msg)
        
        userId = msg.getParam('userId')
        cardNo = int(msg.getParam('cardNo'))
        
        player = self.match.findPlayer(userId)
        if not player:
            ftlog.warn('DizhuErdayiMatchCtrlRoom._do_room__cardRank NoPlayer msg=', msg)
            return
        
        cardRanking = player.group.stage.findCardRanking(cardNo - 1)
        if not cardRanking:
            ftlog.warn('DizhuErdayiMatchCtrlRoom._do_room__cardRank NoCardRanking msg=', msg)
            return
        
        mo = MsgPack()
        mo.setCmd('room')
        mo.setResult('action', 'cardRank')
        ranks = []
        for cardResultSet in cardRanking.rankingList:
            for cardResult in cardResultSet:
                ranks.append({
                    'score':erdayi3api.fmtScore(cardResult.score),
                    'mscore':erdayi3api.fmtScore(cardResult.mpRatioScore),
                    'pcount':len(cardResultSet)
                })
                break
        mo.setResult('ranks', ranks)
        router.sendToUser(mo, player.userId)
        
    def sendMatchStatas(self, userId):
        mp = self._buildMatchStatas(userId)
        router.sendToUser(mp, userId)
 
    @classmethod
    def _calcMatchDuration(self, conf):
        totalCardCount = 0
        for stage in conf.stages:
            totalCardCount += stage.cardCount
        return totalCardCount * conf.start.tableAvgTimes
     
    @classmethod
    def _getMatchCurTimeLeft(cls, inst):
        timestamp = pktimestamp.getCurrentTimestamp()
        if (inst
            and inst.matchConf.start.isTimingType()
            and inst.state < MatchInst.ST_STARTED
            and inst.startTime > timestamp):
            return inst.startTime - timestamp
        return 0

    @classmethod
    def _convertState(cls, state):
        if (state >= MatchInst.ST_IDLE
            and state < MatchInst.ST_STARTED):
            return 0
        if (state >= MatchInst.ST_STARTED
            and state < MatchInst.ST_FINAL):
            return 10
        return 20
     
    @classmethod
    def _getMatchProgress(cls, player):
        return player.group.stage.calcTotalRemTimes(pktimestamp.getCurrentTimestamp())
     
    def _buildMatchStatasByInst(self, inst, mp):
        mp.setResult('roomId', self.bigRoomId)
        mp.setResult('state', self._convertState(inst.state) if inst else 0)
        mp.setResult('inst', inst.instId if inst else str(self.roomId))
        mp.setResult('curPlayer', inst.getTotalSignerCount() if inst else 0)
        mp.setResult('curTimeLeft', self._getMatchCurTimeLeft(inst))
        
        startTimeStr = ''
        if inst and inst.startTime:
            startTimeStr = datetime.fromtimestamp(inst.startTime).strftime('%Y-%m-%d %H:%M')
        mp.setResult('startTime', startTimeStr)
        return mp
     
    def _buildMatchStatasByPlayer(self, player, mp):
        mp.setResult('roomId', self.bigRoomId)
        mp.setResult('state', 20)
        mp.setResult('inst', player.instId)
        mp.setResult('curPlayer', player.group.playerCount)
        mp.setResult('curTimeLeft', 0)
        mp.setResult('startTime', '')
         
        tcount = player.group.calcTotalUncompleteTableCount(player)
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._buildMatchStatasByPlayer',
                        'roomId=', self.bigRoomId,
                        'instId=', player.instId,
                        'userId=', player.userId,
                        'tcount=', tcount)
             
        progress = self._getMatchProgress(player)
        allcount = player.group.playerCount

        _, clientVer, _ = strutil.parseClientId(player.clientId)
        waitInfo = {
            'uncompleted':tcount, # 还有几桌未完成
            'tableRunk':'%d/3' % player.tableRank, # 本桌排名
            'runk':'%d/%d' % (player.rank, allcount), # 总排名
            'chip':float(self._fmtScore(player.score)) # 当前积分
        }
        if clientVer >= 3.37:
            waitInfo['info'] = self._buildWaitInfoMsg(player)
        mp.setResult('waitInfo', waitInfo)
        mp.setResult('progress', progress)
        return mp
         
    def _fmtScore(self, score, n=2):
        fmt = '%d' if int(score) == score else '%%.%sf' % (n)
        return fmt % score
         
    def _buildMatchStatas(self, userId):
        mp = MsgPack()
        mp.setCmd('m_update')
         
        player = self.match.findPlayer(userId)
        if player:
            self._buildMatchStatasByPlayer(player, mp)
        else:
            signer = self.match.findSigner(userId)
            inst = signer.inst if signer else self.match.curInst
            self._buildMatchStatasByInst(inst, mp)
 
        roomInfo = dizhuhallinfo.loadAllRoomInfo(DIZHU_GAMEID).get(self.bigRoomId)

        mp.setResult('onlinePlayerCount', roomInfo.playerCount if roomInfo else 0)
        mp.setResult('signinPlayerCount', roomInfo.signinCount if roomInfo else 0)
        return mp
    
    def sendMatchSigns(self, userId):
        signs = {self.bigRoomId:self._getUserSignsState(userId)}
        mo = MsgPack()
        mo.setCmd('m_signs')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.bigRoomId)
        mo.setResult('userId', userId)
        mo.setResult('signs', signs)
        mo.setResult('isAll', 0)
        router.sendToUser(mo, userId)
         
    def sendMatchRanks(self, userId):
        player = self.match.findPlayer(userId)
        if player:
            self.match.playerNotifier.notifyMatchRank(player)
             
    def _getUserSignsState(self, userId):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._getUserSignsState',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'curInst=', self.match.curInst,
                        'signers=', self.match.curInst._signerMap.keys())
        if self.match.curInst:
            signer = self.match.curInst.findSigner(userId)
            if signer:
                return 1
        player = self.match.findPlayer(userId)
        if player:
            return 2
        return 0
         
    def getMatchInfo(self, userId, mo):
        inst = self.match.curInst
        conf = inst.matchConf if inst else self.match.matchConf
        state = self._convertState(inst.state) if inst else 0
         
        # 为了兼容老客户端m_enter的问题加的
        clientVer = sessiondata.getClientIdVer(userId)
        try:
            self.match.enter(userId)
        except:
            pass
        info = {}
        info['roomId'] = self.roomId
        info['type'] = conf.start.type
        info['name'] = self.roomConf['name']
        if conf.start.isUserCountType():
            info['minPlayer'] = conf.start.userCount
            info['maxPlayer'] = conf.start.userCount
        else:
            info['minPlayer'] = conf.start.userMinCount
            info['maxPlayer'] = conf.start.userMaxCount
             
        info['state'] = self._convertState(state)
        info['curTimeLeft'] = self._getMatchCurTimeLeft(inst) if inst else 0
        mo.setResult('info', info)
        mo.setResult('startTime', datetime.fromtimestamp(inst.startTime).strftime('%Y-%m-%d %H:%M') if inst and inst.startTime else '')
 
        mo.setResult('desc', conf.rankRewardsDesc)
        matchDuration = int(self._calcMatchDuration(conf) / 60)
        mo.setResult('rankRewards', self._buildRankRewards(conf.rankRewardsList))
        mo.setResult('duration', '约%d分钟' % (min(30, matchDuration)))
             
        if clientVer >= 3.37:
            mo.setResult('tips', {
                                  'infos':conf.tips.infos,
                                  'interval':conf.tips.interval
                                  })
            record = MatchRecord.loadRecord(self.gameId, userId, self.match.matchConf.recordId)
            if record:
                mo.setResult('mrecord', {'bestRank':record.bestRank,
                                         'bestRankDate':record.bestRankDate,
                                         'isGroup':record.isGroup,
                                         'crownCount':record.crownCount,
                                         'playCount':record.playCount})
        mo.setResult('fees', matchutil.buildFees(conf.fees))
        # 报名费列表
        mo.setResult('feesList', matchutil.buildFeesList(userId, conf.fees) if conf.fees else [])
        # 分组赛奖励列表
        groupList = []
        if len(conf.stages) > 0 and conf.stages[0].rankRewardsList and conf.stages[0].groupingUserCount:
            groupList = self._buildRankRewards(conf.stages[0].rankRewardsList, defaultEnd = conf.stages[0].groupingUserCount)
        mo.setResult('groupRewardList', groupList)
        # 比赛进程 海选赛-》分组赛-》8强赛-》总决赛
        stagesList = self._buildStages(conf.stages) if conf.stages else []
        mo.setResult('stages', stagesList)
        # 比赛报名的前提条件
        conditionDesc = self._getMatchConditionDesc(self.roomId, userId)
        if conditionDesc:
            mo.setResult('conditionDesc', conditionDesc)
        # 比赛奖励分割线文字
        mo.setResult('splitWord', self._getMatchRewardSplitWord())
        # 获得比赛历史数据
        mo.setResult('hisitory', MatchHistoryHandler.getMatchHistory(userId, self.match.matchConf.recordId))
 
    # 获取比赛分组奖励与非分组奖励之间分割线的描述文字
    def _getMatchRewardSplitWord(self):
        ret = "以下是分组阶段未晋级名次奖励"
        splitConf = configure.getGameJson(DIZHU_GAMEID, 'room.split', {})
        if not splitConf:
            return ret
        bigRoomId = gdata.getBigRoomId(self.roomId)
        roomConf = splitConf.get(str(bigRoomId))
        if not roomConf:
            roomConf = splitConf.get('default')
        if not roomConf:
            return ret
        word = roomConf.get('splitWord')
        from sre_compile import isstring
        if not word or not isstring(word):
            return ret
        ret = word
        return ret
 
    @classmethod
    def _getMatchConditionDesc(cls, roomId, userId):
        matchCondConf = configure.getGameJson(DIZHU_GAMEID, 'bigmatch.filter', {})
        if not matchCondConf:
            if ftlog.is_debug():
                ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc EmptyMatchCondConf roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        else:
            ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc EmptyMatchCondConf roomId=', roomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
        bigRoomId = gdata.getBigRoomId(roomId)
        condConf = matchCondConf.get(str(bigRoomId))
        if not condConf:
            if ftlog.is_debug():
                ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'bigRoomId=', bigRoomId,
                            'condConf=', condConf,
                            'matchCondConf=', matchCondConf)
            return None
        else:
            ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc EmptyMatchCondConf roomId=', roomId,
                        'bigRoomId=', bigRoomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
        condition = condConf.get('condition')
        if not condition:
            if ftlog.is_debug():
                ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc EmptyMatchCondConf.condition roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        desc = condition.get('desc')
        if not desc:
            if ftlog.is_debug():
                ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc EmptyMatchCondConf.condition.desc roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        from sre_compile import isstring
        if not isstring(desc):
            if ftlog.is_debug():
                ftlog.debug('DizhuErdayiMatchCtrlRoom._getMatchConditionDesc EmptyMatchCondConf.condition.desc roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        return desc
 
    def _handleMatchException(self, ex, userId, mp):
        ftlog.warn('DizhuErdayiMatchCtrlRoom._handleMatchException',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'ex=', '%s:%s' % (ex.errorCode, ex.message))
        if isinstance(ex, SigninFeeNotEnoughException):
            self._handleSigninFeeNotEnoughException(ex, userId, mp)
        elif isinstance(ex, (SigninException, AleadyInMatchException)):
            self._handleSigninException(ex, userId, mp)
        else:
            mp.setError(ex.errorCode, ex.message)
            router.sendToUser(mp, userId)
             
    def _handleSigninException(self, ex, userId, mp):
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0
        if ddzver < 3.772:
            infoTodotask = TodoTaskShowInfo(ex.message)
            mp = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, infoTodotask)
            router.sendToUser(mp, userId)
        else:
            self._sendDizhuFailureMsg(self.gameId, userId, '报名失败', ex.message, None)
             
    def _handleSigninFeeNotEnoughException(self, ex, userId, mo):
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(userId)
        clientOs, _clientVer, _ = strutil.parseClientId(clientId)
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0
 
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom._handleSigninFeeNotEnoughException',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'feeItem=', ex.fee.assetKindId,
                        'feeParams=', ex.fee.params)
             
        if ddzver >= 3.772:
            self._handleSigninFeeNotEnoughException_V3_772(ex, userId, mo)
            return
 
        if payOrder:
            clientOs = clientOs.lower()
            product, _shelves = hallstore.findProductByPayOrder(self.gameId, userId, clientId, payOrder)
            if product:
                buyType = ''
                btnTxt = ''
                if ex.fee.assetKindId == hallitem.ASSET_CHIP_KIND_ID and clientOs == 'winpc':
                    user_diamond = userdata.getAttrInt(userId, 'diamond')
                    if user_diamond >= int(product.priceDiamond):
                        buyType = 'consume'
                        btnTxt = '兑换'
                    else:
                        buyType = 'charge'
                        btnTxt = '去充值'
                orderShow = TodoTaskOrderShow.makeByProduct(ex.fee.failure, '', product, buyType)
                orderShow.setParam('sub_action_btn_text', btnTxt)
                mp = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, orderShow)
                router.sendToUser(mp, userId)
                return True
        mp = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, TodoTaskShowInfo(ex.fee.failure))
        router.sendToUser(mp, userId)
 
    def _handleSigninFeeNotEnoughException_V3_772(self, ex, userId, mo):
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(userId)
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoomProtocol._handleSigninFeeNotEnoughException_V3_772',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'feeItem=', ex.fee.assetKindId,
                        'feeParams=', ex.fee.params)
        if payOrder:
            product, _shelves = hallstore.findProductByPayOrder(self.gameId, userId, clientId, payOrder)
            if not product:
                self._sendDizhuFailureMsg(self.gameId, userId, '报名失败', ex.fee.failure, None)
                return
 
            buyType = ''
            btnTxt = ''
            if ex.fee.assetKindId == hallitem.ASSET_CHIP_KIND_ID or ex.fee.assetKindId == hallitem.ASSET_DIAMOND_KIND_ID:
                buyType = 'charge'
                btnTxt = '确定'
            orderShow = TodoTaskOrderShow.makeByProduct(ex.fee.failure, '', product, buyType)
            orderShow.setParam('sub_action_btn_text', btnTxt)
            mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, orderShow)
            router.sendToUser(mo, userId)
            return
 
        ## 其他报名费/gotoshop
        todotask = ex.fee.getParam('todotask')
        todotask_str = None
        button_title = None
        if todotask:
            button_title = "去商城"
            todotaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todotask).newTodoTask(self.gameId, userId, clientId)
            if todotaskObj:
                todotask_str = todotaskObj.toDict()
        self._sendDizhuFailureMsg(self.gameId, userId, '报名失败', ex.fee.failure, todotask_str, button_title)
 
    @classmethod
    def _sendDizhuFailureMsg(cls, gameId, userId, title, message, todotask=None, buttonTitle=None):
        Alert.sendNormalAlert(gameId, userId, title, message, todotask, buttonTitle)
 
    def _ensureCanSignInMatch(self, userId, mp):
        ok, cond = dizhumatchcond.checkMatchSigninCond(userId, self.roomId)
        if not ok:
            raise SigninConditionNotEnoughException(cond.failure)
         
    @classmethod
    def _buildStages(cls, stages):
        ret = []
        for stage in stages:
            matchName = ''
            n = -1
            dec = '%s人晋级' % (stage.riseUserCount)
            if stage.name.find('海选赛') != -1:
                matchName = 'haixuansai'
            elif stage.name.find('晋级赛') != -1:
                matchName = 'jinjisai'
            elif stage.name.find('分组赛') != -1:
                matchName = 'fenzusai'
            elif stage.name.find('强赛') != -1:
                matchName = 'n_qiangsai'
                n = int(stage.name[0:stage.name.find('强赛')])
            elif stage.name.find('总决赛') != -1:
                matchName = 'zongjuesai'
            elif stage.name.find('决赛') != -1:
                matchName = 'juesai'
            ret.append({'isPass':False, 'stationType':matchName, 'n':n, 'isHere':False, 'description': dec, 'name':stage.name})
        return ret
 
    @classmethod
    def _buildRankRewards(cls, rankRewardsList, defaultEnd=10000):
        ret = []
        notNeedShow = set(['user:charm', 'user:exp', 'game:assistance'])
        for rankRewards in rankRewardsList:
            rewardDesc = matchutil.buildRewardsDesc(rankRewards)
            rewardsList = [] # 奖励信息列表 [{name,num,unit,decs,img},{"电饭煲","1","台","电饭煲x1台","${http_download}/hall/item/imgs/item_1017.png"}]
            for r in rankRewards.rewards:
                assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
                if r['count'] > 0 and assetKind and r['itemId'] not in notNeedShow:
                    rewardsList.append({'name': assetKind.displayName,
                                        'num': r['count'],
                                        'unit': assetKind.units,
                                        'desc': assetKind.displayName + 'x' + str(r['count']) + assetKind.units,
                                        'img': assetKind.pic
                                        })
            if rewardDesc:
                ret.append({
                            'range':{'s':rankRewards.startRank, 'e':rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                            'rewards':[], #此处为了兼容3.x版本不显示rewardDesc，cls._buildRewards(rankRewards),
                            'rewardsDesc':rewardDesc,
                            'rewardsList':rewardsList
                            })
            else:
                ret.append({
                            'range':{'s':rankRewards.startRank, 'e':rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                            'rewards':matchutil.buildRewards(rankRewards),
                            'rewardsList':rewardsList
                            })
        return ret

    @classmethod
    def _buildWaitInfoMsg(cls, player):
        conf = {}
        if player.waitReason == WaitReason.BYE:
            # 轮空提示
            return conf.get('byeMsg', u'轮空等待') 
        elif player.waitReason == WaitReason.RISE:
            # 晋级等待
            if player.rank < player.stage.stageConf.riseUserCount:
                return conf.get('maybeRiseMsg', u'您非常有可能晋级，请耐心等待')
            else:
                return conf.get('riseMsg', u'请耐心等待其他玩家')
        return conf.get('waitMsg', u'请耐心等待其他玩家')

    def leaveRoom(self, userId, shadowRoomId, tableId, reason):
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiMatchCtrlRoom.leaveRoom',
                        'roomId=', self.roomId,
                        'tableId=', tableId,
                        'shadowRoomId=', shadowRoomId,
                        'userId=', userId,
                        'reason=', reason)
        if shadowRoomId:
            return match_table_room_remote.leaveRoom(self.gameId, userId, shadowRoomId, tableId, reason)
        return True



