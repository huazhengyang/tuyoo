# -*- coding:utf-8 -*-
'''
Created on 2018年6月6日

@author: zhaojiangang
'''
import urllib

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.util import strutil, webpage


def _sign(params):
    sk = sorted(params.keys())
    strs = ['%s=%s' % (k, str(params[k])) for k in sk]
    md5str = 'market.tuyoo.com-api-%s-market.tuyoo-api' % (''.join(strs))
    return strutil.md5digest(md5str)

def getUrl(api):
    domain = gdata.globalConfig().get('http_analy', 'analy.ywdier.com')
    return 'http://%s/?act=%s&' % (domain, api)
    
def requestAnalysis(api, params):
    url = getUrl(api)
    params['sign'] = _sign(params)
    querys = ['%s=%s' % (k, urllib.quote(str(v))) for k, v in params.iteritems()]
    url += '&'.join(querys)
    
    try:
        datas, url = webpage.webgetJson(url, timeout=6)
        if not datas:
            datas = {}
    except:
        datas, url = {'retcode':-1}, url
    
    if ftlog.is_debug():
        ftlog.debug('analysis_api.requestAnalysis',
                    'api=', api,
                    'url=', url,
                    'params=', params,
                    'datas=', datas)
    
    retcode = datas.get('retcode', -1)
    if retcode != 1:
        return retcode, None
    
    retmsg = datas.get('retmsg')
    return retcode, retmsg if retmsg != None else {}

