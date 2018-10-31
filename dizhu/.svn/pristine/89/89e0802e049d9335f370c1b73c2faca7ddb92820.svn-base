# -*- coding:utf-8 -*-
'''
Created on 2016年1月21日

@author: zhaojiangang
'''
import functools
from sre_compile import isstring
import time

from dizhu.gametable.dizhu_group_match_sender import DizhuGroupMatchSender
from dizhu.gametable.dizhu_table import DizhuTable
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
from poker.entity.dao import sessiondata, onlinedata
from poker.entity.game.rooms.group_match_ctrl.const import StageType, \
    AnimationType
from poker.entity.game.rooms.group_match_ctrl.utils import Logger
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from dizhu.entity import dizhuconf
from freetime.util import log as ftlog

class DizhuGroupMatchTable(DizhuTable):
    MSTART_SLEEP = 3
    def __init__(self, room, tableId):
        super(DizhuGroupMatchTable, self).__init__(room, tableId)
        self._match_table_info = None
        self.gamePlay.sender = DizhuGroupMatchSender(self)
        self._doMatchTableClear()
        
        self._logger = Logger()
        self._logger.add('gameId', self.gameId)
        self._logger.add('roomId', room.roomId)
        self._logger.add('tableId', tableId)
        self._logger.add('matchId', room.bigmatchId)

    def _doTableManage(self, msg, action):
        '''
        处理来自大比赛的table_manage命令
        '''
        if action == 'm_table_start' :
            self.doMatchTableStart(msg)
            return

        if action == 'm_table_info' :
            self.doUpdateMatchTableInfo(msg)
            return

        if action == 'm_table_clear' :
            self.doMatchTableClear(msg)
            return

    def _checkMNotes(self, mnotes):
        if not isinstance(mnotes, dict):
            self._logger.error('GameTable._checkMNotes',
                               'err=', 'matchTableInfo.mnotes must be dict')
            return False
        
        keyTypeList = [('basescore', (str, unicode)),
               ('type', (str, unicode)),
               ('step', (str, unicode)),
               ('isStartStep', (bool)),
               ('isFinalStep', (bool)),
               ('startTime', (str, unicode))]
        for k, t in keyTypeList:
            v = mnotes.get(k, None)
            if not isinstance(v, t):
                self._logger.error('GameTable._checkMNotes',
                                   'err=', 'matchTableInfo.%s must be %s' % (k, t))
                return False
        return True
    
    def _checkSeatInfos(self, seatInfos):
        if not isinstance(seatInfos, list):
            self._logger.error('GameTable._checkSeatInfos', 
                               'err=', 'matchTableInfo.seats must be list')
            return False
        if len(seatInfos) != len(self.seats):
            self._logger.error('GameTable._checkSeatInfos',
                               'seatCount', len(self.seats), 
                               'seatInfoCount=', len(seatInfos),
                               'err=', 'BadSeatInfoCount')
            return False
        for seatInfo in seatInfos:
            if not isinstance(seatInfo, dict):
                self._logger.error('GameTable._checkSeatInfos',
                                   'err=', 'seats.item must be dict')
                return False
            
            userId = seatInfo.get('userId')
            cardCount = seatInfo.get('cardCount')
            if not isinstance(userId, int):
                self._logger.error('GameTable._checkSeatInfos',
                                   'err=', 'seats.item.userId must be int')
                return False
            if not isinstance(cardCount, int):
                self._logger.error('GameTable._checkSeatInfos',
                                   'err=', 'seats.item.cardCount must be int')
                return False
        return True
    
    def _checkMInfos(self, mInfos):
        if not isinstance(mInfos, dict):
            self._logger.error('GameTable._checkMInfos',
                               'err=', 'matchTableInfo.mInfos must be dict')
            return False
        return True
    
    def _checkRanks(self, ranks):
        if not isinstance(ranks, list):
            self._logger.error('GameTable._checkRanks',
                               'err=', 'matchTableInfo.ranks must be list')
            return False
        return True
    
    def _checkStepInfo(self, stepInfo):
        if not isinstance(stepInfo, dict):
            self._logger.error('GameTable._checkStepInfo',
                               'err=', 'matchTableInfo.step must be dict')
            return False
        name = stepInfo.get('name')
        playerCount = stepInfo.get('playerCount')
        riseCount = stepInfo.get('riseCount')
        cardCount = stepInfo.get('cardCount')
        if not isstring(name):
            self._logger.error('GameTable._checkStepInfo',
                               'err=', 'matchTableInfo.step.name must be str')
            return False
        if not isinstance(playerCount, int):
            self._logger.error('GameTable._checkStepInfo',
                               'err=', 'matchTableInfo.step.playerCount must be int')
            return False
        if not isinstance(riseCount, int):
            self._logger.error('GameTable._checkStepInfo',
                               'err=', 'matchTableInfo.step.riseCount must be int')
            return False
        if not isinstance(cardCount, int):
            self._logger.error('GameTable._checkStepInfo',
                               'err=', 'matchTableInfo.step.cardCount must be int')
            return False
        return True
    
    def _getUserIdsFromTableInfo(self, tableInfo):
        userIds = []
        for seatInfo in tableInfo['seats']:
            userIds.append(seatInfo['userId'])
        return userIds
        
    def _checkMatchTableInfo(self, tableInfo):
        return True
        
        if not isinstance(tableInfo, dict):
            self._logger.error('GameTable._checkMatchTableInfo',
                               'err=', 'matchTableInfo must be dict')
            return False
        roomId = tableInfo.get('roomId')
        tableId = tableInfo.get('tableId')
        matchId = tableInfo.get('matchId')
        if self.roomId != roomId or self.tableId != tableId or self.room.bigmatchId != matchId:
            self._logger.error('GameTable._checkMatchTableInfo',
                               'roomIdParam=', roomId,
                               'tableIdParam=', tableId,
                               'matchIdParam=', matchId,
                               'err=', 'diff roomId or tableId or bigmatchId')
            return False
        
        ccrc = tableInfo.get('ccrc')
        if not isinstance(ccrc, int):
            self._logger.error('GameTable._checkMatchTableInfo',
                               'err=', 'ccrc must be int')
            return False
        
        mnotes = tableInfo.get('mnotes')
        if not self._checkMNotes(mnotes):
            return False
        
        seatInfos = tableInfo.get('seats')
        if not self._checkSeatInfos(seatInfos):
            return False
            
        mInfos = tableInfo.get('mInfos')
        if not self._checkMInfos(mInfos):
            return False
    
        ranks = tableInfo.get('ranks')
        if not self._checkRanks(ranks):
            return False
        return True
    
        step = tableInfo.get('step')
        if not self._checkStepInfo(step):
            return False
        return True
    
    def doMatchTableStart(self, msg):
        if self._logger.isDebug():
            self._logger.debug('GameTable.doMatchTableStart',
                               'msg=', msg)
        startTime = int(time.time())
        table_info = msg.getKey('params')
        if self._checkMatchTableInfo(table_info):
            self._doUpdateTableInfo(table_info)
            self._doMatchQuickStart()
        if self._logger.isDebug():
            self._logger.debug('GameTable.doMatchTableStart',
                               'msg=', msg,
                               'used=', int(time.time()) - startTime)
            
    def doUpdateMatchTableInfo(self, msg):
        if self._logger.isDebug():
            self._logger.debug('GameTable.doUpdateMatchTableInfo',
                               'msg=', msg)
        table_info = msg.getKey('params')
        if not self._checkMatchTableInfo(table_info):
            return
        if (self._match_table_info
            and self._match_table_info['ccrc'] != table_info['ccrc']):
            self._logger.error('GameTable.doUpdateMatchTableInfo',
                               'msg=', msg,
                               'ccrc=', self._match_table_info['ccrc'],
                               'ccrcParam=', table_info['ccrc'],
                               'err=', 'diff ccrc')
            return
        self._doUpdateTableInfo(table_info)
        for seatInfo in table_info['seats']:
            clientVer = sessiondata.getClientIdVer(seatInfo['userId'])
            mnotes = self._match_table_info.get('mnotes', {})
            if clientVer < 3.37:
                mn = MsgPack()
                mn.setCmd('m_note')
                mn.setResult('note', mnotes.get('incrnote'))
                mn.setResult('basescore', mnotes.get('basescore'))
                mn.setResult('mInfos', self._match_table_info.get('mInfos', {}))
                router.sendToUser(mn, seatInfo['userId'])
            else:
                mn = MsgPack()
                mn.setCmd('m_note')
                mn.setResult('note', self._buildNote(seatInfo['userId'], table_info))
                mn.setResult('basescore', mnotes.get('basescore'))
                mn.setResult('mInfos', table_info.get('mInfos', {}))
                router.sendToUser(mn, seatInfo['userId'])
 
    def doMatchTableClear(self, msg):
        if self._logger.isDebug():
            self._logger.debug('GameTable.doMatchTableClear',
                               'msg=', msg)
        params = msg.getKey('params')
        matchId = params.get('matchId', -1)
        ccrc = params.get('ccrc', -1)
        if matchId != self.room.bigmatchId:
            self._logger.error('GameTable.doMatchTableClear',
                               'msg=', msg,
                               'err=', 'DiffMatchId')
            return
         
        if not self._match_table_info:
            self._logger.error('GameTable.doMatchTableClear',
                               'msg=', msg,
                               'err=', 'table match is clear')
            return
         
        if ccrc != self._match_table_info['ccrc']:
            self._logger.error('GameTable.doMatchTableClear',
                               'msg=', msg,
                               'ccrc=', self._match_table_info['ccrc'],
                               'err=', 'diff ccrc')
            return
         
        self._doMatchTableClear()
     
    def _doMatchTableClear(self):
        for seatIndex in xrange(len(self.seats)):
            uid = self.seats[seatIndex].userId
            if uid > 0:
                clientId = sessiondata.getClientId(uid)
                #比赛阶段清理牌桌时无需刷新客户端
                self.gamePlay.doStandUp(uid, seatIndex+1, TYRoom.LEAVE_ROOM_REASON_MATCH_END, clientId)
        self.clear(None)
        self._time_stamp = 0
        self._match_table_info = None
  
  
    def _doSit(self, msg, userId, seatId, clientId): 
        '''
        大比赛牌桌只有玩家断线重连时才会触发坐下操作，既重新坐回牌桌
        '''
        super(DizhuGroupMatchTable, self)._doSit(msg, userId, seatId, clientId)
        self._sendRank(userId)


    def _doUpdateTableInfo(self, tableInfo):
        self._time_stamp = time.time()
        self._match_table_info = tableInfo

         
    def _doMatchQuickStart(self):
        tableInfo = self._match_table_info
        
        seatInfos = tableInfo['seats']
        userIds = []
        userSeatList = []
         
        for x in xrange(len(seatInfos)) :
            this_seat = self.seats[x]
            userIds.append(seatInfos[x]['userId'])
            this_seat.userId = seatInfos[x]['userId']
            this_seat.state = TYSeat.SEAT_STATE_WAIT
            this_seat.call123 = -1
            userSeatList.append((seatInfos[x]['userId'], x + 1))
        
        # 初始化用户数据
        for x in xrange(len(self.players)):
            self.players[x].initUser(0, 1)

