# -*- coding:utf-8 -*-
'''
Created on 2016年1月20日

@author: zhaojiangang
'''
from dizhu.entity import dizhuaccount, dizhumatchcond, dizhu_util
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhu.entity.matchrecord import MatchRecord
from dizhu.gameplays import punish
from dizhu.groupmatch.interfacedizhu import MatchStatusDaoDizhu, SignIFDizhu, \
    TableControllerDizhu, PlayerNotifierDizhu, MatchRewardsDizhu, \
    UserInfoLoaderDizhu
from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallpopwnd, hallconf, hallstore, hallitem
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper, \
    TodoTaskOrderShow
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import configure, gdata
from poker.entity.dao import sessiondata, userdata, gamedata
from poker.entity.game.rooms.group_match_ctrl.const import WaitReason, StageType
from poker.entity.game.rooms.group_match_ctrl.exceptions import \
    SigninFeeNotEnoughException, SigninException, SigninConditionNotEnoughException
from poker.entity.game.rooms.group_match_ctrl.match import MatchMaster, \
    MatchArea, MatchMasterStubLocal, MatchAreaStubLocal, MatchInst
from poker.protocol import router, runcmd
from poker.servers.room.rpc.group_match_remote import MatchAreaStubRemote, \
    MatchMasterStubRemote
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class GroupMatch(object):
    _matchMap = {}
            
    WINLOSE_SLEEP = 2
    @classmethod
    def getMatch(cls, roomId):
        return cls._matchMap.get(roomId, None)
    
    @classmethod
    def setMatch(cls, roomId, match):
        cls._matchMap[roomId] = match
        
    @classmethod
    def isMaster(cls, conf, room):
        return room.roomId == cls.getMasterRoomId(conf, room)
    
    @classmethod
    def getMasterRoomId(cls, conf, room):
        if conf.start.isUserCountType():
            return room.roomId
        ctrlRoomIdList = sorted(gdata.bigRoomidsMap().get(room.bigRoomId, []))
        return ctrlRoomIdList[0]
    
    @classmethod
    def buildMatch(cls, conf, room):
        match = None
        master = None
        ctrlRoomIdList = gdata.bigRoomidsMap().get(room.bigRoomId, [])
        if conf.start.isUserCountType():
            conf.start.userMaxCountPerMatch = conf.start.userMaxCount
            conf.start.signinMaxCount = conf.start.signinMaxCount
        else:
            conf.start.userMaxCountPerMatch = int(conf.start.userMaxCount / max(len(ctrlRoomIdList), 1))
            conf.start.signinMaxCountPerMatch = int(conf.start.signinMaxCount / max(len(ctrlRoomIdList), 1))
            
        if cls.isMaster(conf, room):
            master, match = cls.buildMaster(conf, room)
            room.matchMaster = master
        else:
            match = cls.buildArea(conf, room)
        ftlog.info('GroupMatch.buildMatch roomId=', room.roomId,
                   'ctrlRoomIdList=', ctrlRoomIdList,
                   'ctrlRoomCount=', len(ctrlRoomIdList),
                   'userMaxCount=', conf.start.userMaxCount,
                   'userMaxCountPerMatch=', conf.start.userMaxCountPerMatch,
                   'signinMaxCount=', conf.start.signinMaxCount,
                   'signinMaxCountPerMatch=', conf.start.signinMaxCountPerMatch)
        if master:
            master.matchStatusDao = MatchStatusDaoDizhu(room)
        match.signIF = SignIFDizhu(room, conf.tableId, conf.seatId)
        match.tableController= TableControllerDizhu(room)
        match.playerNotifier = PlayerNotifierDizhu(room)
        match.matchRewards = MatchRewardsDizhu(room)
        match.userInfoLoader = UserInfoLoaderDizhu()
        return match, master

    @classmethod
    def buildMaster(cls, conf, room):
        ftlog.info('GroupMatch.buildMaster roomId=', room.roomId)
        master = MatchMaster(room, room.bigmatchId, conf)
        area = MatchArea(room, room.bigmatchId, conf, MatchMasterStubLocal(master))
        master.addAreaStub(MatchAreaStubLocal(master, area))
        if not conf.start.isUserCountType():
            ctrlRoomIdList = gdata.bigRoomidsMap().get(room.bigRoomId, [])
            for ctrlRoomId in ctrlRoomIdList:
                if ctrlRoomId != area.roomId:
                    master.addAreaStub(MatchAreaStubRemote(master, ctrlRoomId))
        return master, area
    
    @classmethod
    def buildArea(cls, conf, room):
        masterCtrlRoomId = cls.getMasterRoomId(conf, room)
        ftlog.info('GroupMatch.buildArea roomId=', room.roomId,
                   'masterCtrlRoomId=', masterCtrlRoomId)
        return MatchArea(room, room.bigmatchId, conf, MatchMasterStubRemote(masterCtrlRoomId))

    @classmethod
    def getMatchStatesByInst(cls, match, room, inst, mo):
        mo.setResult('roomId', room.bigRoomId)
        mo.setResult('state', cls.convertState(inst.state) if inst else 0)
        mo.setResult('inst', inst.instId if inst else str(room.roomId))
        mo.setResult('curPlayer', inst.getTotalSignerCount() if inst else 0)
        mo.setResult('curTimeLeft', cls.getMatchCurTimeLeft(inst))
        mo.setResult('startTime', inst.startTimeStr if inst else '')
        
    @classmethod
    def getMatchStatesByPlayer(cls, match, room, player, mo):
        mo.setResult('roomId', room.bigRoomId)
        mo.setResult('state', 20)
        mo.setResult('inst', player.instId)
        mo.setResult('curPlayer', player.group.playerCount)
        mo.setResult('curTimeLeft', 0)
        mo.setResult('startTime', '')
        
        tcount = player.group.calcTotalUncompleteTableCount()
        if (tcount > 1
            and player.group.stageConf.type == StageType.DIEOUT
            and player.cardCount < player.group.stageConf.cardCount):
            # 定局需要减掉本桌
            tcount -= 1
            if ftlog.is_debug():
                ftlog.debug('GroupMatch.getMatchStatesByPlayer roomId=', room.bigRoomId,
                            'instId=', player.instId,
                            'userId=', player.userId,
                            'tcount=', tcount)
            
        progress = cls.getMatchProgress(player)
        allcount = player.group.playerCount
        _, clientVer, _ = strutil.parseClientId(player.clientId)
        waitInfo = {
            'uncompleted':tcount, # 还有几桌未完成
            'tableRunk':'%d/3' % player.tableRank, # 本桌排名
            'runk':'%d/%d' % (player.rank, allcount), # 总排名
            'chip':player.score # 当前积分
        }
        if clientVer >= 3.37:
            waitInfo['info'] = cls._buildWaitInfoMsg(room, player)
        mo.setResult('waitInfo', waitInfo)
        mo.setResult('progress', progress)
    
    @classmethod
    def calcTotalSignerCount(cls, match):
        count = 0
        for areaRoomId, areaStatus in match.masterStub.masterStatus.areaStatusMap.iteritems():
            if areaStatus.instStatus:
                if ftlog.is_debug():
                    ftlog.debug('GroupMatch.calcTotalSignerCount',
                                'matchId=', match.matchId,
                                'areaRoomId=', areaRoomId,
                                'instId=', areaStatus.instStatus.instId,
                                'areaSignerCount=', areaStatus.instStatus.signerCount)
                count += areaStatus.instStatus.signerCount
        if ftlog.is_debug():
            ftlog.debug('GroupMatch.calcTotalSignerCount',
                        'matchId=', match.matchId,
                        'areaRoomId=', areaRoomId,
                        'instId=', areaStatus.instStatus.instId,
                        'count=', count)
        return count
    
    @classmethod
    def calcPlayerCount(cls, match):
        count = 0
        for areaRoomId, areaStatus in match.masterStub.masterStatus.areaStatusMap.iteritems():
            for groupId, groupStatus in areaStatus.groupStatusMap.iteritems():
                if ftlog.is_debug():
                    ftlog.debug('GroupMatch.calcPlayerCount',
                                'matchId=', match.matchId,
                                'areaRoomId=', areaRoomId,
                                'groupId=', groupId, 
                                'groupPlayerCount=', groupStatus.playerCount)
                count += groupStatus.playerCount
        if ftlog.is_debug():
            ftlog.debug('GroupMatch.calcPlayerCount',
                        'matchId=', match.matchId,
                        'count=', count)
        return count
    
    @classmethod
    def getMatchStates(cls, room, userId, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, u'非比赛房间')
            return
        
        player = match.findPlayer(userId)
        if player:
            cls.getMatchStatesByPlayer(match, room, player, mo)
        else:
            signer = match.findSigner(userId)
            inst = signer.inst if signer else match.curInst
            cls.getMatchStatesByInst(match, room, inst, mo)

        signerCount = cls.calcTotalSignerCount(match)
        playerCount = cls.calcPlayerCount(match)
        baseNumber = signerCount + playerCount
        mo.setResult('onlinePlayerCount', baseNumber)
        mo.setResult('signinPlayerCount', baseNumber)
        
    @classmethod
    def getMatchInfo(cls, room, uid, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, 'not a match room')
            return

        inst = match.curInst
        conf = inst.matchConf if inst else match.matchConf
        state = cls.convertState(inst.state) if inst else 0
        
        # 为了兼容老客户端m_enter的问题加的
        clientVer = sessiondata.getClientIdVer(uid)
        try:
            match.enter(uid)
        except:
            pass
        info = {}
        info['roomId'] = room.roomId
        info['type'] = conf.start.type
        info['name'] = room.roomConf['name']
        if conf.start.isUserCountType():
            info['minPlayer'] = conf.start.userCount
            info['maxPlayer'] = conf.start.userCount
        else:
            info['minPlayer'] = conf.start.userMinCount
            info['maxPlayer'] = conf.start.userMaxCount
            
        info['state'] = cls.convertState(state)
        info['curTimeLeft'] = cls.getMatchCurTimeLeft(inst) if inst else 0
        mo.setResult('info', info)
        mo.setResult('startTime', inst.startTimeStr if inst else '')

        mo.setResult('desc', conf.rankRewardsDesc)
        matchDuration = int(cls.calcMatchDuration(conf) / 60)
        mo.setResult('rankRewards', cls.buildRankRewards(conf.rankRewardsList))
        mo.setResult('duration', '约%d分钟' % (min(30, matchDuration)))
            
        if clientVer >= 3.37:
            mo.setResult('tips', {'infos':conf.tips.infos,
                                  'interval':conf.tips.interval})
            record = MatchRecord.loadRecord(room.gameId, uid, match.matchConf.recordId)
            if record:
                mo.setResult('mrecord', {'bestRank':record.bestRank,
                                         'bestRankDate':record.bestRankDate,
                                         'isGroup':record.isGroup,
                                         'crownCount':record.crownCount,
                                         'playCount':record.playCount})
        mo.setResult('fees', cls.buildFees(conf.fees))
        # 报名费列表
        mo.setResult('feesList', cls.buildFeesList(uid, conf.fees) if conf.fees else [])
        # 分组赛奖励列表
        groupList = []
        if len(conf.stages) > 0 and conf.stages[0].rankRewardsList and conf.stages[0].groupingUserCount:
            groupList = cls.buildRankRewards(conf.stages[0].rankRewardsList, defaultEnd = conf.stages[0].groupingUserCount)
        mo.setResult('groupRewardList', groupList)
        # 比赛进程 海选赛-》分组赛-》8强赛-》总决赛
        stagesList = cls.buildStages(conf.stages) if conf.stages else []
        mo.setResult('stages', stagesList)
        # 比赛报名的前提条件
        conditionDesc = cls.getMatchConditionDesc(room.roomId, uid)
        if conditionDesc:
            mo.setResult('conditionDesc', conditionDesc)
        # 比赛奖励分割线文字
        mo.setResult('splitWord', cls.getMatchRewardSplitWord(room.roomId))
        # 获得比赛历史数据
        mo.setResult('hisitory', MatchHistoryHandler.getMatchHistory(uid, match.matchConf.recordId))

    # 获取比赛分组奖励与非分组奖励之间分割线的描述文字
    @classmethod
    def getMatchRewardSplitWord(cls, roomId):
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
                ftlog.debug('bigmatch EmptyMatchCondConf roomId=', roomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
            return None
        else:
            ftlog.debug('bigmatch EmptyMatchCondConf roomId=', roomId,
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
            ftlog.debug('bigmatch EmptyMatchCondConf roomId=', roomId,
                    'bigRoomId=', bigRoomId,
                    'gameId=', DIZHU_GAMEID,
                    'userId=', userId,
                    'matchCondConf=', matchCondConf)
        condition = condConf.get('condition')
        if not condition:
            if ftlog.is_debug():
                ftlog.debug('bigmatch EmptyMatchCondConf.condition roomId=', roomId,
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'matchCondConf=', matchCondConf)
            return None
        desc = condition.get('desc')
        if not desc:
            if ftlog.is_debug():
                ftlog.debug('bigmatch EmptyMatchCondConf.condition.desc roomId=', roomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
            return None
        from sre_compile import isstring
        if not isstring(desc):
            if ftlog.is_debug():
                ftlog.debug('bigmatch EmptyMatchCondConf.condition.desc roomId=', roomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
            return None
        return desc

    @classmethod
    def getUserIndex(cls, matchTableInfo, uid):
        for i, seatInfo in enumerate(matchTableInfo['seats']):
            if seatInfo['userId'] == uid:
                return i
        return -1
        
    @classmethod
    def doWinLose(cls, room, table, seatId, isTimeOutKill=False): # TODO:
        if not table._match_table_info:
            ftlog.warn('GroupMatch.doWinLoseTable roomId=', room.roomId,
                       'tableId=', table.tableId,
                       'seatId=', seatId,
                       'isTimeOutKill=', isTimeOutKill,
                       'err=', 'not matchTableInfo')
            return

        if ftlog.is_debug():
            ftlog.debug('GroupMatch.doWinLose roomId=', room.roomId,
                        'tableId=', table.tableId,
                        'seatId=', seatId,
                        'isTimeOutKill=', isTimeOutKill,
                        'stageReward=', table.group.stageConf.conf.get('stageReward'))
        
        # 计算春天
        dizhuseatId = table.status.diZhu
        if seatId != dizhuseatId: 
            if table.seats[dizhuseatId - 1].outCardCount == 1:
                table.status.chuntian = 2
        else:
            s1 = table.seats[(dizhuseatId - 1 + 1) % table.maxSeatN]
            s2 = table.seats[(dizhuseatId - 1 + 2) % table.maxSeatN]
            if s1.outCardCount == 0 and s2.outCardCount == 0:
                table.status.chuntian = 2
                 
        # 翻倍计算 叫地主的倍数
        windoubles = table.status.callGrade
        # 炸弹倍数
        windoubles *= pow(2, table.status.bomb)
        # 春天倍数
        windoubles *= table.status.chuntian
        # 底牌倍数
        windoubles *= table.status.baseCardMulti
        # 明牌倍数
        windoubles *= table.status.show
         
        dizhuwin = 0
        if seatId == dizhuseatId:
            dizhuwin = 1
        if seatId == 0 : # 流局
            dizhuwin = 0
            windoubles = 1
        else:
            windoubles = abs(windoubles)
 
        userids = []
        detalChips = []
        seat_coin = []
        baseBetChip = table._match_table_info['mInfos']['basescore']
        robot_card_count = [0] * len(table.seats)  # 每个座位
        for x in xrange(len(table.seats)):
            uid = table.seats[x].userId
            userids.append(uid)
            if seatId == 0 : # 流局
                detalChip = -baseBetChip
            else:
                if dizhuwin :
                    if x + 1 == dizhuseatId :
                        detalChip = baseBetChip + baseBetChip
                    else:
                        detalChip = -baseBetChip
                else:
                    if x + 1 == dizhuseatId :
                        detalChip = -baseBetChip - baseBetChip
                    else:
                        detalChip = baseBetChip
            detalChip *= windoubles
            detalChips.append(detalChip)
            seat_coin.append(table._match_table_info['mInfos']['scores'][x] + detalChip)
            robot_card_count[x] = table.seats[x].robotCardCount
            ftlog.info('dizhu.game_win userId=', uid, 'roomId=', room.roomId, 'tableId=', table.tableId, 'delta=', detalChip)
        
        punish.Punish.doWinLosePunish(table.runConfig.punishCardCount, table.runConfig.isMatch,
                                      seat_coin, detalChips, robot_card_count)
        for x in xrange(len(table.seats)):
            uid = table.seats[x].userId
            table._match_table_info['mInfos']['scores'][x] = seat_coin[x]

        # 返回当前Table的game_win
        moWin = MsgPack()
        moWin.setCmd('table_call')
        moWin.setResult('action', 'game_win')
        moWin.setResult('isMatch', 1)
        moWin.setResult('gameId', table.gameId)
        moWin.setResult('roomId', table.roomId)
        moWin.setResult('tableId', table.tableId)
#         moWin.setResult('stat', dict(zip(tdz_stat_title, table.status)))
        moWin.setResult('stat', table.status.toInfoDictExt())
        moWin.setResult('dizhuwin', dizhuwin)
        if seatId == 0:
            moWin.setResult('nowin', 1)
        moWin.setResult('slam', 0)
        moWin.setResult('cards', [seat.cards for seat in table.seats])
        
        roundId = table.gameRound.number
        table.clear(userids)
         
        for x in xrange(len(userids)):
            uid = userids[x]
            mrank = 3
            mtableRanking = 3
            moWin.setResult('seat' + str(x + 1), [detalChips[x], seat_coin[x], 0, 0, 0, 0, mrank, mtableRanking])

            if detalChips[x] > 0:
                stageRewards = table.group.stageConf.conf.get('stageReward', None) if table.group.stageConf else None
                if stageRewards:
                    contentItems = TYContentItem.decodeList(stageRewards)
                    assetList = dizhu_util.sendRewardItems(uid, contentItems, '', 'DIZHU_STAGE_REWARD', 0)
                    moWin.setResult('stageReward', stageRewards)
                    ftlog.info('stageRewards send. userId=', uid, 'stageRewards=', stageRewards, 'assetList=', assetList)

            #增加经验
            exp = userdata.incrExp(uid, 20)
            explevel = dizhuaccount.getExpLevel(exp)
            gamedata.setGameAttr(uid, table.gameId, 'level', explevel)
            if ftlog.is_debug():
                ftlog.debug('BigMatch.doWinLoseTable',
                            'addExp=', 20,
                            'curExp=', exp,
                            'curLevel=', explevel)
             
        table.gamePlay.sender.sendToAllTableUser(moWin)
         
        # 发送给match manager
        users = []
        for x in xrange(len(userids)):
            user = {}
            user['userId'] = userids[x]
            user['deltaScore'] = int(detalChips[x])
            user['seatId'] = x + 1
            users.append(user)
         
        mnr_msg = MsgPack()
        mnr_msg.setCmd('room')
        mnr_msg.setParam('action', 'm_winlose')
        mnr_msg.setParam('gameId', table.gameId)
        mnr_msg.setParam('matchId', table.room.bigmatchId)
        mnr_msg.setParam('roomId', table.room.ctrlRoomId)
        mnr_msg.setParam('tableId', table.tableId)
        mnr_msg.setParam('users', users)
        mnr_msg.setParam('ccrc', table._match_table_info['ccrc'])
        
        if cls.WINLOSE_SLEEP > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(cls.WINLOSE_SLEEP)
        # 记录游戏winlose
        try:
            for u in users:
                table.room.reportBiGameEvent('TABLE_WIN', u['userId'], table.roomId,
                                             table.tableId, roundId, u['deltaScore'],
                                             0, 0, [], 'table_win')
        except:
            if ftlog.is_debug():
                ftlog.exception()
        router.sendRoomServer(mnr_msg, table.room.ctrlRoomId)
        
    @classmethod
    def handleMatchException(cls, room, ex, uid, mo):
        ftlog.warn('GroupMatch.handleMatchException',
                   'roomId=', room.roomId,
                   'userId=', uid,
                   'ex=', '%s:%s' % (ex.errorCode, ex.message))
        if isinstance(ex, SigninFeeNotEnoughException):
            cls._handleSigninFeeNotEnoughException(room, ex, uid, mo)
        elif isinstance(ex, SigninException):
            cls._handleSigninException(room, ex, uid, mo)
        else:
            mo.setError(ex.errorCode, ex.message)
            router.sendToUser(mo, uid)
            
    @classmethod
    def _handleSigninException(cls, room, ex, uid, mo):
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0
        if ddzver < 3.772:
            infoTodotask = TodoTaskShowInfo(ex.message)
            mo = TodoTaskHelper.makeTodoTaskMsg(room.gameId, uid, infoTodotask)
            router.sendToUser(mo, uid)
        else:
            cls.sendDizhuFailureMsg(room.gameId, uid, '报名失败', ex.message, None)
            
    @classmethod
    def _handleSigninFeeNotEnoughException(cls, room, ex, uid, mo):
        payOrder = ex.fee.getParam('payOrder')

        clientId = sessiondata.getClientId(uid)
        clientOs, _clientVer, _ = strutil.parseClientId(clientId)
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0

        ftlog.debug("groupmatch._handleSigninFeeNotEnoughException", "userId", uid, "_clientVer=", _clientVer)
        if ddzver >= 3.772:
            cls._handleSigninFeeNotEnoughException_V3_772(room, ex, uid, mo)
            return

        if payOrder:
            clientOs = clientOs.lower()
            product, _shelves = hallstore.findProductByPayOrder(room.gameId, uid, clientId, payOrder)
            if product:
                buyType = ''
                btnTxt = ''
                if ex.fee.assetKindId == hallitem.ASSET_CHIP_KIND_ID and clientOs == 'winpc':
                    user_diamond = userdata.getAttrInt(uid, 'diamond')
                    if user_diamond >= int(product.priceDiamond):
                        buyType = 'consume'
                        btnTxt = '兑换'
                    else:
                        buyType = 'charge'
                        btnTxt = '去充值'
                orderShow = TodoTaskOrderShow.makeByProduct(ex.fee.failure, '', product, buyType)
                orderShow.setParam('sub_action_btn_text', btnTxt)
                mo = TodoTaskHelper.makeTodoTaskMsg(room.gameId, uid, orderShow)
                router.sendToUser(mo, uid)
                return True
        mo = TodoTaskHelper.makeTodoTaskMsg(room.gameId, uid, TodoTaskShowInfo(ex.fee.failure))
        router.sendToUser(mo, uid)

    @classmethod
    def _handleSigninFeeNotEnoughException_V3_772(cls, room, ex, uid, mo):
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(uid)
        ftlog.debug("groupmatch._handleSigninFeeNotEnoughException_V3_772", "userId", uid, "fee.itemId=", ex.fee.assetKindId, "fee.params=", ex.fee.params)
        ftlog.debug("groupmatch._handleSigninFeeNotEnoughException_V3_772, userId=", uid, "payOrder=", payOrder)

        if payOrder:
            product, _shelves = hallstore.findProductByPayOrder(room.gameId, uid, clientId, payOrder)
            if not product:
                cls.sendDizhuFailureMsg(room.gameId, uid, '报名失败', ex.fee.failure, None)
                return

            buyType = ''
            btnTxt = ''
            if ex.fee.assetKindId == hallitem.ASSET_CHIP_KIND_ID: # 金币是报名费
                orderShow = TodoTaskOrderShow.makeByProduct(ex.fee.failure, '', product, buyType)
                orderShow.setParam('sub_action_btn_text', btnTxt)
                mo = TodoTaskHelper.makeTodoTaskMsg(room.gameId, uid, orderShow)
                router.sendToUser(mo, uid)
                return

        ## 其他报名费/gotoshop
        todotask = ex.fee.getParam('todotask')
        todotask_str = None
        button_title = None
        ftlog.debug("groupmatch._handleSigninFeeNotEnoughException_V3_772, userId=", uid, "todotask=", todotask)
        if todotask:
            button_title = "去商城"
            todotask_str = hallpopwnd.decodeTodotaskFactoryByDict(todotask).newTodoTask(room.gameId, uid, clientId).toDict()
        cls.sendDizhuFailureMsg(room.gameId, uid, '报名失败', ex.fee.failure, todotask_str, button_title)

    @classmethod
    def sendDizhuFailureMsg(cls, gameId, userId, title, message, todotask=None, buttonTitle=None):
        Alert.sendNormalAlert(gameId, userId, title, message, todotask, buttonTitle)

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
    def buildFeesList(cls, userId, fees):
        ret = [] # 返回付费列表[{type,desc,selected,img}，{...}]
        # 不用写单位的道具类型集合
        notNeedUnit = set(['user:chip', 'user:exp', 'user:charm', 'ddz:master.score']);
        for fee in fees:
            assetKind = hallitem.itemSystem.findAssetKind(fee.assetKindId)
            if fee.count > 0 and assetKind:
                desc = ''
                if fee.assetKindId in notNeedUnit:
                    desc = str(fee.count) + assetKind.displayName
                else:
                    desc = str(fee.count) + assetKind.units + assetKind.displayName
                from dizhu.activities.toolbox import UserBag
                myCount = UserBag.getAssetsCount(userId, fee.assetKindId)
                ret.append({'type':fee.assetKindId, 'desc':desc, 'img':assetKind.pic, 'selected':False, 'fulfilled':1 if myCount >= fee.count else 0})
        return ret

    @classmethod
    def buildFees(cls, fees):
        ret = []
        for fee in fees:
            if fee.count > 0:
                name = hallconf.translateAssetKindIdToOld(fee.assetKindId)
                ret.append({'item':name, 'count':fee.count})
        return ret

    @classmethod
    def calcMatchDuration(cls, conf):
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
    
    @classmethod
    def buildRankRewards(cls, rankRewardsList, defaultEnd = 10000):
        ret = []
        notNeedShow = set(['user:charm', 'user:exp', 'game:assistance'])
        for rankRewards in rankRewardsList:
            rewardDesc = cls.buildRewardsDesc(rankRewards)
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
                            'rewards':[], #此处为了兼容3.x版本不显示rewardDesc，cls.buildRewards(rankRewards),
                            'rewardsDesc':rewardDesc,
                            'rewardsList':rewardsList
                            })
            else:
                ret.append({
                            'range':{'s':rankRewards.startRank, 'e':rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                            'rewards':cls.buildRewards(rankRewards),
                            'rewardsList':rewardsList
                            })
        return ret
    
    @classmethod
    def buildRewards(cls, rankRewards):
        ret = []
        for r in rankRewards.rewards:
            if r['count'] > 0:
                name = hallconf.translateAssetKindIdToOld(r['itemId'])
                ret.append({'name':name or '', 'count':r['count']})
        return ret
    
    @classmethod
    def buildRewardsDesc(cls, rankRewards):
        notNeedDescNames = set(['user:chip', 'user:coupon', 'ddz.exp'])
    
        allZero = True
        for r in rankRewards.rewards:
            if r['count'] <= 0:
                continue
            if r['itemId'] not in notNeedDescNames:
                return rankRewards.desc
            #allZero = False# #此处为了兼容3.x版本不显示rewardDesc
        return rankRewards.desc if allZero else None
        
    @classmethod
    def ensureCanSignInMatch(cls, room, uid, mo):
        ok, cond = dizhumatchcond.checkMatchSigninCond(uid, room.roomId)
        if not ok:
            raise SigninConditionNotEnoughException(cond.failure)
        
    @classmethod
    def _buildWaitInfoMsg(cls, room, player):
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


