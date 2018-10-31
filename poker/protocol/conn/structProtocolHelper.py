# -*- coding: utf-8 -*-
"""
Created on 2016年3月5日

@author: liaoxx
"""
import struct, json, copy
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog

class CmdObjBase(object, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _unstructMsg(self, binStr):
        pass

    def _constructJson(self, msgMap):
        pass

    def unstructMsg(self, binStr):
        pass

class FireVerify(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class FireVerify28(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _constructJson(self, msgMap):
        pass

class FireVerifyRet(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class FireVerifyRet28(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class FireBroadcast(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class FireBroadcast28(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class CatchVerify(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class CatchVerify28(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _constructJson(self, msgMap):
        pass

class CatchVerifyRetOk(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _constructJson(self, msgMap):
        pass

class CatchVerifyRetOk28(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _unstructMsg(self, binStr):
        pass

    def _constructJson(self, msgMap):
        pass

class CatchVerifyRetFail(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class CatchVerifyRetFail28(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class NFFireVerify(CmdObjBase, ):

    def __init__(self):
        pass

    def _constructJson(self, msgMap):
        pass

class NFFireVerifyRet(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _constructJson(self, msgMap):
        pass

class NFFireBroadcast(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _constructJson(self, msgMap):
        pass

class NFCatchVerify(CmdObjBase, ):

    def __init__(self):
        pass

    def _unstructMsg(self, binStr):
        pass

    def _constructJson(self, msgMap):
        pass

class NFCatchVerifyRet(CmdObjBase, ):

    def __init__(self):
        pass

    def structMsg(self, msgPack):
        pass

    def _constructJson(self, msgMap):
        pass
FireVerifyObj = FireVerify()
FireVerifyRetObj = FireVerifyRet()
FireBroadcastObj = FireBroadcast()
CatchVerifyObj = CatchVerify()
CatchVerifyRetOkObj = CatchVerifyRetOk()
CatchVerifyRetFailObj = CatchVerifyRetFail()
FireVerifyObj28 = FireVerify28()
FireVerifyRetObj28 = FireVerifyRet28()
FireBroadcastObj28 = FireBroadcast28()
CatchVerifyObj28 = CatchVerify28()
CatchVerifyRetOkObj28 = CatchVerifyRetOk28()
CatchVerifyRetFailObj28 = CatchVerifyRetFail28()
NFFireVerifyObj = NFFireVerify()
NFFireVerifyRetObj = NFFireVerifyRet()
NFFireBroadcastObj = NFFireBroadcast()
NFCatchVerifyObj = NFCatchVerify()
NFCatchVerifyRetOkObj = NFCatchVerifyRet()

def _getCmdObj(cmdId):
    pass

def encode(msgstr):
    pass

def decode(msgstr):
    pass

def encodeForRobot(msgPack):
    pass