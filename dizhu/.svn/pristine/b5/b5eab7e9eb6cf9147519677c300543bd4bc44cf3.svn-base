# -*- coding:utf-8 -*-

####################################################################################
#
# Copyright © 2017 TU. All Rights Reserved.
#
####################################################################################

"""

@File: led_util.py

@Description: Led类，支持富文本

@Author: leiyunfei(leiyunfei@tuyoogame.com)

@Depart: 棋牌中心-斗地主项目组

@Create: 2017-05-19 11:46:43

"""


import json

from freetime.util import log as ftlog

from hall.servers.util.rpc import user_remote

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.dao import daobase
from poker.util import strutil


class LedUtil(object):
    """
    LED工具类，支持富文本
    """
    # 富文本Led头
    RICH_TEXT_LED_MSG_HEADER = 'richTextLedMsg'

    @classmethod
    def makeRichTextBody(cls, contents):
        """
        组装富文本格式
        """
        return [{'color': color, 'text': txt} for color, txt in contents]

    @classmethod
    def sendLed(cls, fmtstr, scope=None, active=0):
        """
        发送Led消息到UT服
        param：gameId 插件Id
        param：scope LED显示级别
               详细参考http://192.168.10.93:8090/pages/viewpage.action?pageId=1281059
        param：fmtstr 格式化富文本串[['RRGGBB', 'text']]
        """
        richText = cls.makeRichTextBody(fmtstr)
        if ftlog.is_debug():
            ftlog.debug('sendLed rich text',
                        'text=', richText,
                        'dumptext=', json.dumps({'text': richText}),
                        caller=cls)
        if not scope:
            scope = 'hall%d' % DIZHU_GAMEID
        user_remote.sendHallLed(DIZHU_GAMEID, json.dumps({'text': richText}), ismgr=1, scope=scope, active=active)
        cls.saveLedText(richText)

    @classmethod
    def saveLedText(cls, text):
        """
        在地主插件中保存10条led数据 用于展示
        :param text:  要保存的led文本
        :return: 
        """
        jstr = strutil.dumps(text)
        daobase.executeDizhuCmd('lpush', 'dizhu:Led:6', jstr)
        daobase.executeDizhuCmd('ltrim', 'dizhu:Led:6', 0, 9) #max TEXT count is 10

        if ftlog.is_debug():
            ftlog.debug('LedUtil.saveLed text=', text, 'jstr=', jstr)

    @classmethod
    def getLedText(cls):
        jstr = daobase.executeDizhuCmd('lrange', 'dizhu:Led:6', 0, -1)
        return strutil.loads(jstr)
