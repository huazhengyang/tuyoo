# -*- coding:utf-8 -*-
'''
Created on 2016年9月2日

@author: zhaojiangang
'''
from dizhu.replay.gameround import GameReadyOp, GameShowOp, GameNextOp, \
    GameCallOp, GameJiabeiOp, GameStartOp, GameWildCardOp, GameAbortOp, \
    WinloseDetail, GameOutCardOp, GameWinloseOp, SeatWinloseDetail, Seat, \
    GameReplayRound, GameChatOp, GameRobotOp, GameSmiliesOp
from poker.entity.biz.exceptions import TYBizException


CUR_VERSION = 1
VER_NAME = 'ver'
ACTION_NAME = 'act'
SEAT_INDEX_NAME = 'seat'
TO_SEAT_INDEX_NAME = 'toseat'
SMILIE_NAME = 'smilie'
SMILIE_COUNT_NAME = 'count'
OUT_CARDS_NAME = 'cards'
TOTAL_MULTI_NAME = 'totalMulti'
BOMB_COUNT = 'nbomb'
IS_CHUNTIAN = 'isChuntian'
SEAT_CARDS_NAME = 'seatCards'
BASE_CARDS_NAME = 'baseCards'
WILD_CARD_NAME = 'wildCards'
DZ_SEAT_INDEX_NAME = 'dzSeat'
BASE_CARD_MULTI_NAME = 'bcMulti'
RANGPAI_MULTI_NAME = 'rpMulti'
CALL_MULTI_NAME = 'callMulti'
JIABEI_NAME = 'jiabei'
RANGPAI_NAME = 'rangpai'
CALL_NAME = 'call'
SHOW_MULTI_NAME = 'show'
GRAB_NAME = 'grab'
OPTIME_NAME = 'opTime'
SKILL_INFO_NAME = 'skill'
SEAT_DETAILS_NAME = 'seats'
WINLOSE_DETAIL_NAME = 'winloseDetail'
USERID_NAME = 'userId'
USERNAME_NAME = 'name'
SEX_NAME = 'sex'
HEAD_URL_NAME = 'purl'
VIP_LEVEL_NAME = 'vip'
CHIP_NAME = 'chip'
DELTA_CHIP_NAME = 'dChip'
FINAL_CHIP_NAME = 'fChip'
SCORE_NAME = 'score'
WEARED_ITEMS_NAME = 'wearedItems'
ROOMID_NAME = 'rid'
TABLEID_NAME = 'tid'
MATCHID_NAME = 'mid'
ROOMNAME_NAME = 'name'
PLAYMODE_NAME = 'pm'
ROOM_MULTI_NAME = 'base'
ROOM_FEE_NAME = 'fee'
TIMESTAMP_NAME = 'ts'
SEATS_NAME = 'seats'
OPS_NAME = 'ops'
DIZHU_SEAT_INDEX_NAME = 'dizhu'
DIZHU_WIN_NAME = 'dizhuWin'
SLAM_NAME = 'slam'
SLAM_MULTI_NAME = 'slamMulti'
WIN_STREAM_NAME = 'winS'
IS_FACE_NAME = 'isFace'
VOICE_INDEX_NAME = 'voiceIdx'
MSG_NAME = 'msg'
IS_ROBOT_NAME = 'isRobot'
NUMBER_NAME = 'num'

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
    
class GameReadyOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_CARDS_NAME:op.seatCards,
            BASE_CARDS_NAME:op.baseCards
        }
        
    def decode(self, data):
        return GameReadyOp(data[SEAT_CARDS_NAME], data[BASE_CARDS_NAME])
    
class GameChatOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            IS_FACE_NAME:op.isFace,
            VOICE_INDEX_NAME:op.voiceIdx,
            MSG_NAME:op.msg
        }
        
    def decode(self, data):
        return GameChatOp(data[SEAT_INDEX_NAME], data[IS_FACE_NAME], data[VOICE_INDEX_NAME], data[MSG_NAME])
    
class GameSmiliesOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            IS_FACE_NAME:op.isFace,
            VOICE_INDEX_NAME:op.voiceIdx,
            MSG_NAME:op.msg
        }
        
    def decode(self, data):
        return GameChatOp(data[SEAT_INDEX_NAME], data[IS_FACE_NAME], data[VOICE_INDEX_NAME], data[MSG_NAME])
    
class GameRobotOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            TO_SEAT_INDEX_NAME:op.toSeatIndex,
            SMILIE_NAME:op.smilie,
            SMILIE_COUNT_NAME:op.count,
            DELTA_CHIP_NAME:op.deltaChip,
            FINAL_CHIP_NAME:op.finalChip
        }
        
    def decode(self, data):
        return GameSmiliesOp(data[SEAT_INDEX_NAME],
                             data[TO_SEAT_INDEX_NAME],
                             data[SMILIE_NAME],
                             data[SMILIE_COUNT_NAME],
                             data[DELTA_CHIP_NAME],
                             data[FINAL_CHIP_NAME])
    
class GameShowOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            SHOW_MULTI_NAME:op.showMulti,
            TOTAL_MULTI_NAME:op.totalMulti
        }

    def decode(self, data):
        return GameShowOp(data[SEAT_INDEX_NAME],
                          data[SHOW_MULTI_NAME],
                          data[TOTAL_MULTI_NAME])
    
class GameNextOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            GRAB_NAME:op.grab,
            OPTIME_NAME:op.opTime
        }
        
    def decode(self, data):
        return GameNextOp(data[SEAT_INDEX_NAME],
                          data[GRAB_NAME],
                          data[OPTIME_NAME])
    
class GameCallOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            CALL_NAME:op.call,
            TOTAL_MULTI_NAME:op.totalMulti,
            RANGPAI_NAME:op.rangpai
        }
        
    def decode(self, data):
        return GameCallOp(data[SEAT_INDEX_NAME],
                          data[CALL_NAME],
                          data[TOTAL_MULTI_NAME],
                          data[RANGPAI_NAME])

class GameJiabeiOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            JIABEI_NAME:op.jiabei
        }
        
    def decode(self, data):
        return GameJiabeiOp(data[SEAT_INDEX_NAME],
                            data[JIABEI_NAME])
 
class GameStartOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            DZ_SEAT_INDEX_NAME:op.dizhuSeatIndex,
            SEAT_CARDS_NAME:op.seatCards,
            BASE_CARDS_NAME:op.baseCards,
            BASE_CARD_MULTI_NAME:op.baseCardMulti,
            TOTAL_MULTI_NAME:op.totalMulti
        }
        
    def decode(self, data):
        return GameStartOp(data[DZ_SEAT_INDEX_NAME],
                           data[SEAT_CARDS_NAME],
                           data[BASE_CARDS_NAME],
                           data[BASE_CARD_MULTI_NAME],
                           data[TOTAL_MULTI_NAME])
        
class GameWildCardOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            WILD_CARD_NAME:op.wildCard,
            SEAT_CARDS_NAME:op.seatCards,
            BASE_CARDS_NAME:op.baseCards
        }
    
    def decode(self, data):
        return GameWildCardOp(data[WILD_CARD_NAME],
                              data[SEAT_CARDS_NAME],
                              data[BASE_CARDS_NAME])
    
class GameOutCardOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            SEAT_INDEX_NAME:op.seatIndex,
            OUT_CARDS_NAME:op.outCards,
            TOTAL_MULTI_NAME:op.totalMulti
        }
        
    def decode(self, data):
        return GameOutCardOp(data[SEAT_INDEX_NAME],
                             data[OUT_CARDS_NAME],
                             data[TOTAL_MULTI_NAME])
    
class GameAbortOpCodecDict(BaseCodec):
    def encode(self, op):
        return {
            ACTION_NAME:op.action
        }
    
    def decode(self, data):
        return GameAbortOp()
        
class SeatWinloseDetailCodecDict(BaseCodec):
    def encode(self, obj):
        return {
            SKILL_INFO_NAME:obj.skillInfo,
            TOTAL_MULTI_NAME:obj.totalMulti,
            WIN_STREAM_NAME:obj.winStreak,
            DELTA_CHIP_NAME:obj.deltaChip,
            FINAL_CHIP_NAME:obj.finalChip
        }
    
    def decode(self, data):
        return SeatWinloseDetail(data[SKILL_INFO_NAME],
                                 data[TOTAL_MULTI_NAME],
                                 data[WIN_STREAM_NAME],
                                 data[DELTA_CHIP_NAME],
                                 data[FINAL_CHIP_NAME])
    
class WinloseDetailCodecDict(BaseCodec):
    seatWinloseDetailCodec = SeatWinloseDetailCodecDict()
    
    def encode(self, obj):
        return {
            BOMB_COUNT:obj.bombCount,
            IS_CHUNTIAN:obj.isChuntian,
            SHOW_MULTI_NAME:obj.showMulti,
            BASE_CARD_MULTI_NAME:obj.baseCardMulti,
            RANGPAI_MULTI_NAME:obj.rangpaiMulti,
            CALL_MULTI_NAME:obj.callMulti,
            TOTAL_MULTI_NAME:obj.totalMulti,
            DIZHU_WIN_NAME:obj.dizhuWin,
            SLAM_NAME:obj.slam,
            SLAM_MULTI_NAME:obj.slamMulti,
            SEAT_DETAILS_NAME:self.seatWinloseDetailCodec.encodeList(obj.seatWinloseDetails)
        }
    
    def decode(self, data):
        return WinloseDetail(data[BOMB_COUNT],
                             data[IS_CHUNTIAN],
                             data[SHOW_MULTI_NAME],
                             data[BASE_CARD_MULTI_NAME],
                             data[RANGPAI_MULTI_NAME],
                             data[CALL_MULTI_NAME],
                             data[TOTAL_MULTI_NAME],
                             data[DIZHU_WIN_NAME],
                             data[SLAM_NAME],
                             data[SLAM_MULTI_NAME],
                             self.seatWinloseDetailCodec.decodeList(data[SEAT_DETAILS_NAME]))
     
