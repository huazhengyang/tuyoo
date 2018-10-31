# -*- coding: utf-8 -*-
"""
Created on 2015年11月12日

@author: zhaojiangang
"""
import functools
import json
import random
import stackless
from freetime.core.reactor import mainloop, exitmainloop
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata
from poker.entity.game.rooms.arena_match_ctrl.interfaces import MatchTableController, MatchRankRewardsSender, MatchPlayerNotifier, UserInfoLoader
from poker.entity.game.rooms.arena_match_ctrl.match import MatchConf, Match, MatchTableManager

class SigninFee(object, ):

    def collectFees(self, inst, userId, fees):
        """
        收取用户报名费, 如果报名费不足则抛异常SigninFeeNotEnoughException
        """
        pass

    def returnFees(self, inst, userId, fees):
        """
        退还报名费
        """
        pass

class MatchTableControllerTest(MatchTableController, ):

    def __init__(self, match):
        pass

    def startTable(self, table):
        """
        让桌子开始
        """
        pass

    def clearTable(self, table):
        """

        """
        pass

    def _winlose(self):
        pass

class MatchRankRewardsSenderTest(MatchRankRewardsSender, ):

    def sendRankRewards(self, player, rankRewards):
        """
        给用户发奖
        """
        pass

class MatchPlayerNotifierTest(MatchPlayerNotifier, ):

    def __init__(self):
        pass

    def notifyMatchStart(self, player):
        pass

    def notifyMatchRise(self, player):
        """
        通知用户等待晋级
        """
        pass

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        pass

class UserInfoLoaderTest(UserInfoLoader, ):

    def loadUserAttrs(self, userId, attrs):
        """
        获取用户属性
        """
        pass

    def getSessionClientId(self, userId):
        """
        获取用户sessionClientId
        """
        pass
