# -*- coding:utf-8 -*-
'''
Created on 2014年9月27日

@author: zjgzzz@126.com, Zhouhao
'''
from dizhu.bigmatch.interfacedizhu import SigninFeeDizhu, PlayerLocationDizhu, \
    TableControllerDizhu, PlayerNotifierDizhu, UserInfoLoaderDizhu, \
    SigninRecordDaoDizhu, MatchRewardsDizhu, MatchStatusDaoDizhu
from dizhu.entity import dizhuaccount, dizhumatchcond
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhu.entity.matchrecord import MatchRecord
from dizhu.gameplays import punish
from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
from freetime.util.log import getMethodName
import freetime.util.log as ftlog
from hall.entity import  hallpopwnd
from hall.entity import hallstore, hallitem, hallconf
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper, \
    TodoTaskOrderShow
from poker.entity.configure import configure, gdata
from poker.entity.dao import sessiondata, userdata, gamedata
from poker.entity.game.rooms.big_match_ctrl.const import WaitReason
from poker.entity.game.rooms.big_match_ctrl.exceptions import \
    ClientVersionException, MatchSigninConditionException, \
    SigninFeeNotEnoughException, SigninNotStartException, SigninStoppedException, \
    SigninFullException, MatchAlreadyStartedException, MatchExpiredException
from poker.entity.game.rooms.big_match_ctrl.match import Match, MatchInstance
from poker.entity.game.rooms.big_match_ctrl.matchif import MatchIF
from poker.entity.game.rooms.big_match_ctrl.utils import Utils
from poker.entity.game.rooms.roominfo import loadAllRoomInfo
from poker.protocol import router
from poker.protocol import runcmd
from poker.util import strutil
from poker.util.strutil import parseClientId


