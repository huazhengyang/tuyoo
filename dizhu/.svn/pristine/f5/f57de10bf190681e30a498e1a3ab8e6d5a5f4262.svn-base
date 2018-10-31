# coding=UTF-8
'''
'''
from poker.entity.game.tables.table_seat import TYSeat

__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]


SEAT_DZ_ROBOT = 2  # 托管状态,0表示未托管,1表示托管
SEAT_DZ_CALL = 3  # -1表示还没叫，0表示不叫，1表示1分，2＝2分，3＝3分
SEAT_DZ_CALL2 = 4  # 抢地主时，标示是否抢过, -1表示还没抢, 0表示不抢，1表示抢
SEAT_DZ_CARD = 5  # 0~53数字list
SEAT_DZ_OUTCARD_COUNT = 6  # 出牌数目，用于计算春天等
SEAT_DZ_TIMEOUT_COUNT = 7  # 超时未操作次数，3次自动进入托管状态
SEAT_DZ_SHOW = 8  # 本座位是否明牌
SEAT_DZ_COUPON_CARD = 9
SEAT_DZ_RECIVE_VOICE = 10
SEAT_DZ_ROBOT_CARD_COUNT = 11  # 托管时，当前玩家的手里的剩余牌数

SEAT_DZ_TUOGUAN_COUNT = 12  # 托管时，当前玩家的手里的剩余牌数
SEAT_DZ_OUTCARD = 13  # 0~53数字list zyy 纪录玩家这次出的什么牌
SEAT_DZ_LASTOUTCARD = 14  # 0~53数字list zyy 纪录玩家上一次出的什么牌

tdz_seat_title = ['uid', 'state', 'robot', 'call', 'call2', 'card',
                  'outcnt', 'timeoutcnt', 'show', 'couponcard',
                  'voice', 'robotcards']

tdz_seat_default = [0, TYSeat.SEAT_STATE_WAIT, 0, -1, -1, [], 0, 0, 0, [0, 0, 0], 0, -1, 0,[],[]]

class DizhuSeat(TYSeat):
    def __init__(self, table, copyData=None):
        super(DizhuSeat, self).__init__(table)
        self.seatMulti = 0
        self.huanpaiOut = None
        self.huanpaiIn = None
        self.online = False
        if copyData :
            self.replace(copyData)
        else:
            self.clear(0)

    def clearStatus(self):
        userId = self.userId
        self.update(tdz_seat_default)
        self.seatMulti = 0
        self.userId = userId
        self.huanpaiOut = None
        self.huanpaiIn = None
        
    def clear(self, userId=0):
        self.update(tdz_seat_default)
        self.userId = userId
        self.seatMulti = 0
        self.huanpaiOut = None
        self.huanpaiIn = None

    def toInfoDict(self):
        ret = dict(zip(tdz_seat_title, self))
        ret['double'] = 0 if self.seatMulti == 0 else 1
        ret['online'] = 1 if self.online else 0
        ret['hpOut'] = self.huanpaiOut if self.huanpaiOut else []
        ret['hpIn'] = self.huanpaiIn if self.huanpaiIn else []
        return ret


    @property
    def isRobot(self):
        return self[SEAT_DZ_ROBOT]
    

    @isRobot.setter
    def isRobot(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_ROBOT] = value


    @property
    def tuoguanCount(self):
        return self[SEAT_DZ_TUOGUAN_COUNT]
    

    @tuoguanCount.setter
    def tuoguanCount(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_TUOGUAN_COUNT] = value


    @property
    def call123(self):
        return self[SEAT_DZ_CALL]
    

    @call123.setter
    def call123(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_CALL] = value


    @property
    def callGrab(self):
        return self[SEAT_DZ_CALL2]
    

    @callGrab.setter
    def callGrab(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_CALL2] = value


    @property
    def cards(self):
        return self[SEAT_DZ_CARD]
    

    @cards.setter
    def cards(self, value):
        assert(isinstance(value, (list, tuple)))
        self[SEAT_DZ_CARD] = value

    @property
    def outCards(self):
        return self[SEAT_DZ_OUTCARD]

    @outCards.setter
    def outCards(self, value):
        assert (isinstance(value, (list, tuple)))
        self[SEAT_DZ_OUTCARD] = value

    @property
    def lastOutCards(self):
        return self[SEAT_DZ_LASTOUTCARD]

    @lastOutCards.setter
    def lastOutCards(self, value):
        assert (isinstance(value, (list, tuple)))
        self[SEAT_DZ_LASTOUTCARD] = value


    @property
    def outCardCount(self):
        return self[SEAT_DZ_OUTCARD_COUNT]
    

    @outCardCount.setter
    def outCardCount(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_OUTCARD_COUNT] = value


    @property
    def timeOutCount(self):
        return self[SEAT_DZ_TIMEOUT_COUNT]
    

    @timeOutCount.setter
    def timeOutCount(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_TIMEOUT_COUNT] = value


    @property
    def isShow(self):
        return self[SEAT_DZ_SHOW]
    

    @isShow.setter
    def isShow(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_SHOW] = value


    @property
    def couponCard(self):
        return self[SEAT_DZ_COUPON_CARD]
    

    @couponCard.setter
    def couponCard(self, value):
        assert(isinstance(value, (list, tuple)))
        self[SEAT_DZ_COUPON_CARD] = value


    @property
    def isReciveVoice(self):
        return self[SEAT_DZ_RECIVE_VOICE]
    

    @isReciveVoice.setter
    def isReciveVoice(self, value):
        self[SEAT_DZ_RECIVE_VOICE] = 1 if value else 0


    @property
    def robotCardCount(self):
        return self[SEAT_DZ_ROBOT_CARD_COUNT]


    @robotCardCount.setter
    def robotCardCount(self, value):
        assert(isinstance(value, int))
        self[SEAT_DZ_ROBOT_CARD_COUNT] = value

