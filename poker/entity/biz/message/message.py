# -*- coding: utf-8 -*-
"""
站内消息,类似邮箱功能,可以带附件
"""
from sre_compile import isstring
import freetime.util.log as ftlog
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import daobase
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import ModuleTipEvent
from poker.util import timestamp, strutil
MAX_SIZE = 50
MESSAGE_TYPE_PRIVATE = 1
MESSAGE_TYPE_SYSTEM = 2
MESSAGE_TYPES = {MESSAGE_TYPE_PRIVATE: 'msg.id.private', MESSAGE_TYPE_SYSTEM: 'msg.id.system'}
HALL_GAMEID = 9999
REDIS_KEY = 'message_{}:{}:{}'

class Attachment(object, ):
    """
    附件基类
    """
    TYPE_ID = 'unkown'
    ORDER_KEY = 99999

    def marshal(self):
        """
        对象序列化为字典
        @return: dict
        """
        pass

    def unmarshal(self, d):
        """
        字典反序列化为对象
        @param d:
        @return:
        """
        pass

class AttachmentAsset(Attachment, ):
    """
    附件:物品或者货币
    """
    TYPE_ID = 'asset'
    ORDER_KEY = 1

    def __init__(self, content_item_list=None, eventid=None, eventparam=None):
        """
        @param content_item_list: list<poker.entity.biz.content.TYContentItem>,可以是物品或者货币
        @param eventid: 起因,来历
        @param eventparam: eventid需要的参数
        """
        pass

    @property
    def itemlist(self):
        pass

    @property
    def eventid(self):
        pass

    @property
    def eventparam(self):
        pass

    def marshal(self):
        pass

    def unmarshal(self, d):
        pass

class AttachmentTodoTask(Attachment, ):
    """
    附件:跳转链接
    """
    TYPE_ID = 'todotask'
    ORDER_KEY = 2

    def __init__(self, todo_task, duration=0):
        """
        @param duration: 展示时间(分钟),<=0表示永久
        @param todo_task: hall.entity.TodoTask
        """
        pass

    def marshal(self):
        pass
MESSAGE_ATTACHMENT_CLASS = {AttachmentAsset.TYPE_ID: AttachmentAsset, AttachmentTodoTask.TYPE_ID: AttachmentTodoTask}

def send(gameid, typeid, touid, text, fromuid=None, attachment=None):
    """
    发送消息给指定用户
    @param gameid: 哪个游戏发的
    @param typeid: 类型, L{message.MESSAGE_TYPES}
    @param touid: 接收用户id
    @param text: 消息文本
    @param fromuid: 发送用户id, 默认系统
    @param attachment: 消息附件, 默认没有
    @return:
    """
    pass

def _msg_order(msg):
    pass

def get(userid, typeid):
    """
    获取消息列表
    @param userid:
    @param typeid: 类型, L{message.MESSAGE_TYPES}
    @return:
    """
    pass

def _msg_load_and_expire(userid, rediskey):
    pass

def get_unread_count(userid, typeid):
    """
    取得当前用户的未读站内消息的个数
    """
    pass

def attachment_receive(userid, typeid, msgid, itemsystem):
    """
    收取附件的物品或者货币
    @param itemsystem: poker.entity.biz.item.TYItemSystem
    @param typeid: 类型, L{message.MESSAGE_TYPES}
    @param userid:
    @param msgid: 消息id
    @return:
    """
    pass

def convertOldData(gameId, userId):
    """
    大厅v3.9存储改动,user数据库:
    键message:g(gameid)u(userid),废弃
    键msg:(gameId):(toUid),废弃
    """
    pass

def sendPrivate(gameId, toUid, fromUid, msg, button=None):
    """
    已废弃,留着只为了兼容以前代码
    发送站内消息到用户
    """
    pass

def sendPublic(gameId, toUid, fromUid, msg, button=None):
    """
    已废弃,留着只为了兼容以前代码
    发送站内消息到用户
    """
    pass

def getPrivate(gameId, userId, pageNo=1):
    """
    已废弃,留着只为了兼容以前代码
    取得当前用户的未读私信的内容
    """
    pass

def getPrivateUnReadCount(gameId, userId):
    """
    已废弃,留着只为了兼容以前代码
    取得当前用户的未读站内消息的个数
    """
    pass

def sendGlobal(gameId, msg, button=None):
    """
    已废弃,待删除
    发送站内消息到全体游戏用户
    """
    pass

def getGlobalUnReadCount(gameId, userId):
    """
    已废弃,待删除
    取得当前用户的未读站内消息的个数
    """
    pass

def getGlobal(gameId, userId, pageNo=1):
    """
    已废弃,待删除
    取得当前用户的全局未读私信的内容
    """
    pass