#         ctrlRoomId = self.room.ctrlRoomId
#         ctrlRoomTableId = ctrlRoomId * 10000
        for userId, seatId in userSeatList:
            try:
                onlinedata.setBigRoomOnlineLoc(userId, self.roomId, self.tableId, seatId)
#                 onlinedata.removeOnlineLoc(userId, ctrlRoomId, ctrlRoomTableId)
#                 onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
                if self._logger.isDebug():
                    self._logger.debug('GameTable._doMatchQuickStart setBigRoomOnlineLoc',
                                       'userId=', userId,
                                       'tableId=', self.tableId,
                                       'seatId=', seatId)
            except:
                self._logger.error('GameTable._doMatchQuickStart')

        # 增加从比赛等待界面到下一局开始时的时间间隔
        inter = self.__getWaitToNextMatchInter()
        ftlog.debug("test __getWaitToNextMatchInter inter = ", inter, 'time = ', time.time(), caller=self)
        if inter > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(inter)
        ftlog.debug("test __getWaitToNextMatchInter inter 2 = ", inter, 'time = ', time.time(), caller=self)
        
        for x in xrange(len(self.seats)) :
            this_seat = self.seats[x]
            if this_seat.userId > 0:
                mq = MsgPack()
                mq.setCmd('quick_start')
                mq.setResult('userId', this_seat.userId)
                mq.setResult('gameId', self.gameId)
                mq.setResult('roomId', self.roomId)
                mq.setResult('tableId', self.tableId)
                mq.setResult('seatId', x + 1)
                # 发送用户的quick_start
                router.sendToUser(mq, this_seat.userId)
         
        # 发送table_info
        self.gamePlay.sender.sendTableInfoResAll()

        # 延迟1秒进行animation Info相关处理
        FTTasklet.getCurrentFTTasklet().sleepNb(1)

        playAnmi = self._playAnimationIfNeed(tableInfo)
        
        if playAnmi['playAnimation'] and playAnmi['delaySeconds'] > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(playAnmi['delaySeconds'])
                
        for x in xrange(len(self.players)):
            self.gamePlay.doReady(self.players[x], False)
         
        mnotes = self._match_table_info['mnotes']
        mtype = mnotes['type']
        isFinalStep = mnotes.get('isFinalStep', False)
        if isFinalStep:
            mtype = mtype + u',决胜局！'
        isStartStep = mnotes.get('isStartStep', False)
         
        if isStartStep:
            for userId in userIds:
                clientVer = sessiondata.getClientId(userId)
                if clientVer < 3.37:
                    mn = MsgPack()
                    mn.setCmd('m_note')
                    mn.setResult('note', mtype)
                    mn.setResult('mInfos', self._match_table_info['mInfos'])
                    router.sendToUser(mn, userId)
                else:
                    mn = MsgPack()
                    mn.setCmd('m_note')
                    mn.setResult('note', self._buildNote(userId, tableInfo))
                    mn.setResult('mInfos', self._match_table_info['mInfos'])
                    router.sendToUser(mn, userId)
            bscore = mnotes.get('basescore', '')
            step = mnotes.get('step', '')
            note = bscore + u',' + step
            
            func = functools.partial(self.sendMNoteMsg, userIds, note)
            FTTimer(3, func)
         
        for userId in userIds:
            self._sendRank(userId)
             
    def sendMNoteMsg(self, userIds, note):
        if self._match_table_info:
            for userId in userIds:
                clientVer = sessiondata.getClientIdVer(userId)
                if clientVer < 3.37:
                    mnote = MsgPack()
                    mnote.setCmd('m_note')
                    mnote.setResult('note', note)
                    router.sendToUser(mnote, userId)
                else:
                    mnote = MsgPack()
                    mnote.setCmd('m_note')
                    mnote.setResult('note', self._buildNote(userId, self._match_table_info))
                    router.sendToUser(mnote, userId)

    def _buildNote(self, userId, tableInfo):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        if tableInfo['step']['type'] == StageType.ASS:
            return u'%s：%s人晋级，低于%s分将被淘汰' % (tableInfo['step']['name'],
                                          tableInfo['step']['riseCount'],
                                          tableInfo['mInfos']['asslosechip'])
        else:
            for seatInfo in tableInfo['seats']:
                if seatInfo['userId'] == userId:
                    return u'%s：%s人晋级，第%s副（共%s副）' % (tableInfo['step']['name'],
                                          tableInfo['step']['riseCount'],
                                          seatInfo['cardCount'],
                                          tableInfo['step']['cardCount'])
        return ''
    
    def _buildMatchStepInfo(self, userId, tableInfo):
        res = {'curCount':-1, 'totoal':-1}
        for seatInfo in tableInfo['seats']:
            if seatInfo['userId'] == userId:
                res['curCount'] = seatInfo['cardCount']
                res['totoal'] = tableInfo['step']['cardCount']
        return res
    
    def _playAnimationIfNeed(self, tableInfo):
        ret = {'playAnimation':False, 'delaySeconds':0}
