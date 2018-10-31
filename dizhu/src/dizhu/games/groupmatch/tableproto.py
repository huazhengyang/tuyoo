# -*- coding:utf-8 -*-
'''
Created on 2017年2月17日

@author: zhaojiangang
'''
import functools
import time

from dizhu.entity import dizhuconf, dizhu_util
from dizhu.entity import dizhuhallinfo
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.games.tablecommonproto import DizhuTableProtoCommonBase
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import sessiondata
from poker.entity.game.rooms.group_match_ctrl.const import AnimationType, \
    StageType
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.util import strutil


class DizhuTableProtoGroupMatch(DizhuTableProtoCommonBase):
    WINLOSE_SLEEP = 2
    
    def __init__(self, tableCtrl):
        super(DizhuTableProtoGroupMatch, self).__init__(tableCtrl)
        
    def getMatchTableInfo(self, seat, mo):
        mo.setResult('hasEnterRewards', seat.player.hasEnterRewards)
        matchTableInfo = self.table.matchTableInfo
        mo.setResult('mnotes', matchTableInfo['mnotes'])
        mo.setResult('mInfos', matchTableInfo['mInfos'])
        mo.setResult('step', {
                        'name':matchTableInfo['step']['name'],
                        'des':'%s人参赛，%s人晋级' % (matchTableInfo['step']['playerCount'],
                                                matchTableInfo['step']['riseCount']),
                        'playerCount':matchTableInfo['step']['playerCount'],
                        'note':self.buildNote(seat)
                    })
        
    def buildTableInfoResp(self, seat, isRobot):
        mp = super(DizhuTableProtoGroupMatch, self).buildTableInfoResp(seat, isRobot)
        # 分渠道名称展示
        try:
            clientId = sessiondata.getClientId(seat.userId)
            mp.setResult('roomName', dizhuhallinfo.getMatchSessionName(DIZHU_GAMEID, clientId, self.bigRoomId))
        except:
            pass
        self.getMatchTableInfo(seat, mp)
        return mp
    
    def buildSeatInfo(self, forSeat, seat):
        seatInfo = super(DizhuTableProtoGroupMatch, self).buildSeatInfo(forSeat, seat)
        seatInfo['mscore'], seatInfo['mrank'] = (seat.player.score, seat.player.rank) if seat.player else (0, 0)
        return seatInfo
    
    def sendWinloseRes(self, result):
        mp = self.buildTableMsgRes('table_call', 'game_win')
        mp.setResult('isMatch', 1)
        mp.setResult('stat', self.buildTableStatusInfo())
        mp.setResult('slam', 0)
        mp.setResult('dizhuwin', 1 if result.isDizhuWin() else 0)

        stageRewards = self._sendStageReward(result)
        if stageRewards:
            mp.setResult('stageRewards', stageRewards)

        if not result.gameRound.dizhuSeat:
            mp.setResult('nowin', 1)
        mp.setResult('cards', [seat.status.cards for seat in self.table.seats])
        for sst in result.seatStatements:
            mrank = 3
            mtableRanking = 3
            mp.setResult('seat' + str(sst.seat.seatId),
                         [
                            sst.delta,
                            sst.final,
                            0, 0, 0, 0,
                            mrank,
                            mtableRanking
                         ])
        self.sendToAllSeat(mp)

    def _do_table_manage__m_table_start(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._do_table_manage__m_table_start',
                        'msg=', msg)
        
        startTime = int(time.time())
        tableInfo = msg.getKey('params')
        
        ret = self.tableCtrl.startMatchTable(tableInfo)
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._do_table_manage__m_table_start',
                        'msg=', msg,
                        'ret=', ret,
                        'used=', int(time.time()) - startTime)
    
    def _do_table_manage__m_table_clear(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch.doMatchTableClear',
                        'msg=', msg)
        params = msg.getKey('params')
        matchId = params.get('matchId', -1)
        ccrc = params.get('ccrc', -1)
        self.tableCtrl.clearMatchTable(matchId, ccrc)
    
    def buildMatchStepInfo(self, seat):
        return {
            'curCount':seat.player.matchUserInfo['cardCount'],
            'totoal':self.table.matchTableInfo['step']['cardCount']
        }
    
    def getAnimationType(self, table, clientVer):
        try:
            if clientVer < 3.37:
                return AnimationType.UNKNOWN
            if clientVer < 3.77:
                # 小于3.77版本的还是每一个阶段只播一次
                return table.matchTableInfo['step']['animationType']
            # >=3.77版本动画每次都播放
            rawAnimationTypeInfo = table.matchTableInfo['step']['rawAnimationType']
            return rawAnimationTypeInfo['type']
        except:
            return table.matchTableInfo['step']['animationType']
    
    def getAnimationInter(self, animationType, isStartStep, clientVer):
        if clientVer < 3.77:
            return self.MSTART_SLEEP
        
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        if not delayConf:
            if isStartStep:
                return 5
            return 3
        valKey = 'startStep'
        if not isStartStep:
            valKey = 'type' + str(animationType)
        return delayConf.get(valKey, 3)
    
    def playAnimationIfNeed(self, table):
        ret = {'playAnimation':False, 'delaySeconds':0}
        for seat in table.seats:
            if not seat.player:
                continue
            animationType = self.getAnimationType(table, seat.player.gameClientVer)
            if animationType != AnimationType.UNKNOWN:
                msg = MsgPack()
                msg.setCmd('m_play_animation')
                msg.setResult('gameId', table.gameId)
                msg.setResult('roomId', table.roomId)
                msg.setResult('tableId', table.tableId)
                msg.setResult('type', animationType)
                mnotes = table.matchTableInfo['mnotes']
                isStartStep = mnotes.get('isStartStep', False)
                # 添加是否是第一个阶段的标志，是的话前端播放开始比赛的动画
                msg.setResult('isStartStep', isStartStep)
                # 组织当前比赛是第几局、共几局的信息
                msg.setResult('curMatchStep', self.buildMatchStepInfo(seat))
                self.sendToSeat(msg, seat)
                
                curDelay = self.getAnimationInter(animationType, isStartStep, seat.player.gameClientVer)
                if curDelay > ret['delaySeconds']:
                    ret['delaySeconds'] = curDelay
                ret['playAnimation'] = True
        return ret
    
    def buildNote(self, seat):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        tableInfo = self.table.matchTableInfo
        if tableInfo['step']['type'] == StageType.ASS:
            return u'%s：%s人晋级，低于%s分将被淘汰' % (tableInfo['step']['name'],
                                                tableInfo['step']['riseCount'],
                                                tableInfo['mInfos']['asslosechip'])
        else:
            return u'%s：%s人晋级，第%s副（共%s副）' % (tableInfo['step']['name'],
                                                tableInfo['step']['riseCount'],
                                                seat.player.matchUserInfo['cardCount'],
                                                tableInfo['step']['cardCount'])
        return ''
    
    def sendRank(self, seat):
        _, clientVer, clientChannel = strutil.parseClientId(seat.player.clientId)
        ranks = self.table.matchTableInfo['ranks']
        if not ranks:
            ftlog.warn('DizhuTableProtoGroupMatch.sendRank',
                       'userId=', seat.userId,
                       'TODO the _match_table_info[\'ranks\'] is empty why !!')
            return
        mp = MsgPack()
        mp.setCmd('m_rank')
        if clientVer >= 3.37:
            ranktops = []
            ranktops.append({
                'userId':seat.userId,
                'name':seat.player.matchUserInfo['userName'],
                'score':seat.player.matchUserInfo['score'],
                'rank':seat.player.matchUserInfo['chiprank']
            })
            for i, r in enumerate(ranks):
                ranktops.append({'userId':r[0], 'name':str(r[1]), 'score':r[2], 'rank':i + 1})
            if "momo" in clientChannel: # 解决 momo3.372客户端bug:等待页面JS错误
                for _ in xrange(i+1, 10):
                    ranktops.append({'userId':0, 'name':"", 'score':"", 'rank':0})
            mp.setResult('mranks', ranktops)
        else:
            ranktops = []
            for r in ranks:
                ranktops.append((r[0], r[1], r[2]))
            mp.setResult('mranks', ranktops)
        self.sendToSeat(mp, seat)
        
    def sendMNoteMsg(self, noteInfos):
        for seat, userId, note in noteInfos:
            if seat.userId == userId:
                mp = MsgPack()
                mp.setCmd('m_note')
                mp.setResult('note', note)
                self.sendToSeat(mp, seat)

    def _onSitdown(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._onSitdown',
                        'tableId=', event.table.tableId,
                        'seatId=', event.seat.seatId,
                        'userId=', event.seat.userId)
        
        self.sendQuickStartRes(event.seat, True, TYRoom.ENTER_ROOM_REASON_OK)
        if event.table.idleSeatCount == 0:
            # 所有人都坐下后发tableInfo
            self.sendTableInfoResAll()
            
            # 延迟1秒进行animation Info相关处理
            FTTasklet.getCurrentFTTasklet().sleepNb(1)
    
            playAnmi = self.playAnimationIfNeed(event.table)
            
            if playAnmi['playAnimation'] and playAnmi['delaySeconds'] > 0:
                FTTasklet.getCurrentFTTasklet().sleepNb(playAnmi['delaySeconds'])

        self.sendRobotNotifyCallUp(None)
    
    def _onGameReady(self, event):
        super(DizhuTableProtoGroupMatch, self)._onGameReady(event)
        matchTableInfo = event.table.matchTableInfo
        mnotes = matchTableInfo['mnotes']
        mtype = mnotes['type']
        isFinalStep = mnotes.get('isFinalStep', False)
        if isFinalStep:
            mtype = mtype + u',决胜局！'
        isStartStep = mnotes.get('isStartStep', False)
         
        if isStartStep:
            noteInfos = []
            for seat in event.table.seats:
                _, clientVer, _ = strutil.parseClientId(seat.player.clientId)
                if clientVer < 3.37:
                    mn = MsgPack()
                    mn.setCmd('m_note')
                    mn.setResult('note', mtype)
                    mn.setResult('mInfos', matchTableInfo['mInfos'])
                    self.sendToSeat(mn, seat)
                    mnotes = matchTableInfo['mnotes']
                    bscore = mnotes.get('basescore', '')
                    step = mnotes.get('step', '')
                    note = bscore + u',' + step
                else:
                    note = self.buildNote(seat)
                    mn = MsgPack()
                    mn.setCmd('m_note')
                    mn.setResult('note', note)
                    mn.setResult('mInfos', matchTableInfo['mInfos'])
                    self.sendToSeat(mn, seat)
                noteInfos.append((seat, seat.userId, note))
            func = functools.partial(self.sendMNoteMsg, noteInfos)
            FTTimer(3, func)
        
        for seat in event.table.seats:
            self.sendRank(seat)
    
    def _sendWinloseToMatch(self, result):
        # 发送给match manager
        users = []
        for sst in result.seatStatements:
            user = {}
            user['userId'] = sst.seat.userId
            user['deltaScore'] = sst.delta
            user['seatId'] = sst.seat.seatId
            user['isTuoguan'] = sst.seat.status.isTuoguan
            user['winloseForTuoguanCount'] = sst.seat.player.winloseForTuoguanCount
            user['stageRewardTotal'] = sst.seat.player.stageRewardTotal
            users.append(user)

        mp = MsgPack()
        mp.setCmd('room')
        mp.setParam('action', 'm_winlose')
        mp.setParam('gameId', self.gameId)
        mp.setParam('matchId', self.room.bigmatchId)
        mp.setParam('roomId', self.room.ctrlRoomId)
        mp.setParam('tableId', self.tableId)
        mp.setParam('users', users)
        mp.setParam('ccrc', self.table.matchTableInfo['ccrc'])

        if ftlog.is_debug():
            ftlog.debug('groupMatch._sendWinloseToMatch users=', users)
        
        if self.WINLOSE_SLEEP > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(self.WINLOSE_SLEEP)
        
        router.sendRoomServer(mp, self.room.ctrlRoomId)
        
    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'event=', event,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseRes(event.gameResult)
        self._sendWinloseToMatch(event.gameResult)

    def _sendStageReward(self, result):
        # 各个阶段发阶段奖励
        rewardList = []
        stageRewards = self.room.roomConf['matchConf'].get('stageRewards', {})
        for sst in result.seatStatements:
            userId = sst.seat.userId

            stageindex = self.table.matchTableInfo.get('step', {}).get('stageIndex', 0) + 1
            stageReward = stageRewards.get(str(self.table.room.bigmatchId), {}).get(str(stageindex), [])

            currStageReward = []
            try:
                sstIsDizhu = 'dizhu' if sst.isDizhu else 'nongmin'
                for rewardIndex in range(len(stageReward)):
                    currStageReward.append(
                        {
                            "count": stageReward[rewardIndex].get('count', {}).get(sstIsDizhu, 0),
                            "itemId": stageReward[rewardIndex]['itemId']
                        })
            except Exception, e:
                ftlog.warn('group.stageRewards.info userId=', userId, 'err=', e)

            deltaScore = sst.delta if not sst.seat.isGiveup else -9999999
            clientVer = SessionDizhuVersion.getVersionNumber(userId)

            if ftlog.is_debug():
                ftlog.debug('group.stageRewards.info userId=', userId,
                            'index=', stageindex,
                            'score=', deltaScore,
                            'ver=', clientVer,
                            'reward=', currStageReward,
                            'stageRewardTotal=', sst.seat.player.stageRewardTotal)

            if not currStageReward or deltaScore < 0 or clientVer < 3.90:
                rewardList.append(None)
                continue

            contentItems = TYContentItem.decodeList(currStageReward)
            assetList = dizhu_util.sendRewardItems(userId, contentItems, '', 'DIZHU_STAGE_REWARD', 0)
            clientAssetList = []
            for atp in assetList:
                clientAsset = {"name": atp[0].displayName, "itemId": atp[0].kindId, "count": atp[1]}
                clientAssetList.append(clientAsset)
                sst.seat.player.stageRewardTotal += atp[1]
            rewardList.append(clientAssetList)

            ftlog.info('group.stageRewards.info userId=', userId,
                       'deltaScore=', deltaScore,
                       'stageRewardTotal=', sst.seat.player.stageRewardTotal,
                       'index=', stageindex,
                       'assetList=', [(atp[0].kindId, atp[1]) for atp in assetList],
                       'seatId=', sst.seat.seatId)

        return rewardList

    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseAbortRes(event.gameResult)
        self._sendWinloseToMatch(event.gameResult)

    def sendTableInfoRes(self, seat):
        logUserIds = [66706022]
        if seat.player and seat.userId in logUserIds:
            ftlog.info('DizhuTableProtoGroupMatch.sendTableInfoRes beforeSentMsg',
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
                ftlog.info('DizhuTableProtoGroupMatch.sendTableInfoRes sentMsg',
                           'tableId=', self.tableId,
                           'userId=', seat.userId,
                           'gameClientVer=', seat.player.gameClientVer,
                           'seats=', [(seat.userId, seat.seatId) for seat in self.table.seats],
                           'mp=', mp.pack())


