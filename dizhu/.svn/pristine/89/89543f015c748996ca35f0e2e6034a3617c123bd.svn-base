# -*- coding:utf-8 -*-
'''
Created on 2017年9月14日

@author: wangjifa
'''

import freetime.util.log as ftlog
from dizhu.entity.erdayi import PlayerData


def changeErdayiBindMobile(userId, oldMobile, newMobile):
    realinfo = PlayerData.getRealInfo(userId)
    if realinfo and realinfo.get('idNo'):
        mobile = realinfo.get('mobile')
        realName = realinfo.get('realname')

        if mobile and mobile == oldMobile:
            #player_realinfo = {'idNo': idNo, 'mobile': newMobile, 'realname': realName}
            realinfo['mobile'] = newMobile
            PlayerData.setRealInfo(userId, realinfo)
            ftlog.info('hotfix_erdayi_changeUserBindMobile success. userId=', userId,
                       'realName=', realName,
                       'realInfo=', realinfo)
        else:
            ftlog.info('hotfix_erdayi_changeUserBindMobile failed. userId=', userId, 'realInfo=', realinfo)

    ftlog.info('hotfix_erdayi_changeUserBindMobile userId=', userId, 'realInfo=', realinfo)


# userId = 224283328
# oldMobile = '15995981596'
# newMobile = '18888127998'
changeErdayiBindMobile(224283328, '15995981596', '18888127998')