# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
import random
from sre_compile import isstring
import datetime

from dizhu.entity import dizhuhallinfo, dizhumatchcond, dizhu_util
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhutodotask import makeQuickSigninShow
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhu.entity.matchrecord import MatchRecord
from dizhu.games import matchutil
from dizhu.games.arenamatch.interfacedizhu import MatchTableControllerDizhu, \
    MatchPlayerNotifierDizhu, MatchRankRewardsSenderDizhu, UserInfoLoaderDizhu, \
    SigninFeeDizhu, SigninRecordDaoDizhu, UserLockerDizhu, MatchRankRewardsSelectorDizhu
from dizhu.games.arenamatch.match import DizhuMatchConf, DizhuMatch
from dizhu.games.matchutil import BanHelper, MatchBanException, MatchGameRestartException
from dizhu.servers.table.rpc import match_table_room_remote
from dizhucomm.room.base import DizhuRoom
from dizhucomm.utils.msghandler import MsgHandler
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallstore, hallitem, hallpopwnd, hallconf
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskOrderShow, TodoTaskHelper, \
    TodoTaskShowInfo
from poker.entity.biz import bireport
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata, configure
from poker.entity.dao import onlinedata, sessiondata, userdata, userchip, daobase
from poker.entity.game import game
from poker.entity.game.rooms.arena_match_ctrl.exceptions import MatchException, \
    SigninFeeNotEnoughException, SigninNotStartException, SigninStoppedException, \
    SigninFullException, MatchExpiredException, ClientVersionException, \
    MatchSigninConditionException, AlreadyInMatchException, NotSigninException
from poker.entity.game.rooms.arena_match_ctrl.interfaces import \
    MatchSafeDaoRedis
from poker.entity.game.rooms.arena_match_ctrl.match import Match, MatchPlayer, \
    MatchInstance, MatchConf, MatchTableManager
from poker.entity.game.rooms.group_match_ctrl.const import MatchType
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router, runcmd
from poker.util import strutil


