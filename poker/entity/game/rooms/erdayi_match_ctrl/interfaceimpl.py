# -*- coding: utf-8 -*-
"""
Created on 2016年7月14日

@author: zhaojiangang
"""
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import daobase
from poker.entity.game.rooms.erdayi_match_ctrl.interface import SigninRecordDao, SigninRecord, MatchStatusDao, MatchStatus
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger
from poker.util import strutil

class SigninRecordDaoRedis(SigninRecordDao, ):

    def __init__(self, gameId):
        pass

    def buildKey(self, matchId, instId, ctrlRoomId):
        pass

    @classmethod
    def decodeRecord(cls, userId, jstr):
        pass

    @classmethod
    def encodeRecord(cls, record):
        pass

    def loadAll(self, matchId, instId, ctrlRoomId):
        pass

    def add(self, matchId, instId, ctrlRoomId, record):
        pass

    def remove(self, matchId, instId, ctrlRoomId, userId):
        pass

    def removeAll(self, matchId, instId, ctrlRoomId):
        pass

class MatchStatusDaoRedis(MatchStatusDao, ):

    def __init__(self, room):
        pass

    def load(self, matchId):
        """
        加载比赛信息
        @return: MatchStatus
        """
        pass

    def save(self, status):
        """
        保存比赛信息
        """
        pass

    def getNextMatchingSequence(self, matchId):
        pass

    def getCurrentMatchingSequence(self, matchId):
        pass