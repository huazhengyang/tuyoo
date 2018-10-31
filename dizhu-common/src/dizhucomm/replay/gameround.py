# -*- coding:utf-8 -*-
'''
Created on 2016年8月15日

@author: zhaojiangang
'''

class GameRoundOp(object):
    def __init__(self, action):
        self._action = action
    
    @property
    def action(self):
        return self._action

class GameReadyOp(GameRoundOp):
    ACTION = 'game_ready'
    def __init__(self, seatCards, baseCards):
        super(GameReadyOp, self).__init__(self.ACTION)
        self.seatCards = seatCards
        self.baseCards = baseCards
    
class GameChatOp(GameRoundOp):
    ACTION = 'chat'
    def __init__(self, seatIndex, isFace, voiceIdx, msg):
        super(GameChatOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.isFace = isFace
        self.voiceIdx = voiceIdx
        self.msg = msg
       
class GameSmiliesOp(GameRoundOp):
    ACTION = 'smilies'
    def __init__(self, seatIndex, toSeatIndex, smilie, count, deltaChip, finalChip):
        super(GameSmiliesOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.toSeatIndex = toSeatIndex
        self.smilie = smilie
        self.count = count
        self.deltaChip = deltaChip
        self.finalChip = finalChip
        
class GameRobotOp(GameRoundOp):
    ACTION = 'rb'
    def __init__(self, seatIndex, isRobot):
        super(GameRobotOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.isRobot = isRobot
         
class GameShowOp(GameRoundOp):
    ACTION = 'show'
    def __init__(self, seatIndex, showMulti, totalMulti):
        super(GameShowOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.showMulti = showMulti
        self.totalMulti = totalMulti
    
class GameNextOp(GameRoundOp):
    ACTION = 'next'
    def __init__(self, seatIndex, grab, opTime):
        super(GameNextOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.grab = grab
        self.opTime = opTime

class GameCallOp(GameRoundOp):
    ACTION = 'call'
    def __init__(self, seatIndex, call, totalMulti, rangpai=0):
        super(GameCallOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.call = call
        self.totalMulti = totalMulti
        self.rangpai = rangpai
    
class GameJiabeiOp(GameRoundOp):
    ACTION = 'jiabei'
    def __init__(self, seatIndex, jiabei):
        super(GameJiabeiOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.jiabei = jiabei

class GameStartOp(GameRoundOp):
    ACTION = 'game_start'
    def __init__(self, dizhuSeatIndex, seatCards, baseCards, baseCardMulti, totalMulti):
        super(GameStartOp, self).__init__(self.ACTION)
        self.dizhuSeatIndex = dizhuSeatIndex
        self.seatCards = seatCards
        self.baseCards = baseCards
        self.baseCardMulti = baseCardMulti
        self.totalMulti = totalMulti
    
class GameWildCardOp(GameRoundOp):
    ACTION = 'wild_card'
    def __init__(self, wildCard, seatCards, baseCards):
        super(GameWildCardOp, self).__init__(self.ACTION)
        self.wildCard = wildCard
        self.seatCards = seatCards
        self.baseCards = baseCards
    
class GameOutCardOp(GameRoundOp):
    ACTION = 'card'
    def __init__(self, seatIndex, outCards, totalMulti):
        super(GameOutCardOp, self).__init__(self.ACTION)
        self.seatIndex = seatIndex
        self.outCards = outCards
        self.totalMulti = totalMulti
    
class GameAbortOp(GameRoundOp):
    ACTION = 'game_abort'
    def __init__(self):
        super(GameAbortOp, self).__init__(self.ACTION)
    
class SeatWinloseDetail(object):
    def __init__(self, skillInfo, totalMulti, winStreak, deltaChip, finalChip):
        self.skillInfo = skillInfo
        self.totalMulti = totalMulti
        self.winStreak = winStreak
        self.deltaChip = deltaChip
        self.finalChip = finalChip
        
class WinloseDetail(object):
    def __init__(self, result, bombCount, isChuntian,
                 showMulti, baseCardMulti,
                 rangpaiMulti, callMulti, totalMulti, dizhuWin,
                 slam, slamMulti,
                 seatWinloseDetails):
        self.result = result
        self.bombCount = bombCount
        self.isChuntian = isChuntian
        self.showMulti = showMulti
        self.baseCardMulti = baseCardMulti
        self.rangpaiMulti = rangpaiMulti
        self.callMulti = callMulti
        self.totalMulti = totalMulti
        self.dizhuWin = dizhuWin
        self.slam = slam
        self.slamMulti = slamMulti
        self.seatWinloseDetails = seatWinloseDetails
        
class GameWinloseOp(GameRoundOp):
    ACTION = 'game_win'
    def __init__(self, winloseDetail):
        super(GameWinloseOp, self).__init__(self.ACTION)
        self.winloseDetail = winloseDetail
    
class Seat(object):
    def __init__(self,
                 userId,
                 userName,
                 sex,
                 vipLevel,
                 chip,
                 score,
                 headUrl,
                 wearedItems):
        self.userId = userId
        self.userName = userName
        self.sex = sex
        self.vipLevel = vipLevel
        self.chip = chip
        self.score = score
        self.headUrl = headUrl
        self.wearedItems = wearedItems
        
class GameReplayRound(object):
    def __init__(self, number, roomId, tableId, matchId, replayMatchType,
                 roomName, playMode, grab, roomMulti,
                 roomFee, seats, timestamp):
        self.roundId = '%s_%s' % (roomId, number)
        self.roomId = roomId
        self.tableId = tableId
        self.matchId = matchId
        self.replayMatchType = replayMatchType
        self.roomName = roomName
        self.playMode = playMode
        self.grab = grab
        self.roomMulti = roomMulti
        self.roomFee = roomFee
        self.timestamp = timestamp
        self.winloseDetail = None
        self.dizhuSeatIndex = None
        self._seats = seats
        self._ops = []
        self.number = number
        self.gameOverTimestamp = None
    
    @property
    def seats(self):
        return self._seats
        
    @property
    def ops(self):
        return self._ops

    def findSeatByUserId(self, userId):
        for seat in self._seats:
            if seat.userId == userId:
                return seat
        return None
    
    def gameReady(self, seatCards, baseCards):
        self._ops.append(GameReadyOp(seatCards, baseCards))
    
    def chat(self, seatIndex, isFace, voiceIdx, msg):
        self._ops.append(GameChatOp(seatIndex, isFace, voiceIdx, msg))
        
    def sendSmilies(self, seatIndex, toSeatIndex, smilie, count, deltaChip, finalChip):
        self._ops.append(GameSmiliesOp(seatIndex, toSeatIndex, smilie, count, deltaChip, finalChip))
        
    def robot(self, seatIndex, isRobot):
        self._ops.append(GameRobotOp(seatIndex, isRobot))
        
    def call(self, seatIndex, call, totalMulti, rangpai=0):
        self._ops.append(GameCallOp(seatIndex, call, totalMulti, rangpai))
    
    def show(self, seatIndex, showMulti, totalMulti):
        self._ops.append(GameShowOp(seatIndex, showMulti, totalMulti))
    
    def jiabei(self, seatIndex, jiabei):
        self._ops.append(GameJiabeiOp(seatIndex, jiabei))
        
    def gameStart(self, dizhuSeatIndex, seatCards, baseCards, baseCardMulti, totalMulti):
        self.dizhuSeatIndex = dizhuSeatIndex
        self._ops.append(GameStartOp(dizhuSeatIndex, seatCards, baseCards, baseCardMulti, totalMulti))
    
    def wildCard(self, wildCard, seatCards, baseCards):
        self._ops.append(GameWildCardOp(wildCard, seatCards, baseCards))
    
    def next(self, nextSeatIndex, grab, opTime):
        self._ops.append(GameNextOp(nextSeatIndex, grab, opTime))
    
    def outCard(self, seatIndex, outCards, totalMulti):
        self._ops.append(GameOutCardOp(seatIndex, outCards, totalMulti))
    
    def gameAbort(self):
        self._ops.append(GameAbortOp())
    
    def gameWinlose(self, winloseDetail):
        self.winloseDetail = winloseDetail
        self._ops.append(GameWinloseOp(winloseDetail))
        

