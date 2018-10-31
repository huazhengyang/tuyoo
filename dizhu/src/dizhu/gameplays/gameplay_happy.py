# coding=UTF-8
'''
'''
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
from dizhu.entity import dizhuconf


class DizhuHappyGamePlay(DizhuBaseGamePlay):
    

    def getPlayMode(self):
        return dizhuconf.PLAYMODE_HAPPY
