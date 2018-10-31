# -*- coding: utf-8 -*-

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.entity.biz.exceptions import TYBizException
from hall.servers.common.base_checker import BaseMsgPackChecker
from dizhu.entity.segment.duobao import DuobaoUTServerHelper


@markCmdActionHandler
class DuobaoTcpHandler(BaseMsgPackChecker):

    @markCmdActionMethod(cmd="dizhu", action="treasure_shop_list", clientIdVer=0)
    def doGetDuobaoProductList(self):
        """
        获取夺宝产品列表
        @return:
        """
        msg = runcmd.getMsgPack()
        userId = msg.getParam("userId")
        DuobaoUTServerHelper.handle_get_product_list(userId)

    @markCmdActionMethod(cmd='dizhu', action='duobao_bet', clientIdVer=0)
    def doDuobaoBet(self):
        """
        一元夺宝下注
        """
        msg = runcmd.getMsgPack()
        userId = msg.getParam("userId")
        duobaoId = msg.getParam("duobaoId")
        issue = msg.getParam("issue")
        num = msg.getParam("num")
        DuobaoUTServerHelper.handle_bet(userId, duobaoId, issue, num)


    @markCmdActionMethod(cmd='dizhu', action='duobao_reward', clientIdVer=0)
    def doDuobaoReward(self):
        """
        一元夺宝领奖
        """
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")
        duobaoId = msg.getParam("duobaoId")
        issue = msg.getParam("issue")

        ec = 0
        info = '领取成功'
        reward = {}

        try:
            from hall.entity import hall1yuanduobao
            reward = hall1yuanduobao.duobaoReward(userId, duobaoId, issue)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doubaoReward failer',
                       'userId=', userId,
                       'duobaoId=', duobaoId,
                       'issue=', issue,
                       'ec=', ec,
                       'info=', info)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_reward')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('duobaoId', duobaoId)
        msg.setResult('issue', issue)
        msg.setResult('reward', reward)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='duobao_product', clientIdVer=0)
    def doDuobaoProduct(self):
        """
        一元夺宝商品
        """
        if ftlog.is_debug():
            ftlog.debug('doDuobaoProduct enter')
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")

        from hall.entity import hall1yuanduobao
        productList = hall1yuanduobao.duobaoProduct(userId)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_product')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('productList', productList)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doDuobaoProduct',
                        'userId=', userId,
                        'productList=', productList)

    @markCmdActionMethod(cmd='dizhu', action='duobao_history', clientIdVer=0)
    def doDuobaoHistory(self):
        """
        一元夺宝往期得主
        """
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")
        duobaoId = msg.getParam("duobaoId")
        pageId = msg.getParam("pageId")

        ec = 0
        info = '查询成功'
        historyList = []

        try:
            from hall.entity import hall1yuanduobao
            historyList = hall1yuanduobao.duobaoHistory(userId, duobaoId, pageId)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doDuobaoHistory failer',
                       'userId=', userId,
                       'duobaoId=', duobaoId,
                       'pageId=', pageId,
                       'ec=', ec,
                       'info=', info)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_history')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('duobaoId', duobaoId)
        msg.setResult('pageId', pageId)
        msg.setResult('historyList', historyList)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='duobao_myrecord', clientIdVer=0)
    def doDuobaoMyRecord(self):
        """
        一元夺宝查询我的夺宝记录
        """
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")
        pageId = msg.getParam("pageId")

        recordList = []
        totalLength = 0
        ec = 0
        info = '查询成功'
        try:
            from hall.entity import hall1yuanduobao
            recordList, totalLength = hall1yuanduobao.duobaoMyRecord(userId, pageId)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doDuobaoMyRecord failer',
                       'userId=', userId,
                       'pageId=', pageId,
                       'ec=', ec,
                       'info=', info)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_myrecord')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('pageId', pageId)
        msg.setResult('recordList', recordList)
        msg.setResult('totalLength', totalLength)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)

        if ftlog.is_debug():
            ftlog.debug('doDuobaoMyRecord',
                        'userId=', userId,
                        'pageId=', pageId,
                        'recordList=', recordList,
                        'totalLength=', totalLength)


    @markCmdActionMethod(cmd='dizhu', action='duobao_rewardRecord', clientIdVer=0)
    def doDuobaoMyRewardRecord(self):
        """
        一元夺宝查询我的领奖记录
        """
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")

        from hall.entity import hall1yuanduobao
        rewardRecordList = hall1yuanduobao.duobaoRewardRecord(userId)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_rewardRecord')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('rewardRecordList', rewardRecordList)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='duobao_getWinRecord', clientIdVer=0)
    def doDuobaoGetWinRecord(self):
        """
        一元夺宝查询某一期的得主记录
        """
        msg = runcmd.getMsgPack()
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")
        duobaoId = msg.getParam("duobaoId")
        issue = msg.getParam("issue")

        ec = 0
        info = '查询成功'
        records = {}
        try:
            from hall.entity import hall1yuanduobao
            records = hall1yuanduobao.duobaoGetWinRecord(userId, duobaoId, issue)
        except TYBizException, e:
            ec = e.errorCode
            info = e.message

            ftlog.info('doDuobaoGetWinRecord failer',
                       'userId=', userId,
                       'duobaoId=', duobaoId,
                       'issue=', issue,
                       'ec=', ec,
                       'info=', info)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_getWinRecord')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('duobaoId', duobaoId)
        msg.setResult('issue', issue)
        msg.setResult('records', records)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        router.sendToUser(msg, userId)