# -*- coding:utf-8 -*-
'''
Created on 2017年2月15日

@author: zhaojiangang
'''
from dizhucomm import playmodes
from dizhucomm.core import bug_fix
from dizhucomm.core.const import Oper, StandupReason
from dizhucomm.core.events import SitdownEvent, StandupEvent, SeatReadyEvent, \
    GameReadyEvent, GameStartEvent, CallEvent, CurOpSeatMoveEvent, \
    StartNongminJiabeiEvent, StartDizhuJiabeiEvent, StartHuanpaiEvent, \
    NongminJiabeiEvent, DizhuJiabeiEvent, HuanpaiOutcardsEvent, HuanpaiEndEvent, \
    OutCardEvent, ThrowEmojiEvent, TuoguanEvent, ChatEvent, ShowCardEvent, \
    GameRoundOverEvent, GameRoundAbortEvent, SeatOnlineChanged, CardNoteOpenedEvent, \
    TableTBoxOpened, AutoPlayEvent
from dizhucomm.entity import treasurebox, tablepay, emoji, commconf
from dizhucomm.playmodes.laizi import WildCardEvent
from dizhucomm.utils.msghandler import MsgHandler
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from hall.entity import hallconf
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.util import strutil, timestamp as pktimestamp
from dizhucomm.servers.util.rpc import comm_table_remote
from dizhucomm.core.playmode import PlayMode
from poker.entity.dao import sessiondata
from poker.entity.dao import gamedata


