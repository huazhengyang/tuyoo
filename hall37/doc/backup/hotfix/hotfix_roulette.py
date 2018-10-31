# -*- coding=utf-8 -*-
'''
Created on 2016年7月21日

@author: wuyongsheng
'''

import hall.entity.hallroulette as hallroulette
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import hallvip, halluser
import random, json, time
import freetime.util.log as ftlog
import poker.entity.dao.userchip as pkuserchip
from poker.entity.dao import gamedata as pkgamedata
import hall.servers.center.rpc.roulette_remote as rouletteRpc
from poker.entity.dao import daobase

def findRewardUsers(gameId, issue, reward, clientId):
    x = random.randint(1, hallroulette.soldierSysTem.getSoldierNumber())
    soldier = hallroulette.soldierSysTem.getSoldierforsId(x)
    count = 3
    while(count):
        if soldier :
            break
        x = random.randint(1, hallroulette.soldierSysTem.getSoldierNumber())
        soldier = hallroulette.soldierSysTem.getSoldierforsId(x)
        count -= 1
    ftlog.info('findRewardUsers.gameId=', gameId,
               'issue=', issue,
               'reward=', reward,
               'clientId=', clientId,
               'x=', x,
               'soldier=', soldier)
    if not soldier:
        ftlog.info('findRewardUsers.gameId=', gameId,
                   'issue=', issue,
                   'reward=', reward,
                   'errorMessage=', 'not find the soldier user!')
        return 0, 0
    nowUserId = soldier.get('userId', 0)
    chip = pkuserchip.getUserChipAll(nowUserId)
    vip = hallvip.userVipSystem.getUserVip(nowUserId).vipLevel.level
    userInfo = halluser.getUserInfo(nowUserId, gameId, clientId)
    result = {}
    result['chip'] = chip
    result['vip'] = vip
    result['sex'] = userInfo.get('sex', 0)
    result['purl'] = userInfo.get('purl', '')
    result['sId'] = '%07d'%x
    result['uId'] = nowUserId
    result['issue'] = issue
    result['name'] = userInfo.get('name', '')
    result['nowReward'] = reward
    nowRewardNumber = pkgamedata.incrGameAttr(nowUserId, 9999, 'getRewardNumber', 1)
    result['getRewardNumber'] = nowRewardNumber
    result['isCheckin'] = 0
    result['checkinSoldiers'] = pkgamedata.getGameAttrInt(nowUserId, 9999, 'checkinSoldiers')
    ftlog.info('findRewardUsers.gameId=', gameId,
               'nowUserId=', nowUserId,
               'result=', result)
    return nowUserId, result

def findSoldierForUser(number, userId, clientId):
    from hall.entity import hallroulette
    snatchConf = hallroulette.getSnatchConf()
    needNumber = snatchConf.get('needNumber', 0)
    nowNum = int(daobase.executeMixCmd('hincrby', 'allSoldier', 'soldierNumber', number))
    ftlog.info('sendReward.userId=', userId,
                'number=', number,
                'needNumber=', needNumber,
                'nowNum=', nowNum)
    if nowNum >= needNumber:
        #小兵进行拆分,先发一批，然后抽奖，最后在发一批
        sencondNumber = nowNum - needNumber
        firstNumber = number - sencondNumber
        ftlog.info('sendReward.sencondNumber=', sencondNumber,
                   'firstNumber=', firstNumber)
        daobase.executeMixCmd('hincrby', 'allSoldier', 'soldierNumber', -number)
        _list = hallroulette.soldierSysTem.getSoldier(userId, firstNumber)
        tempIssue = hallroulette.getIssue(False)
        daobase.executeMixCmd('hincrby', 'allSoldier', 'soldierNumber', firstNumber)
        issue = time.strftime("%Y%m%d", time.localtime()) + tempIssue
        nowUserId, nowResult = hallroulette.findRewardUsers(HALL_GAMEID, issue, snatchConf.get('desc',''), clientId)
        if not nowUserId or not nowResult:
            ftlog.info('issue is died because not find the user!!!')
            hallroulette.soldierSysTem.clearSoldierIdToUserGameData(userId, HALL_GAMEID, issue)
            hallroulette.soldierSysTem.clearSoldierNumber()
            hallroulette.soldierSysTem.clearUserIds()
            _nowIssue = hallroulette.getIssue(True)
            return hallroulette.soldierSysTem.getSoldier(userId, sencondNumber)
        hallroulette.sendSoldierRewardToUser(nowUserId, HALL_GAMEID, snatchConf.get('prize',{}))
        ftlog.info('doGetSoldierInfo.issue=', tempIssue,
                   'soldierNumber=', hallroulette.soldierSysTem.getSoldierNumber(),
                   'soldierId=', nowResult['sId'],
                   'rewardContent=', snatchConf.get('desc', 0),
                   'userIds=',json.loads(daobase.executeMixCmd('HGET', 'allSoldier', 'userIds')))
        hallroulette.setRwardData(nowResult)
        _nowIssue = hallroulette.getIssue(True)
        hallroulette.sendMsgToUser(nowUserId, HALL_GAMEID)
        hallroulette.soldierSysTem.clearSoldierIdToUserGameData(userId, HALL_GAMEID, issue)
        hallroulette.soldierSysTem.clearSoldierNumber()
        hallroulette.soldierSysTem.clearUserIds()
        daobase.executeMixCmd('hincrby', 'allSoldier', 'soldierNumber', sencondNumber)
        ftlog.info('sendReward.over.begin.new.issue')
        return hallroulette.soldierSysTem.getSoldier(userId, sencondNumber)
    else:
        #直接下发
        ftlog.info('sendReward.userId=', userId,
                   'number=', number)
        daobase.executeMixCmd('hincrby', 'allSoldier', 'soldierNumber', -number)
        result = hallroulette.soldierSysTem.getSoldier(userId, number)
        daobase.executeMixCmd('hincrby', 'allSoldier', 'soldierNumber', number)
        return result
    
@classmethod
def getSoldierforsId(self, x):
    soldierMap = daobase.executeMixCmd('HGET', 'allSoldier', 'soldiers')
    soldierMap = json.loads(soldierMap)
    temp = soldierMap.get(str(x), None)
    if not temp:
        ftlog.warn('the soldier not find x=', x)
        return
    from datetime import datetime
    issueNow = time.strftime("%Y%m%d", time.localtime()) + hallroulette.getIssue(False)
    ftlog.info('getSoldierforsId.issueNow=', issueNow,
               'x=', x,
               'time=', datetime.now().date().strftime('%Y%m%d'),
               'soldierMap=', soldierMap)
    daobase.executeMixCmd('HSET', 'allSoldier', 'soldiers', 0)
    return temp
    
hallroulette.findRewardUsers = findRewardUsers
rouletteRpc.findSoldierForUser = findSoldierForUser
hallroulette.soldierSysTem.getSoldierforsId = getSoldierforsId