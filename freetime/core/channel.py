# -*- coding: utf-8 -*-
from stackless import bomb
import stackless
import freetime.util.log as ftlog

class FTChannel(stackless.channel, ):

    def send_nowait(self, v):
        pass

    def send_exception_nowait(self, ntype, value):
        pass

    def receive(self):
        pass