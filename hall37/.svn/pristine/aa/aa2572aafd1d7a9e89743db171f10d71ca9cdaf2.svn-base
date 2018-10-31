# -*- coding:utf-8 -*-

from hall import client_ver_judge
from hall.entity import hallvip, datachangenotify
from hall.entity.hallbenefits import TYUserBenefitsData

import poker.entity.dao.userchip as pkuserchip
import poker.util.timestamp as pktimestamp


def sendBenefits(self, gameId, userId, timestamp=None):
    '''
    发放救济金
    @return: isSend(True/False), TYUserBenefits
    '''
    if timestamp is None:
        timestamp = pktimestamp.getCurrentTimestamp()
    chip = pkuserchip.getUserChipAll(userId)
    if chip < self._minChip:
        # 添加关于版本控制的部分,当版本高于4.01且不是VIP玩家时不发送救济金
        from poker.util import strutil
        # 避免其他游戏修改调用接口,用过session来获取clientID
        from poker.entity.dao import sessiondata
        clientId = sessiondata.getClientId(userId)
        _, clientVer, _ = strutil.parseClientId(clientId)
        userVipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        if clientVer >= client_ver_judge.client_ver_451 and userVipLevel == 0:
            return False, self.loadUserBenefits(gameId, userId, timestamp)

        # 用户金币低于指定数目时，发放救济金
        userBenefits = self.loadUserBenefits(gameId, userId, timestamp)
        if not userBenefits.hasLeftTimes():  # 没有剩余次数，弹分享引导
            # oldtime = gamedata.getGameAttr(userId, HALL_GAMEID, 'relief_share_date')
            # if not oldtime or datetime.fromtimestamp(oldtime).date() < datetime.fromtimestamp(timestamp).date():
            #     # 每天最多弹一次
            #     gamedata.setGameAttr(userId, HALL_GAMEID, 'relief_share_date', timestamp)
            #     shareId = hallshare.getShareId('Relieffund', userId, gameId)
            #     share = hallshare.findShare(shareId)
            #     if share:
            #         task = share.buildTodotask(gameId, userId, 'Relieffund')
            #         TodoTaskHelper.sendTodoTask(gameId, userId, task)
            return False, userBenefits

        # 发放救济金
        userBenefits.times += 1
        self._benefitsDao.saveUserBenefitsData(userId, TYUserBenefitsData(userBenefits.times, timestamp))
        self._sendBenefits(gameId, userBenefits)
        # 通知用户金币刷新
        datachangenotify.sendDataChangeNotify(gameId, userId, ['udata'])
        return True, userBenefits
    return False, self.loadUserBenefits(gameId, userId, timestamp)

from hall.entity.hallbenefits import TYBenefitsSystemImpl
TYBenefitsSystemImpl.sendBenefits = sendBenefits