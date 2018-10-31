# -*- coding: utf-8 -*-
"""
Created on 2015年6月29日

@author: zhaojiangang
"""
import random
from sre_compile import isstring
import struct
import freetime.util.log as ftlog
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizBadDataException
from poker.entity.biz.task.dao import TYTaskDataDao
from poker.entity.biz.task.exceptions import TYTaskConfException
from poker.entity.configure import gdata
import poker.util.timestamp as pktimestamp
from poker.util import strutil

class TYTaskInspector(TYConfable, ):

    def __init__(self, interestEventMap):
        pass

    @property
    def interestEventMap(self):
        pass

    def processEvent(self, task, event):
        pass

    def decodeFromDict(self, d):
        pass

    def _decodeFromDictImpl(self, d):
        pass

    def _processEventImpl(self, task, event):
        pass

    def on_task_created(self, task):
        pass

class TYTaskInspectorRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYTaskKind(TYConfable, ):
    """
    任务种类
    """

    def __init__(self):
        pass

    @property
    def taskUnit(self):
        pass

    def decodeFromDict(self, d):
        pass

    def newTaskData(self):
        pass

    def newTaskForDecode(self):
        pass

    def newTask(self, prevTask, timestamp):
        pass

    def _decodeFromDictImpl(self, d):
        pass

    def processEvent(self, task, event):
        pass

class TYTaskData(object, ):
    BASE_STRUCT_FMT = '4iB'
    BASE_STRUCT_LEN = struct.calcsize(BASE_STRUCT_FMT)

    def __init__(self):
        pass

    @classmethod
    def encodeToBytes(cls, taskData):
        pass

    @classmethod
    def decodeFromBytes(cls, taskData, dataBytes):
        pass

    def _getStructFormat(self):
        pass

    def _getFieldNames(self):
        pass

class TYTask(object, ):

    def __init__(self, taskKind):
        pass

    @property
    def kindId(self):
        pass

    @property
    def taskUnit(self):
        pass

    @property
    def taskUnitId(self):
        pass

    @property
    def userId(self):
        pass

    @property
    def userTaskUnit(self):
        pass

    @userTaskUnit.setter
    def userTaskUnit(self, userTaskUnit):
        pass

    @property
    def isFinished(self):
        pass

    def setProgress(self, progress, timestamp):
        pass

    def encodeToTaskData(self):
        pass

    def decodeFromTaskData(self, taskData):
        pass

    def _encodeToTaskData(self, taskData):
        pass

    def _decodeFromTaskData(self, taskData):
        pass

class TYTaskCondition(TYConfable, ):

    def check(self, task, event):
        """
        判断是否符合条件
        @return: True/False
        """
        pass

    def decodeFromDict(self, d):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYTaskConditionRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYTaskKindRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYTaskKindPool(object, ):

    def __init__(self, taskUnit):
        pass

    @property
    def taskUnit(self):
        pass

    @property
    def taskKindList(self):
        pass

    @property
    def nextType(self):
        pass

    @property
    def index(self):
        pass

    @property
    def taskKindMap(self):
        pass

    @property
    def task_order(self):
        pass

    def findTaskKind(self, kindId):
        pass

    def nextTaskKind(self, prevTaskKind=None, task_order=0):
        pass

    def decodeFromDict(self, d):
        pass

class TYTaskUnit(TYConfable, ):
    """
    一个任务单元，包含n个任务池
    """

    def __init__(self, _task_kind_pool_cls=None):
        pass

    @property
    def gameId(self):
        pass

    @property
    def taskUnitId(self):
        pass

    @property
    def taskSystem(self):
        pass

    @property
    def subTaskSystem(self):
        pass

    @property
    def taskKindMap(self):
        pass

    @property
    def poolList(self):
        pass

    @property
    def typeid(self):
        pass

    def findTaskKind(self, kindId):
        """
        根据kindId查找taskKind
        """
        pass

    def decodeFromDict(self, d):
        pass

class TYUserTaskUnit(object, ):

    def __init__(self, userId, taskUnit):
        pass

    @property
    def userId(self):
        pass

    @property
    def taskUnit(self):
        pass

    @property
    def taskUnitId(self):
        pass

    @property
    def taskSystem(self):
        pass

    @property
    def taskList(self):
        pass

    @property
    def taskMap(self):
        pass

    def findTask(self, kindId):
        pass

    def addTask(self, task):
        pass

    def removeAllTask(self):
        pass

    def removeTask(self, task):
        pass

    def updateTask(self, task):
        pass

    def _addTaskToMap(self, task):
        pass

    def _removeFromMap(self, task):
        pass

class TYSubTaskSystem(object, ):

    @property
    def gameId(self):
        pass

    def onTaskUnitLoaded(self, taskUnit):
        """
        当taskUnit加载完成时回调
        """
        pass

    def processEvent(self, userTaskUnit, event):
        """
        事件处理
        """
        pass

    def decodeFromDict(self, d):
        pass

class TYTaskSystem(object, ):

    def getAllTaskUnit(self):
        """
        获取所有任务单元
        """
        pass

    def findTaskKind(self, kindId):
        """
        根据kindId查找taskKind
        """
        pass

    def findTaskUnit(self, taskUnitId):
        """
        根据taskUnitId查找taskUnit
        @return: TYTaskUnit
        """
        pass

class TYTaskSystemImpl(TYTaskSystem, ):

    def __init__(self, gameId, taskDataDao, _task_kind_pool_cls=None):
        pass

    def reloadConf(self, conf):
        pass

    @property
    def gameId(self):
        pass

    def registerSubTaskSystem(self, taskUnitId, subTaskSystem):
        pass

    def getAllTaskUnit(self):
        """
        获取所有任务单元
        """
        pass

    def findTaskKind(self, kindId):
        """
        根据kindId查找taskKind
        """
        pass

    def findTaskUnit(self, taskUnitId):
        """
        根据taskUnitId查找taskUnit
        @return: TYTaskUnit
        """
        pass

    def loadUserTaskUnit(self, userId, taskUnit, timestamp):
        """
        加载用户执行的某个任务单元
        """
        pass

    def loadUserTaskUnits(self, userId, taskUnitList, timestamp):
        """
        加载用户执行的某些任务单元
        """
        pass

    def _registerEvents(self):
        pass

    def _unregisterEvents(self):
        pass

    def _addInterestEventType(self, eventType, gameId):
        pass

    def _handleEvent(self, event):
        pass

    def _saveTask(self, userId, task):
        pass

    def _removeTask(self, userId, task):
        pass

    def _decodeTask(self, userId, kindId, taskDataBytes):
        pass