# -*- coding=utf-8
'''
Created on 2015年7月15日

@author: rex
'''

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod

@markCmdActionHandler
class YouKuHandler(BaseMsgPackChecker):

    def _check_param_taskId(self, msg, key, params):
        paramId = msg.getParam(key)
        try:
            return None, int(paramId)
        except:
            return 'ERROR of id !' + str(paramId), None

    def _check_param_grade(self, msg, key, params):
        paramId = msg.getParam(key)
        try:
            return None, int(paramId)
        except:
            return 'ERROR of id !' + str(paramId), None

    @markCmdActionMethod(cmd='h5_youku_dizhu', action="get_left_raffle_times", clientIdVer=0, scope='game')
    def get_left_raffle_times(self, userId, gameId):
        # timestamp = pktimestamp.getCurrentTimestamp()
        # taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
        from dizhu.activities.h5youku import YouKu
        times = YouKu.getLeftRaffleTimes(userId, gameId)
        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'get_left_raffle_times')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('times', times)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='h5_youku_dizhu', action="raffle", clientIdVer=0, scope='game')
    def raffle(self, userId, gameId):
        ftlog.debug('raffle...')
        from dizhu.activities.h5youku import YouKu
        times = YouKu.getLeftRaffleTimes(userId, gameId)
        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'raffle')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        if times <= 0:
            mo.setResult('prize_id', 0)
            router.sendToUser(mo, userId)
            return
        YouKu.raffle(userId, gameId, mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='h5_youku_dizhu', action="get_raffle_info", clientIdVer=0, scope='game')
    def get_raffle_info(self, userId, gameId):
        # timestamp = pktimestamp.getCurrentTimestamp()
        # taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
        from dizhu.activities.h5youku import YouKu
        left_times = YouKu.getLeftRaffleTimes(userId, gameId)
        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'get_raffle_info')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('left_times', left_times)
        YouKu.get_award_show_list(userId, gameId, mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='h5_youku_dizhu', action="get_prizes", clientIdVer=0, scope='game')
    def get_prizes(self, userId, gameId):
        # timestamp = pktimestamp.getCurrentTimestamp()
        # taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
        from dizhu.activities.h5youku import YouKu
        prizes = YouKu.get_user_ex_prize(userId)
        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'get_prizes')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('prizes', prizes)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='h5_youku_dizhu', action="exchange_vip_reward", clientIdVer=0, scope='game')
    def exchange_vip_reward(self, userId, gameId, grade):
        # timestamp = pktimestamp.getCurrentTimestamp()
        # taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
        from dizhu.activities.h5youku import YouKu
        ret = YouKu.exchange_user_vip_charge(gameId, userId, grade)
        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'exchange_vip_reward')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('grade', grade)
        mo.setResult('code', ret)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='h5_youku_dizhu', action="get_vip_charge_info", clientIdVer=0, scope='game')
    def get_vip_charge_info(self, userId, gameId):
        # timestamp = pktimestamp.getCurrentTimestamp()
        # taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
        from dizhu.activities.h5youku import YouKu
        vip_charge_info = YouKu.get_user_vip_charge_info(userId)
        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'get_vip_charge_info')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('vip_charge_info', vip_charge_info)
        router.sendToUser(mo, userId)
