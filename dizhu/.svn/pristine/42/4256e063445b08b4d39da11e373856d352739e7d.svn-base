# -*- coding=utf-8 -*-

'''
Created on 2014年3月11日

@author: zjgzzz@126.com
'''
from dizhu.replay.codec import BaseCodec
from dizhu.replay.gameround import GameReadyOp, GameShowOp, GameNextOp, \
    GameCallOp, GameJiabeiOp, GameStartOp, GameWildCardOp, GameOutCardOp, \
    GameAbortOp, GameWinloseOp, GameChatOp, GameRobotOp
import freetime.util.log as ftlog


class GameReadyOpCodecDictComplain(BaseCodec):
    def __init__(self, gameRound=None):
        self.gameRound = gameRound
        
    def encode(self, op):
        seats = []
        for i, seat in enumerate(self.gameRound.seats):
            seats.append({
                'seatIndex':i,
                'userId':seat.userId,
                'cards':op.seatCards[i]
            })
        return {
            'action':op.action,
            'baseCards':op.baseCards,
            'seats':seats,
            'baseMulti':self.gameRound.roomMulti,
            'roomFee':self.gameRound.roomFee
        }
        
class GameChatOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'isFace':op.isFace,
            'voiceIdx':op.voiceIdx,
            'msg':op.msg
        }
    
class GameRobotOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'isRobot':op.isRobot
        }
        
class GameShowOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'showMulti':op.showMulti
        }

class GameNextOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'nextSeatIndex':op.seatIndex,
            'grab':op.grab
        }
    
class GameCallOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'call':op.call
        }

class GameJiabeiOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'jiabei':op.jiabei
        }
 
class GameStartOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'dizhuseatIndex':op.dizhuSeatIndex,
            'seatCards':op.seatCards
        }
        
class GameWildCardOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'wildCard':op.wildCard,
            'seatCards':op.seatCards
        }
    
class GameOutCardOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action,
            'seatIndex':op.seatIndex,
            'outCards':op.outCards
        }

class GameAbortOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        return {
            'action':op.action
        }
    
class GameWinloseOpCodecDictComplain(BaseCodec):
    def encode(self, op):
        winlose = {}
        winlose['zhadanMulti'] = pow(2, op.winloseDetail.bombCount)
        winlose['chuntianMulti'] = 2 if op.winloseDetail.isChuntian else 1,
        winlose['mingpaiMulti'] = op.winloseDetail.showMulti
        winlose['baseCardMulti'] = op.winloseDetail.baseCardMulti
        winlose['callMulti'] = op.winloseDetail.callMulti
        winloses = []
        for seatWinloseDetail in op.winloseDetail.seatWinloseDetails:
            winloses.append({
                'deltaChip':seatWinloseDetail.deltaChip,
                'finalChip':seatWinloseDetail.finalChip
            })
        winlose['winloses'] = winloses
        return {
            'action':op.action,
            'winlose':winlose
        }

class SeatCodecDictComplain(BaseCodec):
    def encode(self, obj):
        return {
            'uid':obj.userId,
            'name':obj.userName,
            'sex':obj.sex,
            'vip':obj.vipLevel,
            'chip':obj.chip,
            'score':obj.score,
            'img':obj.headUrl,
            'wItems':obj.wearedItems
        }
    
