# -*- coding:utf-8 -*-
'''
Created on 2015年12月10日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import neituiguang, neituiguangtask, hallitem, hallshare
from hall.entity.neituiguang import NeituiguangException, Invitation
from hall.entity.todotask import TodoTaskHelper, TodoTaskGoldRain, \
    TodoTaskShowInfo, TodoTaskBindPhone
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.rpc import neituiguang_remote
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.dao import userdata
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import datachangenotify


@markCmdActionHandler
class NeiTuiGuangTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(NeiTuiGuangTcpHandler, self).__init__()
        
    def _check_param_taskId(self, msg, key, params):
        value = msg.getParam('taskId')
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of taskId !' + str(value), None
    
    def _check_param_promoteCode(self, msg, key, params):
        value = msg.getParam('promoteCode')
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of promoteCode !' + str(value), None
    
    @classmethod
    def translateState(cls, status):
        if status.isNewUser:
            # 新用户还没填写推荐码
            if not status.inviter:
                return 0
            # 已经填写或者放弃填写
            return 1
        # 老用户
        return 2
        
    @classmethod
    def makeErrorResponse(cls, action, errorCode, info):
        mo = MsgPack()
        mo.setCmd('promote_info')
        mo.setResult('action', action)
        mo.setResult('code', errorCode)
        mo.setResult('info', info)
        return mo
        
    @classmethod
    def encodeTask(cls, task):
        state = 0
        if task.isFinished:
            state = 2 if task.gotReward else 1
        return {
            'id':task.kindId,
            'desc':task.taskKind.desc,
            'reward':task.taskKind.rewardContent.desc if task.taskKind.rewardContent else '',
            'iconUrl':task.taskKind.pic,
            'state':state
        }
    
    @markCmdActionMethod(cmd='promote_info', action='query_state', clientIdVer=0)
    def doQueryState(self, gameId, userId, clientId):
        '''
        内推广状态查询
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        mo = MsgPack()
        mo.setCmd('promote_info')
        mo.setResult('action', 'query_state')
        status = neituiguang.loadStatus(userId, timestamp)
        mo.setResult('state', self.translateState(status))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='promote_info', action='list_invitee', clientIdVer=0)
    def doListInvitee(self, gameId, userId, clientId):
        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(userId, timestamp)
        invitee = status.encodeInvitee()
        
        mo = MsgPack()
        mo.setCmd('promote_info')
        mo.setResult('action', 'list_invitee')
        mo.setResult('invitee', invitee)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='promote_info', action='code_check', clientIdVer=0)
    def doCheckCode(self, gameId, userId, clientId, promoteCode):
        '''
        确立推广关系，也就是领取红包
        校验通过
        设置推荐人
        将用户加到推荐人的推广员名单里
        '''
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            status = neituiguang.loadStatus(userId, timestamp)

            # 检查是否能成为推荐人
            # 转到promoteCode所在的UT进程中去处理
            ec, info = neituiguang_remote.canBeInviter(promoteCode, userId)
            if ec != 0:
                raise NeituiguangException(ec, info)
            
            # 设置推荐人
            neituiguang.setInviter(status, promoteCode)
            
            try:
                # 添加invitee，此处不需要处理失败的情况，前面已经检查了
                ec, info = neituiguang_remote.addInvitee(promoteCode, userId, status.isBindMobile)
                if ec != 0:
                    ftlog.warn('NeiTuiGuangTcpHandler.doCheckCode gameId=', gameId,
                               'userId=', userId,
                               'clientId=', clientId,
                               'promoteCode=', promoteCode,
                               'call=', 'neituiguang_remote.addInvitee',
                               'ec=', ec,
                               'info=', info)
            except:
                ftlog.error('NeiTuiGuangTcpHandler.doCheckCode gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'promoteCode=', promoteCode,
                            'call=', 'neituiguang_remote.addInvitee',
                            'ec=', ec,
                            'info=', info)
            
            ftlog.hinfo('neituiguang.statics eventId=', 'INPUT_PRMOTE_CODE',
                       'userId=', userId,
                       'clientId=', clientId,
                       'promoteCode=', promoteCode,
                       'result=', 'ok')
            mo = MsgPack()
            mo.setCmd('promote_info')
            mo.setResult('action', 'code_check')
            mo.setResult('code', 0)
            router.sendToUser(mo, userId)
        except Exception, e:
            if not isinstance(e, TYBizException) :
                ftlog.error()
            ec, info = (e.errorCode, e.message) if isinstance(e, TYBizException) else (-1, '系统错误')
            ftlog.hinfo('neituiguang.statics eventId=', 'INPUT_PRMOTE_CODE',
                       'userId=', userId,
                       'clientId=', clientId,
                       'promoteCode=', promoteCode,
                       'result=', 'failed',
                       'ec=', ec,
                       'info=', info)
            router.sendToUser(self.makeErrorResponse('code_check', ec, info), userId)
        
    @markCmdActionMethod(cmd='promote_info', action='cancel_code_check', clientIdVer=0)
    def doCancelCodeCheck(self, gameId, userId, clientId):
        '''
        取消code_check
        '''
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            status = neituiguang.loadStatus(userId, timestamp)
            neituiguang.setInviter(status, 0)
            ftlog.hinfo('neituiguang.statics eventId=', 'CANCEL_INPUT_PRMOTE_CODE',
                       'userId=', userId,
                       'clientId=', clientId,
                       'result=', 'ok')
            mo = MsgPack()
            mo.setCmd('promote_info')
            mo.setResult('action', 'cancel_code_check')
            mo.setResult('code', 0)
            router.sendToUser(mo, userId)
        except Exception, e:
            if not isinstance(e, TYBizException) :
                ftlog.error()
            ec, info = (e.errorCode, e.message) if isinstance(e, TYBizException) else (-1, '系统错误')
            ftlog.hinfo('neituiguang.statics eventId=', 'CANCEL_INPUT_PRMOTE_CODE',
                       'userId=', userId,
                       'clientId=', clientId,
                       'result=', 'failed')
            router.sendToUser(self.makeErrorResponse('cancel_code_check', ec, info), userId)
            
    @classmethod
    def calcTaskExpires(cls, userId):
        '''
        结算新手任务是否过期
        '''
        createTimeStr = userdata.getAttr(userId, 'createTime')
        createTime = pktimestamp.timestrToTimestamp(createTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        return pktimestamp.getDayStartTimestamp(createTime) + neituiguang.NEW_USER_DAYS * 86400
        
    @classmethod
    def buildTaskInfoResponse(cls, userId):
        '''
        获取红包任务/新手任务应答
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        taskModel = neituiguangtask.newUserTaskSystem.loadTaskModel(userId, timestamp)
        tasks = [cls.encodeTask(task) for task in taskModel.userTaskUnit.taskList]
        tasks.sort(key=lambda t:t['id'])
        conf = neituiguang.getConf()
        mo = MsgPack()
        mo.setCmd('promote_info')
        mo.setResult('action', 'query_task_info')
        mo.setResult('tasks', tasks)
        mo.setResult('finalTimestamp', cls.calcTaskExpires(userId))
        mo.setResult('detail', conf.taskDetail)
        return mo
    
    @markCmdActionMethod(cmd='promote_info', action='query_task_info', clientIdVer=0)
    def doQueryTaskInfo(self, gameId, userId):
        '''
        查询红包活动详情
        '''
        router.sendToUser(self.buildTaskInfoResponse(userId), userId)
        
    @markCmdActionMethod(cmd='promote_info', action='get_task_reward', clientIdVer=0)
    def doGetTaskReward(self, gameId, userId, taskId):
        '''
        获取活动奖励
        '''
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = neituiguangtask.newUserTaskSystem.loadTaskModel(userId, timestamp)
            task = taskModel.userTaskUnit.findTask(taskId)
            if not task:
                raise TYBizException(-1, '未知的任务:%s' % (taskId))
            expiresTime = self.calcTaskExpires(userId)
            if timestamp >= expiresTime:
                raise TYBizException(-1, '任务已经过期')
            if not userdata.getAttr(userId, 'bindMobile'):
                conf = neituiguang.getConf()
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskBindPhone(conf.pleaseBindPhone, ''))
                return
            assetList = neituiguangtask.newUserTaskSystem.getTaskReward(task, timestamp, 'PROMOTE_TASK', taskId)
            router.sendToUser(self.buildTaskInfoResponse(userId), userId)
            
            rewardStr = TYAssetUtils.buildContentsString(assetList)
            mo = MsgPack()
            mo.setCmd('promote_info')
            mo.setResult('action', 'get_task_reward')
            mo.setResult('code', 0)
            mo.setResult('info', '恭喜您获得了%s' % rewardStr)
            router.sendToUser(mo, userId)
        except TYBizException, e:
            router.sendToUser(self.makeErrorResponse('get_task_reward', e.errorCode, e.message), userId)
            
    @classmethod
    def calcTotalInvitationByState(cls, status, state):
        count = 0
        for invitation in status.inviteeMap.values():
            if invitation.state == state:
                count += 1
        return count
                
    @classmethod
    def buildQueryPrizeResponse(cls, gameId, userId, clientId):
        timestamp = pktimestamp.getCurrentTimestamp()
        conf = neituiguang.getConf()
        status = neituiguang.loadStatus(userId, timestamp)
        totalRewardCount = cls.calcTotalInvitationByState(status, Invitation.STATE_REWARD)
        availableRewardCount = cls.calcTotalInvitationByState(status, Invitation.STATE_ACCEPT)
        mo = MsgPack()
        mo.setCmd('promote_info')
        mo.setResult('action', 'query_prize')
        mo.setResult('detail', conf.prizeDetail)
        mo.setResult('imgUrl', conf.prizeImgUrl)
        mo.setResult('promoteCode', userId)
        
        shareId = hallshare.getShareId('neituiguang2', userId, gameId)
        share = hallshare.findShare(shareId)
        if share:
            mo.setResult('shareId', shareId)
            mo.setResult('shareLoc', conf.shareLoc)
            mo.setResult('weixinInviteDoc', share.getDesc(HALL_GAMEID, userId))
            mo.setResult('weixinInviteUrl', share.getUrl(HALL_GAMEID, userId))
            mo.setResult('smsInviteDoc', share.getSmsDesc(HALL_GAMEID, userId))
            
        totalRewardContent = ''
        if conf.prizeRewardItem:
            totalRewardContent = hallitem.buildContent(conf.prizeRewardItem.assetKindId, conf.prizeRewardItem.count * totalRewardCount)
        prizeGetedInfo = conf.prizeGotTotalRewardDesc if conf.prizeRewardItem and totalRewardCount else conf.prizeNotGotRewardDesc
        prizeGetedInfo = strutil.replaceParams(prizeGetedInfo, {'totalRewardContent':totalRewardContent})
        mo.setResult('prizeGetedInfo', prizeGetedInfo)
        
        availableRewardContent = ''
        if conf.prizeRewardItem:
            availableRewardContent = hallitem.buildContent(conf.prizeRewardItem.assetKindId, conf.prizeRewardItem.count * availableRewardCount)
        prizeAvailableInfo = conf.prizeAvailableRewardDesc if conf.prizeRewardItem else conf.prizeAvailableRewardDesc
        prizeAvailableInfo = strutil.replaceParams(prizeAvailableInfo, {'availableRewardContent':availableRewardContent})
        mo.setResult('prizeAvailableInfo', prizeAvailableInfo)
        
        prizeList = []
        invitationList = sorted(status.inviteeMap.values(), key=lambda i:i.index)
        for invitation in invitationList:
            prizeList.append(cls.encodeInvitation(invitation))
        mo.setResult('prizeList', prizeList)
        mo.setResult('state', 1 if availableRewardCount > 0 else 0)
        return mo
    
    @markCmdActionMethod(cmd='promote_info', action='query_prize', clientIdVer=0)
    def doQueryPrize(self, gameId, userId, clientId):
        '''
        查询奖励
        '''
        try:
            mo = self.buildQueryPrizeResponse(gameId, userId, clientId)
            router.sendToUser(mo, userId)
        except TYBizException, e:
            router.sendToUser(self.makeErrorResponse('query_prize', e.errorCode, e.message), userId)
    
    @classmethod
    def encodeInvitation(cls, invitation):
        name = userdata.getAttr(invitation.userId, 'name')
        state = 0
        if invitation.state == Invitation.STATE_ACCEPT:
            state = 1
        elif invitation.state == Invitation.STATE_REWARD:
            state = 2
        return {'userId':invitation.userId, 'name':name, 'state':state}
    
    @markCmdActionMethod(cmd='promote_info', action='get_prize', clientIdVer=0)
    def doGetPrize(self, gameId, userId, clientId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            status = neituiguang.loadStatus(userId, timestamp)
            if not status.isBindMobile:
                conf = neituiguang.getConf()
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskBindPhone(conf.pleaseBindPhone, ''))
                return
            count, assetList = neituiguang.getAllReward(status)
            if count > 0:
                conf = neituiguang.getConf()
                prizeRewardTips = strutil.replaceParams(conf.prizeRewardTips,
                                                        {'rewardContent':TYAssetUtils.buildContentsString(assetList)})
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskGoldRain(prizeRewardTips))
                
                mo = self.buildQueryPrizeResponse(gameId, userId, clientId)
                router.sendToUser(mo, userId)
            else:
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo('奖励已经领取', True))
            datachangenotify.sendDataChangeNotify(gameId, userId, ['free', 'promotion_loc'])
        except TYBizException, e:
            TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo(e.message, True))
