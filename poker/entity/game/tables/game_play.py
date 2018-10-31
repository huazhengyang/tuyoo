# -*- coding: utf-8 -*-
"""
    经典玩法模块
"""
__author__ = ['Zhou Hao']
import functools
import time
from freetime.util import log as ftlog
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils
from poker.entity.biz import bireport

class TYGamePlay(object, ):
    """

    """
    GAME_PLAY_STATE_WAIT = 0
    GAME_PLAY_STATE_START = 1
    GAME_PLAY_STATE_FINAL = 8
    gamePlayStateStrs = {GAME_PLAY_STATE_WAIT: 'WAIT', GAME_PLAY_STATE_START: 'START', GAME_PLAY_STATE_FINAL: 'FINAL'}

    def __init__(self, table):
        pass

    def getBasicAttrsLog(self, caller=None):
        pass

    def _initField(self):
        """

        """
        pass

    def _initGamePlayData(self):
        """

        """
        pass

    @property
    def _state(self):
        pass

    def setState(self, state):
        pass

    def transitToStateWait(self):
        pass

    def doActionCheckStartGame(self):
        """
        Note： 先补足筹码，然后踢掉筹码不足的玩家
        """
        pass

    def _calcGameStartAnimatTime(self):
        """

        """
        pass

    def transitToStateStartGame(self):
        """

        """
        pass

    def _calcDealCardAnimatTime(self):
        """

        """
        pass

    def _calcGameWinAnimatTime(self):
        """

        """
        pass

    def transitToStateFinal(self):
        pass

    def doActionGameEnd(self):
        pass
    """
            功能性 函数
    """

    def getStateStr(self):
        pass

    def isWaitingState(self):
        pass

    def isStartState(self):
        pass

    def isFinalState(self):
        pass

    def isActionState(self):
        """

        """
        pass

    def isPlayingState(self):
        """

        """
        pass

    def getStateScore(self):
        pass