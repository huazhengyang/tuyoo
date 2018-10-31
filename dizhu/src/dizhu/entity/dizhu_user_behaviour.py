# -*- coding=utf-8 -*-
"""
Created on 2017年11月27日

@author: wangjifa
"""

import random, os
import datetime

import freetime.util.log as ftlog
from dizhu.activities.toolbox import UserInfo
from dizhu.entity import dizhuconf, dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.entity.events import UserTablePlayEvent
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
from hall.entity import datachangenotify
from hall.entity.todotask import TodoTaskHelper, TodoTaskShowRewards
from poker.entity.biz.bireport import reportGameEvent
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata
from poker.entity.dao import daobase, userdata, sessiondata
from poker.entity.events.tyevent import EventUserLogin
from poker.util import strutil
import poker.util.timestamp as pktimestamp

#干预行为的类型：
BEHAVIOUR_TYPE_NONE = 0     # 预测不流失
BEHAVIOUR_TYPE_REWARD = 1   # 发奖
BEHAVIOUR_TYPE_MSG = 2      # 发消息 # 已废弃
BEHAVIOUR_TYPE_NOUSE = 3    # 放置不处理
BEHAVIOUR_TYPE_REWARDED = 4 # 已发过奖
BEHAVIOUR_TYPE_NOUSEED = 5  # 已处理过的放置组

_initing = False

def _checkExpectedUser(userId, behaviourConf):
    if not behaviourConf or behaviourConf.get('open', 0) != 1:
        return False

    # 过滤clientId
    _, intClientId = sessiondata.getClientIdNum(userId)
    intClientIds = behaviourConf.get('intClientIds', [])
    if intClientId in intClientIds:
        return False

    # 过滤注册时间在7天以内的用户
    timestamp = pktimestamp.getCurrentTimestamp()
    if UserInfo.getRegisterDays(userId, timestamp) <= 7:
        return False
    return True


def initialize():
    FTLoopTimer(60, -1, onTimer).start()


def onTimer():
    # 配置时间点执行 默认早晨7点
    global _initing
    behaviourConf = dizhuconf.getUserBehaviourReward()
    if not behaviourConf or behaviourConf.get('open', 0) != 1:
        return

    if not gdata.initializeOk():
        return

    try:
        executeTime = behaviourConf.get('executeTime', "6:05:00")
        executeTime = datetime.datetime.strptime(executeTime, "%H:%M:%S")
        if not _initing:
            if datetime.datetime.now().time() >= executeTime.time():
                _initing = _getInfoFromTxt(behaviourConf)
        else:
            if datetime.datetime.now().time() < executeTime.time():
                _initing = False

    except Exception, e:
        _initing = False
        ftlog.warn('dizhu_user_behaviour.onTimer.config err=', e.message)
        return


def _getInfoFromTxt(behaviourConf):
    try:
        curDate = datetime.datetime.now().strftime('%Y-%m-%d')
        fileName = 'dizhu/behaviour/ddz_prediction_%s.txt' % curDate
        fileName = os.path.join(gdata.pathWebroot(), fileName)

        ret = os.path.isfile(fileName)
        if not ret:
            ftlog.warn('dizhu_user_behaviour.file_not_exist',
                       'fileName=', fileName, 'ret=', ret)
            return False

        index = 0
        with open(fileName) as fileObject:
            for line in fileObject:
                index += 1
                if not line:
                    break

                infos = line.split('\t')
                userId = infos[0]
                status = infos[1].split('\n')[0]

                try:
                    userId = int(userId)
                except ValueError:
                    ftlog.warn('dizhu_user_behaviour.ValueError userId=', userId)
                    continue

                if not _saveUserToRedis(userId, status, behaviourConf):
                    continue

                if ftlog.is_debug():
                    ftlog.debug('dizhu_user_behaviour.DIZHU_BEHAVIOUR_GROUP',
                                'userId=', userId,
                                'state=', status)

                # 1000行sleep 0.1秒
                if index >= 1000:
                    index = 0
                    FTTasklet.getCurrentFTTasklet().sleepNb(0.1)

        ftlog.info('dizhu_user_behaviour.fileLoadOver fileName=', fileName)

    except Exception, e:
        ftlog.warn('dizhu_user_behaviour.loadConf. error=', str(e))
        return False
    return True


def _saveUserToRedis(userId, status, behaviourConf):
    if not userdata.checkUserData(userId):
        return False

    if not _checkExpectedUser(userId, behaviourConf):
        return False

    todayDate = int(dizhu_util.calcTodayIssueNum())
    behaviourInfo = {'type': BEHAVIOUR_TYPE_NONE, 'date': todayDate}
    try:
        ret = daobase.executeUserCmd(userId, 'HGET', 'userBehaviour:6:' + str(userId), 'info')
        if ret:
            ret = strutil.loads(ret)
            behaviourType = ret.get('type', BEHAVIOUR_TYPE_NONE)
            if behaviourType not in [BEHAVIOUR_TYPE_REWARDED, BEHAVIOUR_TYPE_NOUSEED]:
                behaviourInfo['type'] = random.randrange(1, 3, 1) if status == '0' else BEHAVIOUR_TYPE_NONE
                return daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info', strutil.dumps(behaviourInfo))
        else:
            behaviourInfo['type'] = random.randrange(1, 3, 1) if status == '0' else BEHAVIOUR_TYPE_NONE
            return daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info', strutil.dumps(behaviourInfo))
    except Exception, e:
        ftlog.warn('dizhu_user_behaviour._saveUserToRedis userId=', userId, 'err=', e)
    return False


