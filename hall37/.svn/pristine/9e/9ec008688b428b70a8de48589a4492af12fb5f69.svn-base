# -*- coding:utf-8 -*-

import os

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hall_game_update
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.entity.configure import gdata, pokerconf
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod

@markHttpHandler
class HttpGameUpdateInfoHandler(BaseHttpMsgChecker):
    @markHttpMethod(httppath='/v2/game/updateinfo')
    def doGameUpdateInfo(self):
        gameId = runhttp.getParamInt('gameId')
        clientId = runhttp.getParamStr('clientId', '')
        version = runhttp.getParamStr('version', '')
        updateVersion = runhttp.getParamInt('updateVersion', -1)

        ftlog.debug('http gameupdateinfo IN->gameId=', gameId, 'clientId=', clientId,
                    'version=', version, 'updateVersion=', updateVersion)

        mo = MsgPack()
        mo.setCmd('gameupdateinfo')

        if gameId not in gdata.gameIds():
            mo.setError(1, 'gameId error !')
            return mo

        clientIdInt = pokerconf.clientIdToNumber(clientId)
        if clientIdInt <= 0:
            mo.setError(2, 'clientId error !')
            return mo

        if not version:
            mo.setError(3, 'version error !')
            return mo

        if updateVersion < 0:
            mo.setError(4, 'updateVersion error !')
            return mo

        updates = hall_game_update.getUpdateInfo2(gameId, version, updateVersion)

        ftlog.debug('http gameupdateinfo OUT->updates=', updates)

        mo.setResult('gameId', gameId)
        mo.setResult('clientId', clientId)
        mo.setResult('version', version)
        mo.setResult('updateVersion', updateVersion)
        mo.setResult('updates', updates)

        return mo
