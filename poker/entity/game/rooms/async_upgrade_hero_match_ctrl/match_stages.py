# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的轮次/阶段对象们
@author: zhaol

    {
        "cardCount": 1,
        "chipBase": 1,
        "chipUser": 1,
        "name": "第三轮",
        "canBack": 1,
        "backFee": [{
          "desc": "2个钻石",
          "fees": [{
              "count": 2,
              "itemId": "item:1007"
          }],
          "params": {
            "failure": "您的复活费用不足，本比赛报名费需2个钻石"
          }
        }]
      }

"""
from freetime.util import log as ftlog

class AUHMBackFee(object, ):

    def __init__(self):
        pass

    @property
    def payOrder(self):
        pass

    def setPayOrder(self, payOrder):
        pass

    @property
    def count(self):
        pass

    @property
    def itemId(self):
        pass

    def setCount(self, count):
        pass

    def setItemId(self, itemId):
        pass

    def initConfig(self, config):
        """
        初始化配置
        """
        pass

    @property
    def desc(self):
        pass

    def setDesc(self, desc):
        pass

    @property
    def failure(self):
        pass

    def setFailure(self, params):
        pass

    def collectFee(self):
        """
        复活费用
        """
        pass

class AUHMStageNode(object, ):

    def __init__(self):
        pass

    def initConfig(self, config):
        pass

    @property
    def index(self):
        pass

    def setIndex(self, index):
        pass

    @property
    def name(self):
        pass

    def setName(self, name):
        pass

    @property
    def cardCount(self):
        pass

    def setCardCount(self, count):
        pass

    @property
    def chipBase(self):
        pass

    def setChipBase(self, base):
        pass

    @property
    def chipUser(self):
        pass

    def setChipUser(self, user):
        pass

    @property
    def canBack(self):
        pass

    def setCanBack(self, back):
        pass

    @property
    def canBackToNext(self):
        pass

    def setCanBackToNext(self, back):
        pass

    @property
    def backFee(self):
        pass

    def setBackFee(self, fee):
        pass

class AsyncUpgradeHeroMatchStages(object, ):
    """
    快速赛比赛阶段s
    """

    def __init__(self):
        pass

    @property
    def stages(self):
        """
        所有的比赛阶段
        """
        pass

    def setStages(self, stages):
        pass

    def initConfig(self, config):
        """
        根据配置初始化比赛阶段
        """
        pass

    def getStage(self, index):
        """
        根据索引获取比赛阶段
        """
        pass

    def getFirstStage(self):
        """
        获取第一阶段
        """
        pass

    def getFirstStageIndex(self):
        """
        取第一阶段的index
        """
        pass

    def getLastStageIndex(self):
        """
        取最后一个阶段的index
        """
        pass

    def getAllIndexes(self):
        """
        获取所有的关卡编码
        """
        pass

    def getInitScore(self):
        """
        获取本场比赛的初始积分
        """
        pass

    def getNextStage(self, stageIndex):
        """
        获取下一个赛段
        """
        pass

    def findStageByIndex(self, stageIndex):
        """
        根据index查找赛制阶段
        """
        pass

    def getBaseChip(self):
        """
        获取底注
        """
        pass

    def getCardCount(self):
        """
        获取每个赛段的局数
        """
        pass

    def getDesc(self):
        """
        获取阶段描述
        """
        pass

    def getDetailDesc(self):
        """
        获取阶段的详细描述
        """
        pass
if (__name__ == '__main__'):
    config = [{'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe4\xb8\x80\xe8\xbd\xae', 'canBackToNext': 1, 'canBack': 0, 'index': 1, 'backFee': {}}, {'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe4\xba\x8c\xe8\xbd\xae', 'canBackToNext': 0, 'canBack': 1, 'index': 2, 'backFee': {'desc': '2\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3', 'count': 2, 'itemId': 'item:1007', 'failure': '\xe6\x82\xa8\xe7\x9a\x84\xe5\xa4\x8d\xe6\xb4\xbb\xe8\xb4\xb9\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x8c\xe6\x9c\xac\xe6\xaf\x94\xe8\xb5\x9b\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe9\x9c\x802\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3'}}, {'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe4\xb8\x89\xe8\xbd\xae', 'canBackToNext': 0, 'canBack': 1, 'index': 3, 'backFee': {'desc': '2\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3', 'count': 2, 'itemId': 'item:1007', 'failure': '\xe6\x82\xa8\xe7\x9a\x84\xe5\xa4\x8d\xe6\xb4\xbb\xe8\xb4\xb9\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x8c\xe6\x9c\xac\xe6\xaf\x94\xe8\xb5\x9b\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe9\x9c\x802\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3'}}, {'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe5\x9b\x9b\xe8\xbd\xae', 'canBackToNext': 0, 'canBack': 1, 'index': 4, 'backFee': {'desc': '2\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3', 'count': 2, 'itemId': 'item:1007', 'failure': '\xe6\x82\xa8\xe7\x9a\x84\xe5\xa4\x8d\xe6\xb4\xbb\xe8\xb4\xb9\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x8c\xe6\x9c\xac\xe6\xaf\x94\xe8\xb5\x9b\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe9\x9c\x802\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3'}}, {'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe4\xba\x94\xe8\xbd\xae', 'canBackToNext': 0, 'canBack': 1, 'index': 5, 'backFee': {'desc': '2\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3', 'count': 2, 'itemId': 'item:1007', 'failure': '\xe6\x82\xa8\xe7\x9a\x84\xe5\xa4\x8d\xe6\xb4\xbb\xe8\xb4\xb9\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x8c\xe6\x9c\xac\xe6\xaf\x94\xe8\xb5\x9b\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe9\x9c\x802\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3'}}, {'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe5\x85\xad\xe8\xbd\xae', 'canBackToNext': 0, 'canBack': 1, 'index': 6, 'backFee': {'desc': '2\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3', 'count': 2, 'itemId': 'item:1007', 'failure': '\xe6\x82\xa8\xe7\x9a\x84\xe5\xa4\x8d\xe6\xb4\xbb\xe8\xb4\xb9\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x8c\xe6\x9c\xac\xe6\xaf\x94\xe8\xb5\x9b\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe9\x9c\x802\xe4\xb8\xaa\xe9\x92\xbb\xe7\x9f\xb3'}}, {'cardCount': 1, 'chipBase': 1, 'chipUser': 1, 'name': '\xe7\xac\xac\xe4\xb8\x83\xe8\xbd\xae', 'canBackToNext': 0, 'canBack': 0, 'index': 7, 'backFee': {}}]
    stages = AsyncUpgradeHeroMatchStages()
    stages.initConfig(config)