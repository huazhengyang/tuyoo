# -*- coding:utf-8 -*-
'''
Created on 2017年12月22日

@author: zhaojiangang
'''
from datetime import datetime

from freetime.entity.msg import MsgPack
from hall.entity import hall_red_packet_task
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import userdata
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
import freetime.util.log as ftlog


@markCmdActionHandler  
class RedPacketTaskTcpHandler(BaseMsgPackChecker):
    def _check_param_taskId(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of taskId !' + str(value), None
    
    @classmethod
    def calcTaskState(cls, task):
        if task.finishCount > 0:
            return 2 if task.gotReward else 1
        return 0
    
    @classmethod
    def encodeReward(cls, task):
        if task.taskKind.rewardContent:
            items = task.taskKind.rewardContent.getItems()
            if items:
                return {'itemId':items[0].assetKindId, 'count':items[0].count}
        return None
    
    @classmethod
    def encodeTask(cls, userId, clientId, status):
        task = status.task
        state = cls.calcTaskState(task)
        ret = {
            'kindId':task.kindId,
            'state':state,
            'prog':task.progress,
            'total':task.taskKind.count,
            'desc':task.taskKind.desc,
            'reward':cls.encodeReward(task)
        }
        ret['isFirst'] = 1 if status.isFirst else 0
        if task.taskKind.todotaskFac and state == 0:
            todotask = task.taskKind.todotaskFac.newTodoTask(HALL_GAMEID, userId, clientId)
            if todotask:
                ret['todotask'] = todotask.toDict()
        return ret

    @classmethod
    def encodeActs(cls, userId, clientId, acts):
        ret = []
        for act in acts:
            d = {'pic':act.pic}
            if act.todotaskFac:
                todotask = act.todotaskFac.newTodoTask(HALL_GAMEID, userId, clientId)
                if todotask:
                    d['todotask'] = todotask.toDict()
            ret.append(d)
        return ret

    @classmethod
    def _doUpdate(cls, userId, clientId, timestamp):
        mo = MsgPack()
        mo.setCmd('hall_rp_task')
        mo.setResult('action', 'update')
        mo.setResult('userId', userId)
        status = hall_red_packet_task.loadUserStatus(userId)
        curTime = timestamp
        expiresTime = curTime
        createTimeStr = None
        try:
            createTimeStr = userdata.getAttr(userId, 'createTime')
            createDT = datetime.strptime(createTimeStr, '%Y-%m-%d %H:%M:%S.%f')
            createTime = pktimestamp.datetime2Timestamp(createDT)
            expiresTime = pktimestamp.getDayStartTimestamp(createTime) + 86400 * 8
        except:
            ftlog.error('RedPacketTaskTcpHandler._doUpdate BadCreateTime',
                        'userId=', userId,
                        'createTime=', createTimeStr)
        
        mo.setResult('curTime', curTime)
        mo.setResult('expiresTime', expiresTime)
        if status.finished or not status.task:
            acts = hall_red_packet_task.getActs()
            mo.setResult('acts', cls.encodeActs(userId, clientId, acts))
        else:
            mo.setResult('task', cls.encodeTask(userId, clientId, status))

        mo.setResult('helpUrl', hall_red_packet_task.getHelpUrl(userId, clientId))
        mo.setResult('tips', hall_red_packet_task.getTaskTips(userId, clientId))
        mo.setResult('boardTip', hall_red_packet_task.getBoardTip(userId, clientId))
        return mo
    
    @markCmdActionMethod(cmd='hall_rp_task', action='update', clientIdVer=0)
    def doUpdate(self, userId, clientId):
        mo = self._doUpdate(userId, clientId, pktimestamp.getCurrentTimestamp())
        if mo:
            router.sendToUser(mo, userId)
    
    @classmethod
    def _doGainReward(cls, userId, clientId, timestamp):
        mo = MsgPack()
        mo.setCmd('hall_rp_task')
        mo.setResult('action', 'gain_reward')
        mo.setResult('userId', userId)
        try:
            assetList = hall_red_packet_task.gainReward(userId, timestamp)
            if assetList:
                mo.setResult('reward', {'itemId':assetList[0][0].kindId, 'count':assetList[0][1]})
        except TYBizException, e:
            mo.setResult('ec', e.errorCode)
            mo.setResult('info', e.message)
        return mo
    
    @markCmdActionMethod(cmd='hall_rp_task', action='gain_reward', clientIdVer=0)
    def doGainReward(self, userId, clientId):
        timestamp = pktimestamp.getCurrentTimestamp()
        mo = self._doGainReward(userId, clientId, timestamp)
        if mo:
            router.sendToUser(mo, userId)
            mo = self._doUpdate(userId, clientId, timestamp)
            if mo:
                router.sendToUser(mo, userId)
        

    