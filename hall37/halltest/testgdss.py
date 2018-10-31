# -*- coding=utf-8 -*-
from hashlib import md5
import time
import urllib
import urllib2


def md5digest(md5str):
    m = md5()
    m.update(md5str)
    md5code = m.hexdigest()
    return md5code.lower()


def sendout(posturl, apikey, pdatas):
    pdatas['time'] = int(time.time())
    keys = pdatas.keys()[:]
    keys.sort()
    checkstr = ''
    for k in keys:
        checkstr += k + '=' + str(pdatas[k]) + '&'
    checkstr = checkstr[:-1]
    checkstr = checkstr + apikey
    pdatas['code'] = md5digest(checkstr)

    Headers = {'Content-type': 'application/x-www-form-urlencoded'}
    postData = urllib.urlencode(pdatas)
    request = urllib2.Request(url=posturl, data=postData, headers=Headers)
    response = urllib2.urlopen(request)
    if response != None:
        retstr = response.read()
        print retstr
    else:
        print 'ERROR  !!'


def doThirdPartyUserInfo(userId):
    pdatas = {
        'userId': userId
    }
    apikey = 'www.tuyoo.com--third-party-api-e031f2a946854db29211a20f2252c3a3-www.tuyoo.com'
    sendout('http://localhost/_gdss/thirdparty/user/info', apikey, pdatas)

if __name__ == "__main__":
    print '====================================='
    doThirdPartyUserInfo(10001)
    print '====================================='
