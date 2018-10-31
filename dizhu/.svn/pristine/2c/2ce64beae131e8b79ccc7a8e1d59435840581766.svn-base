# -*- coding: utf-8 -*-
'''
Created on 2018年7月13日

@author: wangyonghui
'''
import json
from sre_compile import isstring
import poker.util.timestamp as pktimestamp

import datetime

import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games.endgame.dao import endgamedata
from dizhu.games.endgame.engine.minmax_engine import start_engine
from dizhu.games.endgame.engine.move_player import get_resp_moves
from dizhu.games.endgame.engine.utils import tuyoo_card_to_human, format_input_cards, card_num_to_human_map, v2s, get_rest_cards
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import configure
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus

ENDGAME_USER_CURRENT_ROUND_INFO_KEY = 'roundInfo'
ENDGAME_USER_HISTORY_INFO_KEY = 'history'
ENDGAME_USER_ISSUE_KEY = 'issueNum'


# 每个 UT 进程存储的用户对象 key 为 userId, value 为 EndgamePlayer 对象
endgame_player_map = {

}

class EndgameRoundData(object):
    ''' 残局闯关历史数据, 已经闯关成功的数据 '''
    def __init__(self):
        self.roundNum = 1
        self.playCount = 0
        self.reply = []

    def decodeFromDict(self, d):
        self.roundNum = d.get('roundNum', 1)
        self.playCount = d.get('playCount', 0)
        self.reply = d.get('reply', [])
        return self

    def encodeToDict(self):
        return {
            'roundNum': self.roundNum,
            'playCount': self.playCount,
            'reply': self.reply
        }


class EndgameSeasonConf(object):
    ''' 赛季配置 '''
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.issueNum = None
        self.roundCards = None

    def decodeFromDict(self, d):
        startTime = d.get('startTime')
        try:
            startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
            self.startTime = startTime
        except Exception:
            raise TYBizConfException(d, 'EndgameSeasonConf.startTime must be like "2018-05-14 00:00:00"')

        endTime = d.get('endTime')
        try:
            endTime = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
            self.endTime = endTime
        except Exception:
            raise TYBizConfException(d, 'EndgameSeasonConf.endTime must be like "2018-05-14 00:00:00"')

        self.issueNum = d.get('issueNum')
        if not isstring(self.issueNum):
            raise TYBizConfException(d, 'EndgameSeasonConf.issueNum must str')

        self.roundCards = d.get('roundCards', {})
        if not isinstance(self.roundCards, dict):
            raise TYBizConfException(d, 'EndgameSeasonConf.roundCards must be dict')
        return self


class EndgameConf(object):
    ''' 残局闯关总配置 '''
    def __init__(self):
        self.seasonList = None
        self.maxDepth = None

    def decodeFromDict(self, d):
        seasonList = d.get('seasonList')
        if not isinstance(seasonList, list):
            raise TYBizConfException(d, 'EndgameConf.seasonList must be list')
        self.seasonList = []
        for seasonConf in seasonList:
            seasonInfo = EndgameSeasonConf().decodeFromDict(seasonConf)
            self.seasonList.append(seasonInfo)

        self.maxDepth = d.get('maxDepth', 4)
        if not isinstance(self.maxDepth, int):
            raise TYBizConfException(d, 'EndgameConf.maxDepth must be int')
        return self