#         if self._match_table_info['step']['animationType'] != AnimationType.UNKNOWN:
        for x in xrange(len(self.seats)) :
            this_seat = self.seats[x]
            if this_seat.userId > 0:
                clientVer = sessiondata.getClientIdVer(this_seat.userId)
                animationType = self.__getAnimationType(clientVer)
                if animationType != AnimationType.UNKNOWN:
                    msg = MsgPack()
                    msg.setCmd('m_play_animation')
                    msg.setResult('gameId', self.gameId)
                    msg.setResult('roomId', self.roomId)
                    msg.setResult('tableId', self.tableId)
#                     msg.setResult('type', self._match_table_info['step']['animationType'])
                    msg.setResult('type', animationType)
                    mnotes = self._match_table_info['mnotes']
                    isStartStep = mnotes.get('isStartStep', False)
                    # 添加是否是第一个阶段的标志，是的话前端播放开始比赛的动画
                    msg.setResult('isStartStep', isStartStep)
                    # 组织当前比赛是第几局、共几局的信息
                    msg.setResult('curMatchStep', self._buildMatchStepInfo(this_seat.userId, tableInfo))
                    router.sendToUser(msg, this_seat.userId)
                        
                    curDelay = self.__getAnimationInter(animationType, isStartStep, clientVer)
                    if curDelay > ret['delaySeconds']:
                        ret['delaySeconds'] = curDelay
                    ret['playAnimation'] = True
        return ret
    
    def __getAnimationType(self, clientVer):
        try:
            if clientVer < 3.37:
                return AnimationType.UNKNOWN
            if clientVer < 3.77:
                # 小于3.77版本的还是每一个阶段只播一次
                return self._match_table_info['step']['animationType']
            # >=3.77版本动画每次都播放
            rawAnimationTypeInfo = self._match_table_info['step']['rawAnimationType']