def initBehaviourReward():
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().subscribe(UserTablePlayEvent, _sendUserBehaviourReward)

    from hall.game import TGHall
    TGHall.getEventBus().subscribe(EventUserLogin, _onUnExpectedUserLogin)

def _onUnExpectedUserLogin(event):
    userId = event.userId
    behaviourConf = dizhuconf.getUserBehaviourReward()
    if not _checkExpectedUser(userId, behaviourConf):
        if ftlog.is_debug():
            ftlog.debug('_onUnExpectedUserLogin check failed userId=', userId)
        return

    _, intClientId = sessiondata.getClientIdNum(userId)
    expectedClientIds = behaviourConf.get('expectedClientIds', [])

    try:
        # 只处理配置中的clientId包的表外用户
        if expectedClientIds and intClientId in expectedClientIds:
            todayDate = int(dizhu_util.calcTodayIssueNum())
            olderInfo = daobase.executeUserCmd(event.userId, 'HGET', 'userBehaviour:6:' + str(userId), 'info')
            if olderInfo:
                olderInfo = strutil.loads(olderInfo)
                olderType = olderInfo.get('type', 0)
                olderDate = olderInfo.get('date', 0)
                if olderType in [BEHAVIOUR_TYPE_REWARDED, BEHAVIOUR_TYPE_NOUSEED]:
                    # 已处理过的不再处理
                    return
                if olderDate - todayDate > 1:
                    # 过期记录重新分组
                    behaviourInfo = {'type': random.randrange(1, 4, 2), 'date': todayDate}
                    daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info',
                                           strutil.dumps(behaviourInfo))
                    ftlog.info('_onUnExpectedUserLogin userId=', userId,
                               'info=', behaviourInfo,
                               'olderInfo=', olderInfo)
            else:
                # 未记录过的表外用户平均分到1、3组
                behaviourInfo = {'type': random.randrange(1, 4, 2), 'date': todayDate}
                daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info',
                                       strutil.dumps(behaviourInfo))
    except Exception, e:
        ftlog.warn('_onUnExpectedUserLogin userId=', userId, 'error=', e)

def _sendUserBehaviourReward(event):
    userId = event.userId
    behaviourConf = dizhuconf.getUserBehaviourReward()
    if not _checkExpectedUser(userId, behaviourConf):
        return
    try:
        ret = daobase.executeUserCmd(event.userId, 'HGET', 'userBehaviour:6:' + str(event.userId), 'info')
        if ret:
            behaviourInfo = strutil.loads(ret)
            behaviourDate = behaviourInfo.get('date', 0)
            todayDate = int(dizhu_util.calcTodayIssueNum())
            if todayDate != behaviourDate:
                return

            behaviourType = behaviourInfo.get('type', 0)
            clientId = sessiondata.getClientId(event.userId)
            if behaviourType == BEHAVIOUR_TYPE_REWARD:
                _changeUserBehaviourInfo(event.userId, behaviourInfo, behaviourConf)
                reportGameEvent('DIZHU_BEHAVIOUR_GROUP', event.userId, DIZHU_GAMEID, 0, 0, 0, 0, behaviourType, 0, [],
                                clientId)
            elif behaviourType in [BEHAVIOUR_TYPE_MSG, BEHAVIOUR_TYPE_NOUSE]:
                behaviourInfo['type'] = BEHAVIOUR_TYPE_NOUSEED
                behaviourInfo['date'] = int(dizhu_util.calcTodayIssueNum())
                daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info',
                                       strutil.dumps(behaviourInfo))
                reportGameEvent('DIZHU_BEHAVIOUR_GROUP', event.userId, DIZHU_GAMEID, 0, 0, 0, 0, behaviourType, 0, [], clientId)
        #else #这个分支在玩家登陆时处理过了，无对应属性的玩家不处理。
    except Exception, e:
        ftlog.warn('_sendUserBehaviourReward userId=', userId, 'error=', e)

def _changeUserBehaviourInfo(userId, ret, behaviourConf):
    try:
        reward = behaviourConf.get('reward') if behaviourConf else None
        if not reward:
            return
        ret['type'] = BEHAVIOUR_TYPE_REWARDED
        daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info', strutil.dumps(ret))

        mailStr = behaviourConf.get('mail', '幸运女神的眷顾使你获得了奖励')
        contentItems = TYContentItem.decodeList(reward)
        assetList = dizhu_util.sendRewardItems(userId, contentItems, mailStr, 'USER_BEHAVIOUR_REWARD', userId)
        datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, mailStr)

        # 发奖弹窗
        rewardsList = []
        for assetItemTuple in assetList:
            assetItem = assetItemTuple[0]
            reward = {}
            reward['name'] = assetItem.displayName
            reward['pic'] = assetItem.pic
            reward['count'] = assetItemTuple[1]
            rewardsList.append(reward)

        reward_task = TodoTaskShowRewards(rewardsList)
        TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, reward_task)

        ftlog.info('userBehaviour.sendReward userId=', userId, 'reward=',
                   [(atp[0].kindId, atp[1]) for atp in assetList])

    except Exception, e:
        ftlog.warn('_changeUserBehaviourInfo userId=', userId, 'ret=', ret, 'err=', e)




