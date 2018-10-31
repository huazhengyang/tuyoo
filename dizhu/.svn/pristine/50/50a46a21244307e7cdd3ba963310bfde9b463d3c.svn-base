# -*- coding: utf-8 -*-
'''
Created on 2018年5月10日

@author: wangyonghui
'''
import freetime.util.log as ftlog
from dizhu.entity import dizhu_util
from freetime.core.tasklet import FTTasklet
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import configure
from freetime.entity.msg import MsgPack
from poker.protocol import router


def sendLoginReward(gameId, userId, clientId, iscreate, isdayfirst):
    if iscreate:
        newUserReward = configure.getGameJson(gameId, 'login.reward', {}).get('newUserReward')
        if newUserReward:
            if not newUserReward.get('open', 0):
                return
            rewards = newUserReward.get('rewards')
            if rewards:
                mail = newUserReward.get('mail')
                contentItems = TYContentItem.decodeList(rewards)
                dizhu_util.sendRewardItems(userId, contentItems, mail, 'LOGIN_REWARD', 0)
                FTTasklet.getCurrentFTTasklet().sleepNb(1.5)
                msg = MsgPack()
                msg.setCmd('dizhu')
                msg.setResult('action', 'new_user_reward')
                msg.setResult('rewards', rewards)
                msg.setResult('cardNoteCount', newUserReward.get('cardNoteCount', 0))
                router.sendToUser(msg, userId)
                ftlog.info('dizhu_login_reward.sendLoginReward newUserReward userId=', userId,
                           'gameId=', gameId,
                           'clientId=', clientId,
                           'iscreate=', iscreate,
                           'isdayfirst=', isdayfirst,
                           'rewards=', rewards)
