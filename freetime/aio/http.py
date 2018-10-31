# -*- coding: utf-8 -*-
import OpenSSL
from StringIO import StringIO
import stackless
from time import time
from twisted.internet import reactor
from twisted.web.client import Agent, readBody, FileBodyProducer
from twisted.web.http_headers import Headers
from freetime.util import defertool
from freetime.util.encodeobj import decodeObjUtf8
import freetime.util.log as ftlog
from twisted.web.client import WebClientContextFactory

class _WebClientContextFactory(WebClientContextFactory, ):

    def __init__(self, cfile, kfile):
        """
        :param cfile: PEM 编码的证书文件内容或路径
        :param kfile: PEM 编码的私钥文件内容或路径
        """
        pass

    def getContext(self, hostname, port):
        pass

def runHttp(method, url, header, body, connect_timeout, timeout, httpsCertInfo=None, retrydata=None):
    """
    Run http request by twisted.web.client.Agent
    instead of client.getPage.
    httpsCertInfo 为https协议时使用的证书控制，
        若httpsCertInfo为dict,则使用定制的WebClientContextFactory进行构造Agent对象
        httpsCertInfo 中可以包含： certificate https使用的证书文件的全路径
                                privatekey https使用的私有KEY文件的全路径
    """
    pass

def runHttpNoResponse(method, targetUrl, header, body, base_timeout, retrydata=None, httpsCertInfo=None):
    """
    Run http request by twisted.web.client.Agent
    instead of client.getPage.
    but we dont wait the response
    httpsCertInfo 为https协议时使用的证书控制，
        若httpsCertInfo为dict,则使用定制的WebClientContextFactory进行构造Agent对象
        httpsCertInfo 中可以包含： certificate https使用的证书文件的全路径
                                privatekey https使用的私有KEY文件的全路径
    """
    pass