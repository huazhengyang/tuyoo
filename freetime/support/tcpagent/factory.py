# -*- coding: utf-8 -*-
from twisted.internet.protocol import ReconnectingClientFactory

class FTReconnectFactory(ReconnectingClientFactory, ):

    def __init__(self):
        pass

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        pass