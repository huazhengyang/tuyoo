# -*- coding: utf-8 -*-
"""
@file protocol.py

@mainpage

txRedis is an asynchronous, Twisted, version of redis.py (included in the
redis server source).

The official Redis Command Reference:
http://code.google.com/p/redis/wiki/CommandReference

@section An example demonstrating how to use the client in your code:
@code
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import defer

from txredis.protocol import Redis

@defer.inlineCallbacks
def main():
    clientCreator = protocol.ClientCreator(reactor, Redis)
    redis = yield clientCreator.connectTCP(HOST, PORT)

    res = yield redis.ping()
    print res

    res = yield redis.set('test', 42)
    print res

    test = yield redis.get('test')
    print res

@endcode

Redis google code project: http://code.google.com/p/redis/
Command doc strings taken from the CommandReference wiki page.

"""
from collections import deque
import string
from twisted.internet import defer, protocol
from twisted.protocols import policies
from freetime.util.txredis import exceptions
_NUM_FIRST_CHARS = frozenset((string.digits + '+-.'))

class RedisBase(protocol.Protocol, policies.TimeoutMixin, object, ):
    """

    """
    ERROR = '-'
    SINGLE_LINE = '+'
    INTEGER = ':'
    BULK = '$'
    MULTI_BULK = '*'

    def __init__(self, db=None, password=None, charset='utf8', errors='strict'):
        pass

    def dataReceived(self, data):
        """

        Spec: http://redis.io/topics/protocol
        """
        pass

    def failRequests(self, reason):
        pass

    def connectionMade(self):
        """

        """
        pass

    def connectionLost(self, reason):
        """

        Will fail all pending requests.

        """
        pass

    def timeoutConnection(self):
        """

        Will fail all pending requests with a TimeoutError.

        """
        pass

    def errorReceived(self, data):
        """

        """
        pass

    def singleLineReceived(self, data):
        """

        """
        pass

    def handleMultiBulkElement(self, element):
        pass

    def integerReceived(self, data):
        """

        """
        pass

    def bulkDataReceived(self, data):
        """

        """
        pass

    def tryConvertData(self, data):
        pass

    def multiBulkDataReceived(self):
        """

        The bulks making up this response have been collected in
        the last entry in self._multi_bulk_stack.

        """
        pass

    def handleCompleteMultiBulkData(self, reply):
        pass

    def responseReceived(self, reply):
        """

        If we're waiting for multibulk elements, store this reply. Otherwise
        provide the reply to the waiting request.

        """
        pass

    def getResponse(self):
        """
        @retval a deferred which will fire with response from server.
        """
        pass

    def _encode(self, s):
        """

        """
        pass

    def _send(self, *args):
        """

        Uses the 'unified request protocol' (aka multi-bulk)

        """
        pass

    def send(self, command, *args):
        pass

class HiRedisBase(RedisBase, ):
    """
    parsing.
    """

    def dataReceived(self, data):
        """

        """
        pass