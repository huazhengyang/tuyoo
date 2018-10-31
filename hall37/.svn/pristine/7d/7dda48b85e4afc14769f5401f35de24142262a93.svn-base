# -*- coding=utf-8 -*-
'''
Created on 2016年12月1日

@author: zhaol
'''

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from hall.entity.todotask import TodoTaskHelper, TodoTaskShowInfo
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import userdata
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from poker.util import strutil
from hall.entity import hall_simple_invite, hallitem, datachangenotify
from hall.entity.hall_simple_invite import Invitation 
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.configure import pokerconf
from poker.entity.biz.message import message as pkmessage

@markCmdActionHandler
class InviteTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(InviteTcpHandler, self).__init__()
    
    def _check_param_inviteCode(self, msg, key, params):
        value = msg.getParam('inviteCode')
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of inviteCode !' + str(value), None
    
    def _check_param_inviteeId(self, msg, key, params):
        value = msg.getParam('inviteeId')
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of inviteeId !' + str(value), None
    
    @classmethod
    def translateState(cls, status):
        if not status.inviter:
            return 0
        return 1
    
    @classmethod
    def makeErrorResponse(cls, cmd, action, errorCode, info):
        mo = MsgPack()
        mo.setCmd(cmd)
        mo.setResult('action', action)
        mo.setResult('code', errorCode)
        mo.setResult('info', info)
        mo.setResult('gameId', HALL_GAMEID)
        return mo
    
    @markCmdActionMethod(cmd='game', action='query_invite_config', clientIdVer=0)
    def doQuerySimpleInviteConfig(self, gameId, userId, clientId):
        '''
        获取简单邀请的奖励配置
        '''
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'query_invite_config')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        rewards = hall_simple_invite.getSimpleInviteRewardsConf(userId, gameId, clientId)
        mo.setResult('rewards', rewards)
        router.sendToUser(mo, userId)
    
    @markCmdActionMethod(cmd='game', action='query_invite_info', clientIdVer=0)
    def doQueryInviteInfo(self, gameId, userId, clientId):
        """
        查询邀请信息
        上行：
        {
            "cmd": "game",
            "params": {
                "action": "query_invite_info",
                "gameId": 9999,
                "userId": 10323,
                "clientId": "IOS_3.9001_weixin.weixinPay,alipay.0-hall710.yitiao.ioshrbmj"
            }
        }
        
        下行：
        {
            "cmd": "game",
            "result": {
                "action": "query_invite_info",
                "state": 1,
                "gameId": 9999,
                "bindUserId": 123456,
                "bindName": "123456",
                "bindPic": "",
                "rewardState": 0,
                "bindRewardCount": 12,
                "totalReward": 0,
                "inviteeList": [],
                "gotoInfo": {
                    "title": "\\u4f53\\u9a8c\\u6e38\\u620f\\u9001\\u623f\\u5361\\u5566",
                    "desc": "",
                    "url": "http://www.shediao.com/youle/gamelist.html"
                },
                "inviteShare": {
                    "title": "\\u53ef\\u4ee5\\u548c\\u4eb2\\u53cb\\u4e00\\u8d77\\u6e38\\u620f\\u7684\\u9ebb\\u5c06",
                    "desc": "\\u73a9\\u81ea\\u5efa\\u684c\\u672c\\u5730\\u9ebb\\u5c06\\uff0c\\u62a5\\u6211ID(10323)\\u5c31\\u9886\\u53d612\\u5f20\\u623f\\u5361",
                    "url": "http://www.shediao.com/youle/gamelist.html"
                }
            }
        }
        """
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'query_invite_info')
        status = hall_simple_invite.loadStatus(userId)
        #是否已填写了邀请人
        state = self.translateState(status)
        mo.setResult('state', state)
        mo.setResult('gameId', gameId)
        #绑定奖励数
        conf = hall_simple_invite.getSimpleInviteConf(userId, gameId, clientId)
        if not conf:
            ftlog.error('ClentId:', clientId, ' has no hall_simple_invite config, please check!!!')
            return
        
        if conf.inviteRewardItem:
            mo.setResult('bindRewardCount', conf.inviteRewardItem.count)
        
        userList, _ = self.getInviteesRewardInfo(status, Invitation.STATE_REWARDED, clientId)
        #总奖励数
        mo.setResult('totalReward', self.getTotalReward(status, userId, gameId, clientId))
        mo.setResult('inviteeList', userList)
        router.sendToUser(mo, userId)
            
    @markCmdActionMethod(cmd='game', action='bind_invite_code', clientIdVer=0)
    def doBindInviteCode(self, gameId, userId, clientId, inviteCode):
        """绑定上线推荐人ID"""
        try:
            hall_simple_invite.bindSimpleInviteRelationShip(inviteCode, userId)
            mo = MsgPack()
            mo.setCmd('invite_info')
            mo.setResult('action', 'bind_invite_code')
            mo.setResult('code', 0)
            mo.setResult('state', 1)
            mo.setResult('gameId', gameId)
            #绑定成功，获取推荐人信息
            name, pic = self.getUserNameAndPic(inviteCode)
            mo.setResult('bindName', name)
            mo.setResult('bindPic', pic)
            mo.setResult('bindUserId', inviteCode)
            # 校验自己的领奖状态
            inviteeStatus = hall_simple_invite.loadStatus(userId)
            mo.setResult('rewardState', inviteeStatus.getRewardState(userId, gameId, clientId))
            router.sendToUser(mo, userId)
            
        except Exception, e:
            if not isinstance(e, TYBizException) :
                ftlog.error()
            ec, info = (e.errorCode, e.message) if isinstance(e, TYBizException) else (-1, '系统错误')
            ftlog.info('invite.statics eventId=', 'INPUT_INVITE_CODE',
                       'userId=', userId,
                       'clientId=', clientId,
                       'inviteCode=', inviteCode,
                       'result=', 'failed',
                       'ec=', ec,
                       'info=', info)
            router.sendToUser(self.makeErrorResponse('invite_info', 'bind_invite_code', ec, info), userId)
            
    @markCmdActionMethod(cmd='game', action='get_invite_reward', clientIdVer=0)
    def doGetInviteReward(self, gameId, userId, inviteeId, clientId):
        """
        获取推荐人奖励
        作为上线奖励
        """
        if (not inviteeId) or (inviteeId <= 0):
            TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo('请输入推荐人ID', True))
            return
            
        try:
            status = hall_simple_invite.loadStatus(userId)
            inviteeInvitation = status.findInvitee(inviteeId)
            if not inviteeInvitation:
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo('没有推荐此人，请重新领取', True))
                return
                
            if inviteeInvitation.inviterState == Invitation.STATE_REWARDED:
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo('已经领取推荐奖励', True))
                return
            
            inviteeInvitation.inviterState = Invitation.STATE_REWARDED
            hall_simple_invite.saveStatus(status)
            ftlog.info('doGetInviteReward userId=', status.userId, 'invitee=', inviteeId)
            
            mo = MsgPack()
            mo.setCmd('invite_info')
            mo.setResult('action', 'get_invite_reward')
            mo.setResult('gameId', gameId)
            _, rCounts = self.getInviteesRewardInfo(status, Invitation.STATE_REWARDED, clientId)
            count = self.getTotalReward(status, userId, gameId, clientId)
            rObj = hall_simple_invite.getSimpleInviteRewardByIndex(userId, gameId, rCounts, clientId)
            if rObj:
                mo.setResult('totalReward', count)
                self.addUserItemByKindId(userId, gameId, clientId, rObj.assetKindId, rObj.count)
                
            userInfo = {}
            userInfo['userId'] = inviteeId
            userInfo['rewardState'] = inviteeInvitation.inviterState
            mo.setResult('updateInfo', userInfo)
            router.sendToUser(mo, userId)
            
            # 給userId补发一个系统消息
            inviteeName, _ = self.getUserNameAndPic(inviteeId)
            inviteRewardDesc = hall_simple_invite.getSimpleInviteRewardDescByIndex(userId, gameId, rCounts, clientId)
            if inviteRewardDesc:
                pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, inviteeName + '通过您的分享登录斗地主游戏，您获得' + inviteRewardDesc)
            
        except TYBizException, e:
            TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo(e.message, True))
    
    @classmethod
    def getUserNameAndPic(cls, userId):
        name, pic = userdata.getAttrs(userId, ['name', 'purl'])
        if not name or name == '':
            name = str(userId)
        if not pic:
            pic = ''
        return name, pic
    
    def getTotalReward(self, status, userId, gameId, clientId):
        count = 0
        index = 0
        for invitation in status.inviteeMap.values():
            if invitation.inviterState == Invitation.STATE_REWARDED:
                rObj = hall_simple_invite.getSimpleInviteRewardByIndex(userId, gameId, index, clientId)
                if not rObj:
                    continue
                
                count += rObj.count
                index += 1
                
        return count
            
    @classmethod
    def getInviteesRewardInfo(cls, status, state, clientId):
        userList = []
        count = 0
        for invitation in status.inviteeMap.values():
            if invitation.inviterState == state:
                count += 1
            userInfo = {}
            userId = invitation.userId
            userInfo['userId'] = userId
            name, pic = cls.getUserNameAndPic(userId)
            userInfo['name'] = name
            userInfo['pic'] = pic
            userInfo['rewardState'] = invitation.getInviterState(userId, clientId)
            userList.append(userInfo)  
        
        return userList, count
    
    @classmethod
    def addUserItemByKindId(cls, userId, gameId, clientId, kindId, count):
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        calcGameId = strutil.getGameIdFromHallClientId(clientId)
        userAssets.addAsset(calcGameId, kindId, count, timestamp, 'MAJIANG_FANGKA_INVITE_REWARD', pokerconf.clientIdToNumber(clientId))
        datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
        ftlog.debug('addUserItemByKindId userId:', userId, ' gameId:', gameId, 'kindId', kindId, 'count', count)
