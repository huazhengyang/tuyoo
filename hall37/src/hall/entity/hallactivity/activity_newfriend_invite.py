# -*- coding=utf-8 -*-
"""
@file  : activity_newfriend_invite
@date  : 2016-10-22
@author: GongXiaobo
"""
import copy

from hall.entity import hallshare
from hall.entity import halluser
from hall.entity.hallactivity.activity_type import TYActivityType
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.dao import userdata
from poker.entity.dao.daoconst import UserDataSchema


class TYActNewFriendInvite(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_NEW_FRIEND_INVITE

    def getConfigForClient(self, gameId, userId, clientId):
        clientconf = copy.deepcopy(self._clientConf)
        config = clientconf['config']
        name, purl = userdata.getAttrs(userId, [UserDataSchema.NAME, UserDataSchema.PURL])
        purl, _ = halluser.getUserHeadUrl(userId, clientId, purl)
        replace_dict = {'code': userId, 'name': name, 'image': purl}
        self._fill_button_todotask(userId, config, 'button_friend', replace_dict)
        self._fill_button_todotask(userId, config, 'button_moments', replace_dict)
        return clientconf

    def _fill_button_todotask(self, userId, config, buttonname, replace_dict):
        button = config.get(buttonname)
        if not button:
            return

        if button['visible']:
            share = hallshare.findShare(button["todoTask"]["share"])
            if share:
                todotask = share.buildTodotask(HALL_GAMEID, userId, 'act_new_friend_invite', replace_dict)
                button["todoTask"] = todotask.toDict()
                return

        del config[buttonname]
        return

if __name__ == '__main__':
    pass
