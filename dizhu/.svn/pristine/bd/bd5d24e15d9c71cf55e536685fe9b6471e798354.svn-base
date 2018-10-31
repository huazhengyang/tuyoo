# -*- coding:utf-8 -*-
'''
Created on 2014年9月17日

@author: zjgzzz@126.com
'''
from datetime import datetime
import time
import json

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import datachangenotify
from poker.entity.biz import bireport
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import userchip, sessiondata, userdata, daobase
from poker.entity.game.rooms.big_match_ctrl.config import MatchFee
from poker.entity.game.rooms.big_match_ctrl.const import StageType, \
    MatchFinishReason, AnimationType, WaitReason
from poker.entity.game.rooms.big_match_ctrl.exceptions import \
    SigninFeeNotEnoughException
from poker.entity.game.rooms.big_match_ctrl.interfaces import TableController, \
    PlayerNotifier, PlayerLocation, SigninRecordDao, MatchRewards, MatchStatusDao, \
    SigninFee, UserInfoLoader, MatchStatus
from dizhu.entity.matchrecord import MatchRecord
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.protocol import router
from poker.util.strutil import parseClientId
from freetime.core import timer
from freetime.core.tasklet import FTTasklet
from hall.servers.util.rpc import user_remote, event_remote


def matchlog(*args):
    ftlog.info(*args)

def getMatchGroupStepInfos(group, table):
    infoscores = []
    inforanks = []
    cardCount = 0
    for seat in table.seats:
        if seat.player:
            infoscores.append(seat.player.chip)
            inforanks.append(seat.player.rank)
            cardCount += seat.player.cardCount
        else:
            infoscores.append(0)
            inforanks.append(0)
    cardCount = cardCount / len(table.seats)
    step = u'当前第%d阶段,第%d副' % (group.stage.index + 1, cardCount)
    stage = group.stage
    assLoseChip = stage.getLoseBetChip()
    if stage.conf.type == StageType.ASS :  # ASS 赛制
        mtype = u'ASS打立出局'
        upcount = stage.conf.riseUserCount
        outChip = stage.getAssLoseChip()
        bscore = u'底分:%d,低于%d将被淘汰' % (stage.getLoseBetChip(), stage.getAssLoseChip())
        outline = ['淘汰分:', str(outChip)]
        incrnote = u'底分增加到%d低于%d将被淘汰' % (stage.getLoseBetChip(), stage.getAssLoseChip())
        assLoseChip = stage.getAssLoseChip()
    else:  # 
        mtype = u'定局淘汰'
        upcount = group.stage.conf.riseUserCount
        bscore = u'底分:%d,%d人晋级' % (stage.getLoseBetChip(), upcount)
        outline = ['局数:', str(cardCount) + '/' + str(stage.conf.cardCount)]
        incrnote = u'底分增加到%d' % (stage.getLoseBetChip())

    isStartStep = (cardCount == 1 and stage.index == 0)
    isFinalStep = (cardCount == 1 and (not stage.hasNextStage()))

    mInfos = {'scores' : infoscores,  # 座位排序
              'rank' : inforanks,  # 名次
              'all' : len(group.rankList),  # 总人数
              'info' : [outline,
                        [ "晋级人数:", str(upcount)]
                        ],
              'basescore' : stage.getLoseBetChip(),
              'asslosechip' : assLoseChip,
              }
    return mtype, step, bscore, isStartStep, isFinalStep, incrnote, mInfos

def buildTableClearMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_clear')
    msg.setParam('gameId', table.gameId)
    msg.setParam('matchId', table.group.match.matchId)
    msg.setParam('roomId', table.roomId)
    msg.setParam('tableId', table.tableId)
    msg.setParam('ccrc', table.ccrc)
    return msg

def buildUserInfos(table):
    users = []
    for seat in table.seats:
        if seat.player:
            users.append({
                'userId':seat.player.userId,
                'seatId':seat.seatId,
                'rank':seat.player.rank
            })
    return users

