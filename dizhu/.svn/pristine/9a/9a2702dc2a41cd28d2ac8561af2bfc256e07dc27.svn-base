# coding=UTF-8

from poker.entity.game.tables.table_state import TYTableState


__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]


TABLEDZ_STAT_DIZHU = 1  # 地主的座位号，从1开始
TABLEDZ_STAT_BASECARD = 2  # 3张底牌列表
TABLEDZ_STAT_TOPCARD = 3  # 最后出的牌,用于校验
TABLEDZ_STAT_TOPSEAT = 4  # 最后出牌的座位，用于校验等
TABLEDZ_STAT_CALL = 5  # 叫的分数,用于算分
TABLEDZ_STAT_NOWOP = 6  # 当前操作者座位号，从1开始
TABLEDZ_STAT_BOMB = 7  # 炸弹次数，用于算分加倍
TABLEDZ_STAT_CHUNTIAN = 8  # 春天标志，用于算分加倍
TABLEDZ_STAT_SHOW = 9  # 明牌加倍数，目前取1, 2，5三种倍数
TABLEDZ_STAT_SUPER = 10  # 超级加倍，第一版不实现
TABLEDZ_STAT_BCMULTI = 11  # 底牌加倍
TABLEDZ_STAT_CALLSTR = 12  # 用于实现叫地主抢地主的逻辑
TABLEDZ_STAT_FIRSTSHOW = 13  # 首先明牌开始的座位号
TABLEDZ_STAT_CARD_CRC = 14  # 出牌的校验序号
TABLEDZ_STAT_RANGPAI = 15  # ???
TABLEDZ_STAT_GRAB_CARD = 16  # ???
TABLEDZ_STAT_KICKOUT_CARD = 17  # ???
TABLEDZ_STAT_RANGPAI_MULTI = 18  # ???
TABLEDZ_STAT_WILDCARD = 19  # 用于返回客户端显示的癞子牌

TABLEDZ_STAT_GOOD_SEATID = 20  # 具有好牌点的桌位ID(不返回到客户端)
TABLEDZ_STAT_BASE_CARD_TYPE = 21  # 底牌的牌型(不返回到客户端)
TABLEDZ_STAT_RANGPAI_MULTI_WINLOSE = 22 # 最终牌局结束时二斗计算的让牌的倍率

TABLEDZ_STAT_WILDCARD_BIG = 22  # 用于计算的癞子牌
TABLEDZ_STAT_TOP_VALID_CARD = 23  # 最后一手牌的牌型对象(不返回到客户端, object对象, 无法序列化)

tdz_stat_title = ['state', 'dizhu', 'basecard', 'topcard', 'topseat',
                  'call', 'nowop', 'bomb', 'chuntian', 'show', 'super',
                  'bcmulti', 'callstr', 'firstshow', 'ccrc',
                  'rangpai', 'grabCard', 'kickoutCard', 'rangpaiMulti', 'wildcard']

tdz_stat_title2 = ['goodSeatId', 'baseCardType', 'rangpaiMultiWinLose']


tdz_stat_default = [TYTableState.TABLE_STATE_IDEL, 0, [], [], 0,
                    - 1, 0, 0, 1, 1, 1,
                    1, '', 0, 0,
                    0, -1, [], 1, -1, 0, 0, 1, -1, None] 


