# -*- coding:utf-8 -*-
'''
Created on 2014年7月19日

@author: zjgzzz@126.com
'''

from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf, hall_wxappid
from poker.entity.configure import gdata
from poker.util import strutil, webpage
from poker.entity.dao import sessiondata

BAD_RESPONSE = {'ec':1, 'info':'bad response'}

def sendExCodeToUser(appId,content,mobile):
    params = {
        'appId':appId,
        'mobile':mobile,
        'vcode':content
    }
    _requestSdk('/open/v3/user/doSendSmsToUser', params)

def adNotifyCallBack(appId, userId):
    params = {
        'appId':appId,
        'userId':userId
    }
    _requestSdk('/open/v3/user/adnotifycallback', params)

def couponCharge(gameId, userId, phone, idcard, uname, couponCount, money):
    if not phone:
        return False
    params = {
        'gameId':gameId,
        'userId':userId,
        'chargePhone':phone,
        'idcard':idcard,
        'uname':uname,
        'couponCount':couponCount,
        'money':money
    }
    
    _requestSdk('/open/v1/pay/coupon/charge/request_inner', params)
    return True
    
def _requestSdk(path, params, needresponse=False):
    params['code'] = _sign(params)
    url = '%s%s' % (gdata.httpSdkInner(), path)
    jsonstr, _ = webpage.webget(url, postdata_=params, needresponse=needresponse)
    if needresponse:
        try:
            return strutil.loads(jsonstr)
        except:
            ftlog.error('SDKURL=',url, 'PARAMS=', params)
    return None

def _requestSdk2(path, params, needresponse=False):
    url = '%s%s' % (gdata.httpSdkInner(), path)
    jsonstr, _ = webpage.webget(url, postdata_=params, needresponse=needresponse)
    if needresponse:
        try:
            return strutil.loads(jsonstr)
        except:
            ftlog.error('SDKURL=',url, 'PARAMS=', params)
    return None

def _sign(params):
    sk = sorted(params.keys())
    strs = ['%s=%s' % (k, str(params[k]).strip()) for k in sk]
    md5str = strutil.tyDesEncode('&'.join(strs))
    return strutil.md5digest(md5str)

def sendWeixinRedEnvelope(gameId, userId, itemId, amount):
    clientId = sessiondata.getClientId(userId)
    defaultErrorInfo = '打开红包失败，请稍后再试'
    params = {
        'gameId':gameId,
        'userId':userId,
        'amount':amount,
        'wxappid': hall_wxappid.queryWXAppid(gameId, userId, clientId),
    }
    
    # TODO
    response = _requestSdk('/open/v4/user/act/wx/sendHBToUser', params, True)
    ftlog.debug('sdkclient.sendWeixinRedEnvelope gameId=', gameId,
               'userId=', userId,
               'itemId=', itemId,
               'amount=', amount,
               'response=', response)
    result = response.get('result') if response else None
    if not result:
        return -1, defaultErrorInfo
    ec = result.get('code', 0)
    if ec == 0:
        return 0, None
    return ec, result.get('info') or defaultErrorInfo

def checkResponse(conf, response):
    d = strutil.loads(response)
    status = d.get('status', 0)
    if status == 0:
        password = d.get('data', {}).get('hongbao_code')
        if not password or not isstring(password):
            return -1, conf.get('errorInfo', '红包系统忙，请稍后再试')
        return 0, password
    return status, d.get('info') or conf.get('errorInfo', '红包系统忙，请稍后再试')

def _signForWeixin(params):
    keys = sorted(params.keys())
    checkstr = ''
    for k in keys :
        checkstr += k + '=' + params[k] + '&'
    checkstr = checkstr[:-1]

    apikey = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'
    checkstr = checkstr + apikey
    return strutil.md5digest(checkstr)
    
def getWeixinRedEnvelopePassword(gameId, userId, itemId, amount):
    redenvlopeConf = hallconf.getPublicConf('weixin_redenvlope', {})
    if not redenvlopeConf:
        return -1, '红包系统忙，请稍后再试'
    
    response = None
    try:
        params = {
            'gameId':str(gameId),
            'userId':str(userId),
            'itemId':str(itemId),
            'amount':str(amount)
        }
        params['code'] = _signForWeixin(params)
        response, _ = webpage.webget(redenvlopeConf['url'], postdata_=params, needresponse=True)
        ftlog.debug('sdkclient.getWeixinRedEnvelopePassword gameId=', gameId,
                   'userId=', userId,
                   'itemId=', itemId,
                   'amount=', amount,
                   'response=', response)
        return checkResponse(redenvlopeConf, response)
    except:
        ftlog.error('sdkclient.getWeixinRedEnvelopePassword Exception gameId=', gameId,
                    'userId=', userId,
                    'itemId=', itemId,
                    'amount=', amount,
                    'response=', response)
        return -1, redenvlopeConf.get('errorInfo')

def verifyAccount(userId, authorCode):
    params = {'userId': userId,
              'authorCode': authorCode
              }
    datas = _requestSdk2('/open/v4/user/verifyAuthorCode', params, 1)
    verify = None
    if datas :
        verify = datas.get('result', {}).get('verify', {})
    if isinstance(verify, dict) :
        if verify.get('uid') == userId :
            return 1
    return 0

if __name__ == '__main__':
#     gameId = 6
#     userId = 10001
#     itemId = 18888
#     amount = 1
#     params = {
#         'gameId':str(gameId),
#         'userId':str(userId),
#         'itemId':str(itemId),
#         'amount':str(amount)
#     }
#     print _signForWeixin(params)
    params = {
        'amount':100,
        'gameId':9999,
        'userId':104000286
    }
    print _sign(params)
