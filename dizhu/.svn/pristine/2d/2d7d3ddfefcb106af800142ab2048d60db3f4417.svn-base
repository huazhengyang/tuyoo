# coding=UTF-8
'''
'''
from _collections import deque
from dizhu.entity import tablepay, smilies, treasurebox, dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import dizhu.entity.skillscore as skillscore
from dizhu.gametable.dizhu_player import DizhuPlayer
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from hall.entity import hallconf
from hall.entity.todotask import TodoTaskHelper
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from poker.entity.game.tables.table_sender import TYTableSender
from poker.protocol import router
from poker.util import strutil
from dizhu.gametable.dizhu_state import DizhuState


__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]



class DizhuSender(TYTableSender):
    HIDE_CARD_VER = 3.815

    def __init__(self, table):
        super(DizhuSender, self).__init__(table)
        if not self.table :
            from dizhu.gametable.dizhu_table import DizhuTable
            self.table = DizhuTable()

    def fillCardNote(self, cardNote, cards):
        for card in cards:
            point = self.table.gamePlay.card.rule.cardToPoint(card)
            if point < 13:
                point = self.table.gamePlay.card.rule.pointToCard(point)
            cardNote[point] += 1
        return cardNote
            
    def buildCardNote(self, seatIndex):
        ret = [0 for _ in xrange(15)]
        for i, seat in enumerate(self.table.seats):
            if i != seatIndex:
                self.fillCardNote(ret, seat.cards)
        if self.table.status.state < DizhuState.TABLE_STATE_PLAYING:
            self.fillCardNote(ret, self.table.status.baseCardList)
        if self.table.status.kickOutCardList:
            self.fillCardNote(ret, self.table.status.kickOutCardList)
        if self.table.gamePlay.getPlayMode() == dizhuconf.PLAYMODE_ERDOU:
            ret[2] = ret[3] = 0
        return ret
    
    def buildStatusInfoDict(self, player):
        ret = self.table.status.toInfoDict()
        self.filterTableStat(player, ret)
        return ret
    
    def buildSeatInfo(self, player, seat):
        ret = seat.toInfoDict()
        if player.userId != seat.userId:
            return self.filterSeatInfo(player, ret)
        return ret
