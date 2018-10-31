# -*- coding:utf-8 -*-
'''
Created on 2018年04月07日

@author: zhaoliang
'''
from dizhu.gametable.dizhu_hero_match_table import DizhuPlayerHeroMatch
from poker.entity.game.tables.table_player import TYPlayer

def initUser(self, isNextBuyin, isUsingScore, randomIndex = 0):
    '''
    从redis里获取并初始化player数据, 远程操作
    '''
    ret = super(DizhuPlayerHeroMatch, self).initUser(isNextBuyin, isUsingScore)
    if TYPlayer.isRobot(self.userId):
        from dizhu.wx_resource import wx_resource
        wx_resource.initRobotSetting()
        wxUserInfo = wx_resource.getRobot(randomIndex)
        self.datas['sex'] = wxUserInfo['sex']
        self.datas['name'] = wxUserInfo['name']
        self.datas['purl'] = wxUserInfo['purl']
        self.clientId = 'robot_3.7_-hall6-robot'
    return ret

DizhuPlayerHeroMatch.initUser = initUser