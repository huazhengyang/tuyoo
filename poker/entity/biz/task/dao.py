# -*- coding: utf-8 -*-
"""
Created on 2015年7月13日

@author: zhaojiangang
"""

class TYTaskDataDao(object, ):

    def loadAll(self, gameId, userId):
        """
        加载用户所有任务
        @return: list(kindId, bytes)
        """
        pass

    def saveTask(self, gameId, userId, kindId, taskDataBytes):
        """
        保存一个用户的task
        @param kindId: kindId
        @param taskDataBytes: bytes
        """
        pass

    def removeTask(self, gameId, userId, kindId):
        """
        删除一个用户的task
        @param kindId: kindId
        """
        pass