class BigMatch(MatchIF):
    # key=roomId, value=Match
    _matchMap = {}
    WINLOSE_SLEEP = 2
    
    @classmethod
    def getMatch(cls, roomId):
        return cls._matchMap.get(roomId, None)
    
    @classmethod
    def setMatch(cls, roomId, match):
        cls._matchMap[roomId] = match
    
    @classmethod
    def buildMatch(cls, conf, room):
        match = Match(conf)
        match.matchStatusDao = MatchStatusDaoDizhu(room)
        match.signinFee = SigninFeeDizhu(room)
        match.playerLocation = PlayerLocationDizhu()
        match.tableController= TableControllerDizhu()
        match.playerNotifier = PlayerNotifierDizhu(room)
        match.userInfoLoader = UserInfoLoaderDizhu()
        match.signinRecordDao = SigninRecordDaoDizhu(room)
        match.matchRewards = MatchRewardsDizhu(room)
        return match

    @classmethod
    def getMatchInfo(cls, room, uid, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, 'not a match room')
            return

        inst = match.currentInstance
        if not inst:
            return
        
        conf = inst.conf if inst else match.conf
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
        info['name'] = room.roomConf["name"]
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

        if clientVer >= 2.32:
            mo.setResult('desc', conf.rankRewardsDesc)
        else:
            mo.setResult('desc', conf.desc + '\n' + conf.rankRewardsDesc)

        if clientVer >= 2.7:
            matchDuration = int(cls.calcMatchDuration(conf) / 60)
            mo.setResult('rankRewards', cls.buildRankRewards(conf.rankRewardsList))
            mo.setResult('duration', '约%d分钟' % (min(30, matchDuration)))
            
        if clientVer >= 3.37:
            mo.setResult('tips', {
                                  'infos':conf.tips.infos,
                                  'interval':conf.tips.interval
                                  })
            record = MatchRecord.loadRecord(room.gameId, uid, match.matchId)
            if record:
                mo.setResult('mrecord', {'bestRank':record.bestRank,
                                         'bestRankDate':record.bestRankDate,
                                         'isGroup':record.isGroup,
                                        'crownCount':record.crownCount,
                                        'playCount':record.playCount})
        mo.setResult('fees', cls.matchinfobuildFees(conf.fees))
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
    def matchinfobuildFees(cls, fees):
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
    def buildRewards(cls, rankRewards):
        ret = []
        for r in rankRewards.rewards:
            if r['count'] > 0:
                name = hallconf.translateAssetKindIdToOld(r['itemId'])
                assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
                ret.append({'name':name or '', 'count':r['count'], 'url': assetKind.pic if assetKind else ''})
        return ret

    @classmethod
    def buildRankRewards(cls, rankRewardsList, defaultEnd = 10000):
        ret = []
        for rankRewards in rankRewardsList:
            rewardDesc = cls.buildRewardsDesc(rankRewards)
            rewardsList = [] # 奖励信息列表 [{name,num,unit,decs,img},{"电饭煲","1","台","电饭煲x1台","${http_download}/hall/item/imgs/item_1017.png"}]
            for r in rankRewards.rewards:
                assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
                if r['count'] > 0 and assetKind:
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
    def ensureCanSignInMatch(cls, room, uid, mo):
        ok, cond = dizhumatchcond.checkMatchSigninCond(uid, room.roomId)
        if not ok:
            raise MatchSigninConditionException(4, cond.failure)

    @classmethod
    def convertState(cls, state):
        if (state >= MatchInstance.STATE_IDLE
            and state < MatchInstance.STATE_STARTING):
            return 0
        if (state >= MatchInstance.STATE_STARTING
            and state < MatchInstance.STATE_FINISH):
            return 10
        return 20
    
    @classmethod
    def getMatchCurTimeLeft(cls, inst):
        timestamp = Utils.timestamp()
        if (inst
            and inst.conf.start.isTimingType()
            and inst.state < MatchInstance.STATE_STARTING
            and inst.startTime > timestamp):
            return inst.startTime - timestamp
        return 0
    
    @classmethod
    def getMatchProgress(cls, player):
        if player.group and player.group.stage:
            return player.group.stage.calcRemTimes(player.group)
        return 0


    @classmethod
    def __buildWaitInfoMsg(cls, room, player, group):
        conf = {}
        if player.waitReason == WaitReason.BYE:
            # 轮空提示
            return conf.get('byeMsg', u'轮空等待') 
        elif player.waitReason == WaitReason.RISE:
            # 晋级等待
            if player.rank < group.stage.conf.riseUserCount:
                return conf.get('maybeRiseMsg', u'您非常有可能晋级，请耐心等待')
            else:
                return conf.get('riseMsg', u'请耐心等待其他玩家')
        return conf.get('waitMsg', u'请耐心等待其他玩家')
    
    @classmethod
    def getMatchStates(cls, room, player, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, u'非比赛房间')
            return
        if player and player.inst.match != match:
            mo.setError(1, u'非比赛房间')
            ftlog.warn('BigMatch.getMatchStatesImpl room=', room.roomId,
                        'roomMatch=', match.matchId, 'player.match=', player.inst.match.matchId,
                        'diff match')
            return
        inst = player.inst if player else match.currentInstance
        state = cls.convertState(inst.state) if inst else 0
        mo.setResult('roomId', room.roomId)
        mo.setResult('state', state)
        curPlayer = 0
        if player and player.group:
            curPlayer = len(player.group.rankList)
        else:
            curPlayer = len(inst.playerMap) if inst else 0
        mo.setResult('inst', inst.instId if inst else str(room.roomId))
        mo.setResult('curPlayer', curPlayer)
        mo.setResult('curTimeLeft', cls.getMatchCurTimeLeft(inst))
        mo.setResult('startTime', inst.startTimeStr if inst else '')

        #该比赛在线人数
        online_count = 0
        #该比赛报名人数
        sigin_count = 0
        roominfo = cls.getRoomInfo(gdata.getBigRoomId(room.roomId))
        if roominfo:
            online_count = roominfo.get('playerCount', 0)
            sigin_count = roominfo.get('signinCount', 0)

        mo.setResult('onlinePlayerCount', online_count)
        mo.setResult('signinPlayerCount', sigin_count)
        
        if not player or not player.group:
            return
        tcount = 0
        if player.group.stage:
            tcount = player.group.stage.calcUncompleteTableCount(player.group)
        else:
            tcount = player.group.busyTableCount
        progress = cls.getMatchProgress(player)
        
        allcount = len(player.group.rankList)
        clientVer = parseClientId(player.clientId)[1]
        if clientVer >= 2.32:
            waitInfo = {
                'uncompleted':tcount, # 还有几桌未完成
                'tableRunk':'%d/3' % player.tableRank, # 本桌排名
                'runk':'%d/%d' % (player.rank, allcount), # 总排名
                'chip':player.chip # 当前积分
            }
            if clientVer >= 3.37 and player.group:
                waitInfo['info'] = cls.__buildWaitInfoMsg(room, player, player.group)
            mo.setResult('waitInfo', waitInfo)
        else:
            if tcount == 0 :
                msg = u'请等待...\n本桌排名：%d/3\t全场排名：%d/%d\n积分：%d\n' % (player.tableRank, player.rank, allcount, player.chip)
            else:
                msg = u'还有%d桌未完成，请等待...\n本桌排名：%d/3\t全场排名：%d/%d\n积分：%d\n' % (tcount, player.tableRank, player.rank, allcount, player.chip)
            mo.setResult('waitMsg', msg)
        mo.setResult('progress', progress)

    @classmethod
    def __getUserIndex(cls, matchTableInfo, uid):
        for i, seatInfo in enumerate(matchTableInfo['seats']):
            if seatInfo['userId'] == uid:
                return i
        return -1
    
    @classmethod
    def getMatchUserInfo(cls, room, table, uid, oseat):
        if table._match_table_info:
            try:
                uidIndex = cls.__getUserIndex(table._match_table_info, uid)
                if uidIndex != -1:
                    oseat['mscore'] = table._match_table_info['mInfos']['scores'][uidIndex]
                    oseat['mrank'] = table._match_table_info['mInfos']['rank'][uidIndex]
                    record = MatchRecord.loadRecord(room.gameId, uid, table._match_table_info['matchId'])
                    if record:
                        oseat['mrecord'] = {'bestRank':record.bestRank,
                                            'crownCount':record.crownCount,
                                            'playCount':record.playCount}
                    return
            except:
                ftlog.exception()
        oseat['mscore'] = 0
        oseat['mrank'] = 0
    
    @classmethod
    def getMatchTableInfo(cls, room, table, mo):
        if table._match_table_info:
            ftlog.debug("<<")
            mo.setResult('mnotes', table._match_table_info['mnotes'])
            mo.setResult('mInfos', table._match_table_info['mInfos'])
            mo.setResult('step', {
                            'name':table._match_table_info['step']['name'],
                            'des':'%s人参赛，%s人晋级' % (table._match_table_info['step']['playerCount'],
                                                   table._match_table_info['step']['riseCount']),
                            'playerCount':table._match_table_info['step']['playerCount']
                        })
    

    @classmethod
    def doWinLose(cls, room, table, seatId, isTimeOutKill=False): # TODO:

        if not table._match_table_info:
            ftlog.warn('BigMatch.doWinLoseTable roomId=', room.roomId,
                        'tableId=', table.tableId,
                        'seatId=', seatId, 'isTimeOutKill=', isTimeOutKill,
                        'not matchTableInfo')
            return
        
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
 
