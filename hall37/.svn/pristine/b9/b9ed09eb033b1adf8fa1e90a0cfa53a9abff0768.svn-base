# -*- coding=utf-8
'''
Created on 2016年6月28日

@author: wuyongsheng
'''

import time
from hall.entity.hallconf import HALL_GAMEID
import freetime.util.log as ftlog

    
def sendReward(event):
    runLottery()
    
'''
    判断小兵的总数是否可以开奖
    可以开奖 对小兵数进行减少
            整理剩余小兵的编号
            开奖
            清理用户9999下的小兵数据
            只存储最近三期
    不可以开奖，什么都不做
''' 
def runLottery():
    from hall.entity import hallroulette
    snatchConf = hallroulette.getSnatchConf()
    needNumber = snatchConf.get('needNumber', 0)
    nowNum = hallroulette.getSoldierNumber()
    ftlog.debug('runLottery.needNumber=', needNumber,
               'nowNum=', nowNum)
    if nowNum >= needNumber:
        tempIssue = hallroulette.getIssue(False)
        issue = time.strftime("%Y%m%d", time.localtime()) + tempIssue
        nowUserId, nowResult = hallroulette.findRewardUsers(HALL_GAMEID, issue, snatchConf.get('desc',''))
        if nowUserId and nowResult:
            ftlog.info('roulette_remote.runLottery, issue:', issue
                       , ' userId:', nowUserId
                       , ' userRewardInfo:', nowResult
                       )
            #发奖
            hallroulette.sendSoldierRewardToUser(nowUserId, HALL_GAMEID, snatchConf.get('prize',{}))
            hallroulette.sendMsgToUser(nowUserId, HALL_GAMEID)
            
        #添加上一期的多余小兵到本期内
        _nowIssue = hallroulette.getIssue(True)
        ftlog.info('roulette_remote.runLottery nextIssue:', _nowIssue)