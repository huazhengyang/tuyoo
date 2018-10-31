# coding=UTF-8
'''
'''
import time

from dizhu import gameplays
from dizhu.activities.toolbox import TimeCounter
from dizhu.entity import dizhuconf, smilies, treasurebox
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.gametable import bug_fix
from dizhu.gametable.dizhu_conf import DizhuTableConf
from dizhu.gametable.dizhu_player import DizhuPlayer
from dizhu.gametable.dizhu_seat import DizhuSeat
from dizhu.gametable.dizhu_state import DizhuState
from dizhu.replay import gameround
from dizhu.replay.gameround import GameReplayRound
from dizhu.servers.util.rpc import table_remote
from freetime.util import log as ftlog
from hall.entity import hallchatlog
from poker.entity.configure.configure import CLIENTID_SYSCMD
from poker.entity.dao import tabledata, sessiondata, daobase, userchip
from poker.entity.game.tables.table import TYTable
from poker.entity.game.tables.table_timer import TYTableTimer
from poker.protocol import runcmd
from poker.util import strutil, keywords, timestamp as pktimestamp

__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]

class DizhuTable(TYTable):
    '''
    table只承载:
        1. 桌子的属性
        2. 属性内容相关的build方法
        3. 状态的清理接口方法
        4. 衔接基类的消息调用入口值玩法逻辑处理器
    '''
    def __init__(self, room, tableId):
        super(DizhuTable, self).__init__(room, tableId)
        # 当前配置是否已经发生变化, 初始化原始的桌子运行配置
        self._resetTableConf()
        # 实例化玩法逻辑处理
        self.gamePlay = gameplays.getInstance(self, room.roomConf["playMode"], room.roomConf['typeName'])
        # 牌局记录器GameReplayRound
        self.gameRound = None
        # 初始化桌子计时器
        self.tableTimer = TYTableTimer(self)
        # 初始化桌子计时器
        self.mnoteTimer = TYTableTimer(self)
        # 初始化座位计时器
        self.seatTimers = []
        # key=roundId, value=(GameReplayRound, set<userId>)
        self._gameRoundMap = {}
        # 初始化玩家, 座位, 座位计时器
        for seatIndex in xrange(self.maxSeatN):
            self.seats[seatIndex] = DizhuSeat(self)
            self.players[seatIndex] = self._makePlayer(seatIndex)
            self.seatTimers.append(TYTableTimer(self))
        # 桥接桌子的状态数据
        self._status = DizhuState(self)
        self._initCleanUp = 0
        # 初始化桌子全量配置
        self.clear(None)
        # 清理遗留的代入金币
        self.cleanUpLastUserTableChips()

    def goodCardLucky(self):
        return self.runConfig.lucky
    
    def isFriendTable(self):
        return False
    
    def canJiabei(self):
        return False
    
    def huanpaiCount(self):
        return 0
    
    def _makePlayer(self, seatIndex):
        return DizhuPlayer(self, seatIndex)

    def _checkReloadRunConfig(self):
        ftlog.debug('self._checkReloadRunConfig->', self.configChanged, self.playersNum)
        if self._status.state == DizhuState.TABLE_STATE_IDEL :
            self._resetTableConf()
            ftlog.debug('self._runConfig->', self._runConfig)

    def _resetTableConf(self):
        runconf = strutil.cloneData(self.room.roomConf)
        runconf.update(strutil.cloneData(self.config))
        self._runConfig = DizhuTableConf(runconf)

    def findGameRound(self, roundId):
        return self._gameRoundMap.get(roundId, (None, None))
    
    def _clearReplayRound(self):
        self._curReplayyRound = None
        toRemove = []
        for roundId, (gameRound, _) in self._gameRoundMap.iteritems():
            delta = pktimestamp.getCurrentTimestamp() - (gameRound.gameOverTimestamp or 0)
            # TODO
            if delta > 600:
                toRemove.append(roundId)
        for roundId in toRemove:
            ftlog.info('DizhuTable._clearReplayRound removeRound roomId=', self.roomId,
                       'tableId=', self.tableId,
                       'roundId=', roundId)
            del self._gameRoundMap[roundId]
        
    def _createGameRound(self):
        seats = []
        for player in self.players:
            seats.append(gameround.Seat(player.userId,
                                        player.datas.get('name', ''),
                                        player.datas.get('sex', 0),
                                        player.datas.get('vipInfo', {}).get('level', 0),
                                        player.datas.get('chip', 0),
                                        0,
                                        player.datas.get('purl', ''),
                                        player.datas.get('wearedItems', [])))
        num = daobase.executeTableCmd(self.roomId, self.tableId, 'HINCRBY', 'game.round.number', self.roomId, 1)
        self.gameRound = GameReplayRound(num,
                                         self.roomId,
                                         self.tableId,
                                         self.room.matchId,
                                         self.room.roomConf['name'],
                                         self.room.roomConf['playMode'],
                                         self.runConfig.grab,
                                         self.runConfig.roomMutil,
                                         self.runConfig.roomFee,
                                         seats, pktimestamp.getCurrentTimestamp())
        if not self.isMatch:
            self._gameRoundMap[self.gameRound.roundId] = (self.gameRound, set())
        ftlog.info('DizhuTable._createGameRound roomId=', self.roomId,
                   'tableId=', self.tableId,
                   'roundId=', self.gameRound.roundId)
    
    def isGameReady(self):
        return self.isAllReady()
    
    def isAllReady(self):
        for seat in self.seats:
            if seat.state != DizhuSeat.SEAT_STATE_READY :
                # 某一个座位没有准备, 继续等待
                return False
        return True
    
    def clear(self, userids):
        '''
        完全清理桌子数据和状态, 恢复到初始化的状态
        '''
        ftlog.debug('clear--> begin')
        self._resetTableConf()  
        # 桌子数据恢复
        self._complain = None  # 桌内投诉配置
        self._complain_open = 0  # 桌内投诉是否开启
        self._base_table_info = None  # 基本的信息, 用于快速返回table_info
        self.gameRound = None  # 桌子的牌局控制
        self._clearReplayRound()
        # 重置牌局记录器
        # 重置所有的计时器
        self.cancelTimerAll()
        # 清理桌子状态
        self.status.clear()
        # 清理座位状态, 玩家信息
        for x in xrange(len(self.seats)) :
            seat = self.seats[x]
            player = self.players[x]
            seat.clear()
            player.clear()
            if userids :
                seat.userId = userids[x]
                player.initUser(0, 0)  # TODO isNextBuyin, isUsingScore 参数需要携带进来 
        ftlog.debug('clear-->done')


    def cancelTimerAll(self):
        '''
        清理所有的计时器
        '''
        self.tableTimer.cancel()
        self.mnoteTimer.cancel()
        for t in self.seatTimers :
            t.cancel()
        
    @property
    def status(self):
        return self._status


    @property
    def bigRoomId(self):
        '''
        取得当前房间的配置ID,再配置系统中,房间的附属配置均以此为键值进行配置
        '''
        return self.room.roomDefine.bigRoomId


    @property
    def runConfig(self):
        '''
        取得当前的基本配置, 当系统的配置内容更新时, 如果桌子再游戏中, 那么等下次开局时配置才真正的更新
        '''
        return self._runConfig


    @property
    def isMatch(self):
        '''
        判定当前是否是比赛桌
        '''
        return self._runConfig.isMatch


    def buildBasicInfo(self, reset, userId, clientId):
        '''
        此方法建立table的一些基本信息, 每一副牌, 建立后即不必再次建立
        每副牌结束后, 清理self._base_table_info属性, 
        下次自动重配置中取得新数据建立基本信息
        '''
        if self._base_table_info and not reset:
            return self._base_table_info
        
        ftlog.debug('buildBasicInfo reset !!!!')

        # 基本信息
        info = {"name" : "",
                "creator" : 0,
                "pwd" : "",
                "tableId" : self.tableId,
                "roomId" : self.roomId
                }
        # 宝箱信息
        tbbox, couponrule = treasurebox.getTreasureTableTip(self.bigRoomId)
        # 配置信息
        config = {
                  "tbbox" : tbbox,
                  "couponrule" : couponrule,
                  "maxseat" : self.maxSeatN,
                  "rangpaiMultiType" : self.runConfig.rangpaiMultiType,
                  "autoChange" : self.runConfig.autochange,
                  "base" : self.runConfig.basebet,
                  "basemulti" : self.runConfig.basemulti,
                  "gslam" : self.runConfig.gslam,
                  "grab" : self.runConfig.grab,
                  "chat" : self.runConfig.canchat,
                  "optime" : self.runConfig.optime,
                  "coin2chip" : self.runConfig.coin2chip,
                  "lucky" : self.runConfig.lucky,
                  "untiCheat" : self.runConfig.unticheat,
                  "passtime" : self.runConfig.passtime,
                  "isMingPai" : self.runConfig.showCard,
                  "roommulti" : self.runConfig.roomMutil,
                  "maxcoin" : self.runConfig.maxCoin,
                  "mincoin" : self.runConfig.minCoin,
                  "sfee" : self.runConfig.roomFee,
                  "optimedis" : dizhuconf.getTableNetWorkTipStr(),
                  "matchInfo" : "",  # 老版本数据结构兼容
                  }

        _, clientVer, _ = strutil.parseClientId(clientId)
        if clientVer and clientVer < 3.7 :
            # 小于3.7版本是否能够聊天、防作弊统一使用的是untiCheat字段
            # 对于小于3.7版本的在不防作弊但是不能聊天时处理为防作弊
            if not config['chat'] and not config['untiCheat']:
                config['untiCheat'] = 1

        # 投诉信息
        self._complain_open = 0
        self._complain, _ = dizhuconf.getComplainInfo(self.bigRoomId)
        if self._complain :
            nowstr = time.strftime('%H:%M')
            if strutil.regMatch(self._complain['time'], nowstr):
                self._complain_open = 1
            ftlog.debug('dizhu_table buildBasicInfo _complain_open=', self._complain_open, '_complain=', self._complain, 'reg=', self._complain['time'], 'nowstr=', nowstr, 'roomId=', self.bigRoomId)    
        self._base_table_info = {'config' : config,
                                 'info' : info
                                 }
        return self._base_table_info


    def _doSit(self, msg, userId, seatId, clientId): 
        '''
        玩家操作, 尝试再当前的某个座位上坐下
        '''
        continuityBuyin = msg.getParam('buyin')
        continuityBuyin = 1 if continuityBuyin else 0
        self.gamePlay.doSitDown(userId, seatId, clientId, continuityBuyin)
 

    def _doStandUp(self, msg, userId, seatId, reason, clientId):
        '''
        玩家操作, 尝试离开当前的座位
        子类需要自行判定userId和seatId是否吻合
        '''
        self.gamePlay.doStandUp(userId, seatId, reason, clientId)


    def _doEnter(self, msg, userId, clientId):
        '''
        玩家操作, 尝试进入当前的桌子
        '''
        self.gamePlay.doEnter(userId, clientId)


    def _doLeave(self, msg, userId, clientId):
        '''
        玩家操作, 尝试离开当前的桌子
        实例桌子可以覆盖 _doLeave 方法来进行自己的业务逻辑处理
        '''
        self.gamePlay.doLeave(userId, clientId, True)
    
    def _doTableManage(self, msg, action):
        '''
        桌子内部处理所有的table_manage命令
        '''
        result = {'action' : action, 'isOK' : True}
        if action == 'leave' :
            userId = msg.getParam('userId')
            clientId = runcmd.getClientId(msg)
            isOK, ret = self.gamePlay.doLeave(userId, clientId, False)
            if isOK :
                self.gamePlay.sender.sendTableInfoResAll(0)
            result.update(ret)
            result['isOK'] = isOK

        return result


    def _doTableCall(self, msg, userId, seatId, action, clientId):
        '''
        桌子内部处理所有的table_call命令
        子类需要自行判定userId和seatId是否吻合
        '''
        player = None
        if seatId > 0 and seatId <= self.maxSeatN :
            player = self.players[seatId - 1]
            if(userId != player.userId) :
                ftlog.warn('_doTableCall, the userId is wrong !', userId, seatId, action,
                            'player.userId=', player.userId, clientId)
                return

        if action == 'ready' :
            recvVoice = msg.getParam('recv_voice')
            self.gamePlay.doReady(player, recvVoice)
            return

        if action == 'CL_READY_TIMEUP' :
            self.gamePlay.doReadyTimeOut(player)
            return

        if action == 'CL_READY_NEXT_DELAY' :
            self.gamePlay.doFirstCallDizhu(player)
            return

        if action == 'call' :
            call = msg.getParam('call')
            grab = msg.getParam('grab')
            self.gamePlay.doCallDizhu(player, grab, call, DizhuPlayer.TUGUAN_TYPE_USERACT)
            return

        if action == 'CL_TIMEUP_CALL' :
            self.gamePlay.doCallDizhuTimeOut(player)
            return

        if action == 'CL_TIMEUP_NEXT_STEP':
            self.gamePlay.nextStep(player)
            return

        if action == 'card' :
            cards = msg.getParam('cards')
            mcrc = msg.getParam('ccrc')
            self.gamePlay.doChuPai(player, cards, mcrc, DizhuPlayer.TUGUAN_TYPE_USERACT)
            return

        if action == 'CL_TIMEUP' :
            tuoGuanType = msg.getParam('tuoGuanType')
            mcrc = msg.getParam('ccrc')
            self.gamePlay.doChuPaiTimeOut(player, [], mcrc, tuoGuanType)
            return

        if action == 'robot' :
            self.gamePlay.doTuoGuan(player)
            return

        if action == 'show' :
            self.gamePlay.doShowCard(player)
            return

        if action == 'tbox' :
            self.gamePlay.doTreasurebox(player)
            return
        
        if action == 'cardNoteOpen':
            self.gamePlay.doOpenCardNote(player)
            return

        if action == 'jiabei':
            jiabei = msg.getParam('jiabei', 0)
            self.gamePlay.doJiabei(player, jiabei)
            return
        
        if action == 'JIABEI_TIMEUP':
            self.gamePlay.doJiabeiTimeout()
            return
        
        if action == 'HUANPAI_TIMEUP':
            self.gamePlay.doHuanpaiTimeout()
            return
        
        if action == 'huanpai':
            cards = msg.getParam('cards')
            self.gamePlay.doHuanpai(player, cards)
            return
            
        self._doOtherAction(msg, player, seatId, action, clientId)
        
    def _doOtherAction(self, msg, player, seatId, action, clientId):
        pass
    
    def recordSeatUserId(self, seatId, userId):
        # TODO 如果桌子redis话后, 此处理需要再次调整,无需单独进行数据记录
        tabledata.setTableAttr(self.roomId, self.tableId, 'seat%dUserId' % (seatId), userId)


    def getLastSeatUserId(self, seatId):
        # TODO 如果桌子redis话后, 此处理需要再次调整,无需单独进行数据记录
        return tabledata.getTableAttr(self.roomId, self.tableId, 'seat%dUserId' % (seatId), filterKeywords=False)

    
    @classmethod
    def getSavedSeatUserId(cls, seatMaxN, roomId, tableId):
        attrlist = []
        for x in xrange(seatMaxN) :
            attrlist.append('seat%dUserId' % (x + 1))
        uids = tabledata.getTableAttrs(roomId, tableId, attrlist, filterKeywords=False)
        return strutil.parseInts(*uids)


    def cleanUpLastUserTableChips(self):
        # 此方法清理当前桌子的代入金币, 例如再游戏中时, 系统启动, 带入金币遗留在桌子中, 桌子再次启动时, 进行清理
        # 但是, 若再次启动时, 如果桌子数量减少, 那么带入的金币就不会被自动清理, 需要进行手工清理
        # 或者将这个清理工作, 全部移动到crontab中?
        attrlist = []
        valuelist = []
        for x in xrange(len(self.seats)) :
            attrlist.append('seat%dUserId' % (x + 1))
            valuelist.append(0)
        if attrlist :
            userids = tabledata.getTableAttrs(self.roomId, self.tableId, attrlist, filterKeywords=False)
            tabledata.setTableAttrs(self.roomId, self.tableId, attrlist, valuelist)
            if not userids:
                return
            ftlog.debug('cleanUpLastUserTableChips->uids=', repr(userids))
            for uid in userids :
                if uid and uid > 0 :
                    table_remote._cleanUpTableChipOnStandUp(uid, self.roomId, self.tableId, CLIENTID_SYSCMD)


    def doTableChat(self, userId, seatId, isFace, voiceIdx, chatMsg):
        player = None
        if seatId > 0 and seatId <= self.maxSeatN :
            player = self.players[seatId - 1]
            if(userId != player.userId) :
                ftlog.warn('doTableChat, the userId is wrong !', userId, seatId,
                            'player.userId=', player.userId)
                return
        else:
            ftlog.warn('doTableChat, the seatId is wrong !', userId, seatId)
            return
        
        if isFace == 2 and self.isFriendTable():
            for p in self.players:
                if p.userId > 0 and p.datas :
                    self.gamePlay.sender.sendTableChat(player, isFace, voiceIdx, chatMsg, p.userId, p.datas['name'])
            return
        
        chatMsg = chatMsg[:80]  # 80个字符长度限制
        if isFace == 0 :
            # 纯文本内容
            chatMsg = keywords.replace(chatMsg)
            if dizhuconf.isEnableLogChatMsg():
                username = player.datas.get('name', '')
                hallchatlog.reportChatLog(userId, chatMsg, self.gameId, self.roomId, self.tableId, seatId, 
                                          userName=username, roomName=self.room.roomConf['name'])
                ftlog.info('tableChatLog gameId=%s; room="%s"; table=%s; userId=%s; name="%s"; msg="%s"' % (
                            DIZHU_GAMEID, self.room.roomConf['name'], self.tableId,
                            player.userId, username, chatMsg))
            if self.gameRound:
                self.gameRound.chat(seatId - 1, isFace, voiceIdx, chatMsg)
            for p in self.players:
                toUserId = p.userId
                if toUserId > 0 and p.datas :
                    self.gamePlay.sender.sendTableChat(player, isFace, voiceIdx, chatMsg, toUserId, p.datas['name'])
            return

        if isFace == 1: 
            # 表情图片
            chatMsg = bug_fix._bugFixFilterChatMsgForVer27(chatMsg)
            if self.gameRound:
                self.gameRound.chat(seatId - 1, isFace, voiceIdx, chatMsg)
            for p in self.players:
                toUserId = p.userId
                if toUserId > 0  :
                    msgToUser = chatMsg
                    if toUserId != player.userId :
                        msgToUser = bug_fix._bugFixFilterChatMsgForPNG(toUserId, chatMsg)
                    if msgToUser and p.datas :
                        self.gamePlay.sender.sendTableChat(player, isFace, voiceIdx, msgToUser, toUserId, p.datas['name'])
            return