#         ['uid', 'state', 'robot', 'call', 'call2', 'card',
#                   'outcnt', 'timeoutcnt', 'show', 'couponcard',
#                   'voice', 'robotcards']
        
    def filterSeatInfo(self, player, seatInfo):
        if (player.gameClientVer >= DizhuSender.HIDE_CARD_VER
            and self.table.state < DizhuState.TABLE_STATE_PLAYING):
            seatInfo['card'] = [-1 for _ in len(seatInfo['card'])]
            seatInfo['hpIn'] = [-1 for _ in len(seatInfo['hpIn'])]
            seatInfo['hpOut'] = [-1 for _ in len(seatInfo['hpOut'])]
        return seatInfo
    
    def filterTableStat(self, player, stat):
        if (player.gameClientVer >= DizhuSender.HIDE_CARD_VER
            and self.table.state < DizhuState.TABLE_STATE_PLAYING):
            stat['basecard'] = [-1 for _ in len(stat['basecard'])]
        return stat
    
    def sendRobotNotifyCallUp(self, params):
        hasrobot = self.table.runConfig.hasrobot
        ftlog.debug("|hasrobot, params", hasrobot, params, caller=self)
        if hasrobot :
            ucount, uids = self.table.getSeatUserIds()
            mo = self.createMsgPackRequest("robotmgr")
            if params :
                mo.updateParam(params)
            mo.setAction('callup')
            mo.setParam('userCount', ucount)
            mo.setParam('seatCount', len(uids))
            mo.setParam('users', uids)
            router.sendRobotServer(mo, self.table.tableId)

    def sendRobotNotifyShutDown(self, params):
        hasrobot = self.table.runConfig.hasrobot
        ftlog.debug("|hasrobot, params", hasrobot, params, caller=self)
        if hasrobot :
            ucount, uids = self.table.getSeatUserIds()
            mo = self.createMsgPackRequest("robotmgr")
            if params :
                mo.updateParam(params)
            mo.setAction('shutdown')
            mo.setParam('userCount', ucount)
            mo.setParam('seatCount', len(uids))
            mo.setParam('users', uids)
            router.sendRobotServer(mo, self.table.tableId)

    def sendOnlineChanged(self, player):
        mo = self.createMsgPackRes('table_call', 'online_changed')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('online', 1 if self.table.seats[player.seatIndex].online else 0)
        for p in self.table.players:
            if p != player and p.userId > 0:
                router.sendToUser(mo, p.userId)
                
    def sendQuickStartRes(self, userId, clientId, result):
        ftlog.debug("|params", userId, clientId, result, caller=self)
        mpSitRes = self.createMsgPackRes("quick_start")
        mpSitRes.updateResult(result)
        router.sendToUser(mpSitRes, userId)


    def sendSitRes(self, userId, clientId, result):
        ftlog.debug("|params", userId, clientId, result, caller=self)
        _, clientVer, _ = strutil.parseClientId(clientId)
        mpSitRes = self.createMsgPackRes("sit")
        mpSitRes.updateResult(result)
        router.sendToUser(mpSitRes, userId)
        
        
    def sendTableLeaveRes(self, userId, clientId, result):
        ftlog.debug("|params", userId, clientId, result, caller=self)
        _, clientVer, _ = strutil.parseClientId(clientId)
        mpSitRes = self.createMsgPackRes("table_leave")
        mpSitRes.updateResult(result)
        router.sendToUser(mpSitRes, userId)

    def sendTableInfoResAll(self, isrobot=0):
        ftlog.debug('sendTableInfoResAll !! len players=', self.table.playersNum,
                    'len observers=', self.table.observers)
        for p in self.table.players :
            if p.userId > 0 :
                self.sendTableInfoRes(p.userId, p.clientId, isrobot)
        for p in self.table.observers :
            if p.userId > 0 :
                self.sendTableInfoRes(p.userId, p.clientId, isrobot)


    def sendTableInfoRes(self, userId, clientId, isrobot):
        ftlog.debug('userId', userId, "|clientId", clientId, 'isrobot=', isrobot, caller=self)
        player = self.table.getPlayer(userId)
        if not player:
            ftlog.warn('DizhuSender.sendTableInfoRes NotPlayer tableId=', self.table.tableId,
                       'userId=', userId)
            return
        baseinfo = self.table.buildBasicInfo(False, userId, clientId)
        _, clientVer, _ = strutil.parseClientId(clientId)
        mo = self.createMsgPackRes("table_info")
        playMode = self.table.gamePlay.getPlayMode()
        if clientVer <= 3.7 :
            if playMode == dizhuconf.PLAYMODE_HAPPY or playMode == dizhuconf.PLAYMODE_123 :
                playMode = 'normal'  # FIX, 客户端happy和123都是normal, grab=1就是欢乐
        isMatch = self.table.isMatch
        mo.setResult('isrobot', isrobot)
        mo.setResult('playMode', playMode)
        
        roomLevel = gdata.roomIdDefineMap()[self.table.roomId].configure.get('roomLevel', 1)
        mo.setResult('roomLevel', roomLevel)
        roomName = self.table.room.roomConf['name'] if self.table.room else ''
        mo.setResult('roomName', roomName)
        mo.setResult('isMatch', isMatch)
        mo.setResult('info', baseinfo['info'])
        mo.setResult('config', baseinfo['config'])
        mo.setResult('stat', self.buildStatusInfoDict(player))
        mo.setResult('myCardNote', self.buildCardNote(player.seatIndex))
        if self.table.gameRound:
            mo.setResult('roundId', self.table.gameRound.roundId)
        
        if self.table._complain_open:
            clientIdVer = sessiondata.getClientIdVer(userId)
            clientIdLimit = dizhuconf.getAllComplainInfo().get("clientIdLimit", 3.72)
            if clientIdVer >= clientIdLimit:
                mo.setResult('complain', self.table._complain)
        
        ftlog.debug("before getMatchTableInfo:", mo)
        if isMatch :
            self.table.room.matchPlugin.getMatchTableInfo(self.table.room, self.table, mo)
        ftlog.debug("after getMatchTableInfo:", mo)

        # 当前table的奖券任务奖励 wuyangwei
        bigRoomId = self.table.bigRoomId
        _, itemCount = treasurebox.getTreasureRewardItem(bigRoomId)

        for i in xrange(len(self.table.seats)):
            seat = self.table.seats[i]
            oseat = self.buildSeatInfo(player, seat)
            seatuid = seat.userId
            if seatuid :
                seatPlayer = self.table.players[i]
                oseat.update(seatPlayer.datas)
                oseat['cardNote'] = seatPlayer.getCardNoteCount()
                seatPlayer.cleanDataAfterFirstUserInfo()

                # 当前table的奖券任务奖励 wuyangwei
                oseat['count'] = itemCount

                if isMatch:
                    self.table.room.matchPlugin.getMatchUserInfo(self.table.room, self.table, seatuid, oseat)
            else:
                oseat['uid'] = 0
            mo.setResult('seat' + str(i + 1), oseat)

        tmpobsr = []
        for _, obuser in self.table.observers.items() :
            if obuser :
                tmpobsr.append((obuser.userId, obuser.name))
        mo.setResult('obsr', tmpobsr)
        
        mo.setResult('betpoolClose', 1)
        
        ftlog.debug("cardNote test come to assemble cardNote info, userId = ", userId)
        if player:
            ftlog.debug("cardNote test player cardNoteCount = ", player.getCardNoteCount())
        else:
            ftlog.debug("cardNote test player is None ")
            
        if player and player.getCardNoteCount() < 1:
            tableConf = self.table.room.roomConf.get('tableConf') if self.table.room else None
            cardNoteChip = tableConf.get('cardNoteChip', 0)
            cardNoteDiamod = tableConf.get('cardNoteDiamond', 0)
            cardNote = dizhuconf.getCardNoteTips(userId, player.datas.get('chip', 0),
                                                 clientId, cardNoteChip, cardNoteDiamod)
            if cardNote:
                mo.setResult('cardNote', cardNote)

        if isMatch :
            step = mo.getResult('step')
            if step and self.table._match_table_info:
                # 比赛的当前提示信息
                step['note'] = self.table._buildNote(userId, self.table._match_table_info)
                # 发送消息至客户端
                router.sendToUser(mo, userId)
        else:
            # 桌面充值商品
            player = self.table.getPlayer(userId)
            if not player :
                player = self.table.getObserver(userId)
            if player and player.userId:
                mo.setResult('products', tablepay.getProducts(userId, self.table.roomId, player.clientId))
                # 互动表情配置
                mo.setResult('smiliesConf', smilies.getConfDict(self.table.bigRoomId, userId))
                # 发送消息至客户端
                router.sendToUser(mo, userId)


    def sendToAllTableUser(self, mo):
        ftlog.debug('sendToAllTableUser !! len players=', len(self.table.players),
                    'len observers=', self.table.observers)
        if isinstance(mo, MsgPack) :
            mo = mo.pack()
        for p in self.table.players :
            if p.userId > 0 :
                router.sendToUser(mo, p.userId)
        for p in self.table.observers :
            if p.userId > 0 :
                router.sendToUser(mo, p.userId)


    def sendUserReadyRes(self, player):
        mo = self.createMsgPackRes('table_call', 'ready')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        self.sendToAllTableUser(mo)


    def sendShowCardRes(self, player):
        mo = self.createMsgPackRes('table_call', 'show')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('stat', self.buildStatusInfoDict(player))
        mo.setResult('seatCards', self.buildSeatCards(player, self.table.seats[player.seatIndex]))
        self.sendToAllTableUser(mo)


    def sendGameReadyRes(self):
        for i in xrange(len(self.table.seats)):
            self.sendGameReadyResForSeat(i)

    def sendGameReadyResForSeat(self, seatIndex):
        mo = self.createMsgPackRes('table_call', 'game_ready')
        for i, seat in enumerate(self.table.seats):
            cards = seat.cards
            if (self.table.players[seatIndex].gameClientVer >= DizhuSender.HIDE_CARD_VER
                and i != seatIndex
                and not seat.isShow):
                # 隐藏没有明牌人的牌的牌
                cards = [-1 for _ in xrange(len(seat.cards))]
            mo.setResult('cards' + str(i), cards)
        basecard = self.table.status.baseCardList
        kickoutCard = self.table.status.kickOutCardList
        if self.table.players[seatIndex].gameClientVer >= DizhuSender.HIDE_CARD_VER:
            # 隐藏底牌，剔除的牌
            basecard = [-1 for _ in xrange(len(basecard))]
            kickoutCard = [-1 for _ in xrange(len(kickoutCard))]
        mo.setResult('basecard', basecard)
        mo.setResult('kickoutCard', kickoutCard)
        mo.setResult('rangpai', self.table.status.rangPai)
        mo.setResult('grabCard', self.table.status.grabCard)
        mo.setResult('myCardNote', self.buildCardNote(seatIndex))
        if self.table.gameRound:
            mo.setResult('roundId', self.table.gameRound.roundId)
        if self.table._complain:
            mo.setResult('gameNum', self.table.gameRound.roundId)
        router.sendToUser(mo, self.table.seats[seatIndex].userId)
    
    def sendCallNextRes(self, nextSid, grab):
        mo = self.createMsgPackRes('table_call', 'next')
        mo.setResult('seatId', nextSid)
        mo.setResult('next', nextSid)
        mo.setResult('grab', grab)
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('opTime', self.table.runConfig.optime)
        self.sendToAllTableUser(mo)


    def sendCallRes(self, seatId, userId, call):
        mo = self.createMsgPackRes('table_call', 'call')
        mo.setResult('seatId', seatId)
        mo.setResult('userId', userId)
        mo.setResult('call', call)
        self.sendToAllTableUser(mo)


    def sendWildCardRes(self, wildCard, wildCardBig):
        mo = self.createMsgPackRes('table_call', 'wild_card')
        mo.setResult('wildcard', wildCard)
        mo.setResult('wildCardBig', wildCardBig)
        self.sendToAllTableUser(mo)


    def sendGameStartRes(self):
        mo = self.createMsgPackRes('table_call', 'game_start')
        mo.setResult('action', 'game_start')
        mo.setResult('stat', self.table.status.toInfoDict())
        # 发送每个座位的tbc,tbt
        seatTBBoxInfoList = []
        bigRoomId = self.table.bigRoomId
        for p in self.table.players:
            itemId, itemCount = treasurebox.getTreasureRewardItem(bigRoomId)
            if itemId :
                itemId = hallconf.translateAssetKindIdToOld(itemId)
            seatTBBoxInfoList.append({'tbc':p.datas['tbc'], 'tbt': p.datas['tbt'], 'item':itemId, 'count':itemCount})
        mo.setResult('seattb', seatTBBoxInfoList)
        for p in self.table.players:
            mo.setResult('myCardNote', self.buildCardNote(p.seatIndex))
            router.sendToUser(mo, p.userId)

    def sendPunishTipRes(self, seatId, userId, punishTip):
        mo = self.createMsgPackRes('table_call', 'note')
        mo.setResult('seatId', seatId)
        mo.setResult('userId', userId)
        mo.setResult('bgcolor', 'FF0000')  # 文字背景色
        mo.setResult('fgcolor', '00FF00')  # 文字字体颜色
        mo.setResult('seconds', 3)  # 提示显示的时间，秒
        mo.setResult('info', punishTip)
        router.sendToUser(mo, userId)


    def sendTuoGuanRes(self, seatId):
        robots = []
        for seat in self.table.seats:
            robots.append(seat.isRobot)
        mo = self.createMsgPackRes('table_call', 'rb')
        mo.setResult('robots', robots)
        mo.setResult('seatId', seatId)

        ccount = len(self.table.seats[seatId - 1].cards)
        if ccount > 2:
            mo.setResult('tuoguantip', "我托管，我包赔！有钱就是这么任性！！")
        self.sendToAllTableUser(mo)


    def sendTuoGuanErrorRes(self, userId):
        robots = []
        for seat in self.table.seats:
            robots.append(seat.isRobot)
        mo = self.createMsgPackRes('table_call', 'rb')
        mo.setResult('robots', robots)
        mo.setResult('tips', '托管太频繁,禁止托管操作')
        router.sendToUser(mo, userId)


    def sendChuPaiRes(self, seatId, userId, cards, precard, tuoGuanType):
        for i in xrange(len(self.table.seats)):
            self.sendChuPaiResToSeat(seatId - 1, cards, precard, tuoGuanType, i)

    def sendChuPaiResToSeat(self, seatIndex, cards, precard, tuoGuanType, toSeatIndex):
        mo = self.createMsgPackRes('table_call', 'card')
        mo.setResult('precard', precard)
        mo.setResult('seatId', seatIndex + 1)
        mo.setResult('userId', self.table.seats[seatIndex].userId)
        mo.setResult('cards', cards)
        mo.setResult('lastOutCards', self.table.seats[seatIndex].lastOutCards)
        mo.setResult('myCardNote', self.buildCardNote(toSeatIndex))
        if self.table.players[toSeatIndex].gameClientVer >= self.HIDE_CARD_VER:
            if seatIndex == toSeatIndex or self.table.seats[seatIndex].isShow:
                mo.setResult('handCards', self.table.seats[seatIndex].cards)
            else:
                mo.setResult('handCards', [-1 for _ in xrange(len(self.table.seats[seatIndex].cards))])
        mo.setResult('topcard', self.table.status.topCardList)
        mo.setResult('issvr', 1 if tuoGuanType != DizhuPlayer.TUGUAN_TYPE_USERACT else 0)
        router.sendToUser(mo, self.table.seats[toSeatIndex].userId)
        
    def sendChuPaiNextRes(self, seatId, opTime):
        mo = self.createMsgPackRes('table_call', 'next')
        mo.setResult('next', seatId)
        mo.setResult('seatId', seatId)
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('opTime', opTime)
        self.sendToAllTableUser(mo)


    def sendWinLoseAbortRes(self):
        mo = self.createMsgPackRes('table_call', 'game_win')
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('dizhuwin', 0)
        mo.setResult('nowin', 1)
        mo.setResult('slam', 0)
        mo.setResult('windoubles', 0)
        mo.setResult('save', 0)
        mo.setResult('cards', [seat.cards for seat in self.table.seats])
        slen = len(self.table.players)
        win_streak = []
        for x in xrange(slen):
            p = self.table.players[x]
            win_streak.append(p.datas['winstreak'])
            mo.setResult('seat' + str(x + 1), [0, p.datas['chip'], 0, 15,
                                               p.datas['tbt'], p.datas['tbc'],
                                               p.datas['level'], p.datas['exp'],
                                               0, p.datas['nextexp'], p.datas['title']])

        mo.setResult('winStreak', win_streak)
        self.sendToAllTableUser(mo)

    def sendWinLoseRes(self, result):
        mo = self.createMsgPackRes('table_call', 'game_win')
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('dizhuwin', result['dizhuwin'])
        mo.setResult('slam', result['winslam'])
        mo.setResult('windoubles', result['windoubles'])
        mo.setResult('winStreak', result['winStreak'])
        mo.setResult('luckyItemArgs', result['luckyItemArgs'])
        mo.setResult('save', 1)

        mo.setResult('skillScoreInfos', result['skillScoreInfos'])
        mo.setResult('gameNum', self.table.gameRound.roundId)
        mo.setResult('cards', [seat.cards for seat in self.table.seats])
        
        seat_delta = result['seat_delta']
        seat_coin = result['seat_coin']
        addcoupons = result['addcoupons']
        seat_exps = result['seat_exps']
        table_task = result['table_task']
        final_acc_chips = result['final_acc_chips']
        tb_infos = result['tb_infos']
        plen = len(self.table.players)
        seatInfos = []
        for x in xrange(plen) :
            sp = self.table.players[x]