class GameWinloseOpCodecDict(BaseCodec):
    winloseDetailCodecDict = WinloseDetailCodecDict()
    def encode(self, op):
        return {
            ACTION_NAME:op.action,
            WINLOSE_DETAIL_NAME:self.winloseDetailCodecDict.encode(op.winloseDetail)
        }
    
    def decode(self, data):
        return GameWinloseOp(self.winloseDetailCodecDict.decode(data[WINLOSE_DETAIL_NAME]))

class SeatCodecDict(BaseCodec):
    def encode(self, obj):
        return {
            USERID_NAME:obj.userId,
            USERNAME_NAME:obj.userName,
            SEX_NAME:obj.sex,
            VIP_LEVEL_NAME:obj.vipLevel,
            CHIP_NAME:obj.chip,
            SCORE_NAME:obj.score,
            HEAD_URL_NAME:obj.headUrl,
            WEARED_ITEMS_NAME:obj.wearedItems
        }
    
    def decode(self, data):
        return Seat(data[USERID_NAME],
                    data[USERNAME_NAME],
                    data[SEX_NAME],
                    data[VIP_LEVEL_NAME],
                    data[CHIP_NAME],
                    data[SCORE_NAME],
                    data[HEAD_URL_NAME],
                    data[WEARED_ITEMS_NAME])
    
class GameRoundCodecDict(BaseCodec):
    opCodecMap = {
        GameReadyOp.ACTION:GameReadyOpCodecDict(),
        GameChatOp.ACTION:GameChatOpCodecDict(),
        GameRobotOp.ACTION:GameRobotOpCodecDict(),
        GameSmiliesOp.ACTION:GameSmiliesOpCodecDict(),
        GameShowOp.ACTION:GameShowOpCodecDict(),
        GameNextOp.ACTION:GameNextOpCodecDict(),
        GameCallOp.ACTION:GameCallOpCodecDict(),
        GameJiabeiOp.ACTION:GameJiabeiOpCodecDict(),
        GameStartOp.ACTION:GameStartOpCodecDict(),
        GameWildCardOp.ACTION:GameWildCardOpCodecDict(),
        GameOutCardOp.ACTION:GameOutCardOpCodecDict(),
        GameAbortOp.ACTION:GameAbortOpCodecDict(),
        GameWinloseOp.ACTION:GameWinloseOpCodecDict()
    }
    
    seatCodec = SeatCodecDict()

    def encode(self, obj):
        return {
            VER_NAME:1,
            NUMBER_NAME:obj.number,
            ROOMID_NAME:obj.roomId,
            TABLEID_NAME:obj.tableId,
            MATCHID_NAME:obj.matchId,
            ROOMNAME_NAME:obj.roomName,
            PLAYMODE_NAME:obj.playMode,
            GRAB_NAME:obj.grab,
            ROOM_MULTI_NAME:obj.roomMulti,
            ROOM_FEE_NAME:obj.roomFee,
            TIMESTAMP_NAME:obj.timestamp,
            SEATS_NAME:self.seatCodec.encodeList(obj.seats),
            OPS_NAME:self._encodeOps(obj.ops),
            DIZHU_SEAT_INDEX_NAME:obj.dizhuSeatIndex
        }
    
    def decode(self, data):
        ver = data.get(VER_NAME)
        if ver != 1:
            raise TYBizException('不支持的版本')
        seats = self.seatCodec.decodeList(data[SEATS_NAME])
        dizhuSeatIndex = data[DIZHU_SEAT_INDEX_NAME]
        ret = GameReplayRound(data[NUMBER_NAME],
                              data[ROOMID_NAME],
                              data[TABLEID_NAME],
                              data[MATCHID_NAME],
                              data[ROOMNAME_NAME],
                              data[PLAYMODE_NAME],
                              data[GRAB_NAME],
                              data[ROOM_MULTI_NAME],
                              data[ROOM_FEE_NAME],
                              seats,
                              data[TIMESTAMP_NAME])
        ops = self._decodeOps(data[OPS_NAME])
        ret.dizhuSeatIndex = dizhuSeatIndex
        ret._ops = ops
        return ret
    
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
    
    def _decodeOps(self, opDicts):
        ops  = []
        for d in opDicts:
            codec = self.findOpCodec(d['act'])
            if not codec:
                raise TYBizException(-1, 'Unknown action: %s' % (d['action']))
            ops.append(codec.decode(d))
        return ops
            
    