class GameRoundCodecDictComplain(BaseCodec):
    def __init__(self):
        self.gameReadyCodec = GameReadyOpCodecDictComplain()
        self.opCodecMap = {
            GameReadyOp.ACTION:self.gameReadyCodec,
            GameChatOp.ACTION:GameChatOpCodecDictComplain(),
            GameRobotOp.ACTION:GameRobotOpCodecDictComplain(),
            GameShowOp.ACTION:GameShowOpCodecDictComplain(),
            GameNextOp.ACTION:GameNextOpCodecDictComplain(),
            GameCallOp.ACTION:GameCallOpCodecDictComplain(),
            GameJiabeiOp.ACTION:GameJiabeiOpCodecDictComplain(),
            GameStartOp.ACTION:GameStartOpCodecDictComplain(),
            GameWildCardOp.ACTION:GameWildCardOpCodecDictComplain(),
            GameOutCardOp.ACTION:GameOutCardOpCodecDictComplain(),
            GameAbortOp.ACTION:GameAbortOpCodecDictComplain(),
            GameWinloseOp.ACTION:GameWinloseOpCodecDictComplain()
        }
    
    def encode(self, obj):
        self.gameReadyCodec.gameRound = obj
        return {
            'roomId':obj.roomId,
            'matchId':obj.matchId,
            'tableId':obj.tableId,
            'number':obj.roundId,
            'ops':self._encodeOps(obj.ops)
        }
    
    def findOpCodec(self, action):
        return self.opCodecMap.get(action)
    
    def _encodeOps(self, ops):
        opsDicts = []
        for op in ops:
            codec = self.findOpCodec(op.action)
            if not codec:
                ftlog.warn('GameRoundCodecDictComplain._encodeOps UnknownAction',
                           'action=', op.action)
                continue
            opsDicts.append(codec.encode(op))
        return opsDicts
    
# from poker.util import strutil
# from poker.entity.dao import daobase