#             sp.initUser(0, 0)  # 重新取得数据库的数据
            chip = seat_coin[x]
            if sp.isSupportBuyin :
                chip += final_acc_chips[x]
            waitTime = self.table.runConfig.optime
            if seat_coin[x] < self.table.runConfig.minCoin :
                waitTime = int(waitTime / 3)
#             tbplaytimes, tbplaycount = treasurebox.getTreasureBoxState(sp.userId, self.table.bigRoomId)
            tbplaytimes, tbplaycount = tb_infos[x]
            seat_exp = seat_exps[x]
            mo.setResult('seat' + str(x + 1), [seat_delta[x], chip, addcoupons[x],
                                               waitTime, tbplaytimes, tbplaycount,
                                               seat_exp[0], seat_exp[1], seat_exp[2], seat_exp[3], seat_exp[4],
                                               seat_coin[x]])
            if result.get('pfIndex') == x:
                seatInfos.append({'punished':1})
            else:
                seatInfos.append({})
        mo.setResult('seats', seatInfos)
        
        for x in xrange(plen) :
            player = self.table.players[x]
            userId = player.userId
            # TODO 设定当前玩家的桌面任务
            tasks = table_task[x]
            # tasks = self.fillUserTasks(userId)
            mo.setResult('tasks', tasks)
            
            # 投诉判断
            if self.table._complain_open :
                _, clientIdVer, _ = strutil.parseClientId(player.clientId)  # sessiondata.getClientIdVer(userId)
                clientIdLimit = dizhuconf.getAllComplainInfo().get("clientIdLimit", 3.72)
                if clientIdVer >= clientIdLimit:
                    mo.setResult('complain', self.table._complain)

            # 地主v3.773特效需要知道上一个大师分等级图标
            # 传两个大图
            skilscoreinfo = result['skillScoreInfos'][x]
            masterlevel = skilscoreinfo['level']
            curlevelpic = skillscore.get_skill_score_big_level_pic(masterlevel)
            lastlevelpic = skillscore.get_skill_score_big_level_pic(masterlevel - 1)
            skilscoreinfo['lastbiglevelpic'] = lastlevelpic
            skilscoreinfo['curbiglevelpic'] = curlevelpic

            router.sendToUser(mo, userId)


    def sendToDoTask(self, userId, todotasks):
        mo = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, todotasks)
        router.sendToUser(mo, userId)


    def sendSmilesResError(self, userId, errInfo):
        mo = self.createMsgPackRes('table_call', 'smilies')
        mo.setResult('userId', userId)
        mo.setError(1, errInfo)
        router.sendToUser(mo, userId)
    

    def sendSmilesResOk(self, fromseat, member, toseat, price, smilie, self_charm, other_charm, tip, rcount=1):
        mo = self.createMsgPackRes('table_call', 'smilies')
        mo.setResult('fromseat', fromseat)
        mo.setResult('member', member)
        mo.setResult('toseat', toseat)
        mo.setResult('price', price)
        mo.setResult('smilies', smilie)
        mo.setResult('from_charm', self_charm)
        mo.setResult('to_charm', other_charm)
        mo.setResult('tip', tip)
        mo.setResult('count', rcount) # 新版本客户端才支持发送次数
        
        allplayers = []
        allplayers.extend(self.table.players)
        allplayers.extend(self.table.observers)
        newclient_uids = [] # 使用新版本的uid
        
        for p in allplayers :
            if p.userId <= 0 :
                continue
            newclient_uids.append(int(p.userId))
                
        ftlog.debug('sendSmilesResOk',
                    'smilie=', smilie,
                    'rcount=', rcount,
                    'newclient_uids=', newclient_uids)

        # 新版本只发送一次协议
        for uid in newclient_uids:
            if uid <= 0:
                continue
            router.sendToUser(mo.pack(), uid)
        
    def sendTableChat(self, player, isFace, voiceIdx, chatMsg, toUserId, toUserName):
        mo = self.createMsgPackRes('table_chat')
        mo.setResult('userId', player.userId)
        mo.setResult('msg', chatMsg)
        mo.setResult('isFace', isFace)
        mo.setResult('seatId', player.seatId)
        mo.setResult('userName', toUserName)
        if voiceIdx != -1:
            mo.setResult('voiceIdx', voiceIdx)
        router.sendToUser(mo, toUserId)

    def sendWaitJiabei(self, optime):
        if self.table.status.playingState == DizhuState.PLAYING_STATE_NM_JIABEI:
            mo = self.createMsgPackRes('table_call', 'wait_nm_jiabei')
        elif self.table.status.playingState == DizhuState.PLAYING_STATE_DZ_JIABEI:
            mo = self.createMsgPackRes('table_call', 'wait_dz_jiabei')
        else:
            ftlog.error('DizhuSender.sendWaitJiabei',
                        'playingState=', self.table.status.playingState,
                        'err=', 'BadPlayingState')
            return
        mo.setResult('optime', optime)
        self.sendToAllTableUser(mo)

    def sendJiabeiRes(self, seatId, jiabei):
        mo = self.createMsgPackRes('table_call', 'jiabei')
        mo.setResult('jiabei', jiabei)
        mo.setResult('seatId', seatId)
        mo.setResult('userId', self.table.seats[seatId-1].userId)
        self.sendToAllTableUser(mo)
        
    def sendTreasureBoxRes(self, userId, datas):
        userId = int(userId)
        if userId <= 0:
            return
        mo = self.createMsgPackRes('table_call', 'tbox')
        mo.setResult('userId', userId)
        mo.updateResult(datas)
        router.sendToUser(mo, userId)

    def sendCardNoteOpened(self, player):
        mo = self.createMsgPackRes('table_call', 'cardNote')
        mo.setResult('cardNote', player.getCardNoteCount())
        router.sendToUser(mo, player.userId)
    
    def buildSeatCards(self, player, seat):