class EndgameHelper(object):
    ''' 残局闯关业务处理函数 '''
    @classmethod
    def getCurrentIssueConfig(cls):
        ''' 获取当前期配置 '''
        issueDate = datetime.datetime.now()
        for seasonInfo in _endGameConf.seasonList:
            if seasonInfo.startTime <= issueDate <= seasonInfo.endTime:
                if ftlog.is_debug():
                    ftlog.debug('EndgameHelper.getCurrentIssueConfig seasonInfo=', seasonInfo)
                return seasonInfo
        return None

    @classmethod
    def updateUserIssueRoundData(cls, userId):
        ''' 更新用户赛季牌局数据 '''
        currentIssueNum = cls.getCurrentIssueConfig().issueNum

        if ftlog.is_debug():
            ftlog.debug('EndgameHelper.updateUserIssueRoundData userId=', userId,
                        'currentIssueNum=', currentIssueNum,
                        'userEndgameIssue=', cls.getUserEndgameIssue(userId),
                        'updated=', int(currentIssueNum) != int(cls.getUserEndgameIssue(userId)))

        if int(currentIssueNum) == int(cls.getUserEndgameIssue(userId)):
            return False

        # 清理上赛季信息
        endgamedata.delEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_ISSUE_KEY)
        endgamedata.delEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_CURRENT_ROUND_INFO_KEY)
        endgamedata.delEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_HISTORY_INFO_KEY)
        return True

    @classmethod
    def getUserEndgameIssue(cls, userId):
        ''' 获取玩家当前残局赛季号 '''
        issueStr = endgamedata.getEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_ISSUE_KEY)
        if ftlog.is_debug():
            ftlog.debug('EndgameHelper.getUserEndgameIssue userId=', userId,
                        'currentIssue=', issueStr)
        if not issueStr:
            issueStr = cls.getCurrentIssueConfig().issueNum
            endgamedata.setEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_ISSUE_KEY, issueStr)
            return issueStr
        return issueStr

    @classmethod
    def getUserCurrentRoundData(cls, userId):
        ''' 获取玩家当前残局信息 '''
        roundInfoStr = endgamedata.getEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_CURRENT_ROUND_INFO_KEY)
        if ftlog.is_debug():
            ftlog.debug('EndgameHelper.getUserCurrentRoundData userId=', userId,
                        'roundInfoStr=', roundInfoStr)
        if not roundInfoStr:
            return EndgameRoundData()
        else:
            return EndgameRoundData().decodeFromDict(json.loads(roundInfoStr))

    @classmethod
    def saveUserCurrentRoundData(cls, userId, roundData):
        ''' 保存玩家当前残局信息 '''
        savingDict = roundData.encodeToDict()
        endgamedata.setEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_CURRENT_ROUND_INFO_KEY, json.dumps(savingDict))
        if ftlog.is_debug():
            ftlog.debug('EndgameHelper.saveUserCurrentRoundData userId=', userId,
                        'savingDict=', savingDict)

    @classmethod
    def saveNewRoundInfoToHistory(cls, userId, roundData):
        ''' 保存到历史记录, roundData 需要带 reply 数据'''
        historyList = cls.getUserHistoryRoundDataList(userId)
        historyList.append(roundData.encodeToDict())
        endgamedata.setEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_HISTORY_INFO_KEY, json.dumps(historyList))
        if ftlog.is_debug():
            ftlog.debug('EndgameHelper.saveNewRoundInfoToHistory userId=', userId,
                        'historyList=', historyList)

    @classmethod
    def getUserHistoryRoundDataList(cls, userId):
        ''' 获取残局历史记录 '''
        roundHistoryStr = endgamedata.getEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_HISTORY_INFO_KEY)
        if ftlog.is_debug():
            ftlog.debug('EndgameHelper.getUserHistoryRoundDataList userId=', userId,
                        'roundHistoryStr=', roundHistoryStr)
        if not roundHistoryStr:
            return []
        else:
            return json.loads(roundHistoryStr)

    @classmethod
    def updateRoundInfoHistory(cls, userId, roundData):
        ''' 更新历史闯关信息 '''
        roundHistoryStr = endgamedata.getEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_HISTORY_INFO_KEY)
        if not roundHistoryStr:
            return
        else:
            historyList = json.loads(roundHistoryStr)
            for history in historyList:
                if history.get('roundNum') == roundData.roundNum:
                    history['playCount'] = roundData.playCount
                    history['reply'] = roundData.reply
            endgamedata.setEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_HISTORY_INFO_KEY, json.dumps(historyList))

    @classmethod
    def getUserRoundDataHistory(cls, userId, roundNum):
        ''' 获取用户历史残局数据 '''
        roundHistoryStr = endgamedata.getEndgameAttr(userId, DIZHU_GAMEID, ENDGAME_USER_HISTORY_INFO_KEY)
        if not roundHistoryStr:
            return
        else:
            historyList = json.loads(roundHistoryStr)
            for history in historyList:
                if history.get('roundNum') == roundNum:
                    if ftlog.is_debug():
                        ftlog.debug('EndgameHelper.getUserRoundDataHistory userId=', userId,
                                    'roundNum=', roundNum,
                                    'historyPerRoundData=', history)
                    return EndgameRoundData().decodeFromDict(history)



