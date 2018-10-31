# -*- coding: utf-8 -*-
import json

class MsgPack:

    def __init__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def clone(self):
        pass

    def setCmd(self, cmd):
        pass

    def setAction(self, action):
        pass

    def getAction(self):
        pass

    def setCmdAction(self, cmd, action):
        pass

    def getCmd(self):
        pass

    def setKey(self, key, value):
        pass

    def getKey(self, key):
        pass

    def rmKey(self, key):
        pass

    def pack(self):
        pass

    def unpack(self, jstr):
        pass

    def setError(self, code, info):
        pass

    def getParam(self, pkey, defValue=None):
        pass

    def setParam(self, pkey, pvalue):
        pass

    def updateParam(self, moreParam):
        pass

    def setResult(self, pkey, pvalue):
        pass

    def rmResult(self, key):
        pass

    def updateResult(self, moreResult):
        pass

    def getResult(self, pkey, defValue=None):
        pass

    def isError(self):
        pass

    def getErrorCode(self, defValue=None):
        pass

    def getErrorInfo(self, defValue=None):
        pass

    def getParams(self, *keys):
        pass

    def getResults(self, *keys):
        pass