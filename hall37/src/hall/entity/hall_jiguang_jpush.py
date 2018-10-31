# -*- coding=utf-8 -*-
from poker.entity.configure import configure
from poker.entity.events.tyevent import EventConfigure
from poker.util import webpage, strutil

import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.sdkclient import BAD_RESPONSE
import poker.entity.events.tyeventbus as pkeventbus


_inited = False
defaultServerUrl = 'http://101.200.37.54/push_to_user'
_serverUrl = None

#根据userId 推送外部消息
class JiGuangPush(object):
    '极光推送'
    @classmethod
    #Get方式
    def sendMessage(cls, userId, cloudId, content, title, androidPushType='getui'):
        params = {}
        params['userId'] = userId
        params['cloudId'] = cloudId
        params['content'] = content
        params['title'] = title
        params['androidPushType'] = androidPushType
        res = _sendHttpMessage(params, True)
        return res
        
def _sendHttpMessage(params, needresponse=True):
    if params:
        jsonstr, _ = webpage.webget(_serverUrl, postdata_=params, needresponse=needresponse)
        if ftlog.is_debug():
            ftlog.debug('JiGuangPush._sendHttpMessage',
                'url=', _serverUrl,
                'params=', params,
                'res=', jsonstr)
        if needresponse :
            try:
                data = strutil.loads(jsonstr)
                return data['code']
            except Exception, e:
                ftlog.error('JiGuangPush._sendHttpMessageError=', e.message)
                return BAD_RESPONSE
            return None

def _loadJiGuangPushCfg():
    global _serverUrl
    
    _serverUrl = configure.getGameJson(HALL_GAMEID, 'public', {}).get('http_jpush', defaultServerUrl)

def _intJiGuangPushCfg(event):
    if _inited and event.isChanged('game:9999:public:0'):
        _loadJiGuangPushCfg()

def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _loadJiGuangPushCfg()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _intJiGuangPushCfg)
    
    
    