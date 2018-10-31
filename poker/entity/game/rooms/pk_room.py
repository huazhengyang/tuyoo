# -*- coding: utf-8 -*-
import random, functools
from poker.entity.configure import gdata
from poker.entity.dao.lua_scripts import room_scripts
from poker.entity.game.rooms import TYNormalRoom
import freetime.util.log as ftlog
from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTTimer
from poker.entity.dao.daobase import executeTableCmd, executeTableLua
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.game import TYGame
from poker.entity.dao import userdata, gamedata
from poker.protocol import router
from freetime.util.log import getMethodName
from random import choice, randint

class TYPkRoom(TYNormalRoom, ):
    """
    目前简化的策略：
        发起pk的时候预先获取tableId，更新table的自定义配置比如base_bet，一旦pk组局成功，
        room进程不再处理，通知table pk start，所有逻辑丢给table进程，有人中途主动离开视为pk结束
    """

    def __init__(self, roomdefine):
        pass

    def getIdleTableId(self, userId):
        """
        获得一个空闲桌子 todo
        """
        pass

    def doQuickStart(self, msg):
        pass

    def doRoomPkCreate(self, msg):
        """
        创建pk
        """
        pass

    def doRoomPkInvite(self, msg):
        """
        邀请好友
        :deprecated
        """
        pass

    def doRoomPkInviteResp(self, msg):
        """
        对方回应邀请
        """
        pass

    def doRoomPkCancel(self, msg):
        """
        发起者取消pk
        """
        pass

    def doRoomPkJoin(self, msg):
        """
        加入自建桌
        """
        pass