# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from time import time
import freetime.util.log as ftlog
from poker.entity.dao import daobase
from poker.entity.dao.daoconst import UserPlayTimeSchema
from poker.util import strutil

def _cleanalltime(userId):
    pass

def _setPlayTimeStart(userId, roomId, tableId):
    pass

def _setPlayTimeStop(userId, roomId, tableId):
    pass

def _incrPlayTime(userId, detalTime, gameId, roomId=(-1), tableId=(-1)):
    pass

def _writePlayTime_(userId, detalTime):
    pass