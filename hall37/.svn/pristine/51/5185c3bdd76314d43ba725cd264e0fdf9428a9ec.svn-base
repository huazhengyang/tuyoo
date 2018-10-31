# -*- coding: utf-8 -*-
'''
Created on Aug 21, 2015

@author: hanwf
'''
import freetime.util.log as ftlog
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity import hallconf, hallaccount, hallitem
from poker.entity.dao import gamedata, userdata, userchip, daoconst
from datetime import datetime
from freetime.entity.msg import MsgPack
import base64, json
from poker.entity.biz.message import message
from poker.entity.events.tyevent import DataChangeEvent
from hall.servers.util.rpc import user_remote
from poker.util import strutil


class NeiTuiGuangProtocolBuilder(object):
    
    @classmethod
    def buildNewUserState(cls, gameId, userId, action, state, inviteetip, mo):
        mo.setCmd('promote_info')
        mo.setResult('gameId', gameId)
        mo.setResult('state', state)
        mo.setResult('action', action)
        mo.setResult('inviteePrize', inviteetip)
    
    @classmethod
    def buildBindUserState(cls, gameId, userId, action, state, bindok, mo):
        mo.setCmd('promote_info')
        mo.setResult('gameId', gameId)
        mo.setResult('state', state)
        mo.setResult('bindPhone', bindok)
        mo.setResult('action', action)
    
    @classmethod
    def buildOldUserState(cls, gameId, userId, action, state, bindok, shareId, prizeinfo, weixintip, url, smstip, rules, mo):
        mo.setCmd('promote_info')
        mo.setResult('gameId', gameId)
        mo.setResult('state', state)
        mo.setResult('bindPhone', bindok)
        mo.setResult('action', action)
        mo.setResult('shareId', shareId)
        mo.setResult('promoteCode', str(userId))
        mo.setResult('prizeInfo', prizeinfo)
        mo.setResult('weixinInviteDoc', weixintip)
        mo.setResult('weixinInviteUrl', url)
        mo.setResult('smsInviteDoc', smstip)
        mo.setResult('rules', rules)
    
    @classmethod
    def buildBasicInfo(cls, code, action, tip, mo):
        mo.setCmd('promote_info')
        mo.setResult('code', code)
        mo.setResult('action', action)
        mo.setResult('info', tip)
        
    @classmethod
    def buildBindPrize(cls, code, action, tip, friendId, mo):
        mo.setCmd('promote_info')
        mo.setResult('code', code)
        mo.setResult('action', action)
        mo.setResult('info', tip)
        mo.setResult('friendId', friendId)
    
    @classmethod
    def buildOldUserPrize(cls, code, action, tip, friendId, mo):
        mo.setCmd('promote_info')
        mo.setResult('code', code)
        mo.setResult('action', action)
        mo.setResult('info', tip)
        mo.setResult('friendId', friendId)
    
    @classmethod
    def buildQueryPrize(cls, action, getedPrize, prizeAvailable, friends, mo):
        mo.setCmd('promote_info')
        mo.setResult('action', action)
        mo.setResult('getedPrize', getedPrize)
        mo.setResult('prizeAvailable', prizeAvailable)
        mo.setResult('friends', friends)
    