#             if rawAnimationTypeInfo['type']==AnimationType.VS and rawAnimationTypeInfo['totalCardCount']>0:
#                 return self._match_table_info['step']['animationType']
            return rawAnimationTypeInfo['type']
        except:
            return self._match_table_info['step']['animationType']

    def __getWaitToNextMatchInter(self):
        mnotes = self._match_table_info['mnotes']
        isStartStep = mnotes.get('isStartStep', False)
        if isStartStep:
            # 第一个阶段不做延迟
            return 0
        
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        return delayConf.get('waitToNextMatch', 3)
    
    def __getAnimationInter(self, AnimationType, isStartStep, clientVer):
        
        if str(clientVer)<3.77:
            return self.MSTART_SLEEP
        
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        if not delayConf:
            if isStartStep:
                return 5
            return 3
        valKey = 'startStep'
        if not isStartStep:
            valKey = 'type'+str(AnimationType)
        return delayConf.get(valKey, 3)
    
    def _findMatchSeatInfoByUserId(self, userId):
        if self._match_table_info:
            for seatInfo in self._match_table_info['seats']:
                if seatInfo['userId'] == userId:
                    return seatInfo
        return None
     
    def _sendRank(self, userId):
        _, clientVer, clientChannel, _ = sessiondata.getClientIdInfo(userId)
        ranks = self._match_table_info['ranks']
        if not ranks:
            self._logger.warn('GameTable._sendRank',
                              'TODO the _match_table_info[\'ranks\'] is empty why !!')
            return
        mrank = MsgPack()
        mrank.setCmd('m_rank')
        if clientVer >= 3.37:
            seatInfo = self._findMatchSeatInfoByUserId(userId)
            ranktops = []
            if seatInfo:
                ranktops.append({'userId':userId,
                                 'name':seatInfo['userName'],
                                 'score':seatInfo['score'],
                                 'rank':seatInfo['chiprank']})
            for i, r in enumerate(ranks):
                ranktops.append({'userId':r[0], 'name':str(r[1]), 'score':r[2], 'rank':i + 1})
            if "momo" in clientChannel: # 解决 momo3.372客户端bug:等待页面JS错误
                for _ in xrange(i+1, 10):
                    ranktops.append({'userId':0, 'name':"", 'score':"", 'rank':0})
            mrank.setResult('mranks', ranktops)
        else:
            ranktops = []
            for r in ranks:
                ranktops.append((r[0], r[1], r[2]))
            mrank.setResult('mranks', ranktops)
        router.sendToUser(mrank, userId)


