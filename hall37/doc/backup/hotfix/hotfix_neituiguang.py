# -*- coding:utf-8 -*-
'''
Created on 2016年3月3日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import neituiguang
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.neituiguang import NeituiguangAddInviteeEvent
from hall.game import TGHall
from poker.entity.dao import userdata
import poker.util.timestamp as pktimestamp


def _adjustStatus(status):
    try:
        bindMobile, createTimeStr = userdata.getAttrs(status.userId, ['bindMobile', 'createTime'])
        status._isBindMobile = True if bindMobile else False
        status._registerTime = pktimestamp.timestrToTimestamp(createTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        if status.inviteeMap:
            sl = sorted(status.inviteeMap.values(), key=lambda invitee:invitee.index)
            removeList = sl[neituiguang.MAX_INVITEE:]
            for invitee in removeList:
                del status.inviteeMap[invitee.userId]
    except:
        ftlog.error('neituiguang._adjustStatus userId=', status.userId)
    return status

def _addInvitee(status, invitee, accepted):
    '''
    给userId的推荐列表增加inviteeUserId
    @param userId: 给哪个用户增加
    @param inviteeUserId: 被推荐人
    @return: status
    '''
    # 确认可以成为推荐人
    neituiguang.ensureCanBeInviter(status, invitee)
    if status.inviteeCount + 1 > neituiguang.MAX_INVITEE:
        ftlog.info('neituiguang.addInvitee overCountLimit userId=', status.userId,
                   'invitee=', invitee,
                   'inviteeCount=', status.inviteeCount,
                   'MAX_INVITEE=', neituiguang.MAX_INVITEE)
        return
    # 添加被推荐人
    status._addInvitee(invitee, accepted)
    neituiguang._saveStatus(status)
    ftlog.info('neituiguang.addInvitee userId=', status.userId,
               'invitee=', invitee,
               'accepted=', accepted)
    TGHall.getEventBus().publishEvent(NeituiguangAddInviteeEvent(HALL_GAMEID, status.userId, invitee))

neituiguang.addInvitee = _addInvitee
neituiguang._adjustStatus = _adjustStatus