#         matchlog('Match->doWinLose dizhuwin=', dizhuwin , 'dizhuseatId=', dizhuseatId, 'windoubles=', windoubles)
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
        
        ftlog.debug('doWinLose->after room fee->robot_card_count=', robot_card_count)
#         table.punishClass().doWinLosePunish(table, seat_coin, detalChips)
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
         
        for x in xrange(len(table.seats)):
            uid = table.seats[x].userId
            mrank = 3
            mtableRanking = 3
            moWin.setResult('seat' + str(x + 1), [detalChips[x], seat_coin[x], 0, 0, 0, 0, mrank, mtableRanking])
             
            #增加经验
            exp = userdata.incrExp(uid, 20)
            explevel = dizhuaccount.getExpLevel(exp)
            gamedata.setGameAttr(uid, table.gameId, 'level', explevel)
            ftlog.debug('BigMatch.doWinLoseTable add 20 exp, tootle', exp, 'level', explevel)
             
#         nhWin = []
#         table.makeBroadCastUsers(nhWin)
#         tasklet.sendUdpToMainServer(moWin, nhWin)
        table.gamePlay.sender.sendToAllTableUser(moWin)
         
        # 发送给match manager
        users = []
        for x in xrange(len(table.seats)):
            user = {}
            user['userId'] = table.seats[x].userId
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
                table.room.reportBiGameEvent("TABLE_WIN", u['userId'], table.roomId, table.tableId, roundId, u['deltaScore'], 0, 0, [], 'table_win')