def getUserIds(table):
    userIds = []
    for seat in table.seats:
        if seat.player:
            userIds.append(seat.player.userId)
        else:
            userIds.append(0)
    return userIds

def _buildTableInfoMessage(table, msg):
    msg.setParam('gameId', table.gameId)
    msg.setParam('matchId', table.group.match.matchId)
    msg.setParam('roomId', table.roomId)
    msg.setParam('tableId', table.tableId)
    msg.setParam('ccrc', table.ccrc)
    msg.setParam('stageType', table.stageType)
    if table.group:
        startTimeStr = datetime.fromtimestamp(table.group.startTime).strftime('%Y-%m-%d %H:%M')
        mtype, step, bscore, isStartStep, isFinalStep, incrnote, mInfos = getMatchGroupStepInfos(table.group, table)
        notes = {'basescore' : bscore, 'type' : mtype, 'step': step,
                 'isStartStep' : isStartStep, 'isFinalStep': isFinalStep,
                 'startTime': startTimeStr, 'incrnote':incrnote}
        
        msg.setParam('mnotes', notes)
        msg.setParam('mInfos', mInfos)
        msg.setParam('ranks', table.group._ranktops)
        
        seats = []
        totalCardCount = 0
        for seat in table.seats:
            if seat.player:
                totalCardCount += max(0, seat.player.cardCount - 1)
                seats.append({
                        'userId':seat.player.userId,
                        'cardCount':seat.player.cardCount,
                        'rank':seat.player.rank,
                        'chiprank':seat.player.chiprank,
                        'userName':seat.player.userName,
                        'score':seat.player.chip,
                    })
            else:
                seats.append({
                        'userId':0,
                        'cardCount':0,
                        'rank':0,
                        'chiprank':0,
                        'userName':'',
                        'score':0,
                    })
                
        animationType = table.group.stage.conf.animationType \
            if totalCardCount == 0 else AnimationType.UNKNOWN
        
        msg.setParam('seats', seats)
        msg.setParam('step', {
                        'name':table.group.groupName,
                        'type':table.group.stage.conf.type,
                        'playerCount':table.group.allPlayerCount,
                        'riseCount':min(table.group.stage.conf.riseUserCount, table.group.allPlayerCount),
                        'cardCount':table.group.stage.conf.cardCount,
                        'animationType':animationType,
                        # 3.77版本的要求VS之外的动画每次都播放，加入原始动画信息
                        'rawAnimationType': {'type':table.group.stage.conf.animationType,
                                             'totalCardCount':totalCardCount}
                    })
    return msg

def buildTableInfoMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_info')
    return _buildTableInfoMessage(table, msg)

def buildTableStartMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_start')
    return _buildTableInfoMessage(table, msg)

def buildLoserInfo(room, group, player):
    info = None
    if group.stage.conf.type == StageType.ASS:
        checkChip = group.stage.getAssLoseChip()
        if player.chip < checkChip:
            info = u'由于积分低于' + str(checkChip) + u',您已经被淘汰出局.请再接再厉,争取取得更好名次!'
    if info is None:
        info = u'比赛：%s\n名次：第%d名\n胜败乃兵家常事 大侠请重新来过！' % (room.roomConf["name"], player.rank)
    return info
    
def buildWinInfo(room, group, player, rankRewards):
    if rankRewards:
        return u'比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (room.roomConf["name"], player.rank, rankRewards.desc)
    return u'比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (room.roomConf["name"], player.rank)
    
class PlayerLocationDizhu(PlayerLocation):
    pass

