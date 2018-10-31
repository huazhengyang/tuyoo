# -*- coding:utf-8 -*-
'''
Created on 2018年2月1日

@author: wangyonghui
'''
from dizhu.entity import dizhushare
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.dao import daobase, gamedata
from poker.entity.dao import userdata
from poker.util import strutil
from freetime.util import log as ftlog


class FriendHelper(object):
    '''
    朋友桌打牌自动添加好友
    '''
    @classmethod
    def buildFriendKey(cls, userId):
        return 'wechatfriend:%s:%s' % (DIZHU_GAMEID, userId)

    @classmethod
    def getUserFriendList(cls, userId):
        '''获取用户好友列表'''
        jstr = daobase.executeUserCmd(userId, 'GET', cls.buildFriendKey(userId))
        if ftlog.is_debug():
            ftlog.debug('dizhu_friend.FriendHelper.getUserFriendList',
                        'userId=', userId,
                        'jstr=', jstr)
        if jstr:
            return strutil.loads(jstr)
        return []

    @classmethod
    def addFriend(cls, userId, userList):
        '''添加好友'''
        friendList = cls.getUserFriendList(userId)
        changed = False
        for uId in userList:
            if uId not in friendList and uId != userId:
                changed = True
                friendList.append(uId)
        if ftlog.is_debug():
            ftlog.debug('dizhu_friend.FriendHelper.addFriend',
                        'userId=', userId,
                        'userList=', userList,
                        'changed=', changed,
                        'friendList=', friendList)
        if changed:
            daobase.executeUserCmd(userId, 'SET', cls.buildFriendKey(userId), strutil.dumps(friendList))

    @classmethod
    def getUserFriendRankList(cls, userId):
        '''获取好友排行'''
        friendIdList = cls.getUserFriendList(userId)
        friendIdList.append(userId)
        friendInfoList = []
        for uId in friendIdList:
            name, purl = userdata.getAttrs(uId, ['name', 'purl'])
            totalWinCount = cls.getUserWinCount(uId)
            totalMoney = dizhushare.getUserShareInfo(uId, 'career').red.get('rmb', 0)
            friendInfoList.append({
                'nickname': name,
                'userId': uId,
                'avatar': purl,
                'totalWinCount': totalWinCount,
                'totalMoney': totalMoney
            })
        friendInfoList.sort(key=lambda x: (-x['totalMoney'], -x['totalWinCount']))
        for rank, friendInfo in enumerate(friendInfoList[:50], 1):
            friendInfo['rank'] = rank
        return friendInfoList

    @classmethod
    def getUserWinCount(cls, userId):
        winrate = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['winrate'])
        winrate = strutil.loads(winrate[0], ignoreException=True, execptionValue={'pt': 0, 'wt': 0})
        return winrate.get('pt', 0)