class NeiTuiGuang(object):
    attrname_state = 'neituiguang:state'
    attrname_succchip = 'neituiguang:succchip'
    attrname_failchip = 'neituiguang:failchip'
    attrname_succcoupon = 'neituiguang:succcoupon'
    attrname_failcoupon = 'neituiguang:failcoupon'
    attrname_invitedfriendnum = 'neituiguang:invitedfriendnum'
    attrname_invitedfriendlist = 'neituiguang:invitedfriendlist'
    attrname_promotecode = "neituiguang:promotecode"
    
    @classmethod
    def wrapUid(cls, userId):
        return str(userId)

    @classmethod
    def wrapInvitedFriendList(cls, userId, friendId):
        return str(userId) + ':' + str(friendId) + ':' + cls.attrname_invitedfriendlist
    
    @classmethod
    def intPromoteCode(cls, pcode):
        promoteCode = -1
        try:
            promoteCode = int(pcode)
            if promoteCode < 0:
                promoteCode = -1
        except:
            pass
        return promoteCode
    
    @classmethod
    def initUserState(cls, userId, gameId, createTime, conf):
        state = 0 # 新用户状态
        if cls.isOldUser(userId, gameId, createTime, conf):
            state = 2 # 老用户状态
        return state
    
    @classmethod
    def isOldUser(cls, userId, gameId, createTime, conf):
        limitday = conf.get('validDay', 7)
        createdate = datetime.strptime(createTime.rsplit(' ')[0], '%Y-%m-%d')
        now = datetime.now()
        if (now.date() - createdate.date()).days >= limitday:
            return True
        return False
    
    @classmethod
    def inviteeTip(cls, userId, gameId, createTime, conf):
        prize = strutil.cloneData(conf.get('inviteePrize', {}))
        validday = conf.get('validDay', 7)
        createdate = datetime.strptime(createTime.rsplit(' ')[0], '%Y-%m-%d')
        now = datetime.now()
        if (now.date() - createdate.date()).days >= validday:
            day = 0
        else:
            day = validday - (now.date() - createdate.date()).days
        
        prize['warn'] = prize['warn'].format(REM_DAYS=day)
        return prize
    
    @classmethod
    def bindOk(cls, bindmobile):
        if bindmobile == None or bindmobile == "":
            return 0
        return 1
    
    @classmethod
    def getWeiXinTip(cls, userId, conf):
        conf = conf.get('gameDoc', {})
        return strutil.cloneData(conf.get('weixinInviteDoc')).format(PROMOTE_CODE=userId)
    
    @classmethod
    def getDownUrl(cls, userId, conf):
        conf = conf.get('gameDoc', {})
        userId = base64.b64encode(json.dumps({"code": userId}))
        return strutil.cloneData(conf.get('downloadUrl', '')).format(PROMOTE_CODE=userId)
    
    @classmethod
    def getSMSTip(cls, gameId, userId, conf):
        conf = conf.get('gameDoc', {})
        return strutil.cloneData(conf.get('smsInviteDoc')).format(PROMOTE_CODE=userId, DOWNLOAD_URL=cls.getDownUrl(userId, conf))
    
    @classmethod
    def getprize(cls, gameId, state, conf, prize={}):
        result = conf.get('getPrize', [])
        if state == 1:
            return result[1]
        elif state == 2:
            return result[2]
        else:
            return cls.message(prize)
    
    @classmethod
    def message(cls, prize):
        lrewards = ['恭喜您获得']
        for key, value in prize.items():
            if key == "CHIP" and value:
                lrewards.append('%s金、' % value)
            elif key == "COUPON" and value:
                lrewards.append('%s、' % (hallitem.buildContent('user:coupon', value)))
        message = ''.join(lrewards)
        
        return message.rstrip('、') + '的邀请奖励!'
    
    @classmethod
    def doGetUserState(cls, gameId, userId, clientId, action):
        '''
        获取用户信息，不存在则，验证用户状态，写入用户活动状态表，并返回用户状态
        '''
        conf = hallconf.getNeiTuiGuangConf(clientId)
        mo = MsgPack()
        if not conf:
            ftlog.error('neituiguang doGetUserState conf not found gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'action=', action)
            return mo
        state = gamedata.getGameAttr(userId, gameId, cls.attrname_state)
        createTime = userdata.getAttr(userId, 'createTime')
        if state == None:
            state = cls.initUserState(userId, gameId, createTime, conf)
            userdata.setAttr(userId, cls.attrname_state, state)
            inviteetip = cls.inviteeTip(userId, gameId, createTime, conf)
        else:
            if cls.isOldUser(userId, gameId, createTime, conf):
                state = 2
                userdata.setAttr(userId, cls.attrname_state, state) # 老用户状态
        
        if state == 0:
            NeiTuiGuangProtocolBuilder.buildNewUserState(gameId, userId, action, state, inviteetip, mo)
        elif state == 1:
            bindmobile = userdata.getAttr(userId, 'bindMobile')
            bindok = cls.bindOk(bindmobile)
            NeiTuiGuangProtocolBuilder.buildBindUserState(gameId, userId, action, state, bindok, mo)
        elif state == 2:
            bindmobile = userdata.getAttr(userId, 'bindMobile')
            bindok = cls.bindOk(bindmobile)
            shareId = conf.get('shareId', -1)
            prizeinfo = conf.get('prize_info', [])
            weixintip = cls.getWeiXinTip(userId, conf)
            url = cls.getDownUrl(userId, conf)
            smstip =  cls.getSMSTip(gameId, userId, conf)
            rules = conf.get('rules', [])
            NeiTuiGuangProtocolBuilder.buildOldUserState(gameId, userId, action, state, bindok, shareId, prizeinfo, weixintip, url, smstip, rules, mo)
        else:
            pass 
            
        return mo
    
    @classmethod
    def doPromoteCodeCheck(cls, gameId, userId, clientId, action, promoteCode):
        '''
        验证兑换码ID，有效则获取用户手机绑定信息，若绑定手机，则发送奖励，并更新用户状态。若未绑定手机，则更新用户状态，返回未绑定手机code
        '''
        conf = hallconf.getNeiTuiGuangConf(clientId)
        if not conf:
            ftlog.error('neituiguang doGetUserState conf not found gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'action=', action)
            return
        mo = MsgPack()
        userstate = gamedata.getGameAttr(userId, gameId, cls.attrname_state)
        if userstate == 2:
            NeiTuiGuangProtocolBuilder.buildBasicInfo(0, action, '已经领奖成功', mo)
        else:
            promoteCode = cls.intPromoteCode(promoteCode)
            if promoteCode == -1 or userId == promoteCode:
                NeiTuiGuangProtocolBuilder.buildBasicInfo(1, action, cls.getprize(gameId, 1, conf), mo)
            else:
                userdata.checkUserData(promoteCode)
                createTime = userdata.getAttr(promoteCode, 'createTime')
                if createTime == None:
                    NeiTuiGuangProtocolBuilder.buildBasicInfo(1, action, cls.getprize(gameId, 1, conf), mo)
                else:
                    olduser = cls.isOldUser(promoteCode, gameId, createTime, conf)
                    if not olduser:
                        NeiTuiGuangProtocolBuilder.buildBasicInfo(1, action, cls.getprize(gameId, 1, conf), mo)
                    else:
                        gamedata.setGameAttr(userId, gameId, cls.attrname_promotecode, promoteCode) # 记录兑换码
                        gamedata.setGameAttr(userId, gameId, cls.attrname_state, 1) # 已输入兑换码
                        bindmobile = userdata.getAttr(userId, 'bindMobile')
                        if cls.bindOk(bindmobile):
                            NeiTuiGuangProtocolBuilder.buildBasicInfo(0, action, '验证成功', mo)
                        else:
                            NeiTuiGuangProtocolBuilder.buildBasicInfo(2, action, cls.getprize(gameId, 2, conf), mo)
            return mo
    
    @classmethod
    def doGetPrize(cls, gameId, userId, clientId, action):
        '''
        新用户领奖接口
        '''
        conf = hallconf.getNeiTuiGuangConf(clientId)
        if not conf:
            ftlog.error('neituiguang doGetUserState conf not found gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'action=', action)
            return
        mo = MsgPack()
        bindmobile = userdata.getAttr(userId, 'bindMobile')
        userstate = gamedata.getGameAttr(userId, gameId, cls.attrname_state)
        if cls.bindOk(bindmobile):
            prizeGet = cls.sendBothUserPrize(gameId, userId, userstate, conf)
            
            if prizeGet == -1: # 用户状态错误
                NeiTuiGuangProtocolBuilder.buildBasicInfo(2, action, "用户状态错误", mo)
            else:              # 发送奖励成功
                NeiTuiGuangProtocolBuilder.buildBasicInfo(0, action, cls.getprize(gameId, 0, conf, prizeGet), mo)
        else:   # 未绑定手机
            NeiTuiGuangProtocolBuilder.buildBasicInfo(1, action, cls.getprize(gameId, 2, conf), mo)
    
        return mo
    
    @classmethod
    def doOldUserGetPrize(cls, gameId, userId, friendId, clientId, action):
        '''
        老用户领奖接口
        '''
        conf = hallconf.getNeiTuiGuangConf(clientId)
        if not conf:
            ftlog.error('neituiguang doGetUserState conf not found gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'action=', action)
            return

        mo = MsgPack()
        mpush = None
        userstate = gamedata.getGameAttr(userId, gameId, cls.attrname_state)
        bindmobile = userdata.getAttr(userId, 'bindMobile')
        if userstate == 2:
            if cls.bindOk(bindmobile):
                prizeGet = cls.sendOldUserPrize(userId, friendId, gameId, conf)
                NeiTuiGuangProtocolBuilder.buildOldUserPrize(0, action, cls.getprize(gameId, 0, prizeGet), friendId, mo)
                ##### 推一条用户奖励信息
                mpush = cls.doQueryPrize(gameId, userId, clientId, action)
            else:
                NeiTuiGuangProtocolBuilder.buildBindPrize(1, action, cls.getprize(gameId, 2), friendId, mo)
        else:
            NeiTuiGuangProtocolBuilder.buildBasicInfo(2, action, 'user state error: not support', mo)
    
        return mo, mpush
    
    @classmethod
    def friendNumLimit(cls, userId, gameId, numlimit):
        friendnum = gamedata.getGameAttr(userId, gameId, cls.attrname_invitedfriendnum)
        if friendnum >= numlimit:
            return False
        return True
    
    @classmethod
    def sendBothUserPrize(cls, gameId, userId, userstate, conf):
        # 用户状态是否正确 => 是否绑定手机状态 => 发奖
        result = cls.userStateRoute(gameId, userId, userstate, cls.attrname_state)
        if result != 0:
            return result
        else:
            friendId = gamedata.getGameAttr(userId, gameId, cls.attrname_promotecode)
            numlimit = conf.get('friendNum', 20)
            if cls.friendNumLimit(friendId, gameId, numlimit):
                return cls.sendBothUserPrize2(gameId, userId, friendId, conf)
            else:
                return cls.sendSingleUserPrize2(gameId, userId)
            
    @classmethod
    def userStateRoute(cls, gameId, userId, userstate, attr):
        if userstate == 1:
            gamedata.setGameAttr(userId, gameId, cls.attrname_state, 2)
            return 0
        else:
            return -1 
        
    @classmethod
    def sendBothUserPrize2(cls, gameId, userId, friendId, conf): 
        
        prize = conf.get('prize', {})
        friendnum = user_remote.addfriend(friendId, userId, gameId, prize) # rpc!!!
        prizeGet = {"CHIP": 0}
        
        if friendnum != -1:
            prizeGet = {"CHIP": prize["CHIP"]}
            userchip.incrChip(userId, gameId, prize["CHIP"], daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'ACTIVITY_REWARD', 0, None)
            
            cls.updateNotify(gameId, userId, 'chip')
            message.send(gameId, message.MESSAGE_TYPE_SYSTEM, userId, cls.message(prizeGet))
            
        return prizeGet
    
    @classmethod
    def addfriend(cls, userId, friendId, gameId, prize, numlimit):
        '''
        rpc
        '''
        if not cls.friendNumLimit(userId, gameId, numlimit):
            return -1
        friend = {'userId': friendId, 'state': 0}
        friendlist = gamedata.getGameAttr(userId, gameId, cls.attrname_invitedfriendlist)
        if not friendlist:
            friendlist = []
        else:
            friendlist = json.loads(friendlist)
        
        existed = False
        for f in friendlist:
            if f['userId'] == friendId:
                existed = True
                break
        
        if existed:
            return -1
        else:
            friendlist.append(friend)
            gamedata.setGameAttr(userId, gameId, cls.attrname_invitedfriendlist, json.dumps(friendlist))
            gamedata.incrGameAttr(userId, gameId, cls.attrname_failchip, prize["CHIP"])
            gamedata.incrGameAttr(userId, gameId, cls.attrname_invitedfriendnum, 1)
            friendnum = len(friendlist)
            if friendnum % 5 == 0:
                gamedata.incrGameAttr(userId, gameId, cls.attrname_failcoupon, prize["COUPON"])
                
            return friendnum
    
    @classmethod
    def sendSingleUserPrize2(cls, gameId, userId, conf):
        prize = conf.get('prize', {})
        prizeGet = {"CHIP": prize["CHIP"]}
        userchip.incrChip(userId, gameId, prize["CHIP"], daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'ACTIVITY_REWARD', 0, None)
        cls.updateNotify(gameId, userId, 'chip')
        message.send(gameId, message.MESSAGE_TYPE_SYSTEM, userId, cls.message(prizeGet))
        return prizeGet
        
    
    @classmethod
    def sendOldUserPrize(cls, userId, friendId, gameId, conf):
        prize = conf.get('prize', {})
        
        prizeGet = {"CHIP": 0, "COUPON": 0}
        
        getprize =  cls.getFriendListPrize(userId, friendId, gameId)
        if getprize == [0, 0]:
            return prizeGet
        cls.sendSingleOldUserPrize(userId, gameId, getprize[0]* prize["CHIP"], getprize[1]* prize["COUPON"])
        
        prizeGet["CHIP"] = getprize[0] * prize["CHIP"]
        prizeGet["COUPON"] = getprize[1] * prize["COUPON"]
        
        message.send(gameId, message.MESSAGE_TYPE_SYSTEM, userId, cls.message(prizeGet))
        return prizeGet
    
    @classmethod
    def sendSingleOldUserPrize(cls, userId, gameId, chip, coupon):
        ftlog.info("sendSingleOldUserPrize userId=", userId, "gameId=", gameId, "chip=", chip, "coupon=", coupon)
        notify = []
        if chip != 0:
            userchip.incrChip(userId, gameId, chip, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'ACTIVITY_REWARD', 0, None)
            notify.append('chip')
            gamedata.incrGameAttr(userId, gameId, cls.attrname_succchip, chip)
            gamedata.incrGameAttr(userId, gameId, cls.attrname_failchip, -chip)
        if coupon != 0:
            userchip.incrCoupon(userId, gameId, coupon, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, 'COUPON_DIZHU_NEI_TUI_GUANG', 0, None)
            gamedata.incrGameAttr(userId, gameId, cls.attrname_succcoupon, coupon)
            gamedata.incrGameAttr(userId, gameId, cls.attrname_failcoupon, -coupon)
            notify.append('item')
            
        cls.updateNotify(gameId, userId, notify)
    
    @classmethod
    def getFriendListPrize(cls, userId, friendId, gameId):
        '''
        rpc
        '''
        friendlist = gamedata.getGameAttr(userId, gameId, cls.attrname_invitedfriendlist)
        if not friendlist:
            return [0, 0]
        friendlist = json.loads(friendlist)
        chipget = 0
        couponget = 0
        index = 0
        if friendId == -1:
            for i in friendlist:
                index += 1
                if i['state'] == 0:
                    chipget += 1
                    i['state'] = 1
                    if index % 5 == 0:
                        couponget += 1
        else:
            for i in friendlist:
                index += 1
                if i['userId'] == friendId and i['state'] == 0:
                    chipget += 1
                    i['state'] = 1
                    if index % 5 == 0:
                        couponget += 1
        gamedata.setGameAttr(userId, gameId, cls.attrname_invitedfriendlist, json.dumps(friendlist))
        return [chipget, couponget]
    
    
    @classmethod
    def doQueryPrize(cls, gameId, userId, clientId, action):
        conf = hallconf.getNeiTuiGuangConf(clientId)
        if not conf:
            ftlog.error('neituiguang doQueryPrize conf not found gameId=', gameId, 'userId=', userId, 'clientId=', clientId, 'action=', action)
            return
        mo = MsgPack()
        prize = conf.get('prize', {})
        getedPrize = cls.getUserSuccPrize(gameId, userId)
        prizeAvailable = cls.getUserFailPrize(gameId, userId)
        friends = cls.getFriendList(gameId, userId, clientId, prize)
        NeiTuiGuangProtocolBuilder.buildQueryPrize(action, getedPrize, prizeAvailable, friends, mo)
        return mo

    @classmethod
    def getUserSuccPrize(cls, gameId, userId):
        chip = gamedata.getGameAttr(userId, gameId, cls.attrname_succchip) or 0
        coupon = gamedata.getGameAttr(userId, gameId, cls.attrname_succcoupon) or 0
        return [{"name":"CHIP", "count": chip}, {"name": "COUPON", "count": coupon}]
    
    @classmethod
    def getUserFailPrize(cls, gameId, userId):
        chip = gamedata.getGameAttr(userId, gameId, cls.attrname_failchip) or 0
        coupon = gamedata.getGameAttr(userId, gameId, cls.attrname_failcoupon) or 0
        return [{"name":"CHIP", "count": chip}, {"name": "COUPON", "count": coupon}]
    
    @classmethod
    def getFriendList(cls, gameId, userId, clientId, prize):
        result = []
        friendlist = gamedata.getGameAttr(userId, gameId, cls.attrname_invitedfriendlist) or "[]"
        friendlist = json.loads(friendlist)
        for i in range(len(friendlist)):
            result.append(cls.friendInfo(friendlist[i], prize, i, clientId))
        return result
    
    @classmethod
    def friendInfo(cls, friend, prize, index, clientId):
        userdata.checkUserData(friend["userId"])

        coupon = 0
        if (index+1) % 5 == 0:
            coupon = prize["COUPON"]
        result = {"prizeInfo": {
                                "prize": [{"name":"CHIP", "count": prize["CHIP"]}, {"name": "COUPON", "count": coupon}],
                                "state": friend["state"]
                                }}
        uds = userdata.getAttrs(friend["userId"], ['purl', 'name', 'chip'])
        friendInfo = {
                      "userId": friend["userId"],
                      "headUrl": uds[0],
                      "name": uds[1],
                      "chip": uds[2],
                      "dashifen": cls.getDaShiFenPic(friend["userId"], clientId)
                      }
        result['friendInfo'] = friendInfo
        return result
    
    @classmethod
    def getDaShiFenPic(cls, userId, clientId):
        urls = []
        games = [6, 7, 8]
        info = hallaccount.getGameInfo(userId, clientId)
        for gameId in games:
            dashifen = info.get(gameId, {}).get('dashifen', {})
            if dashifen:
                urls.append(dashifen['pic'])
        return urls
    
    @classmethod
    def doCancelCodeCheck(cls, gameId, userId, clientId, action):
        mo = MsgPack()
        state = 2
        gamedata.setGameAttr(userId, gameId, cls.attrname_state, state)
        NeiTuiGuangProtocolBuilder.buildBasicInfo(0, action, '取消成功', mo)
        return mo
    
    @classmethod
    def updateNotify(cls, gameId, userId, enti):
        dcevt = DataChangeEvent(gameId, userId, 'act.raffle.send.mem').addDataType(enti)
        pkeventbus.globalEventBus.publishEvent(dcevt)
    
    
    