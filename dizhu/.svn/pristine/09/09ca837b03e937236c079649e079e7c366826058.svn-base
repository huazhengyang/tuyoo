# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
import json
import random

import datetime

from dizhu.entity import dizhuhallinfo
from dizhu.entity import dizhumatchcond, matchhistory
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhu.entity.matchrecord import MatchRecord
from dizhu.games import matchutil
from dizhu.games.groupmatch.interfacedizhu import SignIFDizhu, \
    TableControllerDizhu, PlayerNotifierDizhu, MatchRewardsDizhu, \
    UserInfoLoaderDizhu, MatchStatusDaoDizhu, MatchRankRewardsSelectorDizhu
from dizhu.games.matchutil import BanHelper, MatchBanException
from dizhu.servers.table.rpc import match_table_room_remote
from dizhucomm.core.events import UserMatchOverEvent
from dizhucomm.room.base import DizhuRoom
from dizhucomm.utils.msghandler import MsgHandler
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallstore, hallitem, hallpopwnd
from hall.entity.todotask import TodoTaskOrderShow, TodoTaskHelper, \
    TodoTaskShowInfo
from poker.entity.biz import bireport
from poker.entity.configure import gdata, configure
from poker.entity.dao import sessiondata, userdata, userchip, onlinedata
from poker.entity.game.rooms.group_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.group_match_ctrl.const import StageType, WaitReason
from poker.entity.game.rooms.group_match_ctrl.exceptions import MatchException, \
    SigninFeeNotEnoughException, SigninException, SigninConditionNotEnoughException
from poker.entity.game.rooms.group_match_ctrl.match import MatchMaster, \
    MatchArea, MatchMasterStubLocal, MatchAreaStubLocal, MatchInst
