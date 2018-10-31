# -*- coding:utf-8 -*-
'''
Created on 2016年7月9日

@author: luwei
'''
from freetime.entity.msg import MsgPack
from poker.protocol import router


class Alert(object):
    
    @classmethod
    def sendNormalAlert(cls, gameId, userId, title, message, confirmTodotask=None, confirmButtonTitle=None, itemCount=0,itemName='',itemDes='',itemUrl=''):
        '''
        前端小黄鸡弹窗提示，但是一个按钮
        '''
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'ddz:msg:alert')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('title', title)
        mo.setResult('message', message)
        mo.setResult('itemCount', itemCount)
        mo.setResult('itemName', itemName)
        mo.setResult('itemDes', itemDes)
        mo.setResult('itemUrl', itemUrl)

        if confirmButtonTitle:
            mo.setResult('buttonTitle', confirmButtonTitle)
 
        if confirmTodotask:
            mo.setResult('todotask', confirmTodotask)
 
        router.sendToUser(mo, userId)
        return mo

    @classmethod
    def sendNormalAlert2Button(cls, gameId, userId, title, message, confirmTodotask=None, confirmButtonTitle=None, 
                                                                    cancelTodotask=None, cancelButtonTitle=None):
        '''
        前端小黄鸡弹窗提示，显示两个按钮
        '''
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'ddz:msg:alert')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('title', title)
        mo.setResult('message', message)
        mo.setResult('buttonNum', 2)
        
        if confirmButtonTitle:
            mo.setResult('buttonTitle', confirmButtonTitle)

        if confirmTodotask:
            mo.setResult('todotask', confirmTodotask)

        if cancelButtonTitle:
            mo.setResult('cancelButtonTitle', cancelButtonTitle)

        if cancelTodotask:
            mo.setResult('cancelTodotask', cancelTodotask)

        router.sendToUser(mo, userId)
        return mo
