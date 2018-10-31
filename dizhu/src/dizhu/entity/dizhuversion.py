# -*- coding=utf-8 -*-
'''
Created on 2016年06月24日

@author: luwei

获得地主插件的版本号
'''

from poker.entity.dao import gamedata

class SessionDizhuVersion(object):
    _DIZHU_VERSION_KEY = 'session.dizhu.version'

    @classmethod
    def getVersionNumber(cls, userId):
        '''
        获得地主版本号数字
        :param userId: 用户ID
        :return: 版本号数字
        '''
        # return userdata.getAttr(userId, cls._DIZHU_VERSION_KEY)
        return gamedata.getGameAttr(userId, 6, cls._DIZHU_VERSION_KEY)

    @classmethod
    def setVersionNumber(cls, userId, version):
        '''
        设置地主版本号
        :param userId: 用户ID
        :param version: 版本号,数字
        :return:
        '''
        if isinstance(version, basestring):
            version = float(version)
        # return userdata.setAttr(userId, cls._DIZHU_VERSION_KEY, version)
        return gamedata.setGameAttr(userId, 6, cls._DIZHU_VERSION_KEY, version);