# 
# class GameRoundOp(object):
# 
#     
#     def __init__(self, action):
#         self.__action = action
# 
# 
#     @property
#     def action(self):
#         return self.__action
# 
# 
#     def toDict(self):
#         d = {
#              'action':self.__action,
#              }
#         self._encodeDict(d)
#         return d
# 
#     
#     def _encodeDict(self, d):
#         pass
# 
# 
# class Seat(object):
#     
#     def __init__(self, seatIndex, userId, cards):
#         self.__seatIndex = seatIndex
#         self.__userId = userId
#         self.__cards = cards
#         
# 
#     @property
#     def seatIndex(self):
#         return self.__seatIndex
#     
# 
#     @property
#     def userId(self):
#         return self.__userId
#     
# 
#     @property
#     def cards(self):
#         return self.__cards
#     
# 
#     def toDict(self):
#         return {
#                 'seatIndex':self.__seatIndex,
#                 'userId':self.__userId,
#                 'cards':self.__cards
#                 }
# 
#     
# class GameReadyOp(GameRoundOp):
#     
#     ACTION = 'game_ready'
#     
#     def __init__(self, baseMulti, roomFee, seats, baseCards):
#         super(GameReadyOp, self).__init__(GameReadyOp.ACTION)
#         self.__baseMulti = baseMulti
#         self.__roomFee = roomFee
#         self.__seats = seats
#         self.__baseCards = baseCards
#     
#     
#     @property
#     def seats(self):
#         return self.__seats
#     
#     
#     @property
#     def baseCards(self):
#         return self.__baseCards
#     
#     
#     @property
#     def baseMulti(self):
#         return self.__baseMulti
#     
#     
#     @property
#     def roomFee(self):
#         return self.__roomFee
#     
# 
#     def _encodeDict(self, d):
#         seatsList = []
#         for seat in self.__seats:
#             seatsList.append(seat.toDict())
#         d['baseCards'] = self.__baseCards
#         d['seats'] = seatsList
#         d['baseMulti'] = self.__baseMulti
#         d['roomFee'] = self.__roomFee
# 
#     
# class GameShowOp(GameRoundOp):
#     
#     ACTION = 'show'
#     
#     def __init__(self, seatIndex, showMulti):
#         super(GameShowOp, self).__init__(GameShowOp.ACTION)
#         self.__seatIndex = seatIndex
#         self.__showMulti = showMulti
#         
# 
#     @property
#     def seatIndex(self):
#         return self.__seatIndex
#     
# 
#     @property
#     def showMulti(self):
#         return self.__showMulti
#     
# 
#     def _encodeDict(self, d):
#         d['seatIndex'] = self.__seatIndex
#         d['showMulti'] = self.__showMulti
# 
#     
# class GameNextOp(GameRoundOp):
#     
#     ACTION = 'next'
# 
#     def __init__(self, crc, nextSeatIndex, grab):
#         super(GameNextOp, self).__init__(GameNextOp.ACTION)
#         self.__crc = crc
#         self.__nextSeatIndex = nextSeatIndex
#         self.__grab = grab
# 
# 
#     @property
#     def crc(self):
#         return self.__crc
#        
# 
#     @property
#     def nextSeatIndex(self):
#         return self.__nextSeatIndex
#     
# 
#     @property
#     def grab(self):
#         return self.__grab
#     
# 
#     def _encodeDict(self, d):
#         d['crc'] = self.__crc
#         d['nextSeatIndex'] = self.__nextSeatIndex
#         d['grab'] = self.__grab
# 
#     
# class GameCallOp(GameRoundOp):
#     
#     ACTION = 'call'
#     
#     def __init__(self, seatIndex, call, callResult):
#         super(GameCallOp, self).__init__(GameCallOp.ACTION)
#         self.__seatIndex = seatIndex
#         self.__call = call
#         self.__callResult = callResult
#         
# 
#     @property
#     def seatIndex(self):
#         return self.__seatIndex
# 
# 
#     @property
#     def call(self):
#         return self.__call
#     
# 
#     @property
#     def callResult(self):
#         return self.__callResult
#     
# 
#     def _encodeDict(self, d):
#         d['seatIndex'] = self.__seatIndex
#         d['call'] = self.__call
#         d['callResult'] = self.__callResult
# 
#     
# class GameStartOp(GameRoundOp):
#     
#     ACTION = 'game_start'
# 
#     def __init__(self, dizhuseatIndex, seatCards):
#         super(GameStartOp, self).__init__(GameStartOp.ACTION)
#         self.__dizhuseatIndex = dizhuseatIndex
#         self.__seatCards = seatCards
# 
#     
#     @property
#     def dizhuseatIndex(self):
#         return self.__dizhuseatIndex
#     
# 
#     @property
#     def seatCards(self):
#         return self.__seatCards
#     
# 
#     def _encodeDict(self, d):
#         d['dizhuseatIndex'] = self.__dizhuseatIndex
#         d['seatCards'] = self.__seatCards
# 
#     
# class GameWildCardOp(GameRoundOp):
#     
#     ACTION = 'wild_card'
#     
#     def __init__(self, wildCard, seatCards):
#         super(GameWildCardOp, self).__init__(GameWildCardOp.ACTION)
#         self.__wildCard = wildCard
#         self.__seatCards = seatCards
# 
#     
#     @property
#     def wildCard(self):
#         return self.__wildCard
#     
#     
#     @property
#     def seatCards(self):
#         return self.__seatCards
#     
# 
#     def _encodeDict(self, d):
#         d['wildCard'] = self.__wildCard
#         d['seatCards'] = self.__seatCards
# 
#     
# class GameOutCardOp(GameRoundOp):
#     
#     ACTION = 'card'
#     
#     def __init__(self, seatIndex, outCards):
#         super(GameOutCardOp, self).__init__(GameOutCardOp.ACTION)
#         self.__seatIndex = seatIndex
#         self.__outCards = outCards
#             
#     
#     @property
#     def seatIndex(self):
#         return self.__seatIndex
#     
# 
#     @property
#     def outCards(self):
#         return self.__outCards
# 
# 
#     def _encodeDict(self, d):
#         d['seatIndex'] = self.__seatIndex
#         d['outCards'] = self.__outCards
#         
# 
# class GameAbortOp(GameRoundOp):
#     
#     ACTION = 'game_abort'
# 
#     def __init__(self):
#         super(GameAbortOp, self).__init__(GameAbortOp.ACTION)
#         pass
# 
# 
# class UserWinlose(object):
#     
#     def __init__(self, deltaChip, finalChip):
#         self.deltaChip = deltaChip
#         self.finalChip = finalChip
#         
# 
#     def toDict(self):
#         return {
#                 'deltaChip':self.deltaChip,
#                 'finalChip':self.finalChip
#                 }
# 
#     
# class WinloseResult(object):
# 
#     def __init__(self, zhadanMulti, chuntianMulti, mingpaiMulti, baseCardMulti, userWinloses):
#         self.zhadanMulti = zhadanMulti
#         self.chuntianMulti = chuntianMulti
#         self.mingpaiMulti = mingpaiMulti
#         self.baseCardMulti = baseCardMulti
#         self.userWinloses = userWinloses
# 
# 
#     def toDict(self):
#         userWinloseList = []
#         d = {
#              'zhadanMulti':self.zhadanMulti,
#              'chuntianMulti':self.chuntianMulti,
#              'mingpaiMulti':self.mingpaiMulti,
#              'baseCardMulti':self.baseCardMulti
#              }
#         for userWinlose in self.userWinloses:
#             userWinloseList.append(userWinlose.toDict())
#         d['winloses'] = userWinloseList
#         return d
# 
# 
# class GameWinLoseOp(GameRoundOp):
#     
#     ACTION = 'game_win'
#     
#     def __init__(self, winloseResult):
#         super(GameWinLoseOp, self).__init__(GameWinLoseOp.ACTION)
#         self.__winloseResult = winloseResult
#     
#     
#     @property
#     def winloseResult(self):
#         return self.__winloseResult
#     
# 
#     def _encodeDict(self, d):
#         d['winlose'] = self.__winloseResult.toDict()
# 
# 
# class GameRound(object):
#     
# 
#     def __init__(self, roomId, tableId, matchId):
#         self.__number = None
#         self.__roundId = 0
#         self.__roomId = roomId
#         self.__tableId = tableId
#         self.__matchId = matchId
#         self.__ops = []
# 
# 
#     def _delayInit(self):
#         num = daobase.executeTableCmd(self.roomId, self.tableId, 'HINCRBY', 'game.round.number', self.roomId, 1)
#         self.__roundId = num
#         self.__number = str(self.roomId) + '_' + str(num)
# 
# 
#     @property
#     def roundId(self):
#         if self.__roundId == 0 :
#             self._delayInit()
#         return self.__roundId
# 
# 
#     @property
#     def number(self):
#         if self.__number == None :
#             self._delayInit()
#         return self.__number
# 
# 
#     @property
#     def roomId(self):
#         return self.__roomId
#     
#     
#     @property
#     def tableId(self):
#         return self.__tableId
#     
#     
#     @property
#     def matchId(self):
#         return self.__matchId
#     
#     
#     @property
#     def ops(self):
#         return self.__ops
#     
#     
#     def gameReady(self, baseMulti, roomFee, uids, cards, baseCards):
#         seats = []
#         for i in xrange(len(uids)):
#             seats.append(Seat(i, uids[i], cards[i]))
#         self.__ops.append(GameReadyOp(baseMulti, roomFee, seats, baseCards))
#         
#     
#     def call(self, seatIndex, call, callResult):
#         self.__ops.append(GameCallOp(seatIndex, call, callResult))
#     
#     
#     def show(self, seatIndex, showMulti):
#         self.__ops.append(GameShowOp(seatIndex, showMulti))
#         
#     
#     def gameStart(self, dizhuseatIndex, seatCards):
#         self.__ops.append(GameStartOp(dizhuseatIndex, seatCards))
#     
#     
#     def wildCard(self, wildCard, seatCards):
#         self.__ops.append(GameWildCardOp(wildCard, seatCards))
#     
#     
#     def next(self, crc, nextSeatIndex, grab):
#         self.__ops.append(GameNextOp(crc, nextSeatIndex, grab))
#     
#     
#     def outCard(self, seatIndex, outCards):
#         self.__ops.append(GameOutCardOp(seatIndex, outCards))
#     
#     
#     def gameAbort(self):
#         self.__ops.append(GameAbortOp())
#     
#     
#     def gameWinlose(self, winloses):
#         self.__ops.append(GameWinLoseOp(winloses))
#     
# 
#     def toJson(self):
#         return strutil.dumps(self.toDict())
# 
# 
#     def toDict(self):
#         opsList = []
#         for op in self.__ops:
#             opsList.append(op.toDict())
#         d = {
#              'number':self.__number,
#              'roomId':self.__roomId,
#              'tableId':self.__tableId,
#              'matchId':self.__matchId,
#              'ops':opsList
#              }
#         return d
