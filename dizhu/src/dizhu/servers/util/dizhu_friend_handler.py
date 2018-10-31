# -*- coding:utf-8 -*-
'''
Created on 2016年9月26日

@author: zhaojiangang
'''
import json
import freetime.util.log as ftlog
from dizhu.entity.dizhu_friend import FriendHelper
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.dao import gamedata


@markCmdActionHandler
class FriendHandler(BaseMsgPackChecker):
    def __init__(self):
        super(FriendHandler, self).__init__()

    @markCmdActionMethod(cmd='dizhu', action='friend_rank_list', clientIdVer=0, lockParamName='', scope='game')
    def doFriendRankList(self, userId, gameId, clientId):
        rankList = self._get_friend_rank_list(userId, gameId, clientId)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'friend_rank_list')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('rankList', rankList)
        router.sendToUser(msg, userId)

    @classmethod
    def _get_friend_rank_list(cls, userId, gameId, clientId):
        return FriendHelper.getUserFriendRankList(userId)
    
    @markCmdActionMethod(cmd='dizhu', action='get_ft_table_record', clientIdVer=0, lockParamName='', scope='game')
    def getMyFriendTableRecord(self, userId, gameId):
        """获取我的好友桌战绩
        """
        records = gamedata.getGameAttr(userId, DIZHU_GAMEID, "friendTableRecords")
        ftlog.debug("getMyFriendTableRecord userId =", userId, "records =", records)
        if records:
            records = json.loads(records)
        else:
            records = []
        msgRes = MsgPack()
        msgRes.setCmd("dizhu")
        msgRes.setResult('gameId', gameId)
        msgRes.updateResult({"action": "get_ft_table_record"})
        msgRes.setResult("records", records)
        router.sendToUser(msgRes, userId)
