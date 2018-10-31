# -*- coding:utf-8 -*-

'''
天降彩蛋活动
活动期间内，玩家在经典场、欢乐场等有机会获得彩蛋掉落
'''

# Author leiyunfei <leiyunfei@tuyoogame.com>
# Created 2017年3月27日

import random

import freetime.util.log as ftlog

import poker.util.timestamp as pktimestamp
import poker.util.strutil as strutil
import poker.entity.biz.message.message as pkmessage

from hall.entity import hallitem
from hall.entity.hallconf import HALL_GAMEID

from dizhucomm.entity.events import UserTableWinloseEvent
from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID



def hit(candidate):
    # 是否命中：
    p = random.randint(1, 10000)
    return p <= candidate
    

class SkyEggActivity(ActivityNew):
    TYPE_ID = 'ddz.act.sky_egg'

    def __init__(self):
        super(SkyEggActivity, self).__init__()
        self._mail = None
        self._rewardConf = None
        
    def init(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, self._handleTableWinlose)
    
    def cleanup(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().unsubscribe(UserTableWinloseEvent, self._handleTableWinlose)
        
    def _decodeFromDictImpl(self, d):
        # 解析配置加载到内存

        if ftlog.is_debug():
            ftlog.debug('SkyEggActivity._decodeFromDictImpl', d)
        self._rewardConf = d.get('rewards')
        self._mail = d.get('mail')
        ftlog.debug('SkyEggActivity', self._rewardConf)
        return self
       
    def _handleTableWinlose(self, event):
        # 该局结束了, 按照配置概率给参与该局的玩家发送彩蛋奖励，
        # 玩家也可能没有获得彩蛋奖励
        
        userId = event.userId
        roomId = event.roomId
        tableId = event.tableId
        # 获取房间奖励配置
        # 'reward': {'item': 'item:chip', 'count': n}   --> 奖励
        # 'prob': p   --> 奖励万分比
        bigRoomId = strutil.getBigRoomIdFromInstanceRoomId(roomId)
        roomReward = self._rewardConf.get(str(bigRoomId))
        if ftlog.is_debug():
            ftlog.debug('SkyEggActivityRewardConfig: ', self._rewardConf, 'roomId: ', roomId, ' bigRoomId: ', bigRoomId, ' RoomReward: ', roomReward)
        if not roomReward:
            if ftlog.is_debug():
                ftlog.debug('SkyEggActivity ', roomId, 'dismatch SkyEggActivity!!!')
            return
        rp = roomReward.get('prob')
        if not rp:
            ftlog.error('SkyEggActivity Room ', roomId, ' lack of "prob" config item!!!!!')
            return
        reward = roomReward.get('reward')
        contents = roomReward.get('desc')
        if self._mail and contents:
            mail = strutil.replaceParams(self._mail, {'rewardContent':contents})
        else:
            mail = None
    
        if hit(rp) and self.checkTime(pktimestamp.getCurrentTimestamp()) == 0:
            ftlog.info('SkyEggActivity User: ', userId, 'luckly gain reward: ', reward, ' at room: ', roomId, ' table: ', tableId)
            self.sendReward(userId, reward, mail)
            
        if ftlog.is_debug():
            ftlog.debug('SkyEggActivy._handleTableWinlose： UserId = ', userId,
                        'bigRoomId = ', bigRoomId,
                        'reward = ', roomReward,
                        'mail = ', mail,
                        'reward = ', reward)
            
    def sendReward(self, userId, reward, mail):
        # 给幸运玩家发彩蛋
        # TODO: 需不需要发邮件？
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, count, _ = userAssets.addAsset(DIZHU_GAMEID, 
                                                  reward.get('itemId'), 
                                                  reward.get('count'), 
                                                  pktimestamp.getCurrentTimestamp(),
                                                  'ACTIVITY_REWARD',
                                                  self.intActId)
        item = {}
        item['name'] = assetKind.displayName
        item['pic'] = assetKind.pic
        item['count'] = count
        from hall.entity.todotask import TodoTaskHelper, TodoTaskShowRewards
        rewardTodotask = TodoTaskShowRewards([item]) 
        if ftlog.is_debug():
            ftlog.debug('SkyEggActivity send user ', userId, ' "todotask:"', rewardTodotask)

        TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, rewardTodotask)

        pkmessage.sendPrivate(HALL_GAMEID, userId, 0, mail)