class DizhuState(object):


    TABLE_STATE_IDEL = TYTableState.TABLE_STATE_IDEL
    TABLE_STATE_CALLING = 15
    TABLE_STATE_NM_DOUBLE = 16
    TABLE_STATE_DIZHU_DOUBLE = 17
    TABLE_STATE_PLAYING = 20
    
    PLAYING_STATE_NM_JIABEI = 1
    PLAYING_STATE_DZ_JIABEI = 2
    PLAYING_STATE_HUANPAI = 3
    PLAYING_STATE_CHUPAI = 4
    
    def __init__(self, table, copyData=None):
        self.playingState = self.PLAYING_STATE_CHUPAI
        if copyData : 
            self.tystate = copyData
        else:
            self.table = table
            self.tystate = table.state
            self.clear()
        
    def __str__(self):
        return str(self.tystate)

    
    def __repr__(self):
        return repr(self.tystate)

    
    def clear(self):
        self._topValidCards = None
        self.playingState = self.PLAYING_STATE_CHUPAI
        self.tystate.update(tdz_stat_default)
        self.tystate[TABLEDZ_STAT_RANGPAI_MULTI] = self.table.runConfig.rangpaiMultiType


    def toInfoDict(self):
        ret = dict(zip(tdz_stat_title, self.tystate))
        ret['playingState'] = self.playingState
        return ret
    
    def toInfoDictExt(self):
        ret = dict(zip(tdz_stat_title + tdz_stat_title2, self.tystate))
        ret['playingState'] = self.playingState
        return ret

    @property
    def state(self):
        return self.tystate[TYTableState.INDEX_TABLE_STATE]


    @state.setter
    def state(self, state):
        self.tystate.state = state


    @property
    def diZhu(self):
        return self.tystate[TABLEDZ_STAT_DIZHU]
    

    @diZhu.setter
    def diZhu(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_DIZHU] = value


    @property
    def baseCardList(self):
        return self.tystate[TABLEDZ_STAT_BASECARD]


    @baseCardList.setter
    def baseCardList(self, value):
        assert(isinstance(value, (list, tuple)))
        self.tystate[TABLEDZ_STAT_BASECARD] = value


    @property
    def topCardList(self):
        return self.tystate[TABLEDZ_STAT_TOPCARD]
    
    
    @topCardList.setter
    def topCardList(self, value):
        assert(isinstance(value, (list, tuple)))
        self.tystate[TABLEDZ_STAT_TOPCARD] = value


    @property
    def topSeatId(self):
        return self.tystate[TABLEDZ_STAT_TOPSEAT]


    @topSeatId.setter
    def topSeatId(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_TOPSEAT] = value


    @property
    def callGrade(self):
        return self.tystate[TABLEDZ_STAT_CALL]


    @callGrade.setter
    def callGrade(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_CALL] = value


    @property
    def nowOper(self):
        return self.tystate[TABLEDZ_STAT_NOWOP]


    @nowOper.setter
    def nowOper(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_NOWOP] = value


    @property
    def bomb(self):
        return self.tystate[TABLEDZ_STAT_BOMB]


    @bomb.setter
    def bomb(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_BOMB] = value


    @property
    def chuntian(self):
        return self.tystate[TABLEDZ_STAT_CHUNTIAN]


    @chuntian.setter
    def chuntian(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_CHUNTIAN] = value


    @property
    def show(self):
        return self.tystate[TABLEDZ_STAT_SHOW]


    @show.setter
    def show(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_SHOW] = value

    
    @property
    def superMulti(self):
        return self.tystate[TABLEDZ_STAT_SUPER]


    @superMulti.setter
    def superMulti(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_SUPER] = value


    @property
    def baseCardMulti(self):
        return self.tystate[TABLEDZ_STAT_BCMULTI]


    @baseCardMulti.setter
    def baseCardMulti(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_BCMULTI] = value


    @property
    def callStr(self):
        return self.tystate[TABLEDZ_STAT_CALLSTR]


    @callStr.setter
    def callStr(self, value):
        assert(isinstance(value, (str, unicode)))
        self.tystate[TABLEDZ_STAT_CALLSTR] = value


    @property
    def firstShow(self):
        return self.tystate[TABLEDZ_STAT_FIRSTSHOW]


    @firstShow.setter
    def firstShow(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_FIRSTSHOW] = value


    @property
    def cardCrc(self):
        return self.tystate[TABLEDZ_STAT_CARD_CRC]


    @cardCrc.setter
    def cardCrc(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_CARD_CRC] = value


    @property
    def rangPai(self):
        return self.tystate[TABLEDZ_STAT_RANGPAI]


    @rangPai.setter
    def rangPai(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_RANGPAI] = value


    @property
    def grabCard(self):
        return self.tystate[TABLEDZ_STAT_GRAB_CARD]


    @grabCard.setter
    def grabCard(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_GRAB_CARD] = value


    @property
    def kickOutCardList(self):
        return self.tystate[TABLEDZ_STAT_KICKOUT_CARD]


    @kickOutCardList.setter
    def kickOutCardList(self, value):
        assert(isinstance(value, (list, tuple)))
        self.tystate[TABLEDZ_STAT_KICKOUT_CARD] = value


    @property
    def rangPaiMulti(self):
        return self.tystate[TABLEDZ_STAT_RANGPAI_MULTI]


#     @rangPaiMulti.setter
#     def rangPaiMulti(self, value):
#         这事一个只读状态, 为了兼容老协议而存在
#         assert(isinstance(value, int))
#         self.tystate[TABLEDZ_STAT_RANGPAI_MULTI] = value

    @property
    def rangpaiMultiWinLose(self):
        return self.tystate[TABLEDZ_STAT_RANGPAI_MULTI_WINLOSE]


    @rangpaiMultiWinLose.setter
    def rangpaiMultiWinLose(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_RANGPAI_MULTI_WINLOSE] = value

    
    @property
    def goodSeatId(self):
        return self.tystate[TABLEDZ_STAT_GOOD_SEATID]


    @goodSeatId.setter
    def goodSeatId(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_GOOD_SEATID] = value


    @property
    def baseCardType(self):
        return self.tystate[TABLEDZ_STAT_BASE_CARD_TYPE]


    @baseCardType.setter
    def baseCardType(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_BASE_CARD_TYPE] = value


    @property
    def topValidCard(self):
        return self.tystate[TABLEDZ_STAT_TOP_VALID_CARD]


    @topValidCard.setter
    def topValidCard(self, value):
        self.tystate[TABLEDZ_STAT_TOP_VALID_CARD] = value


    @property
    def wildCard(self):
        return self.tystate[TABLEDZ_STAT_WILDCARD]


    @wildCard.setter
    def wildCard(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_WILDCARD] = value


    @property
    def wildCardBig(self):
        return self.tystate[TABLEDZ_STAT_WILDCARD_BIG]


    @wildCardBig.setter
    def wildCardBig(self, value):
        assert(isinstance(value, int))
        self.tystate[TABLEDZ_STAT_WILDCARD_BIG] = value