#         if (player.gameClientVer >= DizhuSender.HIDE_CARD_VER
#             and self.table.state < DizhuState.TABLE_STATE_PLAYING):
#             seatInfo['card'] = [-1 for _ in len(seatInfo['card'])]
        if (player.userId != seat.userId
            and player.gameClientVer >= DizhuSender.HIDE_CARD_VER
            and self.table.state < DizhuState.TABLE_STATE_PLAYING):
            return [-1 for _ in xrange(len(seat.cards))]
        return seat.cards[:]
    
    def sendStartHuanpaiRes(self, optime):
        mo = self.createMsgPackRes('table_call', 'startHuanpai')
        mo.setResult('opTime', optime)
        self.sendToAllTableUser(mo)
        
    def sendHuanpaiRes(self, player):
        mo = self.createMsgPackRes('table_call', 'huanpai')
        mo.setResult('userId', player.userId)
        mo.setResult('seatId', player.seatId)
        self.sendToAllTableUser(mo)
    
    def sendEndHuanpaiRes(self):
        seatCards = [self.buildSeatCards(self.table.players[i], self.table.seats[i]) \
                     for i in xrange(len(self.table.seats))]
        for i, seat in enumerate(self.table.seats):
            mo = self.createMsgPackRes('table_call', 'endHuanpai')
            mo.setResult('outCards', seat.huanpaiOut)
            mo.setResult('inCards', seat.huanpaiIn)
            mo.setResult('myCardNote', self.buildCardNote(i))
            mo.setResult('seatCards', seatCards)
            router.sendToUser(mo, seat.userId)
    
