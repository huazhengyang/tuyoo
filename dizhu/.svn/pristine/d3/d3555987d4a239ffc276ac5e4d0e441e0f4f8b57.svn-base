# -*- coding=utf-8 -*-
'''
Created on 2016-07-15

@author: luwei
'''
from __future__ import division
import time

from dizhu.activities.betguess import ActivityModel, IssueCalculator, \
    UserRecorder
from dizhu.activities.toolbox import Tool
import dizhu.servers.util.rpc.act_betguess_remote as act_betguess_remote
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity.hallactivity.activity import TYActivityDaoImpl
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.util import strutil


@markHttpHandler
class BetguessHttpHandler(BaseHttpMsgChecker):

    def __init__(self):
        pass
    
    def checkCode(self):
        code = ''
        datas = runhttp.getDict()
        if 'code' in datas:
            code = datas['code']
            del datas['code']
        keys = sorted(datas.keys())
        checkstr = ''
        for k in keys:
            checkstr += k + '=' + datas[k] + '&'
        checkstr = checkstr[:-1]

        apikey = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'
        checkstr = checkstr + apikey
        if code != strutil.md5digest(checkstr):
            return -1, 'Verify code error'

        acttime = int(datas.get('time', 0))
        if abs(time.time() - acttime) > 10:
            return -1, 'verify time error'
        return 0, None
    
    @classmethod
    def makeErrorResponse(cls, errormsg=None):
        mo = MsgPack()
        mo.setResult("code", -1)
        mo.setResult("error", errormsg)
        mo.setError(-1, errormsg)
        return mo

    @markHttpMethod(httppath='/_gdss/dizhu/act/betguess/query')
    def doActivityBetguessQueryGdss(self):
        ec, result = self.checkCode()
        if ec != 0:
            mo = MsgPack()
            mo.setError(ec, result)
            return mo
        
        return self.doActivityBetguessQuery()
    
    @markHttpMethod(httppath='/_gdss/dizhu/act/betguess/setresult')
    def doActivityBetguessSetResultGdss(self):
        ec, result = self.checkCode()
        if ec != 0:
            mo = MsgPack()
            mo.setError(ec, result)
            return mo
        
        return self.doActivityBetguessSetResult()

#     @markHttpMethod(httppath='/dizhu/v1/act/betguess/query')
    def doActivityBetguessQuery(self):
        '''
        @param activityGameId: 6(配置里配置的哪个GameId就填哪个GameId)
        @param activityId: 活动ID
        @param issueNumber: '2016-10-31 18:20:00'
        '''
        try:
            activityGameId = runhttp.getParamInt('activityGameId')
            activityId = runhttp.getParamStr('activityId')
            issueNumber = runhttp.getParamStr('issueNumber')
            if activityGameId == None or \
                activityId == None or \
                issueNumber == None:
                return self.makeErrorResponse('params error').pack()

            ftlog.debug('BetguessHttpHandler.doActivityBetguessQuery',
                        'activityGameId=', activityGameId,
                        'activityId=', activityId,
                        'issueNumber=', issueNumber)

            activityModel = ActivityModel.loadModel(activityGameId, activityId, issueNumber)

            err, issueMap = self.getActivityIssueMapConf(activityId)
            if err:
                return err
            
            issueCalculator = IssueCalculator(issueMap)
            issueConf = issueCalculator.getCurrentIssueConf(issueNumber)
            if (issueNumber not in issueMap) or (not issueConf):
                return self.makeErrorResponse('issueNumber not found! issueNumber maybe error').pack()

            bankerPumping = issueConf.get('bankerPumping', 0)
            # 奖池为抽水金额
            totalChip = activityModel.countChipLeft+activityModel.countChipRight
            # 奖池金额
            betPoolChip = int((activityModel.countChipLeft+activityModel.countChipRight)*(1-bankerPumping))
            # 左赔率
            leftBetOdds = betPoolChip/activityModel.countChipLeft if activityModel.countChipLeft>0 else 0
            # 右赔率
            rightBetOdds = betPoolChip/activityModel.countChipRight if activityModel.countChipRight>0 else 0
            
            response = MsgPack()
            response.setResult('totalChip', totalChip)
            response.setResult('betPoolChip', betPoolChip)
            response.setResult('leftBetOdds', leftBetOdds)
            response.setResult('rightBetOdds', rightBetOdds)
            response.setResult('bankerPumping', bankerPumping)
            response.setResult('countChipLeft', activityModel.countChipLeft)
            response.setResult('countChipRight', activityModel.countChipRight)
            response.setResult('resultState', activityModel.resultState)
            
            response.setResult("activityModel", activityModel.__dict__)
            response.setResult('pastIssueNumberList', issueCalculator.getAlreadyPastIssueNumberList())
            return response.pack()
        except:
            ftlog.error()
            return self.makeErrorResponse().pack()
        
