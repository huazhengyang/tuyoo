# -*- coding:utf-8 -*-
from poker.entity.configure import configure, gdata
from poker.entity.events import tyeventbus
from poker.entity.events.tyevent import EventConfigure
import random

import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID

MAX_ROBOT_USERID = 10000
validUrl = "http://ddz.image.tuyoo.com/avatar/head_cat.png"
validName = '滴滴滴滴三名'

_robotMap = {}
_headUrls = []
_userNames = []
_inited = False


class RobotUser(object):
    '随机人'
    def __init__(self, userId):
        self.userId = userId
        self.property = {}
        
    def getAttr(self, key):
        return self.property.get(key)
    
    def setAttr(self, key, value):   
        self.property[key] = value
        return self


def _initRobots():
    global _robotMap

    for i in range(1, MAX_ROBOT_USERID):
        _robotMap[i] = RobotUser(i)

def _loadCfgRobotNamesAndUrls():
    global _userNames
    global _headUrls
    
    if _inited:
        conf = configure.getGameJson(HALL_GAMEID, 'robots', {}, '0')
        names = conf.get('names')
        headUrls = conf.get('headUrls')
        
        if ftlog.is_debug():
            ftlog.debug('hall_robot_user._loadCfgRobotNamesAndUrls',
                        'names=', names,
                        'headUrls=', headUrls)
        if names:
            _userNames = names
        if headUrls:
            _headUrls = headUrls 
        
def _loadRobotsConfig(event):
    if _inited:
        if event.isChanged('game:9999:robots:0'):
            _loadCfgRobotNamesAndUrls()           
        
def _initialize():
    global _inited

    serverType = gdata.serverType()
    if not _inited and serverType == gdata.SRV_TYPE_CENTER:
        _inited = True
        _initRobots()
        _loadCfgRobotNamesAndUrls()
        tyeventbus.globalEventBus.subscribe(EventConfigure, _loadRobotsConfig)
        if ftlog.is_debug():
            ftlog.debug('hall_robot_user._initialize',
                        'names=', _userNames,
                        'headUrls=', _headUrls)

def getRobots():
    return _robotMap

def getRandomImageUrl():
    if _headUrls:        
        return _headUrls[random.randint(0, len(_headUrls) - 1)]
    
    return validUrl

def getRandomName():
    if _userNames:        
        return _userNames[random.randint(0, len(_userNames) - 1)]
    
    return validName

def getRandomRobotId():
    robots = getRobots()
    if robots:
        iRobot = random.randint(0, len(robots) - 1)
        rb = robots[iRobot]
        return rb.userId
    return 1


