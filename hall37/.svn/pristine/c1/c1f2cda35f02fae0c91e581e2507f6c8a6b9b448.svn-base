# -*- coding:utf-8 -*-
'''
Created on 2016年6月17日

@author: zhaojiangang
'''
from hall.entity import datachangenotify
from hall.entity.hallactivity.activity_send_reward import ActivitySendReward
from hall.entity.todotask import TodoTaskDownloadApkPromote, TodoTaskGoldRain, \
    TodoTaskHelper
from poker.entity.dao import gamedata, userchip, daoconst
import freetime.util.log as ftlog

@classmethod
def doSendReward(cls, gameId, userId, clientId, activityId):
    activities = {
        'activity_hall_reward_hszz':{
            'url':'http://apk.dl.tuyoo.com/down/hszz/Clash_Royale.apk',
            'rewardChip':10000,
            'goldRain':'恭喜您获得1万金币',
            'intActId':20000
        },
        'act_hall_reward_wzry':{
            'url':'http://down.s.qq.com/download/apk/10015420_com.tencent.tmgp.sgame.apk',
            'rewardChip':0,
            'goldRain':'恭喜您获得100金币',
            'intActId':20001
        },
        'act_hall_reward_cyhx':{
            'url':'http://down.s.qq.com/download/apk/10015420_com.tencent.tmgp.cf.apk',
            'rewardChip':0,
            'goldRain':'恭喜您获得100金币',
            'intActId':20002
        }        
    }
    actConf = activities.get(activityId)
    if actConf:
        todotasks = [TodoTaskDownloadApkPromote(actConf['url'])]
        if (actConf['rewardChip'] > 0
            and gamedata.setnxGameAttr(userId, gameId, 'act.sendReward:%s' % (activityId), 1) == 1):
            # 发1完金币
            userchip.incrChip(userId, gameId, actConf['rewardChip'],
                              daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                              'ACTIVITY_REWARD',
                              actConf['intActId'],
                              clientId)
            datachangenotify.sendDataChangeNotify(gameId, userId, ['chip'])
            todotasks.append(TodoTaskGoldRain(actConf['goldRain']))
            ftlog.info('ActivitySendReward.doSendReward gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'activityId=', activityId,
                       'rewardChip=', actConf['rewardChip'])
        TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)
        
ActivitySendReward.doSendRewardOld = ActivitySendReward.doSendReward
ActivitySendReward.doSendReward = doSendReward