class TimingMessageSender(object):
    '''
    定时发送消息给玩家
    采用根据uid分组的先进先出的排队，当队列数据发送完毕就会自动停止定时器，不同uid直接数据不会互相影响
    '''
    looptimer = None
    interval = 0.05
    queuemap = {}
     
    @classmethod
    def pushMessagePack(cls, uid, packedmsg):
        ftlog.debug('TimingMessageSender.pushMessagePack',
                    'userId=', uid,
                    'queuemap(keys)=', cls.queuemap.keys())
        if uid not in cls.queuemap:
            cls.queuemap[uid] = deque()
        cls.queuemap[uid].append(packedmsg)
        cls._start()
        return
 
    @classmethod
    def _start(cls):
        ftlog.debug('TimingMessageSender._start')
        if cls.looptimer:
            return
        cls.looptimer = FTLoopTimer(cls.interval, -1, cls._onUpdate)
        cls.looptimer.start()
        cls._onUpdate()
        return
 
    @classmethod
    def _stop(cls):
        ftlog.debug('TimingMessageSender._stop')
        if not cls.looptimer:
            return 
        cls.looptimer.cancel()
        cls.looptimer = None
        cls.queuemap = {}
     
    @classmethod
    def _onUpdate(cls):
        ftlog.debug('TimingMessageSender._onUpdate:begin',
                    'queuemap(keys)=', cls.queuemap.keys())
        if len(cls.queuemap) <= 0:
            cls._stop()
            return
        for uid in cls.queuemap.keys():
            if len(cls.queuemap[uid]) <= 0:
                del cls.queuemap[uid]
                continue
            packedmsg = cls.queuemap[uid].popleft()
            router.sendToUser(packedmsg, uid)
        ftlog.debug('TimingMessageSender._onUpdate:end',
                    'queuemap(keys)=', cls.queuemap.keys())
        return