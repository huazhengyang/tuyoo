# -*- coding=utf-8 -*-
"""
@file  : message_remote
@date  : 2016-07-08
@author: GongXiaobo
"""

from hall.entity import hallpopwnd
from poker.entity.biz.message import message
from poker.entity.biz.message.message import AttachmentAsset, AttachmentTodoTask
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def send(gameid, typeid, userId, text, fromuid=None):
    message.send(gameid, typeid, userId, text, fromuid)
    # print "message_remote,send:", message.get(userId, typeid)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def send_asset(gameid, typeid, userId, text, d, fromuid=None):
    attach = AttachmentAsset()
    attach.unmarshal(d)
    message.send(gameid, typeid, userId, text, fromuid, attach)
    # msgid = message.send(gameid, typeid, userId, text, fromuid, attach)
    # print "message_remote,send_asset:1:", message.get(userId, typeid)
    #
    # def _receive_test():
    #     from hall.entity import hallitem
    #     message.attachment_reveive(userId, typeid, msgid, hallitem.itemSystem)
    #     print "message_remote,send_asset:2:", message.get(userId, typeid)
    # from freetime.core.timer import FTTimer
    # FTTimer(10, _receive_test)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def send_todotask(gameid, typeid, clientid, userId, text, d, duration=0, fromuid=None, **todotask_kwarg):
    todo_task = hallpopwnd.decodeTodotaskFactoryByDict(d).newTodoTask(gameid, userId, clientid, **todotask_kwarg)
    attach = AttachmentTodoTask(todo_task, duration)
    message.send(gameid, typeid, userId, text, fromuid, attach)
    # print "message_remote,send_todotask:", message.get(userId, typeid)
