# -*- coding=utf-8 -*-
'''
Created on 2015年8月6日

@author: zqh
'''
from freetime.util import log as ftlog
from poker.util import strutil

OLD_FACES = set([
                'expression1.gif',
                'expression2.gif',
                'expression3.gif',
                'expression4.gif',
                'expression5.gif',
                'expression6.gif',
                'expression7.gif',
                'expression8.gif'
                ])

def _bugFixFilterChatMsgForPNG(clientId, chatMsg):
    # 新老版本使用的图片格式不一致
    try:
        _, clientVer, _ = strutil.parseClientId(clientId)
        if clientVer >= 2.6 and chatMsg.endswith('.gif'):
            chatMsg = chatMsg[0:-4] + '.png'
        elif clientVer < 2.6 and chatMsg.endswith('.png'):
            chatMsg = chatMsg[0:-4] + '.gif'
            if chatMsg not in OLD_FACES:
                chatMsg = ''
    except:
        ftlog.error()
    return chatMsg

def _bugFixFilterChatMsgForVer27(chatMsg):
    # fix斗地主2.7版本发表情时加了下划线的bug
    # 正常应该发expression1.gif，2.7版会发expression1_1.gif
    # 此处需要将expression1_1.gif转换为expression1.gif
    # 删除[_==>.)
    l = chatMsg.find('_')
    if l != -1:
        r = chatMsg.find('.', l + 1)
        if r != -1:
            chatMsg = chatMsg[0:l] + chatMsg[r:]
    return chatMsg


