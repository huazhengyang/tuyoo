# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import stackless
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import router, oldcmd, rpccore
from poker.protocol import _runenv
from poker.util import strutil
from freetime.core.lock import FTLock
import freetime.entity.service as ftsvr

def isCmdTask():
    """
    判定当前是否是TCP命令,引发的tasklet
    """
    pass

def getMsgPack():
    """
    取得当前TCP的消息
    """
    pass

def newErrorMsgPack(errCode, edrrInfo):
    """
    快速工具, 依据当前接收的命令, 生成一个返回错误信息的MsgPack
    """
    pass

def newOkMsgPack(code=1):
    """
    快速工具, 依据当前接收的命令, 生成一个返回OK信息的MsgPack
    """
    pass

def getClientId(msg=None):
    """
    获取当前命令的clientId的大版本号,
    如果消息中没有clientId,那么取用户的登录时的clientId
    """
    pass

def getClientIdVer(msg):
    """
    获取当前命令的clientId的大版本号,
    如果消息中没有clientId,那么取用户的登录时的clientId
    """
    pass
fish_transfer_actions = set(['fire', 'gup', 'gchg', 'charge_notify', 'get_benefits', 'lottery_task', 'check_bankrupt', 'chgGunCrg', 'miniGame', 'refreshUserData', 'noEvlp', 'activity_reward', 'checkin', 'checkinGetDaysReward', 'dailyQuestReward'])

def handlerCommand(msg):
    """
    TCP消息命令处理总入口
    """
    pass

def _handlerRpcCommand(markParams, msg):
    pass

def _handlerMsgCommand(markParams, msg):
    pass

def filterErrorMessage(msg):
    pass

def _checkCmdParams(handler, paramkeys):
    """
    检查校验当前TCP命令入口的参数
    """
    pass

def debugCmdInfos():
    pass