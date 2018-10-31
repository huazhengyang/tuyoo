# -*- coding:utf-8 -*-
'''
Created on 2016年12月22日

@author: zhaojiangang
'''

class DizhuTableConf(object):
    def __init__(self, datas):
        self._datas = datas
        
    @property
    def datas(self):
        return self._datas
    
    @property
    def readyTimeout(self):
        return self._datas.get('readyTimeout', 20)

    def autoReady(self):
        return self._datas.get('autoReady', 0)
    
    @property
    def optime(self):
        return self._datas.get('optime', 15)
    
    @property
    def optimeFirst(self):
        return self._datas.get('optimeFirst', self.optime + 12)
    
    @property
    def optimeOnlyOneCard(self):
        return self._datas.get('optimeOnlyOneCard', 1)
    
    @property
    def optimeDoubleKing(self):
        return self._datas.get('optimeDoubleKing', 1)
    
    @property
    def optimeCall(self):
        return self.optime
    
    @property
    def optimeTuoguan(self):
        return self._datas.get('optimeTuoguan', 1)
    
    @property
    def optimeOutCard(self):
        return self.optime
    
    @property
    def optimeJiabei(self):
        return self._datas.get('optimeJiabei', 25)
    
    @property
    def optimeHuanpai(self):
        return self._datas.get('optimeHuanpai', 25)
    
    @property
    def basebet(self):
        return self._datas.get('basebet', 1)

    @property
    def basemulti(self):
        return self._datas.get('basemulti', 1)

    @property
    def roomMutil(self):
        return self._datas['roomMutil']
    
    @property
    def roomMulti(self):
        return self._datas['roomMutil']
    
    @property
    def maxCoin(self):
        return self._datas['maxCoin']

    @property
    def minCoin(self):
        return self._datas['minCoin']
    
    @property
    def buyinchip(self):
        return self._datas.get('buyinchip', 0)
    
    @property
    def hasrobot(self):
        return self._datas.get('hasrobot', 0)

    @property
    def robotTimes(self):
        return self._datas.get('robottimes', 0)
    
    @property
    def baseScore(self):
        if 'baseScore' in self._datas:
            return self._datas.get('baseScore')
        return self.basebet * self.basemulti * self.roomMutil

    @property
    def firstCallDelayTimes(self):
        return self._datas.get('firstCallDelayTimes', 0.1)
    
    @property
    def jiabei(self):
        return self._datas.get('jiabei', 0)
    
    @jiabei.setter
    def jiabei(self, value):
        self._datas['jiabei'] = value
        
    @property
    def goodCard(self):
        return self._datas.get('goodCard', 0)
    
    @goodCard.setter
    def goodCard(self, value):
        self._datas['goodCard'] = value
    
    @property
    def lucky(self):
        return self._datas.get('lucky', 0)
    
    @property
    def sendCardConf(self):
        return self._datas.get('sendCard', {})
    
    @property
    def huanpaiCardCount(self):
        return self._datas.get('huanpaiCardCount', 0)
    
    @property
    def rangpaiMultiType(self):
        return self._datas.get('rangpaiMultiType', 1)
    
    @property
    def punishCardCount(self):
        return self._datas.get('punishCardCount', 2)
    
    @property
    def firstCallValue(self):
        return self.datas.get('firstCallValue', 1)
    
    @property
    def maxSeatN(self):
        return self._datas.get('maxSeatN', 3)
    
    @property
    def autochange(self):
        return self._datas.get('autochange', 1)
    
    @property
    def canchat(self):
        return self._datas.get('canchat', 0)
    
    @property
    def cardNote(self):
        '''
        是否开启记牌器
        '''
        return self._datas.get('cardNote', 1)
    
    @property
    def coin2chip(self):
        return self._datas.get('coin2chip', 1)
    
    @property
    def unticheat(self):
        return self._datas.get('unticheat', 0)

    @property
    def mixShowChip(self):
        return self._datas.get('mixShowChip', 0)
    
    @property
    def passtime(self):
        return self._datas.get('passtime', 5)

    @property
    def cardNoteChip(self):
        return self._datas.get('cardNoteChip', 0)

    @property
    def cardNoteDiamond(self):
        return self._datas.get('cardNoteDiamond', 0)

    @property
    def cardNoteChipConsumeUserChip(self):
        return self._datas.get('cardNoteChipConsumeUserChip', 0)
    
    @property
    def cardNoteOpenConf(self):
        return self._datas.get('cardNoteOpen', {
                                'chip': {
                                    'desc': '本局记牌器使用费: ${consumeChip}金币',
                                    'desc.chip_not_enough': '场外金币不足，\n不能使用记牌器喔~',
                                    'desc.month_card': '购买贵族月卡可免费使用记牌器'
                                },
                                'diamond': {
                                    'desc': '今日记牌器使用费:\n ${consumeChip}钻石',
                                    'desc.chip_not_enough': '钻石不足，\n不能使用记牌器喔~',
                                    'desc.month_card': '购买贵族月卡可免费使用记牌器'
                                }
                            })

    @property
    def gslam(self):
        return self._datas.get('gslam', 128)
    
    @property
    def grab(self):
        return self._datas.get('grab', 0)
    
    @property
    def showCard(self):
        return self.datas['showCard']
    
    @property
    def roomFee(self):
        return self._datas.get('roomFee', 0)

    @property
    def fixedRoomFee(self):
        return self._datas.get('fixedRoomFee', 0)

    @property
    def optimedis(self):
        return self._datas.get('optimedis', '您的上家网络不好，等他一会儿吧')

    @property
    def optimeDisbind(self):
        return self._datas.get('optimeDisbind', 90)
    
    @property
    def optimeCallShow(self):
        return self._datas.get('optimeCallShow', 0)

    @property
    def autoPlay(self):
        return self._datas.get('autoPlay', 0)

    @property
    def canQuit(self):
        return self._datas.get('canQuit', 0)
    
    @property
    def optimeCardShow(self):
        return self._datas.get('optimeCardShow', 0)
    
    @property
    def optimeJiabeiShow(self):
        return self._datas.get('optimeJiabeiShow', 0)
    
    @property
    def optimeHuanpaiShow(self):
        return self._datas.get('optimeHuanpaiShow', 0)
    
    @property
    def interruptWinStreakWhenAbort(self):
        return self._datas.get('interruptWinStreakWhenAbort', 0)
    
    @property
    def isSitDownAutoReady(self):
        return self._datas.get('isSitDownAutoReady', 1)
    
    @property
    def abortRestartSwitch(self):
        return self._datas.get('abortRestartSwitch', 0)
    
    @property
    def abortRestartMinVer(self):
        return self._datas.get('abortRestartMinVer', 3.820)
    
    @property
    def freeFeeSwitch(self):
        return self._datas.get('freeFeeSwitch', 0)
    
    @property
    def winnerTaxMulti(self):
        return self._datas.get('winnerTaxMulti', 0)
    
    @property
    def luckeyGiftBaseLine(self):
        return self._datas.get('luckeyGiftBaseLine', 1000)

    @property
    def chatCheat(self):
        return self._datas.get('chatCheat', 0)
    
    @property
    def nongminWinAlone(self):
        return self._datas.get('nongminWinAlone')

    @property
    def continueLuckyGift(self):
        return self._datas.get('continueLuckyGift', 0)
    
    @property
    def continueLuckyVer(self):
        return self._datas.get('continueLuckyVer', 3.818)

    @property
    def continueBuyin(self):
        return self._datas.get('continueBuyin')

    @property
    def chipControlLine(self):
        return self._datas.get('chipControlLine', 0)

    @property
    def newTypeOfGift(self):
        return self._datas.get('newTypeOfGift', 0)

    @property
    def winCoinLimit(self):
        return self._datas.get('winCoinLimit', 0)
    
    
