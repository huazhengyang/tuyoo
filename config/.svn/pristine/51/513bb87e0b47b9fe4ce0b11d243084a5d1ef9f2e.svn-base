# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''

from _loader._base import mainconf
from datetime import datetime


def main(readPath, outPath, module):
    # 读取所有游戏下的配置内容
    cmlist = mainconf.getTcVcDatasAll(readPath, 0)
    # 删除无用的template内容
    mainconf.removeUnUsedTemplates(cmlist)

    # 收集所有被引用的ID
    usedIds = set()
    for cm in cmlist:
        for _, template in cm.tcDatas['templates'].items():
            usedIds.update(template['activities'])
    # 过滤结束时间，删除过期的ID
    nowDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for cm in cmlist:
        acts = cm.tcDatas.get('activities', {})
        for key in acts.keys():
            act = acts[key]
            if act['server_config']['end'] < nowDate:  # 配置已经过期，无效
                if key in usedIds:
                    usedIds.remove(key)
                    print 'FOUND EXPIRED ACTIVITY:', cm.gameId, key
