# -*- coding:utf-8 -*-
'''
Created on 2017年11月28日

@author: zhaojiangang
'''
from datetime import datetime

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.entity.dao import daobase
from poker.util import strutil, webpage
import poker.util.timestamp as pktimestamp
from freetime.core.timer import FTLoopTimer


class ShortUrlx3me(object):
    def __init__(self, apiKey, secretKey):
        self.apiKey = apiKey
        self.secretKey = secretKey
        self.token = None
        self.expires = None
        self.refreshTimer = None

    def translate(self, longUrl):
        '''
        转换长url为短url
        @return: shortUrl
        '''
        try:
            if self.isExpires():
                self.token, self.expires = self.loadToken()
            return self._getShorUrl(longUrl)
        except:
            ftlog.error('ShortUrlx3me.translate',
                        'longUrl=', longUrl)
            return longUrl
    
    def initialize(self, serverType):
        if serverType == gdata.SRV_TYPE_CENTER:
            # 只在CT中执行刷新token的操作
            self.refreshTimer = FTLoopTimer(300, -1, self._refreshTokenIfNeed)
            self.refreshTimer.start()
            FTLoopTimer(0, 0, self._refreshTokenIfNeed).start()
        else:
            self.refreshTimer = FTLoopTimer(300, -1, self._reloadToken)
            self.refreshTimer.start()
            self._reloadToken()

    def loadToken(self):
        jstr = None
        try:
            jstr = daobase.executeMixCmd('get', 'shortUrl.x3me:token')
            if jstr:
                d = strutil.loads(jstr)
                return d['token'], d['expires']
        except:
            ftlog.error('ShortUrlx3me.getToken',
                        'jstr=', jstr)
        return None, None

    def saveToken(self, token, expires):
        d = {'token':token, 'expires':expires}
        jstr = strutil.dumps(d)
        daobase.executeMixCmd('set', 'shortUrl.x3me:token', jstr)
    
    def isExpires(self, timestamp=None):
        # 离过期时间1小时算过期
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        return not self.token or not self.expires or (timestamp + 3600) >= self.expires
    
    def _reloadToken(self):
        self.token, self.expires = self.loadToken()
        ftlog.info('ShortUrlx3me._reloadToken',
                   'token=', self.token,
                   'expires=', self.expires)
        
    def _refreshTokenIfNeed(self, timestamp=None):
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        # 重新从数据库读取，可能数据库里面改变了（人工操作）
        self._reloadToken()
        # 提前一天刷新
        if not self.token or (timestamp + 86400) >= self.expires:
            try:
                token, expires = self._requestToken()
                self.saveToken(token, expires)
                ftlog.info('ShortUrlx3me._refreshTokenIfNeed',
                           'old=', (self.token, self.expires),
                           'new=', (token, expires))
                self.token, self.expires = token, expires
            except:
                ftlog.error('Failed to refresh token',
                            'old=', (self.token, self.expires))
        
    def _requestToken(self):
        code = self._requestCode()
        return self._requestTokenWithCode(code)
    
    def _validResponse(self, response):
        datas = strutil.loads(response)
        return datas['status'], datas['info'], datas['data']
    
    def _requestCode(self):
        response, _ = webpage.webget('https://0x3.me/apis/authorize/getCode', method_='GET')
        status, info, data = self._validResponse(response)
        if ftlog.is_debug():
            ftlog.debug('ShortUrlx3me._requestCode',
                        'response=', response)
        if status != 1:
            ftlog.warn('ShortUrlx3me._requestCode',
                       'response=', response)
            raise TYBizException(-1, '%s:%s' % (status, info))
        return data
    
    def _calcSign(self, params):
        kvs = []
        for key in sorted(params.keys()):
            kvs.append('%s=%s' % (key, params[key]))
        kvs.append(self.secretKey)
        signstr = ''.join(kvs)
        return strutil.md5digest(signstr)

    def _requestTokenWithCode(self, code):
        timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = {'api_key':self.apiKey, 'code':code, 'request_time':timestr}
        params['sign'] = self._calcSign(params)
        response, _ = webpage.webget('https://0x3.me/apis/authorize/getAccessToken', postdata_=params, method_='POST')
        status, info, data = self._validResponse(response)
        if status != 1:
            ftlog.warn('ShortUrlx3me._requestTokenWithCode',
                       'code=', code,
                       'response=', response)
            raise TYBizException(-1, '%s:%s' % (status, info))
        return data['access_token'], int(data['expire_timestamp'])
    
    def _getShorUrl(self, longUrl):
        if not self.token:
            ftlog.warn('ShortUrlx3me._getShorUrl',
                       'err=', 'NoToken')
            return longUrl
        
        response, _ = webpage.webget('https://0x3.me/apis/urls/add', postdata_={'access_token':self.token, 'longurl':longUrl}, method_='POST')
        status, info, data = self._validResponse(response)
        if status != 1:
            raise TYBizException(-1, '%s:%s' % (status, info))

        return data['short_url']


_instance = None


def getShortUrlNew(longUrl, expTime=-1):
    '''
    调用新的短链接API
    expTime ：整数，单位：秒，短连接的有效时间，超出这个时间后，生成的短链接将被删除
                小于0或其他非数字则永久保留，若无则只保存一周
    :return: shortUrl
    例子：
    http://shorturl.ywdier.com/api/shorturl/make?expTime=0&longUrl=http://ddz.dl.tuyoo.com/cdn37/hall/item/imgs/coupon.png
    '''
    headUrl = 'http://shorturl.ywdier.com/api/shorturl/make' # 抛弃IP使用内网域名的方式 ZQH
    params = {
        'expTime': expTime,
        'longUrl': longUrl
    }

    response, _ = webpage.webget(headUrl, querys=params, method_='GET')
    if not response:
        ftlog.warn('hall_short_url.getShortUrlNew error= no response',
                   'headUrl=', headUrl,
                   'params=', params)
        return longUrl
    datas = strutil.loads(response)

    if ftlog.is_debug():
        ftlog.debug('longUrlToShort.ShortUrlx3me._getShorUrl',
                    'longUrl=', longUrl,
                    'headUrl=', headUrl,
                    'method_=', 'GET',
                    'response=', response,
                    'datas=', datas)

    if 'error' in datas:
        ftlog.warn('hall_short_url.getShortUrlNew error=', datas.get('error'),
                   'headUrl=', headUrl)
        return longUrl
    shortUrl = datas.get('url')
    return shortUrl if shortUrl else longUrl

def longUrlToShort(longUrl):
    if hallconf.getHallPublic().get('newShortUrlSwitch', 1):
        return getShortUrlNew(longUrl)

    global _instance
    if not _instance:
        ftlog.warn('hall_short_url.longUrlToShort not init')
        return longUrl
    return _instance.translate(longUrl)


def _initialize():
    global _instance
    newShortUrlSwitch = hallconf.getHallPublic().get('newShortUrlSwitch', 1)
    if not _instance and not newShortUrlSwitch:
        _instance = ShortUrlx3me('bqkVoGCAYx', 'EuOLQYtTwyrrkdSKEZWlgqOHRgMPtoZK')
        _instance.initialize(gdata.serverType())
        ftlog.info('hall_short_url._initialize')


