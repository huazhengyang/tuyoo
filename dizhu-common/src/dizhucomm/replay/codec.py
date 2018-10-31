# -*- coding:utf-8 -*-
'''
Created on 2017年2月9日

@author: zhaojiangang
'''
from dizhucomm.core.playmode import GameRound
from dizhucomm.replay.gameround import GameReadyOp, GameChatOp, GameSmiliesOp, \
    GameRobotOp, GameShowOp, GameNextOp, GameCallOp, GameJiabeiOp, GameStartOp, \
    GameWildCardOp, GameOutCardOp, GameAbortOp, GameWinloseOp
from poker.entity.biz.exceptions import TYBizException


class BaseCodec(object):
    def encode(self, obj):
        raise NotImplementedError
    
    def decode(self, data):
        raise NotImplementedError
    
    def encodeList(self, objs):
        ret = []
        for obj in objs:
            ret.append(self.encode(obj))
        return ret
    
    def decodeList(self, datas):
        ret = []
        for data in datas:
            ret.append(self.decode(data))
        return ret

class GameReadyOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'game_ready',
            'cards':op.seatCards
        }
    
class GameChatOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'chat',
            'seat':op.seatIndex,
            'msg':op.msg,
            'face':op.isFace,
            'voiceIdx':op.voiceIdx
        }
         
class GameSmiliesOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'smilies',
            'seat':op.seatIndex,
            'toSeat':op.toSeatIndex,
            'smilie':op.smilie,
            'count':op.count,
            'deltaChip':op.deltaChip,
            'finalChip':op.finalChip
        }
       
class GameRobotOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'rb',
            'seat':op.seatIndex,
            'rb':op.isRobot
        }
           
class GameShowOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'show',
            'seat':op.seatIndex,
            'mul':op.totalMulti
        }

class GameNextOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'next',
            'seat':op.seatIndex
        }
    
class GameCallOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'call',
            'seat':op.seatIndex,
            'call':op.call,
            'rangpai':op.rangpai,
            'mul':op.totalMulti
        }

class GameJiabeiOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'jiabei',
            'seat':op.seatIndex,
            'jiabei':op.jiabei
        }
 
class GameStartOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'game_start',
            'dizhu':op.dizhuSeatIndex,
            'bc':op.baseCards,
            'bcmulti':op.baseCardMulti,
            'mul':op.totalMulti
        }
        
class GameWildCardOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'wild_card',
            'wcard':op.wildCard,
            'cards':op.seatCards,
            'bc':op.baseCards
        }
    
class GameOutCardOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'card',
            'seat':op.seatIndex,
            'out':op.outCards,
            'mul':op.totalMulti
        }

class GameAbortOpCodecDictReplay(BaseCodec):
    def encode(self, op):
        return {
            'act':'game_abort'
        }
    
class SeatWinloseDetailCodecDictReplay(BaseCodec):
    def encode(self, obj):
        return {
            'skill':obj.skillInfo,
            'delta':obj.deltaChip,
            'final':obj.finalChip,
            'mul':obj.totalMulti,
            'winS':obj.winStreak
        }
    
class WinloseDetailCodecDictReplay(BaseCodec):
    seatWinloseDetailCodec = SeatWinloseDetailCodecDictReplay()
    
    def encode(self, obj):
        return {
            'nowin':1 if obj.result == GameRound.RESULT_DRAW else 0,
            'bobm':obj.bombCount,
            'mul':obj.totalMulti,
            'ct':obj.isChuntian,
            'win':obj.dizhuWin,
            'slam':obj.slam,
            'dmg':obj.slamMulti,
            'seats':self.seatWinloseDetailCodec.encodeList(obj.seatWinloseDetails)
        }

class GameWinloseOpCodecDictReplay(BaseCodec):
    winloseDetailCodecDict = WinloseDetailCodecDictReplay()
    def encode(self, op):
        d = self.winloseDetailCodecDict.encode(op.winloseDetail)
        d['act'] = 'game_win'
        return d

class SeatCodecDictReplay(BaseCodec):
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
            
class GameRoundCodecDictReplay(BaseCodec):
    opCodecMap = {
        GameReadyOp.ACTION:GameReadyOpCodecDictReplay(),
        GameChatOp.ACTION:GameChatOpCodecDictReplay(),
        GameSmiliesOp.ACTION:GameSmiliesOpCodecDictReplay(),
        GameRobotOp.ACTION:GameRobotOpCodecDictReplay(),
        GameShowOp.ACTION:GameShowOpCodecDictReplay(),
        GameNextOp.ACTION:GameNextOpCodecDictReplay(),
        GameCallOp.ACTION:GameCallOpCodecDictReplay(),
        GameJiabeiOp.ACTION:GameJiabeiOpCodecDictReplay(),
        GameStartOp.ACTION:GameStartOpCodecDictReplay(),
        GameWildCardOp.ACTION:GameWildCardOpCodecDictReplay(),
        GameOutCardOp.ACTION:GameOutCardOpCodecDictReplay(),
        GameAbortOp.ACTION:GameAbortOpCodecDictReplay(),
        GameWinloseOp.ACTION:GameWinloseOpCodecDictReplay()
    }
    
    seatCodec = SeatCodecDictReplay()

    def encode(self, obj):
        seats = []
        for seat in obj.seats:
            seats.append(self.seatCodec.encode(seat))
        return {
            'ver':1,
            'match':obj.replayMatchType,
            'name':obj.roomName,
            'mode':obj.playMode,
            'base':obj.roomMulti,
            'grab':obj.grab,
            'seats':seats,
            'ops':self._encodeOps(obj.ops)
        }
    
    def findOpCodec(self, action):
        return self.opCodecMap.get(action)
    
    def _encodeOps(self, ops):
        opsDicts = []
        for op in ops:
            codec = self.findOpCodec(op.action)
            if not codec:
                raise TYBizException(-1, 'Unknown action: %s' % (op.action))
            opsDicts.append(codec.encode(op))
        return opsDicts


