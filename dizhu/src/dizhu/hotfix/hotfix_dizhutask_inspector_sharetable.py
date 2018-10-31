# -*- coding:utf-8 -*-
'''
Created on 2016年12月22日

@author: luwei
'''
from dizhu.entity.dizhutask import DizhuTaskInspectorShareTable
from hall.entity.hallshare import HallShareEvent
from dizhu.replay import replay_service
import freetime.util.log as ftlog


def _processEventImpl(self, task, event):
    if isinstance(event, HallShareEvent):
        # 确认是牌局分享的
        if event.shareid not in replay_service.getAllShareIds():
            return False, 0
        if ftlog.is_debug():
            ftlog.debug('DizhuTaskInspectorShareTable._processEventImpl userId=', task.userId,
                        'taskId=', task.kindId,
                        'event=', event.__dict__)
        return task.setProgress(task.progress + 1, event.timestamp)
    return False, 0

DizhuTaskInspectorShareTable._processEventImpl_old = DizhuTaskInspectorShareTable._processEventImpl
DizhuTaskInspectorShareTable._processEventImpl = _processEventImpl
ftlog.info('hotfix_dizhutask_inspector_sharetable ... ok')
