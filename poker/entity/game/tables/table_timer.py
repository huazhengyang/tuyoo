# -*- coding: utf-8 -*-
"""
Created on 2015年7月7日

@author: zqh
"""
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTTimer
import stackless
from poker.protocol import runcmd

class TYTableTimer(object, ):
    """
    桌子使用的专用的计时器, 当计时器触发时, 触发桌子的同步方法:doTableCall
    """

    def __init__(self, table):
        pass

    def _onTimeOut(self):
        """
        计时器到时, 触发table的doTableCall方法
        """
        pass

    def setup(self, interval, action, msgPackParams, cancelLastTimer=True):
        """
        启动计时器
        interval 倒计时的时间, 单位: 秒
        action table_call命令下(params中)的action值
        msgPackParams 传递的其他的参数数据集合dict, 可以在doTableCall中的msg中使用msg.getParam(key)来取得其中的参数
        """
        pass

    def cancel(self):
        """
        取消当前的计时器
        """
        pass

    def reset(self, interval):
        """
        重置当前的计时器
        """
        pass

    def getInterval(self):
        """
        取得当前计时器的倒计时时间
        """
        pass

    def getTimeOut(self):
        """
        取得当前计时器的剩余的倒计时时间, 若没有开始倒计时, 那么返回0
        """
        pass