# -*- coding:utf-8 -*-
'''
Created on 2017年12月6日

@author: zhaojiangang
'''
import urllib
import urlparse

from hall.entity import hall_share2, hall_short_url
from hall.entity.hall_share2 import ShareContent
from poker.util import strutil
import freetime.util.log as ftlog


def buildUrl(self, userId, parsedClientId, pointId, urlParams):
    urlParams = urlParams if urlParams is not None else {}
    if -1 != self.url.find('${mixDomain}'):
        urlParams['mixDomain'] = hall_share2.genMixDomain()

    url = strutil.replaceParams(self.url, urlParams)
    
    parsedUrl = urlparse.urlparse(url)
    qparams = urlparse.parse_qs(parsedUrl.query) if parsedUrl.query else {}
    qparams = {k:v[0] for k,v in qparams.iteritems()}
    qparams.update({'cid':parsedClientId.cid,
                    'mc':parsedClientId.mc, 'sc':parsedClientId.sc})
    url = urlparse.urlunparse((parsedUrl[0], parsedUrl[1], parsedUrl[2], parsedUrl[3], urllib.urlencode(qparams), parsedUrl[5]))
    ftlog.info('h_12_6_share2.buildUrl',
               'userId=', userId,
               'url=', url)
    return url


def longUrlToShort(longUrl):
    return longUrl


ShareContent.buildUrl = buildUrl
hall_short_url.longUrlToShort = longUrlToShort



