# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''

class MsgHandler(object):
    def handleMsg(self, msg):
        handler = self.findMsgHandler(msg)
        if handler:
            ret = handler(msg)
            return True, ret
        return False, None
    
    def findMsgHandler(self, msg):
        cmd = msg.getCmd()
        action = msg.getAction()
        if action:
            handlerName = '_do_%s__%s' % (cmd, action)
        else:
            handlerName = '_do_%s' % (cmd)
        
        if hasattr(self, handlerName):
            return getattr(self, handlerName)
        
        handlerName = '_do_%s__' % (cmd)
        if hasattr(self, handlerName):
            return getattr(self, handlerName)
        
        return None
    