match_conf = {'matchId': 6060, 'stages': [{'cardCount': 1, 'totalUserCount': 120, 'riseUserCount': 90, 'scoreInit': 1000, 'scoreIntoRate': 1, 'rankLine': [[3200, 1], [1600, 3], [800, 7], [400, 19], [200, 39], [100, 55], [(-100), 60], [(-200), 66], [(-400), 82], [(-800), 102], [(-1600), 114], [(-3200), 118], [(-51200), 120]]}, {'cardCount': 1, 'totalUserCount': 90, 'riseUserCount': 66, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[4400, 1], [3125, 2], [2500, 3], [2000, 4], [1900, 5], [1675, 6], [1525, 7], [1400, 8], [1300, 10], [1100, 11], [1000, 13], [950, 15], [800, 17], [725, 20], [700, 21], [650, 24], [550, 26], [500, 28], [475, 32], [400, 33], [350, 36], [325, 38], [275, 39], [250, 40], [200, 44], [125, 47], [100, 48], [50, 52], [25, 54], [(-50), 55], [(-100), 58], [(-125), 62], [(-200), 63], [(-250), 65], [(-275), 68], [(-325), 69], [(-350), 70], [(-400), 72], [(-475), 73], [(-500), 74], [(-550), 77], [(-650), 79], [(-700), 81], [(-725), 82], [(-950), 83], [(-1100), 85], [(-1300), 86], [(-1450), 87], [(-1750), 88], [(-3050), 89], [(-51500), 90]]}, {'cardCount': 1, 'totalUserCount': 66, 'riseUserCount': 48, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[4400, 1], [3275, 2], [2650, 3], [2225, 4], [1975, 5], [1844, 6], [1675, 7], [1550, 8], [1450, 9], [1344, 10], [1250, 11], [1175, 12], [1150, 13], [1063, 14], [1000, 15], [950, 16], [925, 17], [888, 18], [850, 19], [800, 20], [775, 21], [725, 22], [700, 23], [663, 24], [625, 25], [606, 26], [575, 27], [550, 28], [500, 29], [475, 30], [438, 31], [419, 32], [388, 33], [350, 34], [325, 35], [313, 36], [288, 37], [250, 38], [213, 39], [200, 40], [163, 41], [125, 42], [88, 44], [44, 45], [13, 46], [(-25), 47], [(-50), 48], [(-100), 49], [(-125), 50], [(-163), 51], [(-213), 52], [(-250), 53], [(-275), 54], [(-325), 55], [(-363), 56], [(-425), 57], [(-475), 58], [(-500), 59], [(-594), 60], [(-725), 61], [(-850), 62], [(-1000), 63], [(-1413), 64], [(-2375), 65], [(-51388), 66]]}, {'cardCount': 1, 'totalUserCount': 48, 'riseUserCount': 36, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[4300, 1], [3238, 2], [2575, 3], [2225, 4], [2000, 5], [1825, 6], [1681, 7], [1555, 8], [1438, 9], [1338, 10], [1259, 11], [1175, 12], [1109, 13], [1056, 14], [1000, 15], [944, 16], [894, 17], [850, 18], [800, 19], [756, 20], [709, 21], [663, 22], [625, 23], [578, 24], [533, 25], [494, 26], [463, 27], [419, 28], [381, 29], [341, 30], [294, 31], [256, 32], [209, 33], [163, 34], [116, 35], [63, 36], [13, 37], [(-44), 38], [(-106), 39], [(-156), 40], [(-219), 41], [(-283), 42], [(-372), 43], [(-494), 44], [(-669), 45], [(-916), 46], [(-1506), 47], [(-51266), 48]]}, {'cardCount': 1, 'totalUserCount': 36, 'riseUserCount': 24, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[4077, 1], [3027, 2], [2458, 3], [2146, 4], [1920, 5], [1745, 6], [1594, 7], [1463, 8], [1352, 9], [1255, 10], [1173, 11], [1100, 12], [1030, 13], [965, 14], [901, 15], [838, 16], [777, 17], [719, 18], [660, 19], [604, 20], [549, 21], [494, 22], [439, 23], [381, 24], [320, 25], [256, 26], [186, 27], [114, 28], [38, 29], [(-41), 30], [(-128), 31], [(-230), 32], [(-377), 33], [(-608), 34], [(-1212), 35], [(-51090), 36]]}, {'cardCount': 1, 'totalUserCount': 36, 'riseUserCount': 24, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[4077, 1], [3027, 2], [2458, 3], [2146, 4], [1920, 5], [1745, 6], [1594, 7], [1463, 8], [1352, 9], [1255, 10], [1173, 11], [1100, 12], [1030, 13], [965, 14], [901, 15], [838, 16], [777, 17], [719, 18], [660, 19], [604, 20], [549, 21], [494, 22], [439, 23], [381, 24], [320, 25], [256, 26], [186, 27], [114, 28], [38, 29], [(-41), 30], [(-128), 31], [(-230), 32], [(-377), 33], [(-608), 34], [(-1212), 35], [(-51090), 36]]}, {'cardCount': 1, 'totalUserCount': 24, 'riseUserCount': 12, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[3791, 1], [2748, 2], [2287, 3], [1994, 4], [1757, 5], [1578, 6], [1434, 7], [1312, 8], [1207, 9], [1110, 10], [1014, 11], [923, 12], [837, 13], [755, 14], [672, 15], [584, 16], [492, 17], [389, 18], [280, 19], [164, 20], [28, 21], [(-170), 22], [(-596), 23], [(-50992), 24]]}, {'cardCount': 1, 'totalUserCount': 12, 'riseUserCount': 6, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[3312, 1], [2453, 2], [1994, 3], [1706, 4], [1488, 5], [1298, 6], [1123, 7], [949, 8], [750, 9], [522, 10], [178, 11], [(-50503), 12]]}, {'cardCount': 1, 'totalUserCount': 6, 'riseUserCount': 3, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[2839, 1], [2044, 2], [1601, 3], [1229, 4], [789, 5], [(-50148), 6]]}, {'cardCount': 1, 'totalUserCount': 3, 'riseUserCount': 1, 'scoreInit': 0, 'scoreIntoRate': 0.75, 'rankLine': [[2318, 1], [1436, 2], [(-40651), 3]]}], 'baseScore': 100, 'tableSeatCount': 3, 'minSigninCount': 3, 'maxSigninCount': 1000, 'maxPlayerCount': 120, 'processSigninIntervalSeconds': 5, 'processSigninCountPerTime': 100, 'rankRewardsList': []}

def testRankLine():
    pass

def testOnlineLoc(*args, **kwargs):
    pass

def testMatch(match):
    pass
if (__name__ == '__main__'):
    matchConf = MatchConf()
    matchConf.decodeFromDict(match_conf)
    matchConf.gameId = 6
    matchConf.roomId = 60011001
    matchConf.tableId = (matchConf.roomId * 10000)
    matchConf.seatId = 1
    onlinedata.addOnlineLoc = testOnlineLoc
    onlinedata.removeOnlineLoc = testOnlineLoc
    onlinedata.getOnlineLocSeatId = testOnlineLoc
    onlinedata.getOnlineLocList = testOnlineLoc
    match = Match(matchConf)
    match.tableController = MatchTableControllerTest(match)
    match.tableManager = MatchTableManager(6, 3)
    match.tableManager.addTables(60011001, 0, 40)
    match.playerNotifier = MatchPlayerNotifierTest()
    match.rankRewardsSender = MatchRankRewardsSenderTest()
    match.userInfoLoader = UserInfoLoaderTest()
    match.start()
    FTTimer(2, functools.partial(testMatch, match))
    stackless.tasklet(mainloop)()
    stackless.run()
    print 'main end'
    print match.playerNotifier._playerMap
    print json.dumps(match.playerNotifier._playerMap)