# -*- coding=utf-8
'''
Created on 2015年10月27日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import MatchPlayerSigninEvent, \
    MatchPlayerOverEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil, webpage
import poker.util.timestamp as pktimestamp


def signin(action, params):
    gkey = params.get('gkey')
    key = strutil.md5digest('%s%s' % (gkey, action))
    sstr = '%s%s%s%s%s#%s' % (params.get('uid'),
                              gkey,
                              params.get('skey'),
                              params.get('time'),
                              params.get('matchid'),
                              key)
    return strutil.md5digest(sstr)
    
def getParamsByPlayer(player, timestamp):
    try:
        m360kpParams = player.getSigninParam('m360kp')
        if not m360kpParams:
            return None
        
        gkey = m360kpParams.get('gkey')
        if not gkey or not isstring(gkey):
            return None
        
        snsId = player.snsId
        if not snsId or not snsId.startswith('360:'):
            return None
        
        return {
            'time':timestamp,
            'gkey':gkey,
            'uid':snsId[4:],
            'matchid':player.matchId,
            'skey':1
        }
    except:
        ftlog.error('match360kp.getParamsByPlayer userId=', player.userId,
                    'signinParams=', player.signinParams,
                    'snsId=', player.snsId)
        return None
    
def _onPlayerSignin(event):
    conf = hallconf.getPublicConf('match_360kp', None)
    if not conf or not isinstance(conf, dict):
        if ftlog.is_debug():
            ftlog.debug('match360kp.onPlayerSignin NoConf userId=', event.userId,
                        'matchId=', event.matchId,
                        'signinParams=', event.player.signinParams,
                        'snsId=', event.player.snsId,
                        'conf=', conf)
        return
    
    callbackUrl = conf.get('signinCallbackUrl')
    if not callbackUrl:
        if ftlog.is_debug():
            ftlog.debug('match360kp.onPlayerSignin NoCallbackUrl userId=', event.userId,
                        'matchId=', event.matchId,
                        'signinParams=', event.player.signinParams,
                        'snsId=', event.player.snsId,
                        'conf=', conf)
        return
    
    timestamp = pktimestamp.getCurrentTimestamp()
    params = getParamsByPlayer(event.player, timestamp)
    if not params:
        if ftlog.is_debug():
            ftlog.debug('match360kp.onPlayerSignin NoParams userId=', event.userId,
                        'matchId=', event.matchId,
                        'signinParams=', event.player.signinParams,
                        'snsId=', event.player.snsId,
                        'conf=', conf)
        return
    
    sign = signin('REGIST', params)
    params['sign'] = sign
    
    result = webpage.webgetJson(callbackUrl, datas=params, appKey=None, timeout=conf.get('timeout', 3))
    if ftlog.is_debug():
        ftlog.debug('match360kp.onPlayerSignin userId=', event.userId,
                    'matchId=', event.matchId,
                    'signinParams=', event.player.signinParams,
                    'snsId=', event.player.snsId,
                    'conf=', conf,
                    'result=', result)
            
    if 'errno' in result:
        ftlog.warn('match360kp.onPlayerSignin userId=', event.userId,
                   'matchId=', event.matchId,
                   'signinParams=', event.player.signinParams,
                   'snsId=', event.player.snsId,
                   'conf=', conf,
                   'result=', result)
                
def _onPlayerSignout(event):
    if ftlog.is_debug():
        ftlog.debug('match360kp.onPlayerSignout NoConf userId=', event.userId,
                    'matchId=', event.matchId,
                    'signinParams=', event.player.signinParams,
                    'snsId=', event.player.snsId)

def _onPlayerOver(event):
    conf = hallconf.getPublicConf('match_360kp', None)
    if not conf or not isinstance(conf, dict):
        if ftlog.is_debug():
            ftlog.debug('match360kp.onPlayerOver NoConf userId=', event.userId,
                        'matchId=', event.matchId,
                        'signinParams=', event.player.signinParams,
                        'snsId=', event.player.snsId,
                        'conf=', conf)
        return
    
    callbackUrl = conf.get('matchResultCallbackUrl')
    if not callbackUrl:
        if ftlog.is_debug():
            ftlog.debug('match360kp.onPlayerOver NoCallbackUrl userId=', event.userId,
                        'matchId=', event.matchId,
                        'signinParams=', event.player.signinParams,
                        'snsId=', event.player.snsId,
                        'conf=', conf)
        return
    
    timestamp = pktimestamp.getCurrentTimestamp()
    params = getParamsByPlayer(event.player, timestamp)
    if not params:
        if ftlog.is_debug():
            ftlog.debug('match360kp.onPlayerOver NoParams userId=', event.userId,
                        'matchId=', event.matchId,
                        'signinParams=', event.player.signinParams,
                        'snsId=', event.player.snsId,
                        'conf=', conf)
        return
    
    sign = signin('MATCH_RESULT', params)
    params['sign'] = sign
    matchResult = ''
    reward = ''
    if event.rankRewards:
        matchResult = conf.get('resultDescReward', '')
        reward = event.rankRewards.desc
    else:
        matchResult = conf.get('resultDescNoReward', '')
    
    matchResult = strutil.replaceParams(matchResult, {
                                            'match.name':event.player.inst.match.conf.name,
                                            'rank':event.player.rank,
                                            'reward':reward
                                        })
    params['result'] = matchResult
    
    result = webpage.webgetJson(callbackUrl, datas=params, appKey=None, timeout=conf.get('timeout', 3))
    if ftlog.is_debug():
        ftlog.debug('match360kp.onPlayerOver userId=', event.userId,
                    'matchId=', event.matchId,
                    'signinParams=', event.player.signinParams,
                    'snsId=', event.player.snsId,
                    'conf=', conf,
                    'result=', result)
         
    if not result or 'errno' in result:
        ftlog.warn('match360kp.onPlayerOver userId=', event.userId,
                   'matchId=', event.matchId,
                   'signinParams=', event.player.signinParams,
                   'snsId=', event.player.snsId,
                   'conf=', conf,
                   'result=', result)

def _initialize():
    pkeventbus.globalEventBus.subscribe(MatchPlayerSigninEvent, _onPlayerSignin)
    pkeventbus.globalEventBus.subscribe(MatchPlayerOverEvent, _onPlayerOver)

if __name__ == '__main__':
    print signin('REGIST', {'uid':'398710402', 'gkey':'vdhscvnmqvf', 'skey':1, 'time':1446195106, 'matchid':'6043'})
    print strutil.md5digest('%s%s' % ('vdhscvnmqvf', 'REGIST'))
    