#                 cls.report_bi_game_event(TyContext.BIEventId.TABLE_WIN, u['userId'], table._rid, table._id, table._roundId, u['deltaScore'], 0, 0, [], 'table_win')                
        except:
            if ftlog.is_debug():
                ftlog.exception()
#         serverids = tasklet.gdata.map_room_servers[table.room.bigmatchId]
#         mainClient = tasklet.gdata.clientmap[serverids[0]]
#         mainClient.sendMessage2(None, mnr_msg.pack())
        router.sendRoomServer(mnr_msg, table.room.ctrlRoomId)
    
        
    @classmethod
    def handleMatchException(cls, room, ex, uid, mo):
        ftlog.warn(getMethodName(), "<<|roomId, userId:", room.roomId, uid, ex.message)
        if isinstance(ex, SigninFeeNotEnoughException):
            cls.__handleSigninFeeNotEnoughException(room, ex, uid, mo)
        elif isinstance(ex, (SigninNotStartException,
                             SigninStoppedException,
                             SigninFullException,
                             MatchAlreadyStartedException,
                             MatchExpiredException,
                             ClientVersionException,
                             MatchSigninConditionException)):
            cls.__handleSigninException(room, ex, uid, mo)
        else:
            mo.setError(ex.errorCode, ex.message)
            router.sendToUser(mo, uid)
        
            
    @classmethod
    def __handleSigninException(cls, room, ex, uid, mo):
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0
        if ddzver < 3.772:
            infoTodotask = TodoTaskShowInfo(ex.message)
            mo = TodoTaskHelper.makeTodoTaskMsg(room.gameId, uid, infoTodotask)
            router.sendToUser(mo, uid)
        else:
            cls.sendDizhuFailureMsg(room.gameId, uid, '报名失败', ex.message, None)
                    
    @classmethod
    def __handleSigninFeeNotEnoughException(cls, room, ex, uid, mo):
        msg = runcmd.getMsgPack()
        ddzver = msg.getParam('ddzver', 0) if msg else 0
        ftlog.debug("bigmatch._handleSigninFeeNotEnoughException useId=", uid)
        payOrder = ex.fee.getParam('payOrder')
        clientId = sessiondata.getClientId(uid)
        clientOs, _clientVer, _ = strutil.parseClientId(clientId)

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
        ftlog.debug("bigmatch._handleSigninFeeNotEnoughException_V3_772", "userId", uid, "fee.itemId=", ex.fee.assetKindId, "fee.params=", ex.fee.params)
        ftlog.debug("bigmatch._handleSigninFeeNotEnoughException_V3_772, userId=", uid, "payOrder=", payOrder)

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
        todoTaskObj = None
        ftlog.debug("bigmatch._handleSigninFeeNotEnoughException_V3_772, userId=", uid, "todotask=", todotask)
        if todotask:
            todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todotask).newTodoTask(room.gameId, uid, clientId)
        cls.sendDizhuFailureMsg(room.gameId, uid, '报名失败', ex.fee.failure, todoTaskObj, '去商城')

    @classmethod
    def sendDizhuFailureMsg(cls, gameId, userId, title, message, todotask=None, buttonTitle=None):
        Alert.sendNormalAlert(gameId, userId, title, message, todotask, buttonTitle)

    @classmethod
    def getRoomInfo(cls, roomId):
        '''
        获得大房间信息
        :param roomId:要获得的房间号,大房间号
        :return: {'signinCount': 0, "playerCount": 0}
        '''
        allroominfo = loadAllRoomInfo(6)
        allrooms = {}
        for id in allroominfo:
            subroom = allroominfo.get(id)
            bigroomId = gdata.getBigRoomId(id)
            room = allrooms.get(bigroomId, {'signinCount': 0, "playerCount": 0})
            room['signinCount'] += subroom.signinCount or 0
            room['playerCount'] += subroom.playerCount or 0
            allrooms[bigroomId] = room
        return allrooms.get(roomId)