class TableControllerDizhu(TableController):
    def startTable(self, table):
        '''
        让player在具体的游戏中坐到seat上
        '''
        try:
            matchlog('PlayerControllerImpl.startTable groupId=',
                     table.group.groupId, 'tableId=', table.tableId)
    
            # 发送tableStart
            message = buildTableStartMessage(table)
            router.sendTableServer(message, table.roomId)
        except:
            ftlog.error()
    
    def clearTable(self, table):
        '''
        清理桌子
        '''
        # 发送tableClear
        try:
            tableClearMessage = buildTableClearMessage(table)
            router.sendTableServer(tableClearMessage, table.roomId)
        except:
            ftlog.error()
    
    def updateTableInfo(self, table):
        '''
        桌子信息变化
        '''
        # 发送tableInfo
        try:
            tableInfoMessage = buildTableInfoMessage(table)
            router.sendTableServer(tableInfoMessage, table.roomId)
        except:
            ftlog.error()
    
    def userReconnect(self, table, seat):
        '''
        用户坐下
        '''
        try:
            msg = MsgPack()
            msg.setCmd('table_manage')
            msg.setParam('action', 'm_user_reconn')
            msg.setParam('gameId', table.gameId)
            msg.setParam('matchId', table.group.match.matchId)
            msg.setParam('roomId', table.roomId)
            msg.setParam('tableId', table.tableId)
            msg.setParam('userId', seat.player.userId)
            msg.setParam('seatId', seat.seatId)
            msg.setParam('ccrc', table.ccrc)
            router.sendTableServer(msg, table.roomId)
        except:
            ftlog.error()
        