#       if isFace == 2 : # 语音聊天 -- 已经废弃
#       if isFace == 3 : # 全游戏内的LED消息, 地主没有, 需要另外的实现

    def doTableSmilies(self, userId, seatId, smilie, toSeatId, wcount=1):
        if wcount <= 0:
            wcount = 1
        player = None
        if seatId > 0 and seatId <= self.maxSeatN :
            player = self.players[seatId - 1]
            if userId != player.userId or not player.userId :
                ftlog.warn('doTableSmilies, the userId is wrong !', userId, seatId,
                            'player.userId=', player.userId)
                return
        else:
            ftlog.warn('doTableSmilies, the seatId is wrong !', userId, seatId)
            return
        isSupportBuyin = player.isSupportBuyin
        
        ftlog.debug('doTableSmilies from=', seatId, userId, smilie, toSeatId)
        if toSeatId and toSeatId <= 0 or toSeatId == seatId or toSeatId > len(self.seats) :
            self.gamePlay.sender.sendSmilesResError(userId, '参数错误')
            return

        conf = smilies.getConfDict(self.bigRoomId, userId)
        conf = conf.get(smilie, None)
        if not conf :
            self.gamePlay.sender.sendSmilesResError(userId, '该房间不支持互动表情')
            return
        
        price, self_charm, other_charm = conf['price'], conf['self_charm'], conf['other_charm']
        ftlog.debug('doTableSmilies price', price, self_charm, other_charm)
        if price == None or price < 0:
            self.gamePlay.sender.sendSmilesResError(userId, '该房间不支持互动表情')
            return

        minchip = self.runConfig.minCoin
        if isSupportBuyin :
            minchip = 0
        other_uid = self.seats[toSeatId - 1].userId
        if other_uid <= 0 :
            self.gamePlay.sender.sendSmilesResError(userId, '该玩家已经离开此桌子')
            return

        # 地主需求3.773(发布为3.775)
        # 新版本金币不足也可以发送表情,发送表情后所有表情进入冷却模式等待冷却
        self.doTableSmiliesv3_775(userId, seatId, smilie, toSeatId, player, wcount)

    def doTableSmiliesv3_775(self, userId, seatId, smilie, toSeatId, player, wcount=1):
        '''
        @param wcount: wantcount
        地主新版本支持,互动表情金币不足也可以发送,不过会存在冷却时间,所有互动表情只要使用一个,就会全部进入倒计时状态
        新版本新增了一个表情,为了兼容老版本,需要在新版本发送新增的表情时特殊处理
        '''
        ftlog.debug('doTableSmiliesv3_775:begin',
                    'userId=', userId,
                    'smilie=', smilie,
                    'wcount=', wcount)
        other_uid = self.seats[toSeatId - 1].userId
        if other_uid <= 0 :
            self.gamePlay.sender.sendSmilesResError(userId, '该玩家已经离开此桌子')
            return

        conf = smilies.getConfDict(self.bigRoomId, userId)
        conf = conf.get(smilie, None)
        if not conf :
            self.gamePlay.sender.sendSmilesResError(userId, '该房间不支持互动表情')
            return

        price = conf.get('price', 0)
        mychip = userchip.getChip(userId)

        # 金币不足时,进行冷却时间判断
        ftlog.debug('doTableSmiliesv3_775:chip+cd',
                    'userId=', userId,
                    'smilie=', smilie,
                    'wcount=', wcount)

        if mychip < price and (not self.checkCooldownStatus(userId, smilie, conf)):
            self.gamePlay.sender.sendSmilesResError(userId, '互动表情冷却时间未到')
            return

        price, self_charm, other_charm = conf['price'], conf['self_charm'], conf['other_charm']
        if price == None or price < 0:
            self.gamePlay.sender.sendSmilesResError(userId, '该房间不支持互动表情')
            return

        minchip = self.runConfig.minCoin
        if player.isSupportBuyin :
            minchip = 0

        clientId = sessiondata.getClientId(userId)
        
        # 获得实际要发送的次数rcount(连续发送表情，为了性能一次性处理)
        rcount, deltaChip, finalChip = table_remote.doTableSmiliesFrom_v3_775(self.roomId, self.bigRoomId, self.tableId,
                                     userId, smilie, minchip,
                                     price, self_charm, clientId, wcount)
        ftlog.debug('doTableSmiliesv3_775:rcount', 
                    'userId=', userId,
                    'rcount=', rcount,
                    'deltaChip=', deltaChip,
                    'finalChip=', finalChip)
        table_remote.doTableSmiliesTo(other_uid, other_charm, rcount)

        # 互动表情
        if self.gameRound:
            self.gameRound.sendSmilies(seatId - 1, toSeatId - 1, smilie, rcount, deltaChip, finalChip)
        
        member = self.isMember(player)
        # 发送结果消息
        # 十连发为了支持老版本，只能多次发送协议
        self.gamePlay.sender.sendSmilesResOk(seatId, member, toSeatId, price, smilie, self_charm, other_charm, '', rcount)
        # 同步修改player中的魅力值信息
        if self.players[toSeatId - 1].userId == other_uid : # 玩家可能已经离开或换人
            self.players[toSeatId - 1].adjustCharm(other_charm * rcount)
        if player.userId == userId : # 玩家可能已经离开或换人
            player.adjustCharm(self_charm * rcount)

        ## 重置CD计时
        uniquekey = 'smile.emo'
        TimeCounter.resetingCounterToCurrentTimestamp(uniquekey, userId)

    # ddz v3.775
    def checkCooldownStatus(self, userId, smilie, emoconf):
        '''
        所有互动表情只要使用一个,就会全部进入倒计时状态
        '''
        uniquekey = 'smile.emo'
        duration = TimeCounter.getCountingSeconds(uniquekey, userId)
        if duration < 0:
            TimeCounter.resetingCounterToCurrentTimestamp(uniquekey, userId)
            return True
        return duration >= emoconf.get('cd', 0)
    
    def isMember(self, player):
        timestamp = pktimestamp.getCurrentTimestamp()
        return timestamp < player.datas.get('memberExpires', 0)
    
    def doTableTreasureBox(self, userId, seatId):
        player = None
        if seatId > 0 and seatId <= self.maxSeatN :
            player = self.players[seatId - 1]
            if(userId != player.userId) :
                ftlog.warn('doTableTreasureBox, the userId is wrong !', userId, seatId,
                            'player.userId=', player.userId)
                return
        else:
            ftlog.warn('doTableTreasureBox, the seatId is wrong !', userId, seatId)
            return
        
        ftlog.debug('doTableTreasureBox from=', player.seatId, player.userId)
        datas = table_remote.doTableTreasureBox(userId, self.bigRoomId)
        if ("tbt" in datas) and ("tbc" in datas):
            player.datas["tbt"] = datas["tbt"]
            player.datas["tbc"] = datas["tbc"]
        self.gamePlay.sender.sendTreasureBoxRes(player.userId, datas)


    def _isRobotCanSit(self):
        hasrobot = self.runConfig.hasrobot
        if not hasrobot :
            ftlog.debug('this room has no robot !', self.tableId)
            return 0
        maxCount = self.room.roomConf.get('robotUserMaxCount', -1)
        curCount = -1
        if maxCount > 0 :
            curCount = self.room.getRoomRobotUserCount()
        ftlog.debug('check robot user count curCount=', curCount, 'maxCount=', maxCount, self.tableId)
        if maxCount > 0 and curCount >= maxCount :
            ftlog.debug('robot user reach max count !', curCount, maxCount, self.tableId)
            return 0
        return 1

