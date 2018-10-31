# -*- coding=utf-8
'''
Created on 2016年4月7日

@author: zqh
'''
from stackless import bomb
import stackless

import freetime.util.log as ftlog
from freetime.core.channel import FTChannel

def receive(self):
    try:
        if hasattr(self, 'value'):
            v = self.value
            del self.value
            return v
        if hasattr(self, 'exc'):
            ntype, value = self.exc
            del self.exc
            raise ntype, value
        return stackless.channel.receive(self)
    except Exception, e:
        ftlog.error("Channel receive error")
        raise e
    
FTChannel.receive = receive
