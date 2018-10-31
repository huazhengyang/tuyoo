# -*- coding: utf-8 -*-
'''
Created on 2017年9月12日
@author: ljh
'''

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallsportlottery
from hall.entity.hallsportlottery import SportlotteryConf
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class SportTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        pass

    @markCmdActionMethod(cmd='game_sport', action="sport_main", clientIdVer=0)
    def doSportlotteryProduct(self):
        '''体育竞猜商品'''
        if ftlog.is_debug():
            ftlog.debug('doSportlotteryProduct enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")

        productList = hallsportlottery.sportlotteryProduct(userId)

        msg = MsgPack()
        msg.setCmd('game_sport')
        msg.setResult('action', 'sport_main')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('sportMainList', productList)
        helpDesc = SportlotteryConf.conf().get('helpDesc')
        msg.setResult('helpDesc', helpDesc)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doSportlotteryProduct',
                        'userId=', userId,
                        'productList=', productList)

    @markCmdActionMethod(cmd='game_sport', action="sport_details", clientIdVer=0)
    def doSportlotteryDetails(self):
        '''体育竞猜细节'''
        if ftlog.is_debug():
            ftlog.debug('doSportlotteryDetails enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        date = msg.getParam('date')
        matchId = msg.getParam('uuid')
        type = msg.getParam('type')
        userId = msg.getParam('userId')

        self.doSportDetail(userId, date, matchId, type, gameId)

    def doSportDetail(self, userId, date, matchId, type, gameId):
        details = hallsportlottery.sportlotteryDetail(userId, date, matchId, type)

        msg = MsgPack()
        msg.setCmd('game_sport')
        msg.setResult('action', 'sport_details')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('details', details)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doSportlotteryDetails',
                        'userId=', userId,
                        'details=', details)

    @markCmdActionMethod(cmd='game_sport', action="sport_bet", clientIdVer=0)
    def doSportlotteryBet(self):
        '''体育竞猜下注'''
        if ftlog.is_debug():
            ftlog.debug('doSportlotteryBet enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        clientId = msg.getParam("clientId")
        userId = msg.getParam('userId')
        date = msg.getParam('date')
        matchId = msg.getParam('uuid')
        party = msg.getParam('party')  # 1主胜  2 平  3客胜
        coin = msg.getParam('coin')
        type = msg.getParam('type') # 1足球 0篮球

        ec = 0
        info = '投注成功'
        userChip = 0

        try:

            userChip = hallsportlottery.sportlotteryBet(gameId, clientId, userId, date, matchId,
                                                        party, coin)

            self.doSportDetail(userId, date, matchId, type, gameId)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doSportlotteryBet failer',
                       'userId=', userId,
                       'date=', date,
                       'matchId=', matchId,
                       'party=', party,
                       'coin=', coin,
                       'ec=', ec,
                       'info=', info)

        msg = MsgPack()
        msg.setCmd('game_sport')
        msg.setResult('action', 'sport_bet')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('date', date)
        msg.setResult('uuid', matchId)
        msg.setResult('party', party)
        msg.setResult('coin', coin)
        msg.setResult('userChip', userChip)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doSportlotteryBet',
                        'userId=', userId,
                        'date=', date,
                        'matchId=', matchId,
                        'party=', party,
                        'coin=', coin,
                        'ec=', ec,
                        'info=', info)

    @markCmdActionMethod(cmd='game_sport', action="sport_love", clientIdVer=0)
    def doSportlotteryLove(self):
        '''体育竞猜点赞'''
        if ftlog.is_debug():
            ftlog.debug('doSportlotteryLove enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam('userId')
        date = msg.getParam('date')
        matchId = msg.getParam('uuid')
        love = msg.getParam('love')  # 0home 1away

        ec = 0
        info = '点赞成功'
        try:
            ec, info = hallsportlottery.sportlotteryLove(userId, date, matchId, love)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doSportlotteryLove failer',
                       'userId=', userId,
                       'date=', date,
                       'matchId=', matchId,
                       'love=', love)

        msg = MsgPack()
        msg.setCmd('game_sport')
        msg.setResult('action', 'sport_love')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('date', date)
        msg.setResult('uuid', matchId)
        msg.setResult('love', love)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doSportlotteryLove',
                        'userId=', userId,
                        'date=', date,
                        'matchId=', matchId,
                        'love=', love)

    @markCmdActionMethod(cmd='game_sport', action="sport_reward_list", clientIdVer=0)
    def doSportlotteryRewardList(self):
        '''我的竞猜'''
        if ftlog.is_debug():
            ftlog.debug('doSportlotteryRewardList enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam('userId')

        self.sportlotteryReward(userId, gameId)


    def sportlotteryReward(self, userId, gameId):
        rewardList = hallsportlottery.sportlotteryRewardList(userId)

        msg = MsgPack()
        msg.setCmd('game_sport')
        msg.setResult('action', 'sport_reward_list')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)

        msg.setResult('rewardList', rewardList)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doSportlotteryRewardList',
                        'userId=', userId,
                        'rewardList=', rewardList)


    @markCmdActionMethod(cmd='game_sport', action="sport_getrew", clientIdVer=0)
    def doSportlotteryGetReward(self):
        '''点击领取奖励'''
        if ftlog.is_debug():
            ftlog.debug('doSportlotteryGetReward enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        clientId = msg.getParam("clientId")
        userId = msg.getParam('userId')
        date = msg.getParam('date')
        matchId = msg.getParam('uuid')

        ec = 0
        info = '领取成功'
        final = 0
        try:
            final = hallsportlottery.sportlotteryGetReward(gameId, clientId, userId, date, matchId)
            self.sportlotteryReward(userId, gameId)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doSportlotteryGetReward failer',
                       'userId=', userId,
                       'date=', date,
                       'matchId=', matchId)

        msg = MsgPack()
        msg.setCmd('game_sport')
        msg.setResult('action', 'sport_getrew')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('date', date)
        msg.setResult('uuid', matchId)
        msg.setResult('userChip', final)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doSportlotteryGetReward',
                        'userId=', userId,
                        'date=', date,
                        'matchId=', matchId)
