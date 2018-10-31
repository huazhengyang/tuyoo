# coding=UTF-8
'''
'''
import sys

def dohttpquery(posturl, datadict):
    import urllib2, urllib
    Headers = {'Content-type': 'application/x-www-form-urlencoded'}
    postData = urllib.urlencode(datadict)
    request = urllib2.Request(url=posturl, data=postData, headers=Headers)
    response = urllib2.urlopen(request)
    if response != None :
        retstr = response.read()
        return retstr
    return None


def doHotFix(httpdomain, hotfixpy, serverIds):

    hurl = httpdomain + '/_http_manager_hotfix'

    print '==================================================='
    print 'doHtFixOf->', hurl, hotfixpy
    result = dohttpquery(hurl, 
                         {'hotfixpy' : hotfixpy,
                          'wait' : 1,
                          'serverIds' : serverIds})
    print '==================================================='
    print 'doHotFix->', result


def doTestForceLogout():
    httpdomain = sys.argv[1]
    logoutmsg = sys.argv[2]
    userids = sys.argv[3]
    hurl = httpdomain + '/v2/game/user/forcelogout'
    print dohttpquery(hurl, {'userids' : userids,
                             'logoutmsg' :logoutmsg})
    
if __name__ == "__main__":
    doTestForceLogout()

