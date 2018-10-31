# -*- coding:utf-8 -*-
'''
Created on 2016-11-29

@author: wanghaiping
'''
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from hall.entity import hallshare
from poker.util import strutil
import freetime.util.log as ftlog

'''
userName : 用户名
raceName : 比赛名
rank : 名次
reward : 获得奖励描述
userId : 用户ID
'''
def buildDiplomaShare(userName, raceName, rank, reward, userId):
    shareId = dizhuconf.getPublicConf('diplomaShareId', 0)
    ftlog.debug('buildDiplomaShare shareId = ', shareId)
    if shareId <= 0:
        return None
    
    share = hallshare.findShare(shareId)
    # build share todotask
    params = {
               'userName' : userName,
               'raceName' : raceName,
               'rank' : rank,
               'reward' : reward
              }
    
    todotask = share.buildTodotask(DIZHU_GAMEID, userId, 'diploma_share')
    desc = todotask.getParam('des', '')
    todotask.setParam('des', strutil.replaceParams(desc, params))
    
    return todotask.toDict()