class PlayerNotifierDizhu(PlayerNotifier):
    def __init__(self, room):
        self._room = room
    
    def notifyMatchCancelled(self, player, inst, reason, message=None):
        '''
        通知用户比赛由于reason取消了
        '''
        try:
            msg = MsgPack()
            msg.setCmd('m_over')
            msg.setResult('gameId', inst.match.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('reason', reason)
            msg.setResult('info', message or MatchFinishReason.toString(reason))
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
    
    def notifyMatchGiveupFailed(self, player, group, message):
        '''
        通知用户不能放弃比赛
        '''
        try:
            msg = MsgPack()
            msg.setCmd('room')
            msg.setError(-1, message)
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
            
    def notifyMatchOver(self, player, group, reason, rankRewards):
        '''
        通知用户比赛结束了
        '''
        try:
            if (reason == MatchFinishReason.USER_WIN
                or reason == MatchFinishReason.USER_LOSER):
                try:
                    event_remote.publishMatchWinloseEvent(self._room.gameId,
                                                            player.userId, 
                                                            self._room.match.matchId,
                                                            reason == MatchFinishReason.USER_WIN,
                                                            player.rank,
                                                            group.stage.matching.startPlayerCount,
                                                            rankRewards.conf if rankRewards else None)
                    from dizhu.entity.matchhistory import MatchHistoryHandler
                    MatchHistoryHandler.onMatchOver(player.userId,
                                                player.group.matchConf.recordId,
                                                player.rank,
                                                reason == MatchFinishReason.USER_WIN,
                                                rankRewards.conf if rankRewards else None,
                                                player.group.isGrouping)
                except:
                    ftlog.error()


                # 比赛记录保存
                try:
                    event = {'gameId':self._room.gameId,
                            'userId':player.userId,
                            'matchId':self._room.match.matchId,
                            'rank':player.rank,
                            'isGroup': 1 if player.group.isGrouping else 0}
                    MatchRecord.updateAndSaveRecord(event)

                except:
                    ftlog.error()

            msg = MsgPack()
            msg.setCmd('m_over')
            msg.setResult('gameId', group.match.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('userId', player.userId)
            msg.setResult('reason', reason)
            msg.setResult('rank', player.rank)
            try:
                msg.setResult('beatDownUser', player.beatDownUserName)
            except:
                ftlog.debug('NobeatDownUser big match')
                ftlog.exception()
                
            if rankRewards or reason == MatchFinishReason.USER_WIN:
                msg.setResult('info', buildWinInfo(self._room, group, player, rankRewards))
            else:
                msg.setResult('info', buildLoserInfo(self._room, group, player))
            
            msg.setResult('mucount', group.getStartPlayerCount())
            msg.setResult('date', str(datetime.now().date().today()))
            msg.setResult('time', time.strftime('%H:%M', time.localtime(time.time())))
            msg.setResult('addInfo', '')
            if rankRewards:
                from dizhu.bigmatch.match import BigMatch
                msg.setResult('reward', BigMatch.buildRewards(rankRewards))
                rewardDesc = BigMatch.buildRewardsDesc(rankRewards)
                if rewardDesc:
                    msg.setResult('rewardDesc', rewardDesc)
            msg.setResult('mname', self._room.roomConf["name"])

            record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
            if record:
                msg.setResult('mrecord', {'bestRank':record.bestRank,
                                         'bestRankDate':record.bestRankDate,
                                         'isGroup':record.isGroup,
                                         'crownCount':record.crownCount,
                                         'playCount':record.playCount})
            else:
                from dizhu.activities.toolbox import Tool
                msg.setResult('mrecord', {'bestRank':player.rank,
                                         'bestRankDate':Tool.datetimeToTimestamp(datetime.now()),
                                         'isGroup':1 if player.group.isGrouping else 0,
                                         'crownCount':1 if player.rank == 1 else 0,
                                         'playCount':1})

            router.sendToUser(msg, player.userId)

            if player.rank == 1 and self._room.roomConf.get('championLed'):
                ledtext = '玩家%s在斗地主"%s"中过五关斩六将夺得冠军，获得%s！' % (player.userName, self._room.roomConf['name'], rewardDesc)
                user_remote.sendHallLed(DIZHU_GAMEID, ledtext, 1, 'global', [])
            
            sequence = int(group._stage.instId.split('.')[1])
            self.report_bi_game_event("MATCH_FINISH", player.userId, group.match.matchId, 0, sequence, 0, 0, 0, [], 'match_end')#_stage.matchingId
        except:
            ftlog.error()
            
    def notifyMatchUpdate(self, player):
        '''
        通知比赛更新
        '''
        from dizhu.bigmatch.match import BigMatch
        try:
            msg = MsgPack()
            msg.setCmd('m_update')
            msg.setResult('_debug_user_%d_' % (1), player.userId)
            BigMatch.getMatchStates(self._room, player, msg)
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
    
    def __notifyMatchRank(self, player, group):
        msg = MsgPack()
        msg.setCmd('m_rank')
        ranktops = []
        for r in group._ranktops:
            ranktops.append((r[0], r[1], r[2]))
        msg.setResult('mranks', ranktops)
        router.sendToUser(msg, player.userId)
        
    def __notifyMatchRank2(self, player, group):
        msg = MsgPack()
        msg.setCmd('m_rank')
        ranktops = []
        ranktops.append({'userId':player.userId,
                         'name':player.userName,
                         'score':player.chip,
                         'rank':player.chiprank})
        for i, r in enumerate(group._ranktops):
            ranktops.append({'userId':r[0], 'name':r[1], 'score':r[2], 'rank':i+1})
        if "momo" in player.clientId: # 解决 momo3.372客户端bug:比赛等待页面JS错误
            for _ in xrange(len(ranktops), 10):
                ranktops.append({'userId':0, 'name':"", 'score':"", 'rank':0})
        msg.setResult('mranks', ranktops)
        router.sendToUser(msg, player.userId)
        
    def notifyMatchRank(self, player, group):
        '''
        通知比赛排行榜
        '''
        try:
            clientVer = parseClientId(player.clientId)[1]
            ftlog.debug('PlayerNotifierDizhu.notifyMatchRank userId=', player.userId,
                                  'clientId=', player.clientId,
                                  'groupId=', group.groupId)
            if clientVer >= 3.37:
                self.__notifyMatchRank2(player, group)
            else:
                self.__notifyMatchRank(player, group)
        except:
            ftlog.error()
    
    def __notifyMatchWait(self, player, group, step=None):
        self.notifyMatchUpdate(player)
        self.__notifyMatchRank(player, player.group)

        msg = MsgPack()
        msg.setCmd('m_wait')
        msg.setResult('gameId', group.match.gameId)
        msg.setResult('roomId', self._room.bigRoomId)
        msg.setResult('tableId', group.match.tableId)
        msg.setResult('mname', self._room.roomConf["name"])
        msg.setResult('riseCount', group.stage.conf.riseUserCount)
        if step != None:
            msg.setResult('step', 0)  # 0 - 请稍后  1- 晋级等待
        router.sendToUser(msg, player.userId)
            
    def __notifyMatchWait2(self, player, group, step=None):
        self.notifyMatchUpdate(player)
        self.__notifyMatchRank2(player, player.group)
        
        msg = MsgPack()
        msg.setCmd('m_wait')
        msg.setResult('gameId', group.match.gameId)
        msg.setResult('roomId', self._room.bigRoomId)
        msg.setResult('tableId', group.match.tableId)
        msg.setResult('mname', self._room.roomConf["name"])
        steps = []
        for i in xrange(group.stage.matching.stageCount):
            stage = group.stage.matching.getStage(i)
            isCurrent = True if stage == group.stage else False
            des = '%s人晋级' % (stage.conf.riseUserCount)
            stepInfo = {'des':des}
            if isCurrent:
                stepInfo['isCurrent'] = 1
                stepInfo['name'] = group.groupName
            else:
                stepInfo['name'] = stage.name
            steps.append(stepInfo)
            
        msg.setResult('steps', steps)
        router.sendToUser(msg, player.userId)
            
    def notifyMatchWait(self, player, group, step=None):
        '''
        通知用户等待
        '''
        try:
            ftlog.debug('PlayerNotifierDizhu.notifyMatchWait userId=', player.userId,
                                  'clientId=', player.clientId,
                                  'groupId=', group.groupId)
            
            clientVer = parseClientId(player.clientId)[1]
            if clientVer >= 3.37:
                self.__notifyMatchWait2(player, group, step)
            else:
                self.__notifyMatchWait(player, group, step)
        except:
            ftlog.error()
        
    def notifyMatchStart(self, players, group):
        try:
            ftlog.info('notifyMatchStart->user length=', len(players))
            mstart = MsgPack()
            mstart.setCmd('m_start')
            mstart.setResult('gameId', group.match.gameId)
            mstart.setResult('roomId', self._room.bigRoomId)
            
            userIds = [p.userId for p in players]
            ftlog.info('notifyMatchStart->begin send tcp m_start')
            router.sendToUsers(mstart, userIds)
            ftlog.info('notifyMatchStart->begin end tcp m_start')
            
            ftlog.info('notifyMatchStart->start bi report')
            sequence = int(group._stage.instId.split('.')[1])
            datas = {'userIds' : userIds, 'roomId' : group.match.roomId, 'sequence' : sequence, 'index' : 0}
            timer.FTTimer(2, self.notifyMatchStartDelayReport_, datas)
            ftlog.info('notifyMatchStart->start bi report async !')
        except:
            ftlog.error()
            
    def notifyMatchStartDelayReport_(self):
        argl = FTTasklet.getCurrentFTTasklet().run_argl
        datas = argl[0]
        userIds = datas['userIds']
        roomId = datas['roomId']
        sequence = datas['sequence']
        index = datas['index']
        ftlog.info('notifyMatchStartDelayReport_ index=', index, 'total=', len(userIds))
        nindex = self.notifyMatchStartDelayReport(userIds, roomId, sequence, index)
        if nindex < 0 :
            ftlog.info('notifyMatchStartDelayReport_ end')
        else:
            datas['index'] = nindex 
            timer.FTTimer(0.1, self.notifyMatchStartDelayReport_, datas)


    def notifyMatchStartDelayReport(self, userIds, roomId, sequence, index):
        ulen = len(userIds)
        blockc = 0
        while index < ulen :
            userId = userIds[index]
            self.report_bi_game_event("MATCH_START", userId, roomId, 0, sequence, 0, 0, 0, [], 'match_start')  # _stage.matchingId
            index += 1
            blockc += 1
            if blockc > 10 :
                return index
        return -1


    def __notifyStageStart(self, player, group):
        if group.stage.index == 0:
            self.__notifyMatchWait(player, group, None)
            
    def __notifyStageStart2(self, player, group):
        if group.stage.index == 0:
            if player.waitReason == WaitReason.BYE:
                self.__notifyMatchWait2(player, group, 0)
            else:
                mo = MsgPack()
                mo.setCmd('m_play_animation')
                mo.setResult('gameId', group.match.gameId)
                mo.setResult('roomId', group.match.roomId)
                mo.setResult('type', AnimationType.ASSIGN_TABLE)
                router.sendToUser(mo, player.userId)
        else:
            mo = MsgPack()
            mo.setCmd('m_rise')
            mo.setResult('gameId', self._room.gameId)
            mo.setResult('roomId', self._room.bigRoomId)
            router.sendToUser(mo, player.userId)
            
    def notifyStageStart(self, player, group):
        '''
        通知用户正在配桌
        '''
        try:
            ftlog.debug('PlayerNotifierDizhu.notifyStageStart userId=', player.userId,
                                  'clientId=', player.clientId,
                                  'groupId=', group.groupId)
            clientVer = parseClientId(player.clientId)[1]
            if clientVer >= 3.37:
                self.__notifyStageStart2(player, group)
            else:
                self.__notifyStageStart(player, group)
        except:
            ftlog.error()
    
    def report_bi_game_event(self, eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
        try:
            finalUserChip = userchip.getChip(userId)
            finalTableChip = 0
            clientId = sessiondata.getClientId(userId)
            bireport.reportGameEvent(eventId, userId, 6, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, finalTableChip, finalUserChip)
            ftlog.debug('report_bi_game_event tag=', tag, 'eventId=', eventId, 'userId=', userId, 'gameId=6', 'roomId=', roomId, 'tableId=', tableId, 'roundId=', roundId,
                        caller=self)
        except:
            ftlog.error('report_bi_game_event error tag=', tag, 'eventId=', eventId, 'userId=', userId, 'gameId=6', 'roomId=', roomId, 'tableId=', tableId, 'roundId=', roundId)
            
class SigninRecordDaoDizhu(SigninRecordDao):
    def __init__(self, room):
        self._room = room
    
    def load(self, matchId, instId):
        '''
        加载所有报名记录
        @return: list((userId, signinTime, signinParams))
        '''
        ret = []
        key = 'msignin2:%s:%s' % (self._room.gameId, instId)
        datas = daobase.executeMixCmd('hgetall', key)
        if not datas:
            return []
        i = 0
        while (i + 1 < len(datas)):
            try:
                userId = int(datas[i])
                d = json.loads(datas[i+1])
                ret.append((userId, d['st'], d['sp']))
            except:
                ftlog.error('SigninRecordDaoDizhu.load matchId=', matchId,
                            'instId=', instId,
                            'data=(%s,%s)', (datas[i], datas[i+1]))
            i += 2
        return ret

    def recordSignin(self, matchId, instId, userId, timestamp, signinParams):
        '''
        记录报名信息
        '''
        try:
            key = 'msignin2:%s:%s' % (self._room.gameId, instId)
            jstr = json.dumps({'st':timestamp, 'sp':signinParams})
            daobase.executeMixCmd('hset', key, userId, jstr)
            daobase.executeTableCmd(self._room.roomId, 0, 'SADD', 'signs:' + str(self._room.roomId), userId)
        except:
            ftlog.error()
            
    def removeSignin(self, matchId, instId, userId):
        '''
        删除报名信息
        '''
        try:
            key = 'msignin2:%s:%s' % (self._room.gameId, instId)
            daobase.executeMixCmd('hdel', key, userId)
            daobase.executeTableCmd(self._room.roomId, 0, 'SREM', 'signs:' + str(self._room.roomId), userId)
        except:
            ftlog.error()
            
    def removeAll(self, matchId, instId):
        try:
            key = 'msignin2:%s:%s' % (self._room.gameId, instId)
            daobase.executeMixCmd('del', key)
            daobase.executeTableCmd(self._room.roomId, 0, 'DEL', 'signs:' + str(self._room.roomId))
        except:
            ftlog.error()
        
class MatchRewardsDizhu(MatchRewards):
    def __init__(self, room):
        self._room = room
        
    def sendRewards(self, player, group, rankRewards):
        '''给用户发送奖励'''
        try:
            matchlog('MatchRewardsDizhu.sendRewards', self._room.roomId,
                     group.groupId, player.userId, player.rank, rankRewards.rewards)
            user_remote.addAssets(self._room.gameId, player.userId, rankRewards.rewards,
                                      'MATCH_REWARD', self._room.roomId)
            if rankRewards.message:
                pkmessage.sendPrivate(self._room.gameId, player.userId, 0, rankRewards.message)
                datachangenotify.sendDataChangeNotify(self._room.gameId, player.userId, 'message')
        except:
            ftlog.error()
            
class MatchStatusDaoDizhu(MatchStatusDao):
    def __init__(self, room):
        self._room = room
        
    def load(self, matchId):
        '''
        加载比赛信息
        @return: MatchStatus
        '''
        key = 'mstatus:%s' % (self._room.gameId)
        jstr = daobase.executeMixCmd('hget', key, matchId)
        if jstr:
            d = json.loads(jstr)
            return MatchStatus(matchId, d['seq'], d['startTime'])
        return None
    
    def save(self, status):
        '''
        保存比赛信息
        '''
        try:
            key = 'mstatus:%s' % (self._room.gameId)
            d = {'seq':status.sequence, 'startTime':status.startTime}
            jstr = json.dumps(d)
            daobase.executeMixCmd('hset', key, status.matchId, jstr)
        except:
            ftlog.error()
            
class SigninFeeDizhu(SigninFee):
    def __init__(self, room):
        self._room = room
        
    def collectFees(self, inst, userId, fees):
        '''
        收取用户报名费
        '''
        if userId <= 10000:
            return
        
        contentItemList = []
        for fee in fees:
            contentItemList.append({'itemId':fee.assetKindId, 'count':fee.count})
        assetKindId, count = user_remote.consumeAssets(self._room.gameId, userId, contentItemList,
                                                           'MATCH_SIGNIN_FEE', self._room.roomId)
        
        if assetKindId:
            fee = None
            for fee in fees:
                if fee.assetKindId == assetKindId:
                    raise SigninFeeNotEnoughException(inst, fee)
            raise SigninFeeNotEnoughException(inst, MatchFee(assetKindId, count, {}))

    def returnFees(self, inst, userId, fees):
        '''
        退还报名费
        '''
        try:
            if userId <= 10000:
                return
            
            contentItemList = []
            for fee in fees:
                contentItemList.append({'itemId':fee.assetKindId, 'count':fee.count})
            user_remote.addAssets(self._room.gameId, userId, contentItemList, 'MATCH_RETURN_FEE', self._room.roomId)
        except:
            ftlog.error()
            
class UserInfoLoaderDizhu(UserInfoLoader):
    def loadUserName(self, userId):
        '''
        获取用户名称
        '''
        name = userdata.getAttr(userId, 'name')
        return name if name is not None else ''

    def loadUserAttrs(self, userId, attrList):
        '''
        '''
        return userdata.getAttrs(userId, attrList)
