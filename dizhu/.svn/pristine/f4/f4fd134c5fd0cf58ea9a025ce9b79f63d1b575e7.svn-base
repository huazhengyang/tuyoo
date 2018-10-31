# -*- coding:utf-8 -*-
'''
Created on 2018年9月13日

@author: wangyonghui
'''
from dizhu.entity.wx_share_control import WxShareControlHelper
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import freetime.util.log as ftlog


@markCmdActionHandler
class WxShareControlHandler(BaseMsgPackChecker):
    @markCmdActionMethod(cmd='dizhu', action='share_control_info', clientIdVer=0, scope='game')
    def doGetShareControlInfo(self, userId):
        self._doGetShareControlInfo(userId)

    def _doGetShareControlInfo(self, userId):
        burialInfo = WxShareControlHelper.getUserShareControlInfo(userId)
        if ftlog.is_debug():
            ftlog.debug('WxShareControlHandler._doGetShareControlInfo userId=', userId,
                        'burialInfo=', burialInfo)
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'share_control_info')
        mo.setResult('userId', userId)
        mo.setResult('shareFakeSwitch', burialInfo['shareFakeSwitch'])
        mo.setResult('burialIdList', burialInfo['burialIdList'])
        router.sendToUser(mo, userId)