class EndgamePlayer(object):
    ''' 用户对象 '''
    STATE_PLAYING = 1
    STATE_WIN = 2
    STATE_LOSE = 3

    def __init__(self, userId, initLandlordCards, initFarmerCards, isHelp=False):
        self.userId = userId
        self.initLandlordCards = initLandlordCards
        self.initFarmerCards = initFarmerCards
        self.landlordCards = [card for card in initLandlordCards]
        self.farmerCards = [card for card in initFarmerCards]
        self.reply = []
        self.lastFarmerMove = []  # 转换后的对应的point值
        self.currentRoundNum = EndgameHelper.getUserCurrentRoundData(userId).roundNum
        self.maxRoundNum = 1
        self.state = self.STATE_PLAYING
        self.historyRoundData = None
        self.expireTimeStamp = pktimestamp.getCurrentTimestamp() + 3600
        self.isHelp = isHelp

    def outCards(self, cards):
        self.expireTimeStamp = pktimestamp.getCurrentTimestamp() + 3600
        # 地主手牌
        landlordCards = tuyoo_card_to_human(self.landlordCards)
        landlordCards = format_input_cards(landlordCards)

        # 农民手牌（AI 机器人）
        farmerCards = tuyoo_card_to_human(self.farmerCards)
        farmerCards = format_input_cards(farmerCards)

        # 地主出的牌
        landlordMove = tuyoo_card_to_human(cards)
        landlordMove = format_input_cards(landlordMove)


        # 检查地主出牌的有效性，地主可能出的所有组合
        possibleMoves = get_resp_moves(landlordCards, self.lastFarmerMove)
        possibleMoves = [sorted(move) for move in possibleMoves]
        landlordMove = sorted(landlordMove)
        if landlordMove not in possibleMoves:
            ftlog.warn('EndgamePlayer.outCards landlord card validate error userId=', self.userId,
                       'landlordCards=', landlordCards,
                       'landlordMove=', landlordMove,
                       'possibleMoves=', possibleMoves
                       )
            raise Exception('出牌校验错误')

        # 地主出牌后剩余手牌
        landlordCards = get_rest_cards(landlordCards, landlordMove)
        # 清除地主出的牌
        if cards:
            self.landlordCards = [card for card in self.landlordCards if card not in cards]


        self.reply.append(cards)

        farmerMove = []
        removeFarmerCards = []
        result_dict = {}

        udata = EndgameHelper.getUserCurrentRoundData(self.userId)
        if len(self.landlordCards) == 0:
            # 地主赢
            self.state = self.STATE_WIN

            if not self.isHelp:
                if self.historyRoundData:
                    self.historyRoundData.playCount += 1
                    self.historyRoundData.reply = self.reply
                    EndgameHelper.updateRoundInfoHistory(self.userId, self.historyRoundData)
                else:
                    # 保存历史记录
                    udata.reply = self.reply
                    EndgameHelper.saveNewRoundInfoToHistory(self.userId, udata)

                    # 进行下一关
                    udata.roundNum += 1
                    udata.playCount = 0
                    udata.reply = []
                    EndgameHelper.saveUserCurrentRoundData(self.userId, udata)
        else:
            # 农民最佳出牌
            farmerMove, result_dict = start_engine(lorder_cards=landlordCards, farmer_cards=farmerCards,
                                      lorder_move=landlordMove, max_depth=_endGameConf.maxDepth)
            # 需要清零的农民出的牌
            removeFarmerCards = []
            for card in farmerMove:
                for c in self.farmerCards:
                    if card_num_to_human_map[c] == v2s[card]:
                        removeFarmerCards.append(c)
                        self.farmerCards.remove(c)
                        break
            if len(self.farmerCards) == 0:
                # AI 赢
                self.state = self.STATE_LOSE
            self.reply.append(removeFarmerCards)

        if ftlog.is_debug():
            ftlog.debug('EndgamePlayer.outCards userId=', self.userId,
                        'initLandlordCards=', [card_num_to_human_map[c] for c in self.initLandlordCards],
                        'initFarmerCards=', [card_num_to_human_map[c] for c in self.initFarmerCards],
                        'landlordCards=', [card_num_to_human_map[c] for c in self.landlordCards],
                        'farmerCards=', [card_num_to_human_map[c] for c in self.farmerCards],
                        'reply=', self.reply,
                        'lastFarmerMove=', [v2s[c] for c in self.lastFarmerMove],
                        'cards=', [card_num_to_human_map[c] for c in cards],
                        'farmerMove=', [v2s[c] for c in farmerMove],
                        'result_dict=', result_dict,
                        'isHelp=', self.isHelp
                        )
        # 返回机器人出的牌
        return {
            'removeFarmerCards': removeFarmerCards,
            'state': self.state,
            'isHelp': self.isHelp,
            'roundNum': min(udata.roundNum, self.maxRoundNum),
            'reply': self.reply,
            'initLandlordCards': self.initLandlordCards,
            'initFarmerCards': self.initFarmerCards
        }



_inited = False
_issueList = []
_endGameConf = None

def getEndgameConf():
    return _endGameConf


def _reloadConf():
    global _endGameConf
    d = configure.getGameJson(DIZHU_GAMEID, 'endgame', {}, 0)
    conf = EndgameConf().decodeFromDict(d)
    _endGameConf = conf

    ftlog.info('endgame._reloadConf succeed',
               '_endGameConf=', _endGameConf)

def _onConfChanged(event):
    if _inited and event.isChanged('game:6:endgame:0'):
        ftlog.debug('endgame._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('endgame._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        loop_timer = FTLoopTimer(3600, -1, process_players)
        loop_timer.start()
    ftlog.debug('endgame._initialize end')


def process_players():
    count = 0
    deletedUserList = []
    for userId, user in endgame_player_map.items():
        count += 1
        if pktimestamp.getCurrentTimestamp() > user.expireTimeStamp:
            try:
                deletedUserList.append(userId)
                del endgame_player_map[userId]
            except:
                pass
        if count >= 1000:
            count = 0
            FTTasklet.getCurrentFTTasklet().sleepNb(0.5)
    if ftlog.is_debug():
        ftlog.debug('endgame.process_players deletedUserList=', deletedUserList)