class DizhuTableProto(MsgHandler):
    HIDE_CARD_VER = 3.815

    TABLE_STATE_IDLE = 10
    TABLE_STATE_HUANPAI = 12
    TABLE_STATE_CALLING = 15
    TABLE_STATE_NM_JIABEI = 16
    TABLE_STATE_DIZHU_JIABEI = 17
    TABLE_STATE_PLAYING = 20
    TABLE_STATE_FINAL = TABLE_STATE_PLAYING
    
    TABLE_PLAYING_STATE_NM_JIABEI = 1
    TABLE_PLAYING_STATE_DIZHU_JIABEI = 2
    TABLE_PLAYING_STATE_HUANPAI = 3
    TABLE_PLAYING_STATE_CHUPAI = 4
    
    STATE_TRANS_MAP = {
        'idle': (TABLE_STATE_IDLE, TABLE_PLAYING_STATE_HUANPAI),
        'calling': (TABLE_STATE_CALLING, TABLE_PLAYING_STATE_HUANPAI),
        'nongminjiabei': (TABLE_STATE_NM_JIABEI, TABLE_PLAYING_STATE_HUANPAI),
        'dizhujiabei': (TABLE_STATE_DIZHU_JIABEI, TABLE_PLAYING_STATE_HUANPAI),
        'playing': (TABLE_STATE_PLAYING, TABLE_PLAYING_STATE_CHUPAI),
        'playing.nongminjiabei': (TABLE_STATE_PLAYING, TABLE_PLAYING_STATE_NM_JIABEI),
        'playing.dizhujiabei': (TABLE_STATE_PLAYING, TABLE_PLAYING_STATE_DIZHU_JIABEI),
        'playing.huanpai': (TABLE_STATE_PLAYING, TABLE_PLAYING_STATE_HUANPAI),
        'huanpai': (TABLE_STATE_HUANPAI, TABLE_PLAYING_STATE_HUANPAI),
        'playing.chupai': (TABLE_STATE_PLAYING, TABLE_PLAYING_STATE_CHUPAI),
        'final': (TABLE_STATE_FINAL, TABLE_PLAYING_STATE_CHUPAI),
    }
    
    def __init__(self, tableCtrl):
        super(DizhuTableProto, self).__init__()
        self.tableCtrl = tableCtrl
    
    @property
    def gameId(self):
        return self.tableCtrl.gameId
    
    @property
    def roomId(self):
        return self.tableCtrl.roomId
    
    @property
    def bigRoomId(self):
        return self.tableCtrl.bigRoomId
    
    @property
    def tableId(self):
        return self.tableCtrl.tableId
    
    @property
    def table(self):
        return self.tableCtrl.table
    
    @property
    def room(self):
        return self.table.room
    
    def getTableState(self):
        return self.STATE_TRANS_MAP.get(self.table.state.name, (self.TABLE_STATE_IDLE, self.TABLE_PLAYING_STATE_CHUPAI))[0]
    
    def getTablePlayingState(self):
        return self.STATE_TRANS_MAP.get(self.table.state.name, (self.TABLE_STATE_IDLE, self.TABLE_PLAYING_STATE_CHUPAI))[1]
    
    def buildTableMsgRes(self, cmd, action=None):
        mp = MsgPack()
        mp.setCmd(cmd)
        if action:
            mp.setResult('action', action)
        mp.setResult('gameId', self.gameId)
        mp.setResult('roomId', self.roomId)
        mp.setResult('tableId', self.tableId)
        return mp
    
    def buildTableMsgReq(self, cmd, action=None):
        mp = MsgPack()
        mp.setCmd(cmd)
        if action : 
            mp.setParam('action', action)
        mp.setParam('gameId', self.gameId)
        mp.setParam('roomId', self.roomId)
        mp.setParam('tableId', self.tableId)
        return mp
    
    def buildTableBasicInfo(self):
        info = {}
        info['name'] = ''
        info['creator'] = 0
        info['pwd'] = ''
        info['tableId'] = self.tableId
        info['roomId'] = self.roomId
        return info
    
    def buildTableBasicConfig(self, player):
        '''
        原table.buildBasicInfo中的config数据
        '''
        # 宝箱信息
        tbbox, couponrule = treasurebox.getTreasureTableTip(self.gameId, self.bigRoomId)
        # 配置信息
        config = {}
        config['tbbox'] = tbbox
        config['couponrule'] = couponrule
        
        config['maxseat'] = self.table.runConf.maxSeatN
        config['rangpaiMultiType'] = self.table.runConf.rangpaiMultiType
        config['autoChange'] = self.table.runConf.autochange
        config['base'] = self.table.runConf.basebet
        config['basemulti'] = self.table.runConf.basemulti
        config['gslam'] = self.table.runConf.gslam
        config['grab'] = self.table.runConf.grab
        config['chat'] = self.table.runConf.canchat
        config['cardNote'] = self.table.runConf.cardNote
        config['optime'] = self.table.runConf.optimeOutCard
        config['coin2chip'] = self.table.runConf.coin2chip
        config['lucky'] = self.table.runConf.lucky
        config['untiCheat'] = self.table.runConf.unticheat
        config['passtime'] = self.table.runConf.passtime
        config['mixShowChip'] = self.table.runConf.mixShowChip
        
        config['isMingPai'] = self.table.runConf.showCard
        config['roommulti'] = self.table.runConf.roomMutil
        config['maxcoin'] = self.table.runConf.maxCoin
        config['mincoin'] = self.table.runConf.minCoin
        config['sfee'] = self.table.runConf.roomFee
        config['optimedis'] = self.table.runConf.optimedis
        config['matchInfo'] = '' # 老版本数据结构兼容
        config['autoPlay'] = self.table.runConf.autoPlay
        config['canQuit'] = self.table.runConf.canQuit
        config['winCoinLimit'] = self.table.runConf.winCoinLimit

        # 小于3.7版本是否能够聊天、防作弊统一使用的是untiCheat字段
        # 对于小于3.7版本的在不防作弊但是不能聊天时处理为防作弊
        _, clientVer, _ = strutil.parseClientId(player.clientId)
        if clientVer and clientVer < 3.7 :
            if not config['chat'] and not config['untiCheat']:
                config['untiCheat'] = 1        
        return config
    
    def filterSeatInfo(self, seat, seatInfo):
        tableState = self.getTableState()
        if (seat.player.gameClientVer >= self.HIDE_CARD_VER
            and tableState < self.TABLE_STATE_PLAYING):
            seatInfo['card'] = [-1 for _ in xrange(len(seatInfo['card']))]
            seatInfo['hpIn'] = [-1 for _ in xrange(len(seatInfo['hpIn']))]
            seatInfo['hpOut'] = [-1 for _ in xrange(len(seatInfo['hpOut']))]
        return seatInfo
    
    def buildSeatCards(self, forSeat, seat):
        tableState = self.getTableState()
        seatCards = seat.status.cards[:] if seat.status else []
        if (forSeat != seat
            and not seat.status.isShowCards
            and forSeat.player.gameClientVer >= self.HIDE_CARD_VER
            and tableState <= self.TABLE_STATE_PLAYING):
            return [-1 for _ in xrange(len(seatCards))]
        return seatCards[:]
    
    def buildSeatInfo(self, forSeat, seat):
        '''
        为forSeat构建seat的seatInfo
        '''
        stat = {
            'uid': 0, 'state':seat.state, 'robot':0, 'call':-1, 'call2': -1,
            'card':[], 'outcnt':0, 'timeoutcnt':0, 'show':0, 'couponcard':[0,0,0], 
            'voice':0, 'robotcards':-1, 'double':0, 'online':0, 'hpOut':[], 'hpIn':[]
        }
        # 准备前的玩家在线状态设置
        stat['online'] = int(seat.player.online) if seat.player else 0
        if not seat.status:
            return stat
        
        stat['uid'] = seat.userId or 0
        # 托管状态，0代表未托管，1代表托管
        stat['robot'] =  int(seat.status.isTuoguan)
        # -1表示还没叫，0表示不叫，1表示1分，2＝2分，3＝3分
        stat['call'] = seat.status.callValue
        # 抢地主时，标示是否抢过, -1表示还没抢, 0表示不抢，1表示抢
        stat['call2'] = 1 if seat.status.callValue > 0 else seat.status.callValue
        # 牌型
        stat['card'] = seat.status.cards
        # zzy 上手牌
        if len(seat.status.outCards) >= 2:
            stat['lastOutCard'] = seat.status.outCards[-2]
        # 出牌数目，用于计算春天等
        stat['outcnt'] = seat.status.outCardTimes
        # 超时未操作次数，3次自动进入托管状态
        stat['timeoutcnt'] = seat.status.timeoutCount
        # 本座位是否明牌
        stat['show'] = int(seat.status.isShowCards)
        # 弃用
        stat['couponcard'] = [0,0,0]
        # 
        stat['voice'] = int(seat.isReciveVoice)
        # 托管时，当前玩家的手里的剩余牌数
        stat['robotcards'] = len(seat.status.cards) if seat.status.isTuoguan else 0
        # 加倍倍数
        stat['double'] = 1 if seat.status.seatMulti == 2 else 0
        # 是否在线
        stat['online'] = int(seat.player.online)
        # 换牌换出牌
        stat['hpOut'] = seat.status.huanpaiOutcards or []
        # 换牌换入牌
        stat['hpIn'] = seat.status.huanpaiIncards or []
        
        if forSeat != seat:
            self.filterSeatInfo(forSeat, stat)
        return stat
    
    def filterTableStatusInfo(self, seat, statusInfo):
        tableState = self.getTableState()
        if (seat.player
            and seat.player.gameClientVer >= self.HIDE_CARD_VER
            and tableState < self.TABLE_STATE_PLAYING):
            statusInfo['basecard'] = [-1 for _ in xrange(len(statusInfo['basecard']))]
        if seat.player:
            statusInfo['isauto'] = seat.status.isAutoPlay if seat.status else -1
        return statusInfo
    
    def buildTableStatusInfo(self):
        stat = {
            'state':self.TABLE_STATE_IDLE, 'dizhu':0, 'basecard':[], 'topcard':[], 'topseat':0,
            'call':-1, 'nowop':0, 'bomb':0, 'chuntian':1, 'show':1, 'super':1,
            'bcmulti':1, 'callstr':'', 'firstshow':0, 'ccrc':0,
            'rangpai':0, 'grabCard':-1, 'kickoutCard':[], 'rangpaiMulti':1, 'wildcard':-1, 'isauto': -1
        }
        
        # 顶层状态ID
        stat['state'] =  self.getTableState()
        # 子状态ID
        stat['playingState'] = self.getTablePlayingState()
        if not self.table.gameRound:
            return stat
        # 地主的座位号
        if self.table.gameRound.dizhuSeat:
            stat['dizhu'] = self.table.gameRound.dizhuSeat.seatId
        # 3张底牌列表
        if self.table.gameRound.baseCards:
            stat['basecard'] = self.table.gameRound.baseCards
        # 最后出的牌，用于校验
        if self.table.gameRound.topValidCards:
            stat['topcard'] = self.table.gameRound.topValidCards.cards
        # 叫抢地主倍数，用于算分
        if len(self.table.gameRound.callList) > 0:
            stat['call'] = self.table.gameRound.callMulti
        # 当前操作者座位号
        if self.table.gameRound.curOpSeat:
            stat['nowop'] = self.table.gameRound.curOpSeat.seatId
        # 炸弹次数
        stat['bomb'] = self.table.gameRound.bombCount
        # 春天状态标识，用于算分
        if self.table.gameRound.isChuntian:
            stat['chuntian'] = 2
        if self.table.gameRound.topSeat:
            stat['topseat'] = self.table.gameRound.topSeat.seatId
        # 名牌加倍数，目前取1,2,5三种倍数
        stat['show'] = self.table.gameRound.showMulti
        # 超级加倍，无用
        stat['super'] = 1
        # 底牌加倍 
        stat['bcmulti'] = self.table.gameRound.baseCardMulti
        # 暂时先认为无用
        stat['callstr'] = '' # TODO:
        # 暂时先认为无用
        stat['firstshow'] = 0 # TODO:
        # 出牌的校验序号
        stat['ccrc'] = self.table.gameRound.cardCrc
        # 让牌数量（二斗玩法）
        stat['rangpai'] = self.table.gameRound.rangpai
        # 暂时先认为无用
        stat['grabCard'] = -1 # TODO:
        # 去除的牌（二斗玩法）
        stat['kickoutCard'] = self.table.gameRound.kickoutCards
        # 让牌倍数（二斗用的）
        stat['rangpaiMulti'] = self.table.gameRound.rangpaiMulti
        # 癞子牌（癞子玩法）
        wildCard = self.table.gameRound.wildCard
        wildCard = wildCard if wildCard != None else -1
        stat['wildcard'] = wildCard
        return stat
    
    def buildTableStatusInfoForSeat(self, seat):
        '''
        牌桌状态
        @param isHideCard: 是否隐藏底牌
        '''
        stat = self.buildTableStatusInfo()
        
        self.filterTableStatusInfo(seat, stat)
        
        return stat
    
    def fillTableCardNote(self, cardNote, cards):
        cardRule = self.table.playMode.cardRule
        for card in cards:
            point = cardRule.cardToPoint(card)
            if point < 13:
                point = cardRule.pointToCard(point)
            cardNote[point] += 1
        return cardNote
    
    def buildTableCardNote(self, seat):
        ret = [0 for _ in xrange(15)]
        if self.table.gameRound:
            tableState = self.getTableState()
            for tseat in self.table.seats:
                if tseat != seat:
                    self.fillTableCardNote(ret, tseat.status.cards)
            if tableState < self.TABLE_STATE_PLAYING:
                self.fillTableCardNote(ret, self.table.gameRound.baseCards)
            if self.table.gameRound.kickoutCards:
                self.fillTableCardNote(ret, self.table.gameRound.kickoutCards)
            if len(self.table.seats) == 2:
                ret[2] = ret[3] = 0
        return ret
    
    def sendToSeat(self, mp, seat):
        if seat.player and not seat.isGiveup and not seat.player.isQuit:
            router.sendToUser(mp, seat.userId)

    def sendToAllSeat(self, mp):
        for seat in self.table.seats:
            self.sendToSeat(mp, seat)

    def sendOnlineChanged(self, seat):
        mp = self.buildTableMsgRes('table_call', 'online_changed')
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        mp.setResult('online', 1 if seat.player.online else 0)
        self.sendToAllSeat(mp)

    def buildQuickStartResp(self, seat, isOK, reason):
        mp = self.buildTableMsgRes('quick_start')
        mp.setResult('isOK', isOK)
        mp.setResult('seatId', seat.seatId)
        mp.setResult('reason', reason)
        return mp
    
    def sendQuickStartRes(self, seat, isOK, reason):
        mp = self.buildQuickStartResp(seat, isOK, reason)
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto.sendQuickStartRes',
                        'tableId=', self.tableId,
                        'seatId=', seat.seatId,
                        'userId=', seat.userId,
                        'isOk=', isOK,
                        'reason=', reason,
                        'mp=', mp._ht)
        self.sendToSeat(mp, seat)
    
    def buildTableInfoResp(self, seat, isRobot):
        _, clientVer, _ = strutil.parseClientId(seat.player.clientId)
        mp = self.buildTableMsgRes('table_info')
        playMode = self.table.playMode.name
        if clientVer <= 3.7:
            if playMode == playmodes.PLAYMODE_HAPPY or playMode == playmodes.PLAYMODE_123:
                playMode = 'normal'  # FIX, 客户端happy和123都是normal, grab=1就是欢乐
        mp.setResult('playMode', playMode)
        mp.setResult('isrobot', isRobot)
        mp.setResult('roomLevel', self.table.room.roomConf.get('roomLevel', 1))
        mp.setResult('roomName', self.table.room.roomConf.get('name', ''))
        mp.setResult('isMatch', self.table.room.isMatch)
        mp.setResult('info', self.buildTableBasicInfo())
        mp.setResult('config', self.buildTableBasicConfig(seat.player))
        mp.setResult('stat', self.buildTableStatusInfoForSeat(seat))
        mp.setResult('myCardNote', self.buildTableCardNote(seat))
        mp.setResult('betpoolClose', 1)
        if self.table.gameRound:
            mp.setResult('roundId', self.table.gameRound.roundId)
        
        _, itemCount = treasurebox.getTreasureRewardItem(self.gameId, self.bigRoomId)
        for i, tseat in enumerate(self.table.seats):
            seatinfo = self.buildSeatInfo(seat, tseat)
            if tseat.player:
                seatinfo.update(tseat.player.datas)
                # 记牌器数量
                seatinfo['cardNote'] = tseat.player.getCardNoteCount()
                # 当前table的奖券任务奖励
                seatinfo['count'] = itemCount
                # 比赛分
                seatinfo['mscore'] = tseat.player.score
                tseat.player.cleanDataAfterFirstUserInfo()
            seatinfo['uid'] = tseat.userId
            mp.setResult('seat%s' % (i+1), seatinfo)
        
        # 处理记牌器
        if seat.player and seat.player.getCardNoteCount() < 1:
            # 记牌器开启的配置
            cardNoteOpenConf = self.table.runConf.cardNoteOpenConf
            # 记牌器价格
            cardNoteChip = self.table.runConf.cardNoteChip
            cardNoteDiamod = self.table.runConf.cardNoteDiamond

            # 处理牌桌记牌器
            if cardNoteOpenConf:
                isBuyMonthCard = False

                if cardNoteDiamod:
                    if clientVer >= 4.56:
                        isBuyMonthCard = True
                        cardNoteTip = cardNoteOpenConf.get('desc.month_card', '购买贵族月卡可免费使用记牌器')
                    else:
                        cardNoteTip = cardNoteOpenConf.get('diamond', {}).get('desc', '')
                    cardNoteTip = strutil.replaceParams(cardNoteTip, {'consumeChip': str(cardNoteDiamod)})

                    if ftlog.is_debug():
                        ftlog.debug('dizhucomm.buildTableInfoResp.cardNoteDiamod userId=', seat.player.userId,
                                    'openable=', 1, 'desc=', cardNoteTip, 'isBuyMonthCard=', isBuyMonthCard)
                    cardNote = {'openable': 1, 'desc': cardNoteTip, 'isBuyMonthCard': isBuyMonthCard}
                    mp.setResult('cardNote', cardNote)
                elif isinstance(cardNoteChip, int) and cardNoteChip > 0:

                    openable = 1
                    desc = cardNoteOpenConf.get('desc', '')
                    if seat.player.chip < cardNoteChip:
                        openable = 0
                        desc = cardNoteOpenConf.get('desc.chip_not_enough', '')

                    # 大厅版本4.56以上 修改描述
                    if clientVer >= 4.56:
                        desc = cardNoteOpenConf.get('desc.month_card', '购买贵族月卡可免费使用记牌器')

                    desc = strutil.replaceParams(desc, {'consumeChip': str(cardNoteChip)})
                    if ftlog.is_debug():
                        ftlog.debug('dizhucomm.buildTableInfoResp.cardNoteChip userId=', seat.player.userId,
                                    'openable=', 1, 'desc=', desc,
                                    'isBuyMonthCard=', isBuyMonthCard)

                    cardNote = {"openable": openable, "desc": desc, "isBuyMonthCard": isBuyMonthCard}
                    mp.setResult('cardNote', cardNote)

        if not self.table.room.isMatch:
            player = seat.player
            if player and player.userId:
                # 商品信息 TODO
                mp.setResult('products', tablepay.getProducts(self.gameId, player.userId, self.bigRoomId, player.clientId))
                # 互动表情
                emojiConf = emoji.getEmojiConf(self.gameId, self.bigRoomId, seat.player.datas.get('vipInfo', {}).get('level', 0))
                if emojiConf:
                    mp.setResult('smiliesConf', emojiConf)

        return mp
    
    def sendTableInfoRes(self, seat):
        logUserIds = [66706022]
        if seat.player and seat.userId in logUserIds:
            ftlog.info('DizhuTableProto.sendTableInfoRes beforeSentMsg',
                       'tableId=', self.tableId,
                       'userId=', seat.userId,
                       'gameClientVer=', seat.player.gameClientVer,
                       'isGiveup=', seat.isGiveup,
                       'isQuit=', seat.player.isQuit,
                       'seats=', [(s.userId, s.seatId) for s in self.table.seats])
            
        if seat.player and not seat.isGiveup and not seat.player.isQuit:
            mp = self.buildTableInfoResp(seat, 0)
            router.sendToUser(mp, seat.userId)
            if seat.userId in logUserIds:
                ftlog.info('DizhuTableProto.sendTableInfoRes sentMsg',
                           'tableId=', self.tableId,
                           'userId=', seat.userId,
                           'gameClientVer=', seat.player.gameClientVer,
                           'seats=', [(seat.userId, seat.seatId) for seat in self.table.seats],
                           'mp=', mp.pack())
                
    def sendTableInfoResAll(self):
        for seat in self.table.seats:
            self.sendTableInfoRes(seat)

    def sendCardNoteOpened(self, seat):
        mo = self.buildTableMsgRes('table_call', 'cardNote')
        mo.setResult('cardNote', seat.player.getCardNoteCount())
        router.sendToUser(mo, seat.userId)
        
    def buildUserReadyRes(self, seat):
        mp = self.buildTableMsgRes('table_call', 'ready')
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        return mp
    
    def sendUserReadyResAll(self, seat):
        mp = self.buildUserReadyRes(seat)
        self.sendToAllSeat(mp)
        
    def buildRobotNotifyCallUp(self, params):
        hasrobot = self.table.runConf.hasrobot
        if hasrobot:
            players = self.table.getPlayers()
            userIds = self.table.getSeatUserIds()
            mp = self.buildTableMsgReq('robotmgr')
            if params :
                mp.updateParam(params)
            mp.setAction('callup')
            mp.setParam('userCount', len(players))
            mp.setParam('seatCount', len(self.table.seats))
            mp.setParam('users', userIds)
            return mp
        return None
    
    def sendRobotNotifyCallUp(self, params):
        mp = self.buildRobotNotifyCallUp(params)
        if mp:
            router.sendRobotServer(mp, self.tableId)

    def buildRobotNotifyShutdown(self, params):
        hasrobot = self.table.runConf.hasrobot
        ftlog.debug("|hasrobot, params", hasrobot, params, caller=self)
        if hasrobot :
            players = self.table.getPlayers()
            userIds = self.table.getSeatUserIds()
            mp = self.buildTableMsgReq("robotmgr")
            if params :
                mp.updateParam(params)
            mp.setAction('shutdown')
            mp.setParam('userCount', len(players))
            mp.setParam('seatCount', len(self.table.seats))
            mp.setParam('users', userIds)
            router.sendRobotServer(mp, self.tableId)
    
    def sendRobotNotifyShutDown(self, params):
        mp = self.buildRobotNotifyShutdown(params)
        if mp:
            router.sendRobotServer(mp, self.tableId)

    def buildGameReadyRes(self, seat):
        mp = self.buildTableMsgRes('table_call', 'game_ready')
        for i, tseat in enumerate(self.table.gameRound.seats):
            cards = tseat.status.cards
            if (seat.player.gameClientVer >= self.HIDE_CARD_VER
                and tseat != seat
                and not seat.status.isShowCards):
                cards = [-1 for _ in xrange(len(cards))]
            mp.setResult('cards' + str(i), cards)
        basecard = self.table.gameRound.baseCards
        kickoutCards = self.table.gameRound.kickoutCards
        if seat.player.gameClientVer >= self.HIDE_CARD_VER:
            basecard = [-1 for _ in xrange(len(basecard))]
            kickoutCards = [-1 for _ in xrange(len(kickoutCards))]
        mp.setResult('basecard', basecard)
        mp.setResult('kickoutCard', kickoutCards)
        mp.setResult('rangpai', self.table.gameRound.rangpai)
        mp.setResult('grabCard', self.table.gameRound.grabCard)
        mp.setResult('myCardNote', self.buildTableCardNote(seat))
        if self.table.gameRound:
            mp.setResult('roundId', self.table.gameRound.roundId)
        mp.setResult('gameNum', self.table.gameRound.roundId)
        return mp
    
    def sendGameReadyResForSeat(self, seat):
        if seat.player and not seat.isGiveup:
            mp = self.buildGameReadyRes(seat)
            router.sendToUser(mp, seat.userId)

    def sendGameReadyResAll(self):
        for seat in self.table.seats:
            self.sendGameReadyResForSeat(seat)

    def buildShowCardsResForSeat(self, forSeat, showCardsSeat):
        mp = self.buildTableMsgRes('table_call', 'show')
        mp.setResult('seatId', showCardsSeat.seatId)
        mp.setResult('userId', showCardsSeat.userId)
        mp.setResult('stat', self.buildTableStatusInfoForSeat(showCardsSeat))
        mp.setResult('seatCards', self.buildSeatCards(forSeat, showCardsSeat))
        return mp
    
    def sendShowCardsResForSeat(self, forSeat, showCardsSeat):
        if forSeat.player and not forSeat.isGiveup:
            mp = self.buildShowCardsResForSeat(forSeat, showCardsSeat)
            router.sendToUser(mp, forSeat.userId)

    def sendShowCardsRes(self, seat):
        for tseat in self.table.seats:
            self.sendShowCardsResForSeat(tseat, seat)
        
    def buildWildCardResp(self, wildCard, wildCardBig):
        mp = self.buildTableMsgRes('table_call', 'wild_card')
        mp.setResult('wildcard', wildCard)
        mp.setResult('wildCardBig', wildCardBig)
        return mp
    
    def sendWildCardRes(self, wildCard, wildCardBig):
        mp = self.buildWildCardResp(wildCard, wildCardBig)
        self.sendToAllSeat(mp)

    def buildGameStartResForSeat(self, seat):
        mp = self.buildTableMsgRes('table_call', 'game_start')
        mp.setResult('stat', self.buildTableStatusInfoForSeat(seat))
        seatTBBoxInfoList = []
        for tseat in self.table.seats:
            if tseat.player:
                itemId, itemCount = treasurebox.getTreasureRewardItem(self.gameId, self.bigRoomId)
                if itemId:
                    itemId = hallconf.translateAssetKindIdToOld(itemId)
                tempTbc = tseat.player.datas.get('tbc', 0)
                tempTbt = tseat.player.datas.get('tbt', 0)
                seatTBBoxInfoList.append({'tbc':tempTbc,
                                          'tbt': tempTbt,
                                          'item':itemId,
                                          'count':itemCount
                                          })

                # zyy 自动领取宝箱
                # clientId = sessiondata.getClientId(tseat.player.userId)
                # _, clientVer, _ = strutil.parseClientId(clientId)
                # if float(clientVer) >= 5.0 and float(clientVer) < 6.0:
                #     if itemId and (tempTbc == tempTbt):
                #         userId = tseat.player.userId
                #         ftlog.debug('doTboxGetRewardNotify', 'userId=', userId)
                #         mo = MsgPack()
                #         mo.setCmd('dizhu')
                #         mo.setResult("gameId", self.gameId)
                #         mo.setResult("userId", userId)
                #         mo.setResult("action", 'tbox_getReward_notify')
                #         datas = treasurebox.doTreasureBox1(self.gameId,userId)
                #         ftlog.debug('buidTboxReward datas=', datas)
                #         mo.updateResult(datas)
                #         ftlog.debug("doTboxGetRewardNotify", "userId=", userId, "mo=", mo)
                #         router.sendToUser(mo, userId)

        mp.setResult('seattb', seatTBBoxInfoList)
        mp.setResult('myCardNote', self.buildTableCardNote(seat))
        return mp
    
    def sendGameStartRes(self, seat):
        if seat.player and not seat.isGiveup:
            mp = self.buildGameStartResForSeat(seat)
            router.sendToUser(mp, seat.userId)
            
    def sendGameStartResAll(self):
        for seat in self.table.seats:
            self.sendGameStartRes(seat)
    
    def buildCallNextResForSeat(self, nextSeat, grab, forSeat, optime):
        '''
        通知下一个操作者叫分
        '''
        mp = self.buildTableMsgRes('table_call', 'next')
        mp.setResult('next', nextSeat.seatId)
        mp.setResult('seatId', nextSeat.seatId)
        mp.setResult('grab', grab)
        mp.setResult('stat', self.buildTableStatusInfoForSeat(forSeat))
        mp.setResult('opTime', self.table.runConf.optimeCallShow or optime)
        return mp

    def sendCallNextRes(self, nextSeat, grab, optime):
        for tseat in self.table.seats:
            if tseat.player and not tseat.isGiveup:
                mp = self.buildCallNextResForSeat(nextSeat, grab, tseat, optime)
                router.sendToUser(mp, tseat.userId)

    def buildCallRes(self, seat, callValue, oper=Oper.USER):
        '''
        通知叫分
        '''
        mp = self.buildTableMsgRes('table_call', 'call')
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        mp.setResult('call', callValue)
        mp.setResult('oper', oper)
        return mp
    
    def sendCallRes(self, seat, callValue, oper=Oper.USER):
        mp = self.buildCallRes(seat, callValue, oper)
        self.sendToAllSeat(mp)
        
    def buildPunishTipRes(self, seat, punishTip):
        mp = self.buildTableMsgRes('table_call', 'note')
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        mp.setResult('bgcolor', 'FF0000')  # 文字背景色
        mp.setResult('fgcolor', '00FF00')  # 文字字体颜色
        mp.setResult('seconds', 3)  # 提示显示的时间，秒
        mp.setResult('info', punishTip)
        return mp
    
    def sendPunishTipRes(self, seat, punishTip):
        if seat.player and not seat.isGiveup:
            mp = self.buildPunishTipRes(seat, punishTip)
            router.sendToUser(mp, seat.userId)
    
    def buildTuoguanRes(self, seat):
        robots = []
        for tseat in self.table.seats:
            if tseat.status and tseat.status.isTuoguan:
                robots.append(tseat.status.isTuoguan)
            else:
                robots.append(0)
        mp = self.buildTableMsgRes('table_call', 'rb')
        mp.setResult('robots', robots)
        mp.setResult('seatId', seat.seatId)

        if seat.status and seat.status.isPunish:
            mp.setResult('tuoguantip', "以托管状态结束牌局的玩家，将包赔金币/积分。")
        return mp
    
    def sendTuoGuanRes(self, seat):
        mp = self.buildTuoguanRes(seat)
        self.sendToAllSeat(mp)
        
    def buildTuoguanErrorRes(self, seat):
        robots = []
        for tseat in self.table.seats:
            if tseat.status and tseat.status.isTuoguan:
                robots.append(tseat.status.isTuoguan)
            else:
                robots.append(0)
        mp = self.buildTableMsgRes('table_call', 'rb')
        mp.setResult('robots', robots)
        mp.setResult('tips', '托管太频繁,禁止托管操作')
        return mp
        
    def sendTuoGuanErrorRes(self, seat):
        mp = self.buildTuoguanErrorRes(seat)
        self.sendToSeat(mp, seat)

    def buildAutoPlayRes(self, seat):
        mp = self.buildTableMsgRes('table_call', 'auto_play')
        mp.setResult('isauto', seat.status.isAutoPlay)
        return mp

    def sendAutoPlayRes(self, seat):
        mp = self.buildAutoPlayRes(seat)
        self.sendToSeat(mp, seat)

    def buildOutCardsResForSeat(self, seat, cards, precard, oper, forSeat):
        mp = self.buildTableMsgRes('table_call', 'card')
        mp.setResult('precard', precard)
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        mp.setResult('cards', cards)
        mp.setResult('stat', self.buildTableStatusInfoForSeat(seat))
        mp.setResult('myCardNote', self.buildTableCardNote(forSeat))
        if forSeat.player.gameClientVer >= self.HIDE_CARD_VER:
            if forSeat == seat or seat.status.isShowCards:
                mp.setResult('handCards', seat.status.cards)
            else:
                mp.setResult('handCards', [-1 for _ in xrange(len(seat.status.cards))])
        mp.setResult('topcard', self.table.gameRound.topValidCards.cards if self.table.gameRound.topValidCards else [])
        mp.setResult('issvr', 1 if oper == Oper.ROBOT else 0)
        return mp
    
    def sendChuPaiResForSeat(self, seat, cards, precard, oper, forSeat):
        if forSeat.player and not forSeat.isGiveup:
            mp = self.buildOutCardsResForSeat(seat, cards, precard, oper, forSeat)
            router.sendToUser(mp, forSeat.userId)
 
    def sendOutCardsRes(self, seat, cards, precard, oper):
        for tseat in self.table.seats:
            self.sendChuPaiResForSeat(seat, cards, precard, oper, tseat)
            
    def buildOutCardsNextResForSeat(self, seat, opTime, toSeat):
        mp = self.buildTableMsgRes('table_call', 'next')
        mp.setResult('next', seat.seatId)
        mp.setResult('seatId', seat.seatId)
        mp.setResult('stat', self.buildTableStatusInfoForSeat(toSeat))
        mp.setResult('opTime', self.table.runConf.optimeCardShow or opTime)
        return mp
    
    def sendOutCardNextRes(self, seat, opTime):
        for tseat in self.table.seats:
            if tseat.player and not tseat.isGiveup:
                mp = self.buildOutCardsNextResForSeat(seat, opTime, tseat)
                router.sendToUser(mp, tseat.userId)
    
    def buildWinloseAbortRes(self, result):
        mp = self.buildTableMsgRes('table_call', 'game_win')
        mp.setResult('stat', self.buildTableStatusInfo())
        mp.setResult('dizhuwin', 0)
        mp.setResult('nowin', 1)
        mp.setResult('slam', 0)
        mp.setResult('windoubles', 0)
        mp.setResult('save', 0)
        mp.setResult('cards', [seat.status.cards for seat in self.table.seats])
        win_streak = []
        for i, sst in enumerate(result.seatStatements):
            player = sst.seat.player
            win_streak.append(player.datas.get('winstreak', 0))
            mp.setResult('seat' + str(i + 1), [sst.delta, player.score, 0, 15,
                                               player.getData('tbt', 0),
                                               player.getData('tbc', 0),
                                               player.getData('level', 0),
                                               player.getData('exp', 0),
                                               0,
                                               player.getData('nextexp', 0),
                                               player.getData('title', '')])
        mp.setResult('winStreak', win_streak)
        return mp
    
    def sendWinloseAbortRes(self, result):
        mp = self.buildWinloseAbortRes(result)
        self.sendToAllSeat(mp)

    def buildResultDetails(self, result):
        return {}
    
    def buildWinloseRes(self, result, details, save):
        mp = self.buildTableMsgRes('table_call', 'game_win')
        # 牌桌状态信息
        mp.setResult('stat', self.buildTableStatusInfo())
        # 地主是否胜利
        mp.setResult('dizhuwin', 1 if result.dizhuStatement.isWin else 0)
        # 是否大满贯
        mp.setResult('slam', 1 if result.slam else 0)
        # 大满贯倍数
        mp.setResult('windoubles', result.gameRound.totalMulti)
        # 连胜次数
        mp.setResult('winStreak', details.get('winStreak'))
        # 好运礼包
        mp.setResult('luckyItemArgs', details.get('luckyItemArgs'))
        mp.setResult('save', save)
        # 局号
        mp.setResult('gameNum', result.gameRound.roundId)
        # 所有人的牌型
        mp.setResult('cards', details.get('cards'))
        # 所有人的大师分信息
        mp.setResult('skillScoreInfos', details.get('skillScoreInfos'))
        mp.setResult('seats', details.get('seatInfos'))

        for i, seatDetails in enumerate(details.get('seatDetails', [])):
            mp.setResult('seat%s' % (i+1), seatDetails)

        for seat in self.table.seats:
            if seat.player and not seat.isGiveup:
                # 是否支持complain
                _, clientIdVer, _ = strutil.parseClientId(seat.player.clientId)
                template, tips, clientIdLimit = commconf.getRoomComplainConf(self.gameId, self.bigRoomId)
                if clientIdVer >= clientIdLimit:
                    mp.setResult('complain', template)

        #自运营添加历史最高连胜数据
        winstreakdata = []
        for seat in self.table.seats:
            if seat.player:
                lasttemp = gamedata.getGameAttr(seat.player.userId, 6, 'lastwinstreak') or 0
                maxtemp = gamedata.getGameAttr(seat.player.userId, 6, 'maxwinstreak') or 0
                temp = [lasttemp,maxtemp]
                winstreakdata.append(temp)
        mp.setResult('zyyWinStreak', winstreakdata)

        return mp

    def sendWinloseRes(self, result):
        details = self.buildResultDetails(result)
        mp = self.buildWinloseRes(result, details, 1)
        for _, seat in enumerate(self.table.seats):
            if seat.player and not seat.isGiveup:
                # 分享时的二维码等信息
                clientId = sessiondata.getClientId(seat.player.userId)
                shareInfo = commconf.getNewShareInfoByCondiction(self.gameId, clientId, 'winstreak')
                mp.setResult('share', shareInfo)
                router.sendToUser(mp, seat.userId)

                if ftlog.is_debug():
                    ftlog.debug('sendWinloseRes.shareInfoLog userId=', seat.userId, 'shareInfo=', shareInfo)

        if ftlog.is_debug():
            ftlog.debug('sendWinloseRes.shareInfoLog mp=', mp)

    def buildEmoji(self, fromSeat, toSeat, price, smilie, self_charm, other_charm, count=1):
        '''
        发送互动表情
        @param count: 表情发送次数(新版本才支持)
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        member = timestamp < fromSeat.player.getData('memberExpires', 0)
        mp = self.buildTableMsgRes('table_call', 'smilies')
        mp.setResult('fromseat', fromSeat.seatId)
        mp.setResult('member', member)
        mp.setResult('toseat', toSeat.seatId)
        mp.setResult('price', price)
        mp.setResult('smilies', smilie)
        mp.setResult('from_charm', self_charm)
        mp.setResult('to_charm', other_charm)
        mp.setResult('tip', '')
        mp.setResult('count', count) # 新版本客户端才支持发送次数
        return mp
    
    def sendSmilesResError(self, userId, errInfo):
        mo = self.buildTableMsgRes('table_call', 'smilies')
        mo.setResult('userId', userId)
        mo.setError(1, errInfo)
        router.sendToUser(mo, userId)
        
    def sendSmilesResOk(self, fromSeat, toSeat, price, smilie, self_charm, other_charm, count):
        mp = self.buildEmoji(fromSeat, toSeat, price, smilie, self_charm, other_charm, count)
        for seat in self.table.seats:
            if seat.player and not seat.isGiveup:
                _, selfCharmSeat, otherCharmSeat, _, _ = self.tableCtrl._getEmojiConf(seat, smilie)
                _, clientVer, _ = strutil.parseClientId(seat.player.clientId)
                if self_charm:
                    mp.setResult('from_charm', selfCharmSeat)
                if other_charm:
                    mp.setResult('to_charm', otherCharmSeat)
                router.sendToUser(mp, seat.userId)

    def sendTBoxOpenedRes(self, seat, data):
        if seat.player and not seat.isGiveup:
            mo = self.buildTableMsgRes('table_call', 'tbox')
            mo.setResult('userId', seat.userId)
            mo.updateResult(data)
            router.sendToUser(mo, seat.userId)
            
    def buildTableChatRes(self, seat, isFace, voiceIdx, chatMsg):
        mp = self.buildTableMsgRes('table_chat')
        mp.setResult('userId', seat.userId)
        mp.setResult('msg', chatMsg)
        mp.setResult('isFace', isFace)
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userName', seat.player.name)
        if voiceIdx != -1:
            mp.setResult('voiceIdx', voiceIdx)
        return mp
        
    def sendTableChatRes(self, seat, isFace, voiceIdx, chatMsg):
        # 如果是农民，只能地主收到聊天信息
        for tseat in self.table.seats:
            if tseat.player and not seat.isGiveup:
                if tseat.userId != seat.userId:
                    if isFace != 1 and self.table.runConf.chatCheat and self.table.gameRound and seat != self.table.gameRound.dizhuSeat and tseat != self.table.gameRound.dizhuSeat:
                        continue
                    chatMsg = bug_fix._bugFixFilterChatMsgForPNG(tseat.player.clientId, chatMsg)
                mp = self.buildTableChatRes(seat, isFace, voiceIdx, chatMsg)
                router.sendToUser(mp, tseat.userId)
    
    def buildStartNongminJiabei(self):
        '''
        通知客户端进入农民加倍阶段
        '''
        mp = self.buildTableMsgRes('table_call', 'wait_nm_jiabei')
        mp.setResult('optime', self.table.runConf.optimeJiabeiShow or self.table.runConf.optimeJiabei)
        return mp
    
    def sendStartNongminJiabei(self):
        mp = self.buildStartNongminJiabei()
        self.sendToAllSeat(mp)
        
    def buildStartDizhuJiabei(self):
        '''
        通知客户端进入地主加倍阶段
        '''
        mp = self.buildTableMsgRes('table_call', 'wait_dz_jiabei')
        mp.setResult('optime', self.table.runConf.optimeJiabeiShow or self.table.runConf.optimeJiabei)
        return mp
    
    def sendStartDizhuJiabei(self):
        mp = self.buildStartDizhuJiabei()
        self.sendToAllSeat(mp)

    def buildSeatJiabei(self, seat, multi):
        '''
        玩家加倍通知客户端的协议
        @param multi: 加倍的倍数
        '''
        mp = self.buildTableMsgRes('table_call', 'jiabei')
        mp.setResult('jiabei', multi)
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        return mp
    
    def sendJiabeiRes(self, seat, multi):
        mp = self.buildSeatJiabei(seat, multi)
        self.sendToAllSeat(mp)
    
    def buildStartHuanpai(self):
        '''
        进入开始换牌阶段
        '''
        mp = self.buildTableMsgRes('table_call', 'startHuanpai')
        mp.setResult('opTime', self.table.runConf.optimeHuanpaiShow or self.table.runConf.optimeHuanpai)
        return mp
    
    def sendStartHuanpai(self):
        mp = self.buildStartHuanpai()
        self.sendToAllSeat(mp)
        
    def buildSeatHuanpai(self, seat):
        '''
        换牌阶段中某个玩家选出要换的牌型
        '''
        mp = self.buildTableMsgRes('table_call', 'huanpai')
        mp.setResult('userId', seat.userId)
        mp.setResult('seatId', seat.seatId)
        return mp
    
    def sendHuanpaiRes(self, seat):
        mp = self.buildSeatHuanpai(seat)
        self.sendToAllSeat(mp)
    
    def buildHuanpaiEnd(self, seat, turnDirection=0):
        '''
        换牌结束，换牌阶段完毕
        '''
        seatCards = []
        for s in self.table.gameRound.seats:
            if s.seatId == seat.seatId:
                seatCards.append(s.status.cards[:])
            else:
                seatCards.append([-1] * len(s.status.cards))

        mp = self.buildTableMsgRes('table_call', 'endHuanpai')
        # 换牌出牌的牌型
        mp.setResult('outCards', seat.status.huanpaiOutcards)
        # 换牌收到的牌型
        mp.setResult('inCards', seat.status.huanpaiIncards)
        # 每个玩家当前的手牌
        mp.setResult('seatCards', seatCards)
        # 换牌方向
        mp.setResult('turnDirection', turnDirection)
        mp.setResult('myCardNote', self.buildTableCardNote(seat))
        return mp
    
    def sendHuanpaiEndRes(self, turnDirection=0):
        for seat in self.table.seats:
            if seat.player and not seat.isGiveup:
                mp = self.buildHuanpaiEnd(seat, turnDirection)
                router.sendToUser(mp, seat.userId)

    def sendTableLeaveRes(self, userId, clientId, result):
        _, clientVer, _ = strutil.parseClientId(clientId)
        mp = self.buildTableMsgRes('table_leave')
        mp.updateResult(result)
        router.sendToUser(mp, userId)

    def sendTableQuitRes(self, seat, reason):
        mp = self.buildTableMsgRes('table_call', 'quit')
        mp.setResult('seatId', seat.seatId)
        mp.setResult('userId', seat.userId)
        mp.setResult('reason', reason)
        router.sendToUser(mp, seat.userId)

    def _do_table__sit(self, msg):
        userId = msg.getParam('userId')
        try:
            self.tableCtrl.userOnline(userId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table__sit',
                       'msg=', msg,
                       'e=', e)

    def _do_table__smilies(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        toSeatId = msg.getParam('toseat')
        emojiId = msg.getParam('smilies')
        count = msg.getParam('number', 1)
        try:
            self.tableCtrl.throwEmoji(userId, seatId, toSeatId, emojiId, count)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table__smilies',
                       'msg=', msg,
                       'e=', e)

    def _do_table__chat(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        isFace = msg.getParam('isFace')
        msgInfo = msg.getParam('msg')
        voiceIdx = msg.getParam('voiceIdx')
        try:
            self.tableCtrl.chat(userId, seatId, isFace, msgInfo, voiceIdx)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table__chat',
                       'msg=', msg,
                       'e=', e)

    def _do_table__tbox(self, msg):
        userId = msg.getParam('userId')
        try:
            data = comm_table_remote.doTableTreasureBox(self.gameId, userId, self.bigRoomId)
            mo = self.buildTableMsgRes('table_call', 'tbox')
            mo.setResult('userId', userId)
            mo.updateResult(data)
            router.sendToUser(mo, userId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table__tbox',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__ready(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        isReciveVoice = msg.getParam('recv_voice', False)
        try:
            self.tableCtrl.ready(userId, seatId, isReciveVoice)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__ready',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__call(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        callValue = msg.getParam('call')
        try:
            self.tableCtrl.call(userId, seatId, callValue)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__call',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__card(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        cards = msg.getParam('cards')
        ccrc = msg.getParam('ccrc')
        try:
            self.tableCtrl.outCard(userId, seatId, cards, ccrc)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__card',
                       'msg=', msg,
                       'e=', e)
            
    def _do_table_call__robot(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        try:
            self.tableCtrl.tuoguan(userId, seatId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__robot',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__auto_play(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        isAutoPlay = msg.getParam('isauto')
        try:
            if ftlog.is_debug():
                ftlog.debug('DizhuTableProto._do_table_call__autoplay',
                            'msg=', msg)
            self.tableCtrl.autoplay(userId, seatId, isAutoPlay)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__autoplay',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__show(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        try:
            self.tableCtrl.showCard(userId, seatId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__show',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__cardNoteOpen(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        try:
            self.tableCtrl.openCardNote(userId, seatId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__cardNoteOpen',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__tbox(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        try:
            self.tableCtrl.openTBox(userId, seatId)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__tbox',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__jiabei(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        jiabei = msg.getParam('jiabei', 0)
        try:
            self.tableCtrl.jiabei(userId, seatId, jiabei)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__jiabei',
                       'msg=', msg,
                       'e=', e)

    def _do_table_call__huanpai(self, msg):
        userId = msg.getParam('userId')
        seatId = msg.getParam('seatId')
        outCards = msg.getParam('cards')
        try:
            self.tableCtrl.huanpaiOutCards(userId, seatId, outCards)
        except Exception, e:
            ftlog.warn('DizhuTableProto._do_table_call__huanpai',
                       'msg=', msg,
                       'e=', e)

    def _onSitdown(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onSitdown',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId))
        
        self.sendQuickStartRes(event.seat, True, TYRoom.ENTER_ROOM_REASON_OK)
        self.sendTableInfoResAll()
        self.sendRobotNotifyCallUp(None)
        
    def _onStandup(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onStandup',
                        'tableId=', event.table.tableId,
                        'seatId=', event.seat.seatId,
                        'userId=', event.player.userId,
                        'reason=', event.reason)
        
        if event.reason not in (StandupReason.GAME_OVER,
                                StandupReason.GAME_ABORT,
                                StandupReason.FORCE_CLEAR):
            self.sendTableInfoResAll()
        
        if event.reason != StandupReason.FORCE_CLEAR:
            self.sendRobotNotifyShutDown(None)
        
    def _onSeatReady(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onSeatReady',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId))
        self.sendUserReadyResAll(event.seat)

    def _onGameReady(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onGameReady',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendGameReadyResAll()

    def _onGameStart(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onGameStart',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendGameStartResAll()
        
    def _onWildCard(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onWildCard', 
                        'tableId=', event.table.tableId,
                        'wildCard=', event.wildCard,
                        'wildCardBig=', event.wildCardBig)
        self.sendWildCardRes(event.wildCard, event.wildCardBig)
    
    def _onCardNoteOpened(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onCardNoteOpened',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId))
        self.sendCardNoteOpened(event.seat)
        
    def _onSeatOnlineChanged(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onSeatReady',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId))
        # 自己需要发送quickstart和tableInfo
        self.sendQuickStartRes(event.seat, True, TYRoom.ENTER_ROOM_REASON_OK)
        self.sendTableInfoRes(event.seat)
        self.sendOnlineChanged(event.seat)
    
    def _onCall(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onCall',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'oper=', event.oper,
                        'callValue=', event.callValue)
        self.sendCallRes(event.seat, event.callValue, event.oper)
    
    def _onCurOpSeatMove(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onCurOpSeatMove',
                        'tableId=', event.table.tableId,
                        'prevOpSeat=', (event.prevOpSeat.userId, event.prevOpSeat.seatId) if event.prevOpSeat else None,
                        'curOpSeat=', (event.curOpSeat.userId, event.curOpSeat.seatId),
                        'optime=', event.optime,
                        'autoOp=', event.autoOp,
                        'dizhuSeatId=', event.table.gameRound.dizhuSeat.seatId if event.table.gameRound.dizhuSeat else 0)
        if not event.table.gameRound.dizhuSeat:
            grab = 1 if event.table.gameRound.callList else 0
            self.sendCallNextRes(event.curOpSeat, grab, event.optime)
        else:
            if not event.autoOp:
                self.sendOutCardNextRes(event.curOpSeat, event.optime)
        
    def _onOutCard(self, event):
        cards = event.validCards.cards if event.validCards else []
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onOutCard',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'cards=', cards)
        self.sendOutCardsRes(event.seat, cards, event.prevCards, event.oper)
    
    def _onOutCardError(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onOutCardError',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'cards=', event.validCards.cards if event.validCards else [],
                        'ccrc=', event.ccrc)
        self.sendTableInfoRes(event.seat)
        
    def _onStartNongminJiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onStartNongminJiabei',
                        'tableId=', event.table.tableId)
        self.sendStartNongminJiabei()
    
    def _onStartDizhujiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onStartDizhujiabei',
                        'tableId=', event.table.tableId)
        self.sendStartDizhuJiabei()
    
    def _onStartHuanpai(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onStartHuanpai',
                        'tableId=', event.table.tableId)
        self.sendStartHuanpai()
    
    def _onNongminJiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onNongminJiabei',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'multi=', event.multi)
        self.sendJiabeiRes(event.seat, 1 if event.multi > 1 else 0)

    def _onDizhuJiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onDizhuJiabei',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'multi=', event.multi)
        self.sendJiabeiRes(event.seat, 1 if event.multi > 1 else 0)
        
    def _onHuanpaiOutcards(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onHuanpaiOutcards',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'outCards=', event.outCards)
        self.sendHuanpaiRes(event.seat)
    
    def _onHuanpaiEnd(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onHuanpaiEnd',
                        'tableId=', event.table.tableId)
        turnDirection = event.turnDirection
        self.sendHuanpaiEndRes(turnDirection=turnDirection)
    
    def _onThrowEmoji(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onThrowEmoji',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seatFrom.userId, event.seatFrom.seatId),
                        'toSeat=', (event.seatTo.userId, event.seatTo.seatId),
                        'emojiId=', event.emojiId,
                        'count=', event.count)
        self.sendSmilesResOk(event.seatFrom,
                             event.seatTo,
                             event.deltaChip,
                             event.emojiId,
                             event.charmDeltaFrom,
                             event.charmDeltaTo,
                             event.count)
                
    def _onTuoguan(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onHuanpaiOutcards',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'isTuoguan=', event.isTuoguan)
        self.sendTuoGuanRes(event.seat)

    def _onAutoPlay(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onAutoPlay',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'isAutoPlay=', event.isAutoPlay)
        self.sendAutoPlayRes(event.seat)
    
    def _onShowCards(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onHuanpaiOutcards',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId))
        self.sendShowCardsRes(event.seat)
    
    def _onTableTBoxOpened(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onTableTBoxOpened',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'data=', event.data)
        self.sendTBoxOpenedRes(event.seat, event.data)

    def _onChat(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onChat',
                        'tableId=', event.table.tableId,
                        'seat=', (event.seat.userId, event.seat.seatId),
                        'isFace=', event.isFace,
                        'voiceIdx=', event.voiceIdx,
                        'msg=', event.msg)
        self.sendTableChatRes(event.seat, event.isFace, event.voiceIdx, event.msg)
    
    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseRes(event.gameResult)
        
    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
            
        # 流局自动重开则不给客户端返回消息
        if not PlayMode.isAbortRestart(event.table, event.table.seats):
            self.sendWinloseAbortRes(event.gameResult)

    def setupTable(self):
        self.table.on(SitdownEvent, self._onSitdown)
        self.table.on(StandupEvent, self._onStandup)
        self.table.on(SeatReadyEvent, self._onSeatReady)
        self.table.on(GameReadyEvent, self._onGameReady)
        self.table.on(GameStartEvent, self._onGameStart)
        self.table.on(WildCardEvent, self._onWildCard)
        
        self.table.on(CardNoteOpenedEvent, self._onCardNoteOpened)
        self.table.on(SeatOnlineChanged, self._onSeatOnlineChanged)
        
        self.table.on(CallEvent, self._onCall)
        self.table.on(CurOpSeatMoveEvent, self._onCurOpSeatMove)
        
        self.table.on(StartNongminJiabeiEvent, self._onStartNongminJiabei)
        self.table.on(StartDizhuJiabeiEvent, self._onStartDizhujiabei)
        self.table.on(StartHuanpaiEvent, self._onStartHuanpai)
        
        self.table.on(NongminJiabeiEvent, self._onNongminJiabei)
        self.table.on(DizhuJiabeiEvent, self._onDizhuJiabei)
        self.table.on(HuanpaiOutcardsEvent, self._onHuanpaiOutcards)
        self.table.on(HuanpaiEndEvent, self._onHuanpaiEnd)

        self.table.on(OutCardEvent, self._onOutCard)
        self.table.on(ShowCardEvent, self._onShowCards)
        
        self.table.on(ThrowEmojiEvent, self._onThrowEmoji)
        self.table.on(TuoguanEvent, self._onTuoguan)
        self.table.on(AutoPlayEvent, self._onAutoPlay)
        self.table.on(ChatEvent, self._onChat)
        self.table.on(TableTBoxOpened, self._onTableTBoxOpened)
        
        self.table.on(GameRoundOverEvent, self._onGameRoundOver)
        self.table.on(GameRoundAbortEvent, self._onGameRoundAbort)
