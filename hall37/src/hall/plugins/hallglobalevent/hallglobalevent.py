# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

try:
    from freetime5.util import ftlog
    from tuyoo5.core import tygame
    from tuyoo5.core import typlugin
    from tuyoo5.plugins.globalevent.globalevent import TyPluginGlobalEvent
    
    
    class HallPluginGlobalEvent(TyPluginGlobalEvent):
    
        def __init__(self):
            super(HallPluginGlobalEvent, self).__init__()
    
        @typlugin.markPluginEntry(initBeforeConfig=['UT'])
        def initPluginBeforeUt(self):
            self.initPub()
            self.initSub()
    
        @typlugin.markPluginEntry(event=tygame.GlobalChargeEvent, srvType='UT')
        def onGlobalChargeEvent(self, event):
            ftlog.info('onGlobalChargeEvent->', event, event._encodeToJsonDict())

except:
    import freetime.util.log as ftlog
    ftlog.info('The freetime5 not patched GlobalChargeEvent !')
