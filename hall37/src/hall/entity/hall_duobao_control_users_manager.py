# -*- coding: utf-8 -*-
'''
Created on 2018年03月21日16:11:03
@author: zyb
每个配置项必须是JSON格式
夺宝抑制用户管理
'''
class DuobaoControlUserManager(object):
    def __init__(self, userIds, ips):# duobaoid:{userId:time, ...} duobaoid{ip:time,...}
        self.userIds = userIds
        self.ips = ips
    
gduoBaoControllUserManager = DuobaoControlUserManager({}, {})

def getInstance():
    return gduoBaoControllUserManager
            
#没有找到夺宝id对应的map就创建一个
def getUserIdsIpsByDuoBaoId(duobaoId):
    if not gduoBaoControllUserManager.userIds.has_key(duobaoId):
        gduoBaoControllUserManager.userIds[duobaoId] = {}
    if not gduoBaoControllUserManager.ips.has_key(duobaoId):
        gduoBaoControllUserManager.ips[duobaoId] = {}
    return gduoBaoControllUserManager.userIds[duobaoId], gduoBaoControllUserManager.ips[duobaoId]


