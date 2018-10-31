# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaojiangang
'''
from poker.util import strutil

RESOURCE_ROBOTS = []

def getResourcePath(fileName):
    '''
    取得当前文件下某一个资源的绝对路径
    '''
    import os
    cpath = os.path.abspath(__file__)
    cpath = os.path.dirname(cpath)
    fpath = cpath + os.path.sep + fileName
    return fpath

def loadResource(fileName):
    '''
    取得当前文件下某一个资源的文件内容
    '''
    fpath = getResourcePath(fileName)
    f = open(fpath)
    c = f.read()
    f.close()
    return c

def getRobot(index):
    '''
    @param
        index - 索引
    @return:
        返回索引为index的机器人名称
    '''
    global RESOURCE_ROBOTS
    initRobotSetting()
        
    index = index % len(RESOURCE_ROBOTS)
    return RESOURCE_ROBOTS[index]

def initRobotSetting():
    global RESOURCE_ROBOTS
    
    if len(RESOURCE_ROBOTS) == 0:
        res = loadResource('wx_users.json')
        rinfo = strutil.loads(res)
        RESOURCE_ROBOTS = rinfo['wx_users']
        
def getRobotCount():
    global RESOURCE_ROBOTS
    initRobotSetting()
    return len(RESOURCE_ROBOTS)

def getRobotByUserId(userId):
    """根据userId获取机器人"""
    global RESOURCE_ROBOTS
    
    for robot in RESOURCE_ROBOTS:
        if robot['userId'] == userId:
            return robot
    return None