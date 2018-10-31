# -*- coding=utf-8 -*-
'''
Created on 2016-07-15

@author: luwei
'''
from dizhu.entity.erdayi import PlayerControl, ErrorEnum
import freetime.util.log as ftlog
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod


@markHttpHandler
class ErdayiHttpHandler(BaseHttpMsgChecker):

    def __init__(self):
        pass

    def checkBaseParams(self):
        userId = runhttp.getParamInt('userId')
        if userId <= 0:
            return userId, PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_USERID)
        
        # sign = runhttp.getParamStr('sign')
        # if not sign:
        #     return userId, PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_SIGN)

        authInfo = runhttp.getParamStr('authInfo')
        if not authInfo:
            return userId, PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_AUTHINFO)
        
        return userId, None
    
    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/getVCode')
    def do_player_getVCode(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            mobile = runhttp.getParamStr('mobile')
            if not mobile:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_MOBILE)
            ftlog.debug('do_player_getVCode', 
                        'userId=', userId,
                        'mobile=', mobile)
            response = PlayerControl.getVCode(userId, mobile)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/bindRealInfo')
    def do_player_bindRealInfo(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            realname = runhttp.getParamStr('realname')
            if not realname or len(realname)<=0:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_PARAM)
            idNo = runhttp.getParamStr('idNo')
            if not idNo:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_PARAM)
            mobile = runhttp.getParamStr('mobile')
            if not mobile:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_PARAM)
            vcode = runhttp.getParamInt('vcode')
            if not vcode:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_VCODE)

            ftlog.debug('do_player_bindRealInfo', 
                        'userId=', userId,
                        'realname=', realname,
                        'idNo=', idNo,
                        'mobile=', mobile,
                        'vcode=', vcode)
            
            response = PlayerControl.bindRealInfo(userId, realname, idNo, mobile, vcode)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/bindBankAccount')
    def do_player_bindBankAccount(self):
        if ftlog.is_debug():
            request = runhttp.getRequest()
            ftlog.debug('ErdayiHttpHandler.do_player_bindBankAccount',
                        'params=', runhttp.getDict())
            ftlog.debug('ErdayiHttpHandler.do_player_bindBankAccount',
                        'request=', request)
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            bankNo = runhttp.getParamStr('bankNo')
            if not bankNo:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_PARAM)
            bankName = runhttp.getParamStr('bankName')
            if not bankName:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_PARAM)
            bankAccount = runhttp.getParamStr('bankAccount')
            if not bankAccount:
                return PlayerControl.makeResponse(userId, ErrorEnum.ERR_BAD_PARAM)

            ftlog.debug('do_player_bindBankAccount', 
                        'userId=', userId,
                        'bankNo=', bankNo,
                        'bankName=', bankName,
                        'bankAccount=', bankAccount)
            
            response = PlayerControl.bindBankAccount(userId, bankNo, bankName, bankAccount)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/withdraw')
    def do_player_withdraw(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_withdraw', 
                        'userId=', userId)
            response = PlayerControl.withdraw(userId)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()


    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/getInfo')
    def do_player_getInfo(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_getInfo', 
                        'userId=', userId)
            response = PlayerControl.getInfo(userId)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()
        
    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/getBindMobile')
    def do_player_getBindMobile(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_ex_getBindMobile', 
                        'userId=', userId)
            import poker.entity.dao.userdata as pkuserdata
            bindMobile = pkuserdata.getAttr(userId, 'bindMobile')
            response = PlayerControl.makeResponse()
            response.setResult('bindMobile', bindMobile)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/ex/getWalletInfo')
    def do_player_ex_getWalletInfo(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_ex_getWalletInfo', 
                        'userId=', userId)
            response = PlayerControl.getWalletInfo(userId)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/ex/getMasterInfo')
    def do_player_ex_getMasterInfo(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_ex_getMasterInfo', 
                        'userId=', userId)
            response = PlayerControl.getMasterInfo(userId)
            return response.pack()
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()


    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/test/reportEviewRound')
    def do_player_ex_reportEviewRound(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_ex_reportEviewRound', 
                        'userId=', userId)
            from dizhu.erdayimatch.erdayi3api import Report3rdInterface
            roomId = runhttp.getParamStr('roomId')
            matchId = runhttp.getParamStr('matchId')
            tableId = runhttp.getParamStr('tableId')
            seatId = runhttp.getParamStr('seatId')
            groupId = runhttp.getParamStr('groupId')
            score = runhttp.getParamStr('score')
            mpscore = runhttp.getParamStr('mpscore')
            mpRatio = runhttp.getParamStr('mpRatio')
            mpRatioRank = runhttp.getParamStr('mpRatioRank')
            mpRatioScore = runhttp.getParamStr('mpRatioScore')
            cardType = runhttp.getParamStr('cardType')
            cardHole = runhttp.getParamStr('cardHole')
            Report3rdInterface.reportEviewRound(int(roomId), matchId, userId, tableId, seatId, groupId,
                                               score, mpscore, mpRatio, mpRatioRank, mpRatioScore, cardType, cardHole)
            return {'status':'ok'}
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/test/reportRankFinish')
    def do_player_ex_reportRankFinish(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_ex_reportRankFinish', 
                        'userId=', userId)
            from dizhu.erdayimatch.erdayi3api import Report3rdInterface
            roomId = runhttp.getParamStr('roomId')
            matchId = runhttp.getParamStr('matchId')
            Report3rdInterface.reportRankFinish(roomId, matchId)
            return {'status':'ok'}
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()

    @markHttpMethod(httppath='/dizhu/v1/erdayi/player/test/matchReg')
    def do_player_ex_matchReg(self):
        try:
            userId, err = self.checkBaseParams()
            if err:
                return err.pack()
            ftlog.debug('do_player_ex_matchReg', 
                        'userId=', userId)
            from dizhu.erdayimatch.erdayi3api import Report3rdInterface
            roomId = runhttp.getParamStr('roomId')
            matchId = runhttp.getParamStr('matchId')
            Report3rdInterface.matchReg(roomId, matchId, userId, 'luwei')
            return {'status':'ok'}
        except:
            ftlog.error()
            return PlayerControl.makeResponse(userId, ErrorEnum.ERR_UNKNOWN).pack()
