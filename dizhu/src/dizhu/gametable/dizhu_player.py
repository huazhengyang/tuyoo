# coding=UTF-8
'''
'''
from freetime.util import log as ftlog
from poker.entity.game.tables.table_player import TYPlayer


__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]


class DizhuPlayer(TYPlayer):

    TUGUAN_TYPE_USERACT = 0  # 正常用户操作出牌
    TUGUAN_TYPE_TIMEOUT = 1  # 正常操作超时
    TUGUAN_TYPE_ALREADY_TUOGUAN = 2  # 已经托管后,再次出牌
    TUGUAN_TYPE_SYS_FAST_CARD = 3  # 系统调度快速出牌
    
    '''
    玩家的属性取得(缓存)和操作
    '''
    def __init__(self, table, seatIndex, copyData=None):
        self.inningCardNote = 0
        self.cardNoteCount = 0
        if copyData :
            super(DizhuPlayer, self).__init__(None, copyData.get('seatIndex'))
            self.clientId = copyData.get('clientId')
            self.datas = copyData.get('datas')
            self.__userId = copyData.get('userId')
            self.isSupportBuyin = copyData.get('isSupportBuyin')
            self.inningCardNote = copyData.get('inningCardNote', 0)
        else:
            super(DizhuPlayer, self).__init__(table, seatIndex)
            self.clear()


    def __str__(self):
        return 'DizhuPlayer(' + str(self.userId) + ')' + str(id(self))

    
    def __repr__(self):
        return 'DizhuPlayer(' + str(self.userId) + ')' + str(id(self))


    @property
    def userId(self):
        if self.table :
            return super(DizhuPlayer, self).userId
        else:
            return self.__userId

    
    def clear(self):
        '''清理玩家牌桌金币
        Args:
            isUsingScore：是否使用积分，是的话tableChip与Chip之间不做转换操作
        '''
        self.isUsingScore = 0
        self.clientId = ''
        self.inningCardNote = 0
        self.cardNoteCount = 0
        self.datas = {}
        if ftlog.is_debug():
            ftlog.debug('DizhuPlayer.clear player=', self)

    def openCardNote(self):
        if self.getCardNoteCount() <= 0:
            self.inningCardNote = 1
            return True
        return False
    
    def getCardNoteCount(self):
        if self.inningCardNote > 0:
            return 1
        return self.cardNoteCount
    
    def getWearedItems(self):
        return self.datas.get('wearedItems', [])
    
    def adjustCharm(self, incCharm):
        if 'charm' in self.datas :
            charm = self.datas['charm']
            charm = charm + incCharm
            charm = 0 if charm < 0 else charm
            self.datas['charm'] = charm


    @property
    def winrateWins(self):
        return self.datas['wins']
    
    
    @property
    def winratePlays(self):
        return self.datas['plays']
    

    def cleanDataAfterFirstUserInfo(self):
        '''
        桌面带入的提示, 只需要显示一次, 发送第一次table_info后, 就删除提示信息
        '''
        if 'buyinTip' in self.datas :
            self.datas['buyinTip'] = ''
        pass

    @property
    def gameClientVer(self):
        return self.datas.get('gameClientVer', 0)
    
    def initUser(self, isNextBuyin, isUsingScore):
        '''
        从redis里获取并初始化player数据, 远程操作
        '''
        from dizhu.servers.util.rpc import table_remote
        isSupportBuyin, cardNoteCount, clientId, datas = table_remote.doInitTableUserData(self.userId, self.table.bigRoomId,
                                                                  self.table.tableId, isNextBuyin,
                                                                  self.table.runConfig.buyinchip,
                                                                  self.table.isMatch)
        self.isUsingScore = isUsingScore
        self.clientId = clientId
        self.isSupportBuyin = isSupportBuyin
        self.cardNoteCount = cardNoteCount
        self.inningCardNote = 0
        self.datas = datas
        if ftlog.is_debug():
            ftlog.debug('DizhuPlayer->userId=', self.userId, 'seatIndex=', self.seatIndex,
                        'isUsingScore=', self.isUsingScore, 'isSupportBuyin=', self.isSupportBuyin,
                        'clientId=', self.clientId, 'cardNoteCount=', self.cardNoteCount,
                        'inningCardNote=', self.inningCardNote,
                        'data=', self.datas,
                        'player=', self)

    