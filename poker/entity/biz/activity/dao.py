# -*- coding: utf-8 -*-

class TYActivityDao(object, ):

    @classmethod
    def getActivitiesForClient(cls, clientId):
        """
        取得客户端的活动配置
        @return: [activity1, activity2, ...], default: None
        """
        pass

    @classmethod
    def getActivityConfig(cls, activityId):
        """
        取得activityId对应的活动的配置
        @return: {}, default: None
        """
        pass

    @classmethod
    def getClientActivityConfig(cls, clientId, activityId):
        """
        取得客户端某个活动的配置
        @return: {}, default: None
        """
        pass