#     @markHttpMethod(httppath='/dizhu/v1/act/betguess/setresult')
    def doActivityBetguessSetResult(self):
        '''
        @param activityGameId: 6(配置里配置的哪个GameId就填哪个GameId)
        @param activityId: 活动ID
        @param issueNumber: '2016-10-31 18:20:00'
        @param resultState: 0,1,2
        '''
        try:
            activityGameId = runhttp.getParamInt('activityGameId')
            activityId = runhttp.getParamStr('activityId')
            issueNumber = runhttp.getParamStr('issueNumber')
            resultState = runhttp.getParamInt('resultState')
            if activityGameId == None or \
                activityId == None or \
                issueNumber == None or \
                resultState == None:
                return self.makeErrorResponse('params error').pack()
            
            ftlog.debug('BetguessHttpHandler.doActivityBetguessSetResult',
                        'activityGameId=', activityGameId,
                        'activityId=', activityId,
                        'issueNumber=', issueNumber,
                        'resultState=', resultState)
            
            err, issueMap = self.getActivityIssueMapConf(activityId)
            if err:
                return err
                        
            # 验证issueNumber是否存在
            if issueNumber not in issueMap:
                return self.makeErrorResponse('issueNumber not found! issueNumber maybe error').pack()
            
            # 给活动设置竞猜结果
            if not ActivityModel.updateResult(activityGameId, activityId, issueNumber, resultState):
                return self.makeErrorResponse('result set failed! resultState maybe error').pack()

            # 获得最新的活动数据
            activityModel = ActivityModel.loadModel(activityGameId, activityId, issueNumber)
            if activityModel.resultState == activityModel.RESULT_STATE_NONE:
                return self.makeErrorResponse('activityModel.resultState not set!').pack()
            
            # 遍历参与玩家
            chipCounter = 0
            userIdList = UserRecorder.getUsers(activityGameId, activityId, issueNumber)
            for userId in userIdList:
                response = act_betguess_remote.sendRewards(userId, 
                                                        activityModel.countChipLeft, activityModel.countChipRight, activityModel.resultState, 
                                                        activityGameId, activityId, issueNumber)
                if response.get('err'):
                    return self.makeErrorResponse(response.get('err')).pack()
                chipCounter += response.get('chip', 0)
            
            activityModel = ActivityModel.loadModel(activityGameId, activityId, issueNumber)
            response = MsgPack()
            response.setResult("activityModel", activityModel.__dict__)
            response.setResult('allchip', chipCounter)
            return response.pack()
        except:
            ftlog.error()
            return self.makeErrorResponse().pack()

    def getActivityIssueMapConf(self, activityId):
        '''
        返回的第一个值err，若存在则代表发生错误
        返回的第二个值issueMap，若发生错误则为空
        '''
        actconf = TYActivityDaoImpl.getActivityConfig(activityId)
        ftlog.debug('BetguessHttpHandler.getActivityIssueMapConf:actconf=', actconf)
        if not actconf:
            return self.makeErrorResponse('actconf not found! activityId maybe error').pack()
        
        issueMap = Tool.dictGet(actconf, 'config.issueMap', {})
        ftlog.debug('BetguessHttpHandler.getActivityIssueMapConf:issueMap=', issueMap)
        if not issueMap:
            return self.makeErrorResponse('actconf.config.issueMap not found! actconf maybe error').pack()
        
        return None, issueMap
        

#     @markHttpMethod(httppath='/dizhu/v1/act/betguess/userbet')
#     def doActivityBetguessUserBet(self):
#         '''
#         @param activityGameId: 6(配置里配置的哪个GameId就填哪个GameId)
#         @param activityId: 活动ID
#         @param issueNumber: '2016-10-31 18:20:00'
#         @param userId: userId
#         @param betChip: 下注金币
#         @param isLeft: 0(False),1(True)
#         '''
#         try:
#             activityGameId = runhttp.getParamInt('activityGameId')
#             activityId = runhttp.getParamStr('activityId')
#             issueNumber = runhttp.getParamStr('issueNumber')
#             userId = runhttp.getParamInt('userId')
#             betChip = runhttp.getParamInt('betChip')
#             isLeft = runhttp.getParamInt('isLeft')
#             if activityGameId == None or \
#                 activityId == None or \
#                 issueNumber == None or \
#                 userId == None or \
#                 betChip == None or \
#                 isLeft == None:
#                 return self.makeErrorResponse('params error').pack()
# 
#             ftlog.debug('BetguessHttpHandler.doActivityBetguessUserBet',
#                         'userId=', userId,
#                         'betChip=', betChip,
#                         'isLeft=', isLeft,
#                         'activityGameId=', activityGameId,
#                         'activityId=', activityId,
#                         'issueNumber=', issueNumber)
# 
#             err, ret = act_betguess_remote.userBet(userId, betChip, isLeft==1, issueNumber, activityId)
#             if err:
#                 return self.makeErrorResponse(err).pack()
#             
#             activityModel = ActivityModel.loadModel(activityGameId, activityId, issueNumber)
#             response = MsgPack()
#             response.setResult("activityModel", activityModel.__dict__)
#             response.setResult("activityData", ret)
#             return response.pack()
#         except:
#             ftlog.error()
#             return self.makeErrorResponse().pack()