from poker.entity.game.rooms.group_match_ctrl.models import TableManager
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router, runcmd
from poker.servers.room.rpc.group_match_remote import MatchAreaStubRemote, \
    MatchMasterStubRemote
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class DizhuCtrlRoomGroupMatch(DizhuRoom, MsgHandler):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomGroupMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self.conf = None
        self.match = None
        self.matchMaster = None
        self.masterRoomId = None
        self.isMaster = False
        self._initMatch()
    
    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        if tableId == self.roomId * 10000:
            player = self.match.findPlayer(userId)
            if player:
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomGroupMatch.doCheckUserLoc',
                                'gameId=', gameId,
                                'userId=', userId,
                                'tableId=', tableId,
                                'clientId=', clientId,
                                'ret=', (self.conf.seatId, 0))
                return self.conf.seatId, 0
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch.doCheckUserLoc',
                        'gameId=', gameId,
                        'userId=', userId,
                        'tableId=', tableId,
                        'clientId=', clientId,
                        'ret=', (-1, 0))
        return -1, 0
    
    @classmethod
    def calcMatchDuration(self, conf):
        totalCardCount = 0
        for stage in conf.stages:
            totalCardCount += stage.cardCount
        return totalCardCount * conf.start.tableAvgTimes
    
    @classmethod
    def getMatchCurTimeLeft(cls, inst):
        timestamp = pktimestamp.getCurrentTimestamp()
        if (inst
            and inst.matchConf.start.isTimingType()
            and inst.state < inst.ST_START
            and inst.startTime > timestamp):
            return inst.startTime - timestamp
        return 0
    
    @classmethod
    def convertState(cls, state):
        if (state >= MatchInst.ST_IDLE
            and state < MatchInst.ST_START):
            return 0
        if (state >= MatchInst.ST_START
            and state < MatchInst.ST_FINAL):
            return 10
        return 20
    
    @classmethod
    def getMatchProgress(cls, player):
        return player.group.calcTotalRemTimes(pktimestamp.getCurrentTimestamp())
    
    def buildMatchStatasByInst(self, inst, mp):
        mp.setResult('roomId', self.bigRoomId)
        mp.setResult('state', self.convertState(inst.state) if inst else 0)
        mp.setResult('inst', inst.instId if inst else str(self.roomId))
        mp.setResult('curPlayer', inst.getTotalSignerCount() if inst else 0)
        mp.setResult('curTimeLeft', self.getMatchCurTimeLeft(inst))
        mp.setResult('startTime', inst.startTimeStr if inst else '')
        return mp
    
    def buildMatchStatasByPlayer(self, player, mp):
        mp.setResult('roomId', self.bigRoomId)
        mp.setResult('state', 20)
        mp.setResult('inst', player.instId)
        mp.setResult('curPlayer', player.group.playerCount)
        mp.setResult('curTimeLeft', 0)
        mp.setResult('startTime', '')
        
        tcount = player.group.calcTotalUncompleteTableCount()
        if (tcount > 1
            and player.group.stageConf.type == StageType.DIEOUT
            and player.cardCount < player.group.stageConf.cardCount):
            # 定局需要减掉本桌
            tcount -= 1
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch.getMatchStatesByPlayer roomId=', self.bigRoomId,
                            'instId=', player.instId,
                            'userId=', player.userId,
                            'tcount=', tcount)
            
        progress = self.getMatchProgress(player)
        allcount = player.group.playerCount
        _, clientVer, _ = strutil.parseClientId(player.clientId)
        waitInfo = {
            'uncompleted':tcount, # 还有几桌未完成
            'tableRunk':'%d/3' % player.tableRank, # 本桌排名
            'runk':'%d/%d' % (player.rank, allcount), # 总排名
            'chip':player.score # 当前积分
        }
        if clientVer >= 3.37:
            waitInfo['info'] = self._buildWaitInfoMsg(player)
        mp.setResult('waitInfo', waitInfo)
        mp.setResult('progress', progress)
        return mp
    
    def calcTotalSignerCount(self):
        count = 0
        for areaRoomId, areaStatus in self.match.masterStub.masterStatus.areaStatusMap.iteritems():
            if areaStatus.instStatus:
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomGroupMatch.calcTotalSignerCount',
                                'matchId=', self.match.matchId,
                                'areaRoomId=', areaRoomId,
                                'instId=', areaStatus.instStatus.instId,
                                'areaSignerCount=', areaStatus.instStatus.signerCount)
                count += areaStatus.instStatus.signerCount
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch.calcTotalSignerCount',
                            'matchId=', self.match.matchId,
                            'areaRoomId=', areaRoomId,
                            'instId=', areaStatus.instStatus.instId if areaStatus.instStatus else -1,
                            'count=', count)
        return count
    
    def calcPlayerCount(self):
        count = 0
        for areaRoomId, areaStatus in self.match.masterStub.masterStatus.areaStatusMap.iteritems():
            for groupId, groupStatus in areaStatus.groupStatusMap.iteritems():
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomGroupMatch.calcPlayerCount',
                                'matchId=', self.match.matchId,
                                'areaRoomId=', areaRoomId,
                                'groupId=', groupId, 
                                'groupPlayerCount=', groupStatus.playerCount)
                count += groupStatus.playerCount
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch.calcPlayerCount',
                        'matchId=', self.match.matchId,
                        'count=', count)
        return count
    
    def buildMatchStatas(self, userId):
        mp = MsgPack()
        mp.setCmd('m_update')
        
        player = self.match.findPlayer(userId)
        if player:
            self.buildMatchStatasByPlayer(player, mp)
        else:
            signer = self.match.findSigner(userId)
            inst = signer.inst if signer else self.match.curInst
            self.buildMatchStatasByInst(inst, mp)
        
        signerCount = self.calcTotalSignerCount()
        playerCount = self.calcPlayerCount()
        baseNumber = signerCount + playerCount
        mp.setResult('onlinePlayerCount', baseNumber)
        mp.setResult('signinPlayerCount', baseNumber)
        return mp
    
    def sendMatchStatas(self, userId):
        mp = self.buildMatchStatas(userId)
        router.sendToUser(mp, userId)

    def sendMatchSigns(self, userId):
        signs = {self.bigRoomId:self.getUserSignsState(userId)}
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
            
    def getUserSignsState(self, userId):
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch.getUserSignsState',
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
        
    def getMatchInfo(self, userId, mp):
        inst = self.match.curInst
        conf = inst.matchConf if inst else self.match.matchConf
        state = self.convertState(inst.state) if inst else 0
        
        # 为了兼容老客户端m_enter的问题加的
        clientVer = sessiondata.getClientIdVer(userId)
        try:
            self.match.enter(userId)
        except:
            pass
        info = {}
        info['roomId'] = self.roomId
        info['type'] = conf.start.type
        try:
            clientId = sessiondata.getClientId(userId)
            info['name'] = dizhuhallinfo.getMatchSessionName(DIZHU_GAMEID, clientId, self.bigRoomId)
        except:
            info['name'] = self.roomConf['name']
        if conf.start.isUserCountType():
            info['minPlayer'] = conf.start.userCount
            info['maxPlayer'] = conf.start.userCount
        else:
            info['minPlayer'] = conf.start.userMinCount
            info['maxPlayer'] = conf.start.userMaxCount
            
        info['state'] = self.convertState(state)
        info['curTimeLeft'] = self.getMatchCurTimeLeft(inst) if inst else 0
        mp.setResult('info', info)
        mp.setResult('startTime', inst.startTimeStr if inst else '')
        matchDuration = int(self.calcMatchDuration(conf) / 60)
        mp.setResult('rankRewards', self.buildRankRewards(self.match.matchRankRewardsSelector.getRewardsList(userId, conf.rankRewardsList)))
        mp.setResult('duration', '约%d分钟' % (min(30, matchDuration)))
            
        if clientVer >= 3.37:
            mp.setResult('tips', {
                                  'infos':conf.tips.infos,
                                  'interval':conf.tips.interval
                                  })
            record = MatchRecord.loadRecord(self.gameId, userId, self.match.matchConf.recordId)
            if record:
                mp.setResult('mrecord', {'bestRank':record.bestRank,
                                         'bestRankDate':record.bestRankDate,
                                         'isGroup':record.isGroup,
                                        'crownCount':record.crownCount,
                                        'playCount':record.playCount})
        mp.setResult('fees', matchutil.buildFees(conf.fees))
        # 报名费列表
        mp.setResult('feesList', matchutil.buildFeesList(userId, conf.fees) if conf.fees else [])
        # 分组赛奖励列表
        groupList = []
        if len(conf.stages) > 0 and conf.stages[0].rankRewardsList and conf.stages[0].groupingUserCount:
            groupList = self.buildRankRewards(conf.stages[0].rankRewardsList, defaultEnd = conf.stages[0].groupingUserCount)
        mp.setResult('groupRewardList', groupList)
        # 比赛进程 海选赛-》分组赛-》8强赛-》总决赛
        stagesList = self.buildStages(conf.stages) if conf.stages else []
        mp.setResult('stages', stagesList)
        # 比赛报名的前提条件
        conditionDesc = self.getMatchConditionDesc(self.roomId, userId)
        if conditionDesc:
            mp.setResult('conditionDesc', conditionDesc)
        # 比赛奖励分割线文字
        mp.setResult('splitWord', self.getMatchRewardSplitWord())
        # 获得比赛历史数据
        mp.setResult('hisitory', MatchHistoryHandler.getMatchHistory(userId, self.match.matchConf.recordId))

    # 获取比赛分组奖励与非分组奖励之间分割线的描述文字
    def getMatchRewardSplitWord(self):
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
    def getMatchConditionDesc(cls, roomId, userId):
        matchCondConf = configure.getGameJson(DIZHU_GAMEID, 'bigmatch.filter', {})
        if not matchCondConf:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch EmptyMatchCondConf roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        else:
            ftlog.debug('DizhuCtrlRoomGroupMatch EmptyMatchCondConf roomId=', roomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
        bigRoomId = gdata.getBigRoomId(roomId)
        condConf = matchCondConf.get(str(bigRoomId))
        if not condConf:
            if ftlog.is_debug():
                ftlog.debug('bigmatch roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'bigRoomId=', bigRoomId,
                            'condConf=', condConf,
                            'matchCondConf=', matchCondConf)
            return None
        else:
            ftlog.debug('DizhuCtrlRoomGroupMatch EmptyMatchCondConf roomId=', roomId,
                        'bigRoomId=', bigRoomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
        condition = condConf.get('condition')
        if not condition:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch EmptyMatchCondConf.condition roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        desc = condition.get('desc')
        if not desc:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch EmptyMatchCondConf.condition.desc roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        from sre_compile import isstring
        if not isstring(desc):
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch EmptyMatchCondConf.condition.desc roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        return desc

    def _do_room__leave(self, msg):
        userId = msg.getParam('userId')
        reason = msg.getParam('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
        needSendRes = msg.getParam('needSendRes', True)
        roomId = msg.getParam('roomId')
        clientRoomId = msg.getParam('clientRoomId', 0)

        if self.match.curInst:
            signer = self.match.curInst.findSigner(userId)
            if signer:
                # 报名了离开房间
                self.match.curInst.leave(signer)

            room = gdata.rooms()[roomId]
            player = room.match.findPlayer(userId)
            canQuit = room.roomConf.get('canQuit', 0)
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomGroupMatch.leaveRoom',
                            'roomId=', self.roomId,
                            'userId=', userId)
            bigRoomId = gdata.getBigRoomId(roomId)
            if clientRoomId and bigRoomId != clientRoomId:
                # 已经开始比赛了
                if reason == TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:  # 断线不离开房间
                    return
                tableId = player.table.tableId if player and player.table else 0
                realRoomId = player.table.roomId if player and player.table else 0
                # 解决由于时差导致的用户换桌后房间与桌子对不上
                if tableId and clientRoomId != realRoomId:
                    return
                if not canQuit or not self.leaveRoom(userId, clientRoomId, tableId, reason):
                    reason = TYRoom.LEAVE_ROOM_REASON_FORBIT
                else:
                    if player and clientRoomId:
                        player.isQuit = 1
                ftlog.info('DizhuCtrlRoomGroupMatch._do_room__leave userId=', player.userId if player else -1,
                           'isQuit=', player.isQuit if player else -1,
                           'roomId=', roomId,
                           'clientRoomId=', clientRoomId,
                           'reason=', reason)
                mp = MsgPack()
                mp.setCmd('room_leave')
                mp.setResult('reason', reason)
                mp.setResult('gameId', self.gameId)
                mp.setResult('roomId', clientRoomId)
                mp.setResult('userId', userId)
                router.sendToUser(mp, userId)
            else:
                if player and canQuit and clientRoomId and reason != TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:
                    if player.seat:
                        return
                    player.isQuit = 1
                    self.match.signIF.unlockUser(self.matchId, self.match.roomId, player.instId, player.userId, None)
                elif player and clientRoomId and reason != TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:
                    res = self.match.giveup(userId)
                    if not res:
                        return
                ftlog.info('DizhuCtrlRoomGroupMatch._do_room__leave userId=', player.userId if player else -1,
                           'isQuit=', player.isQuit if player else -1,
                           'roomId=', roomId,
                           'clientRoomId=', clientRoomId,
                           'reason=', reason)
                mp = MsgPack()
                mp.setCmd('room_leave')
                mp.setResult('reason', reason)
                mp.setResult('gameId', self.gameId)
                mp.setResult('roomId', clientRoomId)
                mp.setResult('userId', userId)
                self.match.leave(userId)
                router.sendToUser(mp, userId)

    def leaveRoom(self, userId, shadowRoomId, tableId, reason):
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch.leaveRoom',
                        'roomId=', self.roomId,
                        'shadowRoomId=', shadowRoomId,
                        'userId=', userId,
                        'tableId=', tableId,
                        'reason=', reason)
        if shadowRoomId:
            return match_table_room_remote.leaveRoom(self.gameId, userId, shadowRoomId, tableId, reason)
        return True
        
    def _do_room__update(self, msg):
        userId = msg.getParam('userId')
        self.sendMatchStatas(userId)
        self.sendMatchRanks(userId)
        
    def _do_room__enter(self, msg):
        userId = msg.getParam('userId')
        mo = MsgPack()
        mo.setCmd('m_enter')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.roomId)
        mo.setResult('userId', userId)
        
        try:
            self.match.enter(userId)
        except MatchException, e:
            self.matchPlugin.handleMatchException(self, e, userId, mo)
        router.sendToUser(mo, userId)
        
    def _do_room__signin(self, msg):
        userId = msg.getParam('userId')
        signinParams = msg.getParam('signinParams', {})
        feeIndex = msg.getParam('feeIndex', 0)
        
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch._do_room__signin',
                       'roomId=', self.roomId,
                       'userId=', userId,
                       'signinParams=', signinParams,
                       'feeIndex=', feeIndex)

        mp = MsgPack()
        mp.setCmd('m_signin')
        try:
            # 检查禁赛
            res, remains = BanHelper.checkBanValid(userId, self.bigRoomId)
            if res:
                raise MatchBanException(remains)

            self.ensureCanSignInMatch(userId, mp)
            signer = self.match.signin(userId, signinParams, feeIndex)
            clientId = signer.clientId if signer else sessiondata.getClientId(userId)
            finalUserChip = userchip.getChip(userId)
            try:
                sequence = int(self.match.curInst.instId.split('.')[1])
            except:
                sequence = 0
            bireport.reportGameEvent('MATCH_SIGN_UP', userId, DIZHU_GAMEID, self.roomId, 0, sequence, 0,
                                     0, 0, [], clientId, 0, finalUserChip)
        except (MatchException, MatchBanException), e:
            self._handleMatchException(e, userId, mp)

        self.sendMatchStatas(userId)
        self.sendMatchSigns(userId)
        
    def _do_room__signout(self, msg):
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
                try:
                    sequence = int(self.match.curInst.instId.split('.')[1])
                except:
                    sequence = 0
                bireport.reportGameEvent('MATCH_SIGN_OUT', userId, DIZHU_GAMEID, self.roomId,
                                         0, sequence, 0, 0, 0, [], signer.clientId, 0, finalUserChip)
        except MatchException, e:
            self._handleMatchException(e, userId, mo)
        router.sendToUser(mo, userId)
    
    def _do_room__m_winlose(self, msg):
        matchId = msg.getParam('matchId', 0)
        tableId = msg.getParam('tableId', 0)
        ccrc = msg.getParam('ccrc', -1)
        
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch._do_room__m_winlose',
                        'matchId=', matchId,
                        'tableId=', tableId,
                        'ccrc=', ccrc)
   
        userWinloseList = msg.getParam('users')
        assert(isinstance(userWinloseList, list))
        
        allPlayers = []
        for userWinlose in userWinloseList:
            userId = userWinlose.get('userId', 0)
            seatId = userWinlose.get('seatId', 0)
            deltaScore = userWinlose.get('deltaScore', 0)
            winloseForTuoguanCount = userWinlose.get('winloseForTuoguanCount', 0)
            isTuoguan = userWinlose.get('isTuoguan', False)
            stageRewadTotal = userWinlose.get('stageRewardTotal', 0)
            if userId > 0:
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomGroupMatch._do_room__m_winlose',
                                'matchId=', matchId,
                                'tableId=', tableId,
                                'ccrc=', ccrc,
                                'userId=', userId,
                                'seatId=', seatId,
                                'deltaScore=', deltaScore,
                                'stageRewadTotal=', stageRewadTotal)
                # 判断用户结算托管状态 tuoguanCountStatus 0: 不处理， 1：player.winloseForTuoguanCount + 1 2: 达到临界值，踢出用户
                tuoguanCountStatus = 0
                if isTuoguan and self.roomConf.get('tuoguanKickout', 0) > 0:
                    if winloseForTuoguanCount >= 1:
                        tuoguanCountStatus = 2
                    else:
                        tuoguanCountStatus = 1
                player = self.match.winlose(tableId, ccrc, seatId, userId, deltaScore, deltaScore >= 0, tuoguanCountStatus)
                if player:
                    player.stageRewardTotal = stageRewadTotal
                    allPlayers.append(player)
        try:
            for ele in allPlayers:
                # 找他的后一名
                nextRankPlayer = self._findUserByTableRank(allPlayers, ele.tableRank+1)
                if not nextRankPlayer:
                    continue
                ele.beatDownUserName = nextRankPlayer.userName
        except:
            ftlog.exception()
    
    def _findUserByTableRank(self, container, tableRank):
        for ele in container:
            if ele.tableRank == tableRank:
                return ele
        return None
    
    def _do_room__giveup(self, msg):
        userId = msg.getParam('userId')
        if not self.match.giveup(userId):
            roomId = msg.getParam('roomId')
            room = gdata.rooms()[roomId]
            player = room.match.findPlayer(userId)
            if player and not player.isQuit:
                mo = MsgPack()
                mo.setCmd('room')
                mo.setError(-1, '不能退出比赛')
                router.sendToUser(mo, userId)
        
    def _do_room__des(self, msg):
        userId = msg.getParam('userId')
        mp = MsgPack()
        mp.setCmd('m_des')
        mp.setResult('gameId', self.gameId)
        self.getMatchInfo(userId, mp)
        router.sendToUser(mp, userId)

    def _do_room__quick_start(self, msg):
        assert(self.roomId == msg.getParam('roomId'))
        userId = msg.getParam('userId')
        tableId = msg.getParam('tableId')
        shadowRoomId = msg.getParam('shadowRoomId')
        clientId = msg.getParam('clientId')
        
        ftlog.info('DizhuCtrlRoomGroupMatch._do_room__quick_start',
                   'userId=', userId,
                   'tableId=', tableId,
                   'shadowRoomId=', shadowRoomId,
                   'clientId=', clientId)
   
        if tableId == self.roomId * 10000:
            isOk = True  # 玩家在队列里时断线重连
            player = self.match.findPlayer(userId)
            if player is None:
                ftlog.warn('DizhuCtrlRoomGroupMatch._do_room__quick_start',
                           'userId=', userId,
                           'tableId=', tableId,
                           'shadowRoomId=', shadowRoomId,
                           'clientId=', clientId,
                           'err=', 'NotFoundPlayer')
                try:
                    onlinedata.removeOnlineLoc(userId, self.roomId, tableId)
                except:
                    ftlog.error('DizhuCtrlRoomGroupMatch._do_room__quick_start',
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
                self.match.playerNotifier.notifyMatchWait(player, 1)
        else:
            reason = TYRoom.ENTER_ROOM_REASON_INNER_ERROR
            info = u'在线状态错误或其他系统内部错误'
            self.sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, 0, info)
            
    def _handleMatchException(self, ex, userId, mp):
        ftlog.warn('DizhuCtrlRoomGroupMatch._handleMatchException',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'ex=', '%s:%s' % (ex.errorCode, ex.message))
        if isinstance(ex, SigninFeeNotEnoughException):
            self._handleSigninFeeNotEnoughException(ex, userId, mp)
        elif isinstance(ex, (SigninException, MatchBanException)):
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
            self.sendDizhuFailureMsg(self.gameId, userId, '报名失败', ex.message, None)
            
    def _handleSigninFeeNotEnoughException(self, ex, userId, mo):
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(userId)
        clientOs, _clientVer, _ = strutil.parseClientId(clientId)
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0

        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomGroupMatch._handleSigninFeeNotEnoughException',
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
            ftlog.debug('DizhuCtrlRoomGroupMatch._handleSigninFeeNotEnoughException_V3_772',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'feeItem=', ex.fee.assetKindId,
                        'feeParams=', ex.fee.params)
        if payOrder:
            product, _shelves = hallstore.findProductByPayOrder(self.gameId, userId, clientId, payOrder)
            if not product:
                self.sendDizhuFailureMsg(self.gameId, userId, '报名失败', ex.fee.failure, None)
                return

            buyType = ''
            btnTxt = ''
            if ex.fee.assetKindId == hallitem.ASSET_CHIP_KIND_ID or ex.fee.assetKindId == hallitem.ASSET_DIAMOND_KIND_ID:
                buyType = 'charge'
                btnTxt = '确定'
            orderShow = TodoTaskOrderShow.makeByProduct(ex.fee.failure, '', product, buyType, ex.fee.count, ex.fee.assetKindId)
            orderShow.setParam('sub_action_btn_text', btnTxt)
            mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, orderShow)
            router.sendToUser(mo, userId)
            return

        ## 其他报名费/gotoshop
        title = '报名失败'
        todotask = ex.fee.getParam('todotask')
        todotask_str = None
        button_title = None
        if todotask:
            button_title = "去商城"
            todotaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todotask).newTodoTask(self.gameId, userId, clientId)
            if todotaskObj:
                todotask_str = todotaskObj.toDict()
        itemCount = 0
        itemName = ''
        itemDes = ''
        itemUrl = ''
        if 'item' in ex.fee.assetKindId and ex.fee.count > 0:
            assetKind = hallitem.itemSystem.findAssetKind(ex.fee.assetKindId)
            if assetKind:
                title = '道具不足'
                itemCount = ex.fee.count
                itemName = assetKind.displayName
                itemDes = assetKind.desc
                itemUrl = assetKind.pic
        self.sendDizhuFailureMsg(self.gameId, userId, title, ex.fee.failure, todotask_str, button_title, itemCount,
                                 itemName, itemDes, itemUrl)

    @classmethod
    def sendDizhuFailureMsg(cls, gameId, userId, title, message, todotask=None, buttonTitle=None,itemCount=0,itemName='',itemDes='',itemUrl=''):
        Alert.sendNormalAlert(gameId, userId, title, message, todotask, buttonTitle,itemCount,
                                 itemName, itemDes, itemUrl)

    def ensureCanSignInMatch(self, userId, mp):
        ok, cond = dizhumatchcond.checkMatchSigninCond(userId, self.roomId)
        if not ok:
            raise SigninConditionNotEnoughException(cond.failure)
        
    @classmethod
    def buildStages(cls, stages):
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
    def buildRankRewards(cls, rankRewardsList, defaultEnd=10000):
        ret = []
        notNeedShow = set(['user:charm', 'user:exp', 'game:assistance'])
        for rankRewards in rankRewardsList:
            rewardDesc = matchutil.buildRewardsDesc(rankRewards)
            rewardsList = [] # 奖励信息列表 [{name,num,unit,decs,img},{"电饭煲","1","台","电饭煲x1台","${http_download}/hall/item/imgs/item_1017.png"}]
            for r in rankRewards.rewards:
                assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
                if r['count'] > 0 and assetKind and r['itemId'] not in notNeedShow:
                    rewardsList.append({'name': r.get('displayName') if r.get('displayName', '') else assetKind.displayName,
                                        'num': 1 if r.get('img', '') else r['count'],
                                        'unit': assetKind.units,
                                        'desc': r.get('desc') if r.get('desc', '') else assetKind.buildContent(r['count']),
                                        'img': r.get('img') if r.get('img', '') else assetKind.pic,
                                        'itemId': r.get('itemId', '')
                                        })
            if rewardDesc:
                ret.append({
                            'range':{'s':rankRewards.startRank, 'e':rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                            'rewards':[], #此处为了兼容3.x版本不显示rewardDesc，cls.buildRewards(rankRewards),
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
            if player.rank < player.group.stageConf.riseUserCount:
                return conf.get('maybeRiseMsg', u'您非常有可能晋级，请耐心等待')
            else:
                return conf.get('riseMsg', u'请耐心等待其他玩家')
        return conf.get('waitMsg', u'请耐心等待其他玩家')
    
    def _initMatch(self):
        ftlog.info('DizhuGroupMatchCtrlRoom._initMatch',
                   'roomId=', self.roomId,
                   'bigmatchId=', self.bigmatchId)

        # 监听事件
        self.on(UserMatchOverEvent, self._onUserMatchOver)

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
        
        ftlog.info('DizhuGroupMatchCtrlRoom._initMatch',
                   'roomId=', self.roomId,
                   'masterRoomId=', self.masterRoomId,
                   'isMaster=', self.isMaster,
                   'bigmatchId=', self.bigmatchId,
                   'shadowRoomIds=', list(shadowRoomIds))
        
        for roomId in shadowRoomIds:
            count = self.roomDefine.configure['gameTableCount']
            baseid = roomId * 10000
            ftlog.info('DizhuGroupMatchCtrlRoom._initMatch',
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
                ftlog.error('DizhuGroupMatchCtrlRoom._initMatch',
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
            master.start()
        match.start()
    
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

        master = None
        if self.isMaster:
            master, match = self.buildMaster()
        else:
            match = self.buildArea()
        ftlog.info('DizhuGroupMatchCtrlRoom.buildMatch roomId=', self.roomId,
                   'ctrlRoomIdList=', ctrlRoomIdList,
                   'ctrlRoomCount=', len(ctrlRoomIdList),
                   'userMaxCount=', self.conf.start.userMaxCount,
                   'userMaxCountPerMatch=', self.conf.start.userMaxCountPerMatch,
                   'signinMaxCount=', self.conf.start.signinMaxCount,
                   'signinMaxCountPerMatch=', self.conf.start.signinMaxCountPerMatch)
        if master:
            master.matchStatusDao = MatchStatusDaoDizhu(self)
        match.signIF = SignIFDizhu(self, self.conf.tableId, self.conf.seatId)
        match.tableController= TableControllerDizhu(self)
        match.playerNotifier = PlayerNotifierDizhu(self)
        match.matchRankRewardsSelector = MatchRankRewardsSelectorDizhu(self)
        match.matchRewards = MatchRewardsDizhu(self)
        match.userInfoLoader = UserInfoLoaderDizhu()
        return match, master

    def buildMaster(self):
        ftlog.info('DizhuGroupCtrlRoom.buildMaster'
                   'roomId=', self.roomId,
                   'masterRoomId=', self.masterRoomId,
                   'isMaster=', self.isMaster,
                   'bigmatchId=', self.bigmatchId)
        master = MatchMaster(self, self.bigmatchId, self.conf)
        area = MatchArea(self, self.bigmatchId, self.conf, MatchMasterStubLocal(master))
        master.addAreaStub(MatchAreaStubLocal(master, area))
        if not self.conf.start.isUserCountType():
            ctrlRoomIdList = gdata.bigRoomidsMap().get(self.bigRoomId, [])
            for ctrlRoomId in ctrlRoomIdList:
                if ctrlRoomId != area.roomId:
                    master.addAreaStub(MatchAreaStubRemote(master, ctrlRoomId))
        return master, area
    
    def buildArea(self):
        ftlog.info('DizhuGroupCtrlRoom.buildArea roomId=', self.roomId,
                   'masterCtrlRoomId=', self.masterRoomId)
        return MatchArea(self, self.bigmatchId, self.conf, MatchMasterStubRemote(self.masterRoomId))

    def _onUserMatchOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuGroupCtrlRoom._onUserMatchOver',
                        'matchId=', event.matchId,
                        'sequence=', event.sequence,
                        'userId=', event.player.userId,
                        'rank=', event.player.rank,
                        'rewards=', event.rankRewards)

        # 存储数据
        if event.room.match.matchConf.persistCount > 0 and event.player.rank < event.room.match.matchConf.persistCount:
            name, purl = userdata.getAttrs(event.player.userId, ['name', 'purl'])
            info = {
                'name': str(name),
                'purl': purl,
                'userId': event.player.userId,
                'rewardsDesc': event.rankRewards,
                'rank': event.player.rank,
                'timestamp': pktimestamp.getCurrentTimestamp()
            }
            matchhistory.insertMatchHistoryRank(event.matchId, event.sequence, event.player.rank,
                                                datetime.datetime.fromtimestamp(event.room.match.curInst.startTime).strftime("%Y%m%d"), json.dumps(info))


