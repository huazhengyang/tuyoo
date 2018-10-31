# -*- coding: utf-8 -*-
'''
Created on 2017年09月18日

@author: zqh
请不要删除或随意修改此文件，此py文件作为停服前的关闭房间、检测功能而使用
'''
from poker.entity.dao import userdata
from hall.entity import hall_simple_invite
from freetime.util import log as ftlog

def ensureCanBeInviter(status, invitee):
    if not userdata.checkUserData(invitee):
        raise hall_simple_invite.BadInviterException('您的账号信息有误')
    
    if status.userId == invitee:
        raise hall_simple_invite.BadInviterException('不能推荐自己')
    
    if status.findInvitee(invitee):
        raise hall_simple_invite.BadInviterException('已推荐此用户')
    
    if status.inviteeCount + 1 > hall_simple_invite.MAX_INVITEE:
        ftlog.info('invite.addInvitee overCountLimit userId=', status.userId,
                   'invitee=', invitee,
                   'inviteeCount=', status.inviteeCount,
                   'MAX_INVITEE=', hall_simple_invite.MAX_INVITEE)
        raise hall_simple_invite.BadInviterException('推荐用户达到上限')
    
hall_simple_invite.ensureCanBeInviter = ensureCanBeInviter