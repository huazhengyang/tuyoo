# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''

from datetime import datetime

from _loader._base import mainconf


def main(readPath, outPath, module):
    # 读取所有游戏下的配置内容
    cmlist = mainconf.getTcVcDatasAll(readPath, 0)
    # 删除无用的template内容
    mainconf.removeUnUsedTemplates(cmlist)

    # 收集所有被引用的ID
    usedIds = set()
    for cm in cmlist:
        for _, template in cm.tcDatas['templates'].items():
            usedIds.update(template['ads'])

    # 过滤结束时间，删除过期的ID
    nowDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for cm in cmlist:
        ads = cm.tcDatas.get('ads', [])
        for x in xrange(len(ads) - 1, -1, -1):
            if ads[x]['endTime'] < nowDate:  # 配置已经过期，无效
                aid = ads[x]['id']
                if aid in usedIds:
                    usedIds.remove(aid)
                    print 'FOUND EXPIRED ADS:', cm.gameId, ads[x]['id']
