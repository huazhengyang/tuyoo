# coding=UTF-8
'''
'''
from poker.util import strutil

__author__ = [
    '"Zqh"',
]


class DizhuTableConf(object):

    def __init__(self, datas):
        self.datas = datas


    def getAllDatas(self):
        return self.datas 

    @property
    def cardNoteChip(self):
        return self.datas.get('cardNoteChip', 0)
    
    @property
    def basebet(self):
        return self.datas['basebet']
    

    @property
    def basemulti(self):
        return self.datas['basemulti']

    @property
    def roomMutil(self):
        return self.datas['roomMutil']


    @property
    def tableMulti(self):
        return self.basebet * self.basemulti * self.roomMutil


    @property
    def roomFee(self):
        return self.datas['roomFee']


    @property
    def rangpaiMultiType(self):
        return self.datas['rangpaiMultiType']


    @property
    def autochange(self):
        return self.datas['autochange']


    @property
    def gslam(self):
        return self.datas['gslam']


    @property
    def grab(self):
        return self.datas['grab']


    @property
    def canchat(self):
        return self.datas['canchat']


    @property
    def optime(self):
        return self.datas['optime']


    @property
    def optimeFirst(self):
        return self.datas.get('optimeFirst', self.optime + 12)


    @property
    def optimeAlreadyTuoGuan(self):
        return self.datas.get('optimeAlreadyTuoGuan', 1)


    @property
    def optimeOnlyOneCard(self):
        return self.datas.get('optimeOnlyOneCard', 1)


    @property
    def optimeDoubleKing(self):
        return self.datas.get('optimeDoubleKing', 1)

    @property
    def optimeDisbind(self):
        return self.datas.get('optimeDisbind', 90)
    
    @property
    def coin2chip(self):
        return self.datas['coin2chip']


    @property
    def lucky(self):
        return self.datas['lucky']


    @property
    def unticheat(self):
        return self.datas['unticheat']


    @property
    def passtime(self):
        return self.datas['passtime']


    @property
    def showCard(self):
        return self.datas['showCard']


    @property
    def maxCoin(self):
        return self.datas['maxCoin']


    @property
    def minCoin(self):
        return self.datas['minCoin']


    @property
    def isMatch(self):
        return self.datas['ismatch']


    @property
    def goodCard(self):
        return self.datas['goodCard']


    @property
    def playMode(self):
        return self.datas['playMode']


    @property
    def sendCardConfig(self):
        return self.datas.get('sendCard', {})


    @property
    def goodSeatRerandom(self):
        # 如果某个座位有好牌点儿，并且首叫不是这个座位则需要重新随机一次
        return self.datas.get('goodSeatRerandom', 0)


    @property
    def buyinchip(self):
        return self.datas.get('buyinchip', 0)


    @property
    def hasrobot(self):
        return self.datas.get('hasrobot', 0)


    @property
    def robotTimes(self):
        return self.datas.get('robottimes', 0)


    @property
    def punishAutoCall(self):
        return self.datas.get('punishAutoCall', 0)


    @property
    def punishAutoGrab(self):
        return self.datas.get('punishAutoGrab', 0)


    @property
    def punishCardCount(self):
        return self.datas.get('punishCardCount', 2)


    @property
    def punishTip(self):
        tip = self.datas.get('punishTip', '本局结束时,如果您的牌数大于${punish.cardCount}张,并处于托管状态,将接受系统处罚')
        return strutil.replaceParams(tip, {'punish.cardCount':self.punishCardCount})


    @property
    def firstCallValue(self):
        return self.datas.get('firstCallValue', 1)


    @property
    def sendCoupon(self):
        return self.datas.get('sendCoupon', 0)


    @property
    def actionReadyTimeOut(self):
        return self.datas.get('readyTimeout', 20)

    @property
    def ftContinueTimeout(self):
        return self.datas.get('ftContinueTimeout', 3)
    
    @property
    def actionFirstCallDelayTimes(self):
        return self.datas.get('firstCallDelayTimes', 0.1)
    
    @property
    def notStartTimeout(self):
        return self.datas.get('notStartTimeout', 3600 * 2)