class DizhuCtrlRoomArenaMatch(DizhuRoom, MsgHandler):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomArenaMatch, self).__init__(roomDefine)
        self.bigmatchId = self.bigRoomId
        self.conf = None
        self._initMatch()
    
    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        if tableId == self.roomId * 10000:
            player = self.match.findPlayer(userId)
            if player:
                if ftlog.is_debug():
                    ftlog.debug('DizhuCtrlRoomArenaMatch.doCheckUserLoc',
                                'gameId=', gameId,
                                'userId=', userId,
                                'tableId=', tableId,
                                'clientId=', clientId,
                                'ret=', (self.conf.seatId, 0))
                return self.conf.seatId, 0
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch.doCheckUserLoc',
                        'gameId=', gameId,
                        'userId=', userId,
                        'tableId=', tableId,
                        'clientId=', clientId,
                        'ret=', (-1, 0))
        return -1, 0
    
    def _onConfReload(self):
        conf = DizhuMatchConf().decodeFromDict(self.matchConf)
        conf.gameId = self.gameId
        conf.roomId = self.roomId
        conf.tableId = self.roomId * 10000  # 用来表示玩家在房间队列的特殊tableId
        conf.seatId = 1
        for feeReward in conf.feeRewardList:
            if not feeReward.roomName:
                feeReward.roomName = self.roomConf.get('name')
        if self.match:
            self.match.reloadConf(conf)
    
    def _initMatch(self):
        ftlog.info('DizhuCtrlRoomArenaMatch._initMatch',
                   'roomId=', self.roomId,
                   'bigmatchId=', self.bigmatchId)
        
        conf = DizhuMatchConf().decodeFromDict(self.matchConf)
        conf.gameId = self.gameId
        conf.roomId = self.roomId
        conf.tableId = self.roomId * 10000  # 用来表示玩家在房间队列的特殊tableId
        conf.seatId = 1
        for feeReward in conf.feeRewardList:
            if not feeReward.roomName:
                feeReward.roomName = self.roomConf.get('name')
        self.conf = conf
        
        tableManager = MatchTableManager(self.gameId, conf.tableSeatCount)
        shadowRoomIds = self.roomDefine.shadowRoomIds

        ftlog.info('DizhuCtrlRoomArenaMatch._initMatch',
                   'roomId=', self.roomId,
                   'bigmatchId=', self.bigmatchId,
                   'shadowRoomIds=', list(shadowRoomIds))
        
        for roomId in shadowRoomIds:
            count = self.roomDefine.configure['gameTableCount']
            baseid = roomId * 10000
            ftlog.info('DizhuCtrlRoomArenaMatch._initMatch',
                       'roomId=', self.roomId,
                       'bigmatchId=', self.bigmatchId,
                       'shadowRoomId=', roomId,
                       'tableCount=', count,
                       'baseid=', baseid)
            tableManager.addTables(roomId, baseid, count)
        random.shuffle(tableManager._idleTables)
        
        match = DizhuMatch(conf)
        match.tableController = MatchTableControllerDizhu(self)
        match.playerNotifier = MatchPlayerNotifierDizhu(self)
        match.matchRankRewardsSelector = MatchRankRewardsSelectorDizhu(self)
        match.matchRewardsSender = MatchRankRewardsSenderDizhu(self)
        match.userInfoLoader = UserInfoLoaderDizhu()
        match.signinFee = SigninFeeDizhu(self)
        match.signinRecordDao = SigninRecordDaoDizhu(self)
        match.userLocker = UserLockerDizhu()
        match.tableManager = tableManager
        if not match.matchSafeDao:
            match.matchSafeDao = MatchSafeDaoRedis()
        
        if (gdata.mode() == gdata.RUN_MODE_ONLINE):
            playerCapacity = int(tableManager.allTableCount * tableManager.tableSeatCount * 0.9)
            ftlog.info('DizhuCtrlRoomArenaMatch._initMatch AddIdleTable',
                       'roomId=', self.roomId,
                       'allTableCount=', tableManager.allTableCount,
                       'tableSeatCount=', tableManager.tableSeatCount,
                       'playerCapacity=', playerCapacity,
                       'matchUserMaxCount=', conf.maxPlayerCount)
            assert(playerCapacity >= conf.maxPlayerCount)
        
        self.match = match
        match.start()

    @classmethod
    def translateState(cls, state):
        if (state < MatchInstance.STATE_STARTED):
            return 0
        if (state < MatchInstance.STATE_STOP):
            return 10
        return 20

    def checkTime(self, startTime, stopTime):
        if not startTime or not stopTime:
            return True
        from datetime import datetime
        time_now = datetime.now().time()
        
        time_start = datetime.strptime(startTime, '%H:%M').time()
        time_end = datetime.strptime(stopTime, '%H:%M').time()
        
        # 今天的启示时间点到明天的终止时间点
        if time_start >= time_end:
            return time_start <= time_now or time_now < time_end
        return time_start <= time_now and time_now < time_end

    def calcMatchDuration(self, conf):
        totalCardCount = 0
        for stage in conf.stages:
            totalCardCount += stage.cardCount
        return totalCardCount * 81

    # 获取比赛分组奖励与非分组奖励之间分割线的描述文字
    def getMatchRewardSplitWord(self, roomId):
        ret = "以下是分组阶段未晋级名次奖励"
        splitConf = configure.getGameJson(DIZHU_GAMEID, 'room.split', {})
        if not splitConf:
            return ret
        bigRoomId = gdata.getBigRoomId(roomId)
        roomConf = splitConf.get(str(bigRoomId))
        if not roomConf:
            roomConf = splitConf.get('default')
        if not roomConf:
            return ret
        word = roomConf.get('splitWord')
        if not word or not isstring(word):
            return ret
        ret = word
        return ret

    def buildStages(self, stages):
        '''
        stage.name 必须由这些字组成 {'0' '1' '2' '3' '4' '5' '6' '7' '8' '9' 
        '比' '第' '分' '海' '级' '晋' '决' '轮' '强' '赛' '选' '总' '组'}
        '''
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

    def buildRewardsDesc(self, rankRewards):
        notNeedDescNames = set(['user:chip', 'ddz.exp'])
        allZero = True
        for r in rankRewards.rewards:
            if r['count'] <= 0:
                continue
            if r['itemId'] not in notNeedDescNames:
                return rankRewards.desc
            # 奖券统一修改为红包券
            if r['itemId'] == 'user:coupon':
                assetKind = hallitem.itemSystem.findAssetKind('user:coupon')
                return assetKind.displayName if assetKind else None
            # allZero = False# #此处为了兼容3.x版本不显示rewardDesc
        return rankRewards.desc if allZero else None
    
    def buildRankRewards(self, rankRewardsList, defaultEnd=10000):
        ret = []
        notNeedShow = set(['user:charm', 'user:exp', 'game:assistance'])
        for rankRewards in rankRewardsList:
            rewardDesc = self.buildRewardsDesc(rankRewards)
            rewardsList = []  # 奖励信息列表 [{name,num,unit,decs,img},{"电饭煲","1","台","电饭煲x1台","${http_download}/hall/item/imgs/item_1017.png"}]
            for r in rankRewards.rewards:
                assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
                if r['count'] > 0 and assetKind and r['itemId'] not in notNeedShow:
                    rewardsList.append({'name': r.get('displayName') if r.get('displayName', '') else assetKind.displayName,
                                        'num': 1 if r.get('img', '') else r['count'],
                                        'unit': assetKind.units,
                                        'desc': r.get('desc') if r.get('desc', '') else assetKind.buildContent(r['count']),
                                        'img': r.get('img', '') if r.get('img', '') else assetKind.pic,
                                        'itemId': r.get('itemId', '')
                                        })
            if ftlog.is_debug():
                ftlog.debug('arenaMatch.buildRankRewards rewardsList=', rewardsList)
            if rewardDesc:
                ret.append({
                            'range':{'s':rankRewards.startRank, 'e':rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                            'rewards':[],  # 此处为了兼容3.x版本不显示rewardDesc，cls.buildRewards(rankRewards),
                            'rewardsDesc':rewardDesc,
                            'rewardsList':rewardsList
                            })
            else:
                ret.append({
                            'range':{'s':rankRewards.startRank, 'e':rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                            'rewards':self.buildRewards(rankRewards),
                            'rewardsList':rewardsList
                            })
        return ret

    def buildRewards(self, rankRewards):
        ret = []
        for r in rankRewards.rewards:
            if r.count > 0:
                name = hallconf.translateAssetKindIdToOld(r.assetKindId)
                ret.append({'name':name or '', 'count':r.count, 'itemId':r.assetKindId})
        return ret

    # 获取比赛前提条件描述
    def getMatchConditionDesc(self, roomId, userId):
        matchCondConf = configure.getGameJson(DIZHU_GAMEID, 'bigmatch.filter', {})
        if not matchCondConf:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch.getMatchConditionDesc EmptyMatchCondConf',
                            'roomId=', roomId,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None

        bigRoomId = gdata.getBigRoomId(roomId)
        condConf = matchCondConf.get(str(bigRoomId))
        if not condConf:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch.getMatchConditionDesc EmptyCondConf',
                            'roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'bigRoomId=', bigRoomId,
                            'condConf=', condConf,
                            'matchCondConf=', matchCondConf)
            return None
        else:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch.getMatchConditionDesc',
                            'roomId=', roomId,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
        condition = condConf.get('condition')
        if not condition:
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch.getMatchConditionDesc EmptyCond',
                            'roomId=', roomId,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        desc = condition.get('desc')
        if not desc or not isstring(desc):
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch.getMatchConditionDesc EmptyMatchCondConf.condition.desc',
                            'roomId=', roomId,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        return desc
    
    def _do_room__m_winlose(self, msg):
        matchId = msg.getParam('matchId', 0)
        tableId = msg.getParam('tableId', 0)
        ccrc = msg.getParam('ccrc', -1)
        
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__m_winlose ',
                        'matchId=', matchId,
                        'tableId=', tableId,
                        'ccrc=', ccrc)
        
        userWinloseList = msg.getParam('users')
        assert(isinstance(userWinloseList, list))
        
        allPlayers = []
        for userWinlose in userWinloseList:
            userId = userWinlose.get('userId', 0)
            seatId = userWinlose.get('seatId', 0)
            winloseForTuoguan = userWinlose.get('isTuoguan', 0)
            deltaScore = userWinlose.get('deltaScore', 0)
            stageRewardTotal = userWinlose.get('stageRewardTotal', 0)
            if userId > 0:
                player = self.match.winlose(tableId, ccrc, seatId, userId, deltaScore, deltaScore >= 0, winloseForTuoguan=winloseForTuoguan)
                if player:
                    player.stageRewardTotal = stageRewardTotal
                    allPlayers.append(player)
                if ftlog.is_debug() and userId > 10000:
                    ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__m_winlose userId=', userId,
                                'seatId=', seatId,
                                'deltaScore=', deltaScore,
                                'stageRewadTotal=', stageRewardTotal,
                                'player.stageRewadTotal=', player.stageRewardTotal)
        try:
            for ele in allPlayers:
                # 找他的后一名
                nextRankPlayer = self._findUserByTableRank(allPlayers, ele.tableRank + 1)
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

    def _do_room__leave(self, msg):
        userId = msg.getParam('userId')
        reason = msg.getParam('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
        needSendRes = msg.getParam('needSendRes', True)
        roomId = msg.getParam('roomId')

        # 报名状态断线不踢出房间
        issignin = daobase.executeTableCmd(roomId, 0, 'SISMEMBER', 'signs:' + str(roomId), userId)
        if issignin and reason == TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:
            return

        clientRoomId = msg.getParam('clientRoomId', 0)
        bigRoomId = gdata.getBigRoomId(roomId)
        room = gdata.rooms()[roomId]
        player = room.match.findPlayer(userId)
        canQuit = room.roomConf.get('canQuit', 0)
        if clientRoomId and bigRoomId != clientRoomId:
            tableId = player.table.tableId if player and player.table else 0
            realRoomId = player.table.roomId if player and player.table else 0
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch.leaveRoom',
                            'roomId=', self.roomId,
                            'clientRoomId=', clientRoomId,
                            'tableId=', tableId,
                            'reason=', reason,
                            'userId=', userId)
            if reason == TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:  # 断线不离开房间
                return

            # 解决由于时差导致的用户换桌后房间与桌子对不上
            if tableId and clientRoomId != realRoomId:
                return

            if not canQuit or not self.leaveRoom(userId, clientRoomId, tableId, reason):
                reason = TYRoom.LEAVE_ROOM_REASON_FORBIT
            else:
                if player:
                    player.isQuit = 1
            ftlog.info('DizhuCtrlRoomArenaMatch._do_room__leave userId=', player.userId if player else -1,
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
                player.isQuit = 1
                self.match.currentInstance._unlockPlayer(player)
            elif player and clientRoomId and reason != TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:
                res = self.match.giveup(userId)
                if not res:
                    return
            ftlog.info('DizhuCtrlRoomArenaMatch._do_room__leave userId=', player.userId if player else -1,
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
            try:
                self.match.leave(userId)
            except NotSigninException:
                pass
            router.sendToUser(mp, userId)

    def leaveRoom(self, userId, shadowRoomId, tableId, reason):
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch.leaveRoom',
                        'roomId=', self.roomId,
                        'tableId=', tableId,
                        'shadowRoomId=', shadowRoomId,
                        'userId=', userId,
                        'reason=', reason)
        if shadowRoomId:
            return match_table_room_remote.leaveRoom(self.gameId, userId, shadowRoomId, tableId, reason)
        return True
        
    def _do_room__update(self, msg):
        userId = msg.getParam('userId')
        signinParams = msg.getParam('signinParams', {})
        self.sendMatchStatas(userId, signinParams)
        self.sendMatchRanks(userId)
        
    def _do_room__enter(self, msg):
        userId = msg.getParam('userId')
        mo = MsgPack()
        mo.setCmd('m_enter')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.roomId)
        mo.setResult('userId', userId)
        
        try:
            if not self.match.currentInstance:
                mo.setError(1, u'比赛已经下线')
            else:
                if not self.match.enter(userId):
                    mo.setError(1, u'已经在比赛中')
        except TYBizException, e:
            self._handleMatchException(e, userId, mo)
        router.sendToUser(mo, userId)
        
    def _do_room__signin(self, msg):
        userId = msg.getParam('userId')
        signinParams = msg.getParam('signinParams', {})
        feeIndex = msg.getParam('feeIndex', 0)
        
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__signin',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'signinParams=', signinParams,
                        'feeIndex=', feeIndex)

        mp = MsgPack()
        mp.setCmd('m_signin')
        try:
            # 检查服务器重启
            if game.isShutDown():
                raise MatchGameRestartException()

            # 检查禁赛
            res, remains = BanHelper.checkBanValid(userId, int(signinParams.get('mixId')) if signinParams.get('mixId') else self.bigRoomId)
            if res:
                raise MatchBanException(remains)

            # 检查开放时间
            for conf in self.matchConf.get('feeRewardList', []):
                if conf.get('mixId') and conf.get('mixId') == signinParams.get('mixId'):
                    if not dizhu_util.checkRoomOpenTime(conf, datetime.datetime.now().time()):
                        raise MatchExpiredException(matchId=self.match.matchId, message=conf.get('openTimeListTip', ''))

            self.ensureCanSignInMatch(userId, mp)
            player = self.match.signin(userId, signinParams, feeIndex)
            clientId = player.clientId if player else sessiondata.getClientId(userId)
            finalUserChip = userchip.getChip(userId)
            bireport.reportGameEvent('MATCH_SIGN_UP', userId, DIZHU_GAMEID, self.roomId, 0, 0, 0,
                                     0, 0, [], clientId, 0, finalUserChip)
        except (MatchException, MatchBanException, MatchGameRestartException), e:
            self._handleMatchException(e, userId, mp)

        self.sendMatchStatas(userId)
        self.sendMatchSigns(userId, mixId=signinParams.get('mixId'))

    def _do_room__quicksignin(self, msg):
        userId = msg.getParam('userId')
        signinParams = msg.getParam('signinParams', {})
        feeIndex = msg.getParam('feeIndex', 0)
        isTip = msg.getParam('isTip', 0)  # 0: 直接开始， 1: 弹todo_task
        mixId = signinParams.get('mixId', 0)
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__quicksignin',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'signinParams=', signinParams,
                        'isTip=', isTip,
                        'feeIndex=', feeIndex)

        mp = MsgPack()
        mp.setCmd('m_qiucksignin')
        try:
            # 检查服务器重启
            if game.isShutDown():
                raise MatchGameRestartException()

            # 检查禁赛
            res, remains = BanHelper.checkBanValid(userId, int(signinParams.get('mixId')) if signinParams.get('mixId') else self.bigRoomId)
            if res:
                raise MatchBanException(remains)

            # 检查开放时间
            for conf in self.matchConf.get('feeRewardList', []):
                if conf.get('mixId') and conf.get('mixId') == signinParams.get('mixId'):
                    if not dizhu_util.checkRoomOpenTime(conf, datetime.datetime.now().time()):
                        raise MatchExpiredException(matchId=self.match.matchId, message=conf.get('openTimeListTip', ''))
            self.ensureCanSignInMatch(userId, mp)
            fees = self.match.matchConf.getFees(mixId)
            if fees:
                for index, fee in enumerate(fees):
                    feeIndex = index

                    if index < len(fees) - 1:
                        nextFee = fees[index + 1]
                        if not self._checkHasEnoughQuickSigninItem(userId, fee) and self._checkHasEnoughQuickSigninItem(userId, nextFee):
                            feeIndex = index + 1
                            if isTip:
                                tasks = [makeQuickSigninShow('报名失败', nextFee.getParam('nextTip', ''),
                                                             self.roomId,
                                                             0)]
                                if ftlog.is_debug():
                                    ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__quicksignin_todotask',
                                                'gameId=', self.gameId,
                                                'userId=', userId,
                                                'itemKind=', fee.assetKindId,
                                                'itemCount=', fee.count,
                                                'nextItemKind=', nextFee.assetKindId,
                                                'nextItemCount=', nextFee.count,
                                                'tasks=', tasks)
                                # 给弹窗 todo_task
                                TodoTaskHelper.sendTodoTask(self.gameId, userId, tasks)
                                return
                        if not self._checkHasEnoughQuickSigninItem(userId, fee) and not self._checkHasEnoughQuickSigninItem(userId, nextFee):
                            continue
                        break
            player = self.match.signin(userId, signinParams, feeIndex)
            clientId = player.clientId if player else sessiondata.getClientId(userId)
            finalUserChip = userchip.getChip(userId)
            bireport.reportGameEvent('MATCH_SIGN_UP', userId, DIZHU_GAMEID, self.roomId, 0, 0, 0,
                                     0, 0, [], clientId, 0, finalUserChip)
        except (MatchException, MatchBanException, MatchGameRestartException), e:
            self._handleMatchException(e, userId, mp)

        self.sendMatchStatas(userId)
        self.sendMatchSigns(userId, mixId=signinParams.get('mixId'))

        
    def _do_room__signout(self, msg):
        userId = msg.getParam('userId')
        mo = MsgPack()
        mo.setCmd('m_signout')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.bigRoomId)
        mo.setResult('userId', userId)
        try:
            player = self.match.signout(userId)
            if player:
                finalUserChip = userchip.getChip(userId)
                bireport.reportGameEvent('MATCH_SIGN_OUT', userId, DIZHU_GAMEID, self.roomId,
                                         0, 0, 0, 0, 0, [], player.clientId, 0, finalUserChip)
        except MatchException, e:
            self._handleMatchException(e, userId, mo)
        router.sendToUser(mo, userId)
        
    def _do_room__giveup(self, msg):
        userId = msg.getParam('userId')
        self.match.giveup(userId)
        
    def _do_room__des(self, msg):
        userId = msg.getParam('userId')
        signinParams = msg.getParam('signinParams', {})
        mo = MsgPack()
        mo.setCmd('m_des')
        mo.setResult('gameId', self.gameId)
        self.getMatchInfo(userId, signinParams, mo)
        router.sendToUser(mo, userId)
            
    def _do_room__quick_start(self, msg):
        assert(self.roomId == msg.getParam('roomId'))
        player = None
        userId = msg.getParam('userId')
        shadowRoomId = msg.getParam('shadowRoomId')
        tableId = msg.getParam('tableId')
        clientId = msg.getParam('clientId')
        ftlog.info('DizhuCtrlRoomArenaMatch._do_room__quick_start',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'shadowRoomId=', shadowRoomId,
                   'tableId=', tableId)
   
        if tableId == self.roomId * 10000:
            isOk = True  # 玩家在队列里时断线重连
            player = self.match.findPlayer(userId)
            
            if ftlog.is_debug():
                ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__quick_start reconnect userId=', userId,
                            'tableId=', tableId,
                            'player=', player.__dict__ if player else None)
                
            if player is None:
                ftlog.warn('DizhuCtrlRoomArenaMatch._do_room__quick_start NotFoundPlayer',
                           'roomId=', self.roomId,
                           'userId=', userId)
                onlinedata.removeOnlineLoc(userId, self.roomId, tableId)
                isOk = False
        else:
            isOk = False

        if isOk:
            reason = TYRoom.ENTER_ROOM_REASON_OK
            self.sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, self.match.tableId, mixId=player.mixId if player else None)
            # 如果用户已经被分组则发送等待信息
            if player.stage and player.state in (MatchPlayer.STATE_WAIT, MatchPlayer.STATE_RISE):
                self.match.playerNotifier.notifyMatchWait(player)

            # 如果用户处在处在则发送等待消息
            if pktimestamp.getCurrentTimestamp() <= player.reviveExpirationTime:
                self.match.playerNotifier.notifyMatchUserRevive(player, player.stage.stageConf.reviveCondition)
        else:
            reason = TYRoom.ENTER_ROOM_REASON_INNER_ERROR
            info = '在线状态错误或其他系统内部错误'
            self.sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, 0, info, mixId=player.mixId if player else None)

    def sendQuickStartRes(self, gameId, userId, reason, roomId=0, tableId=0, info="", mixId=None):
        mp = MsgPack()
        mp.setCmd('quick_start')
        mp.setResult('info', info)
        mp.setResult('mixId', mixId)
        mp.setResult('userId', userId)
        mp.setResult('gameId', gameId)
        mp.setResult('roomId', roomId)
        mp.setResult('tableId', tableId)
        mp.setResult('seatId', 0) # 兼容检查seatId参数的地主客户端
        mp.setResult('reason', reason)
        router.sendToUser(mp, userId)

    def _do_room__revival(self, msg):
        userId = msg.getParam('userId')
        isOK = msg.getParam('isOk', 0)
        player = self.match.findPlayer(userId)
        reviveCondition = player.stage.stageConf.reviveCondition
        if player and reviveCondition:
            itemId = reviveCondition.get('fee', {}).get('itemId')
            count = reviveCondition.get('fee', {}).get('count')
            if itemId and count and isOK:
                userAssets = hallitem.itemSystem.loadUserAssets(player.userId)
                timestamp = pktimestamp.getCurrentTimestamp()
                balance = userAssets.balance(HALL_GAMEID, itemId, timestamp)
                if balance and balance >= count:
                    _, consumeCount, _ = userAssets.consumeAsset(DIZHU_GAMEID, itemId, count, timestamp, 'MATCH_REVIVE', 0)
                    if consumeCount == count:
                        # 消费成功, 考虑锁的关系，时间竞争
                        ret = self.match.currentInstance.doUserRevive(player, True)
                        if not ret:
                            # 退费
                            userAssets.addAsset(DIZHU_GAMEID, itemId, count, timestamp, 'MATCH_REVIVE', 0)
                            ftlog.info('DizhuCtrlRoomArenaMatch._do_room__m_revive returnFee',
                                       'gameId=', self.gameId,
                                       'roomId=', self.roomId,
                                       'userId=', userId,
                                       'stageIndex=', player.stage.index,
                                       'reviveCondition=', reviveCondition)
                        if ret:
                            # 日志记录
                            try:
                                sequence = int(player.matchInst.instId.split('.')[1])
                                matchutil.report_bi_game_event('MATCH_REVIVE', player.userId, player.matchInst.matchId, 0, sequence, 0, 0, 0,
                                                               [int(player.mixId) if player.mixId else 0, player.stage.index, count], 'match_revive')

                                ftlog.info('DizhuCtrlRoomArenaMatch._do_room__m_revive success',
                                           'gameId=', self.gameId,
                                           'roomId=', self.roomId,
                                           'userId=', userId,
                                           'stageIndex=', player.stage.index,
                                           'reviveCondition=', reviveCondition)
                            except Exception, e:
                                ftlog.error('DizhuCtrlRoomArenaMatch._do_room__m_revive',
                                            'gameId=', self.gameId,
                                            'userId=', userId,
                                            'err=', e.message)

                else:
                    # 发送不够的todotask
                    payOrder = reviveCondition.get('fee', {}).get('params', {}).get('payOrder')
                    failure = reviveCondition.get('fee', {}).get('params', {}).get('failure')
                    mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, player.userId, TodoTaskShowInfo(failure))
                    if payOrder:
                        clientId = sessiondata.getClientId(player.userId)
                        product, _shelves = hallstore.findProductByPayOrder(self.gameId, player.userId, clientId, payOrder)
                        if product:
                            orderShow = TodoTaskOrderShow.makeByProduct(failure, '', product, 'charge', reviveCondition.get('fee', {}).get('count', 0), reviveCondition.get('fee', {}).get('itemId', ''))
                            orderShow.setParam('sub_action_btn_text', '购买')
                            mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, player.userId, orderShow)
                    router.sendToUser(mo, userId)

            else:
                self.match.currentInstance.doUserRevive(player, False)

            
    def buildMatchStatas(self, userId, signinParams=None):
        mp = MsgPack()
        mp.setCmd('m_update')
        
        player = self.match.findPlayer(userId)
        if player and player.matchInst.match != self.match:
            mp.setError(1, u'非比赛房间')
            ftlog.warn('DizhuCtrlRoomArenaMatch.buildMatchStatas room=', self.roomId,
                       'matchId=', self.match.matchId,
                       'userId=', userId,
                       'player.match=', player.matchInst.matchId,
                       'diff match')
            return mp
        inst = player.matchInst if player else self.match.currentInstance
        state = self.translateState(inst.state) if inst else 0
        mp.setResult('roomId', self.roomId)
        mp.setResult('state', state)
        curPlayer = 0
        if player and player.stage:
            curPlayer = player.stage.stageConf.totalUserCount
        else:
            if inst and inst.state == MatchInstance.STATE_STARTED:
                maxUserCount = int(inst.matchConf.stages[0].totalUserCount)
                minUserCount = maxUserCount - max(1, int(maxUserCount * 0.15))
                curPlayer = random.randint(minUserCount, maxUserCount - 1)  # inst.getSigninCount()
                
        mp.setResult('inst', inst.instId)
        mp.setResult('curPlayer', curPlayer)
        mp.setResult('curTimeLeft', 0)
        mp.setResult('startTime', '')
        mp.setResult('mixId', signinParams.get('mixId') if signinParams else None)

        roomInfo = dizhuhallinfo.loadAllRoomInfo(DIZHU_GAMEID).get(self.bigRoomId)

        peopleNumberBase = max(roomInfo.playerCount, roomInfo.signinCount)
        dumpUserCount = 0
        for conf in self.matchConf.get('feeRewardList', []):
            if signinParams and conf.get('mixId') == signinParams.get('mixId'):
                try:
                    peopleNumberBase = round(peopleNumberBase * conf.get('mixUserRate', 1))
                    peopleNumberBase = int(peopleNumberBase)
                    dumpUserCount = int(conf.get('dummyUserCount'))
                except:
                    pass
        peopleNumber = max(peopleNumberBase * 9 + dumpUserCount - random.randint(80, 88), 0)
        startTime = self.roomConf.get('matchConf', {}).get('startTime')
        stopTime = self.roomConf.get('matchConf', {}).get('stopTime')
        # Arena比赛在开赛时间之内
        if self.checkTime(startTime, stopTime):
            mp.setResult('onlinePlayerCount', peopleNumber)
            mp.setResult('signinPlayerCount', peopleNumber)
        else:
            mp.setResult('onlinePlayerCount', roomInfo.playerCount if roomInfo else 0)
            mp.setResult('signinPlayerCount', roomInfo.signinCount if roomInfo else 0)

        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch.buildMatchStatas room=', self.roomId,
                        'matchId=', self.match.matchId,
                        'userId=', userId,
                        'player=', player,
                        'stageIndex=', player.stage.index if player and player.stage else -1)
        
        if not player or not player.stage:
            return mp
        
        tcount = 1
        allcount = player.stage.stageConf.totalUserCount
        rank = player.rank
        if player.seat:
            rank = player.tableDisplayRank
        waitInfo = {
            'uncompleted':tcount,  # 还有几桌未完成
            'tableRunk':'%d/3' % player.tableRank,  # 本桌排名
            'runk':'%d/%d' % (rank, allcount),  # 总排名
            'chip':player.score,  # 当前积分
        }
        if player.state == MatchPlayer.STATE_WAIT and player.stage.index != 0:
            waitInfo['info'] = '您已经成功晋级，请等待其他玩家完成本轮比赛'
        mp.setResult('waitInfo', waitInfo)
        mp.setResult('progress', 0)
        return mp
    
    def sendMatchStatas(self, userId, signinParams=None):
        mp = self.buildMatchStatas(userId, signinParams)
        router.sendToUser(mp, userId)

    def sendMatchSigns(self, userId, mixId=None):
        signs = {self.bigRoomId:self.getUserSignsState(userId)}
        mo = MsgPack()
        mo.setCmd('m_signs')
        mo.setResult('gameId', self.gameId)
        mo.setResult('roomId', self.bigRoomId)
        mo.setResult('userId', userId)
        mo.setResult('signs', signs)
        mo.setResult('mixId', mixId)
        mo.setResult('isAll', 0)
        router.sendToUser(mo, userId)
        
    def sendMatchRanks(self, userId):
        player = self.match.findMatchingPlayer(userId)
        if player:
            self.match.playerNotifier.notifyMatchRank(player)
    
    def getUserSignsState(self, userId):
        player = self.match.findPlayer(userId)
        if not player:
            return 0
        if player.state == MatchPlayer.STATE_SIGNIN:
            return 1
        else:
            return 2
        
    def getMatchInfo(self, userId, signinParams, mo):
        inst = self.match.currentInstance
        if not inst:
            return
        
        mixId = signinParams.get('mixId', None)
        conf = inst.matchConf if inst else self.match.matchConf

        if mixId is None:
            player = self.match.findPlayer(userId)
            if player:
                mixId = player.mixId

        info = {}
        info['roomId'] = self.roomId
        info['mixId'] = mixId
        info['type'] = MatchType.USER_COUNT
        arenaContent = dizhuhallinfo.getArenaMatchProvinceContent(userId, int(mixId) if mixId else self.bigRoomId, None)
        showName = conf.getRoomName(mixId)
        if arenaContent:
            showName = arenaContent.get('showName') or showName
        info['name'] = showName
        info['minPlayer'] = info['maxPlayer'] = conf.stages[0].totalUserCount
        info['state'] = self.translateState(inst.state)
        info['curTimeLeft'] = 0
        mo.setResult('info', info)
        mo.setResult('startTime', '')

        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch.getMatchInfo',
                        'userId=', userId,
                        'signinParams=', signinParams,
                        'mixId=', mixId,
                        'info=', info,
                        'arenaContent=', arenaContent)

        matchDuration = int(self.calcMatchDuration(conf) / 60)
        mo.setResult('rankRewards', self.buildRankRewards(self.match.matchRankRewardsSelector.getRewardsList(userId, conf.getRankRewardsList(mixId), mixId)))
        mo.setResult('duration', '约%d分钟' % (min(30, matchDuration)))
            
        mo.setResult('tips', {'infos':conf.tips.infos,
                              'interval':conf.tips.interval
                              })
        
        record = MatchRecord.loadRecord(self.gameId, userId, self.match.matchId, mixId)
        if record:
            mo.setResult('mrecord', {'bestRank':record.bestRank,
                                     'bestRankDate':record.bestRankDate,
                                     'isGroup':record.isGroup,
                                     'crownCount':record.crownCount,
                                     'playCount':record.playCount})
        mo.setResult('fees', [])
        # 报名费列表
        mo.setResult('feesList', matchutil.buildFeesList(userId, conf.getFees(mixId)))
        # 分组赛奖励列表 arena_match没有分组奖励
        mo.setResult('groupRewardList', [])
        # 比赛进程 海选赛-》分组赛-》8强赛-》总决赛
        stagesList = self.buildStages(conf.stages) if conf.stages else []
        mo.setResult('stages', stagesList)
        # 比赛报名的前提条件
        conditionDesc = self.getMatchConditionDesc(self.roomId, userId)
        if conditionDesc:
            mo.setResult('conditionDesc', conditionDesc)
        # 比赛奖励分割线文字
        mo.setResult('splitWord', self.getMatchRewardSplitWord(self.roomId))
        # 获得比赛历史数据
        mo.setResult('hisitory', MatchHistoryHandler.getMatchHistory(userId, self.match.matchConf.recordId, mixId=mixId))

    def _handleMatchException(self, ex, userId, mo):
        ftlog.warn('DizhuCtrlRoomArenaMatch._handleMatchException',
                   'roomId=', self.roomId,
                   'userId=', userId,
                   'ec=', ex.errorCode,
                   'info=', ex.message)
        if isinstance(ex, SigninFeeNotEnoughException):
            self._handleSigninFeeNotEnoughException(ex, userId, mo)
        elif isinstance(ex, (SigninNotStartException,
                             SigninStoppedException,
                             SigninFullException,
                             AlreadyInMatchException,
                             MatchExpiredException,
                             ClientVersionException,
                             MatchBanException,
                             MatchGameRestartException,
                             MatchSigninConditionException)):
            self._handleSigninException(ex, userId, mo)
        else:
            mo.setError(ex.errorCode, ex.message)
            router.sendToUser(mo, userId)

    def _handleSigninException(self, ex, userId, mo):
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0
        if ddzver < 3.772:
            infoTodotask = TodoTaskShowInfo(ex.message)
            mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, infoTodotask)
            router.sendToUser(mo, userId)
        else:
            self.sendDizhuFailureMsg(self.gameId, userId, '报名失败', ex.message, None)

    def _handleSigninFeeNotEnoughException(self, ex, userId, mo):
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(userId)
        clientOs, _clientVer, _ = strutil.parseClientId(clientId)
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0

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
                mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, orderShow)
                router.sendToUser(mo, userId)
                return True
        mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, TodoTaskShowInfo(ex.fee.failure))
        router.sendToUser(mo, userId)

    def _handleSigninFeeNotEnoughException_V3_772(self, ex, userId, mo):
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(userId)
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch._handleSigninFeeNotEnoughException_V3_772',
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

        # # 其他报名费/gotoshop
        title = '报名失败'
        todotask = ex.fee.getParam('todotask')
        todoTaskObj = None
        button_title = None
        if todotask:
            button_title = "去商城"
            todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todotask).newTodoTask(self.gameId, userId, clientId)
        itemCount = 0
        itemName = ''
        itemDes = ''
        itemUrl = ''
        if 'item' in ex.fee.assetKindId and ex.fee.count>0:
            assetKind = hallitem.itemSystem.findAssetKind(ex.fee.assetKindId)
            if assetKind:
                title = '道具不足'
                itemCount = ex.fee.count
                itemName = assetKind.displayName
                itemDes = assetKind.desc
                itemUrl = assetKind.pic
        self.sendDizhuFailureMsg(self.gameId, userId, title, ex.fee.failure, todoTaskObj.toDict() if todoTaskObj else None, button_title,itemCount,itemName,itemDes,itemUrl)

    def sendDizhuFailureMsg(self, gameId, userId, title, message, todotask=None, buttonTitle=None,itemCount=0,itemName='',itemDes='',itemUrl=''):
        Alert.sendNormalAlert(gameId, userId, title, message, todotask, buttonTitle,itemCount,itemName,itemDes,itemUrl)

    def _checkHasEnoughQuickSigninItem(self, userId, fee):
        # 检查参物品数量
        from dizhu.activities.toolbox import UserBag
        quickSigninItem = UserBag.getAssetsCount(userId, fee.assetKindId)
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomArenaMatch._do_room__quicksignin_item',
                        'gameId=', self.gameId,
                        'userId=', userId,
                        'itemKind=', fee.assetKindId,
                        'itemCount=', fee.count,
                        'quickSigninItemRemaining=', quickSigninItem)
        if not quickSigninItem or quickSigninItem < fee.count:
            return 0
        return 1

    def ensureCanSignInMatch(self, userId, mp):
        ok, cond = dizhumatchcond.checkMatchSigninCond(userId, self.roomId)
        if not ok:
            raise MatchSigninConditionException(self.match.matchId, 4, cond.failure)
