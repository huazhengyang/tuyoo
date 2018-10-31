# -*- coding: utf-8 -*-
'''
Created on 2015-5-12
@author: 赵良
添加控制退出SDK功能，配置的热更新文件
'''

from poker.entity.configure import configure
from hall.entity import hallconf

HALL_GAMEID = 9999

def getExitRemindVCConf():
    return configure.getGameJson(HALL_GAMEID, 'exit_remind', {}, configure.CLIENT_ID_MATCHER)

hallconf.getExitRemindVCConf = getExitRemindVCConf