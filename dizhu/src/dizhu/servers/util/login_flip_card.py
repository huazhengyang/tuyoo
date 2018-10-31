# -*- coding=utf-8 -*-
'''
Created on 2015年7月7日

@author: zhaojiangang
'''
from dizhu.entity import dizhuflipcard
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.item.item import TYAssetUtils
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp


@markCmdActionHandler
class LoginRewardFlipCardHandler(BaseMsgPackChecker):


    @markCmdActionMethod(cmd='game', action='login_reward_flip_card', clientIdVer=0, scope='game')
    def doLoginRewardFlipCard(self, gameId, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('LoginRewardFlipCardHandler.doLoginRewardFlipCard', gameId, userId, msg, caller=self)
        try:
            index = msg.getParam('index', 0)
            flipped, status, reward = dizhuflipcard.flipCard.flipCard(userId, index, pktimestamp.getCurrentTimestamp())
            if flipped:
                ftlog.debug('TGDizhu.doLoginRewardFlipCard gameId=', gameId,
                           'userId=', userId,
                           'nslogin=', status.nslogin,
                           'flippedrewards=', [(i, ci.assetKindId, ci.count) for i, ci in status.itemMap.iteritems()],
                           'remfliptimes=', status.getRemFlipCount(),
                           'reward=', TYAssetUtils.buildContent(reward))
            
            mo = MsgPack()
            mo.setCmd('login_reward_flip_card')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('nlogin', status.nslogin)
            mo.setResult('remfliptimes', status.getRemFlipCount())
            mo.setResult('rewards', dizhuflipcard.encodeFlipCardMap(status.itemMap))
            mo.setResult('paddings', dizhuflipcard.encodePaddings(status.paddings))
            router.sendToUser(mo, userId)
        except:
            ftlog.error()

