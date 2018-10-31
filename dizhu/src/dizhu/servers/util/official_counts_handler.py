# -*- coding: utf-8 -*-
import freetime.util.log as ftlog
from dizhu.entity.official_counts import wx_official
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class OfficialCountsMessageHandler(BaseMsgPackChecker):
    def __init__(self):
        super(OfficialCountsMessageHandler, self).__init__()

    def _check_param_rankDict(self, msg, key, params):
        rankDict = msg.getParam(key)
        if isinstance(rankDict, dict):
            return None, rankDict
        return None, {}

    @markCmdActionMethod(cmd='dizhu', action='rank_info', clientIdVer=0, lockParamName='', scope='game')
    def doRankInfo(self, userId, rankDict):
        if ftlog.is_debug():
            ftlog.debug('action==>rank_info',
                        'userId= ', userId,
                        'rankDict= ', rankDict)
        wx_official.doRankInfo(userId, rankDict)
