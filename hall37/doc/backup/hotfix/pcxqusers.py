# -*- coding=utf-8 -*-
from poker.entity.configure import gdata
from poker.entity.dao import daobase, userdata, gamedata, userchip, daoconst
from datetime import datetime
import random
import freetime.util.log as ftlog
import json

PCCLIENTID = 'Winpc_3.60_360.360.0-hall3.360.kxxq'
itemdatas = {
            "7016" : "\xf5\x03\x00\x00Q1&V\x01\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00",
            "7017" : "\xf0\x03\x00\x00Q1&V\x05\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x01\x00\x00\x00\x00",
            "7018" : "\xef\x03\x00\x00Q1&V\x14\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x01\x00\x00\x00\x00",
            "7019" :  "\xd2\a\x00\x00Q1&V2\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x01\x00\x00\x00\x00"
             }

def do_xq_user(snsidNum, chessExp, totalNum, winNum, loseNum, drawNum):
    snsId = '360:' + str(snsidNum)
    uid = daobase._executeKeyMapCmd('get', 'snsidmap:' + str(snsId))
    ftlog.info('PCXQ_USER snsidNum=', snsidNum, 'uid=', uid)
    if uid :
        # 老用户
        uid = int(uid)
        do_xq_update_old_user(uid, snsId, chessExp, totalNum, winNum, loseNum, drawNum)
    else:
        # 新用户
        do_xq_creat_new_user(snsId, chessExp, totalNum, winNum, loseNum, drawNum)
    pass


def do_xq_update_old_user(uid, snsId, chessExp, totalNum, winNum, loseNum, drawNum):
    ret = userdata.checkUserData(uid, PCCLIENTID, 3)
    ftlog.info('PCXQ_USER load already user data !', uid, snsId, 'ret=', ret)
    chessExpOld, chessRecordOld = gamedata.getGameAttrs(uid, 3, ['chessExp', 'chessRecord'], False)
    creat = 0
    if chessExpOld == None or chessRecordOld == None :
        creat = 1
    else:
        try:
            chessExpOld = int(chessExpOld)
        except:
            creat = 1
        try:
            chessRecordOld = json.loads(chessRecordOld)
            totalNum = totalNum + int(chessRecordOld.get('totalNum'))
            winNum = winNum + int(chessRecordOld.get('winNum'))
            loseNum = loseNum + int(chessRecordOld.get('loseNum'))
            drawNum = drawNum + int(chessRecordOld.get('drawNum'))
        except:
            creat = 1

    if creat :
        ftlog.info('PCXQ_USER creat old user XQ gamedata !', uid, snsId, 'chessExpOld=', chessExpOld, 'chessRecordOld=', chessRecordOld)
        creat_gamedata(uid, chessExp, totalNum, winNum, loseNum, drawNum)
    else:
        ftlog.info('PCXQ_USER update old user XQ gamedata !', uid, snsId, 'chessExpOld=', chessExpOld, 'chessRecordOld=', chessRecordOld)
        chessExp = max(chessExpOld, chessExp)
        chessRecordOld['totalNum'] = totalNum
        chessRecordOld['winNum'] = winNum
        chessRecordOld['loseNum'] = loseNum
        chessRecordOld['drawNum'] = drawNum
        gamedata.setGameAttrs(uid, 3, ['chessExp', 'chessRecord'], [chessExp, json.dumps(chessRecordOld)])


def do_xq_creat_new_user(snsId, chessExp, totalNum, winNum, loseNum, drawNum):
    
    uid = daobase.executeMixCmd('incrby', 'global.userid', 1)
    #assert(uid > 148670897)
    ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    datas = {
             'password' : 'ty' + str(random.randint(100000, 999999)),
             'mdevid' : '',
             'isbind' : 1,
             'snsId' : snsId,
             'name' : '',
             'source' : '',
             'purl' : 'http://ddz.image.tuyoo.com/avatar/head_china.png',
             'address' : '',
             'sex' : 0,
             'state' : 0,
             'payCount' : 0,
             'snsinfo' : '',
             'vip' : 0,
             'dayang' : 0,
             'idcardno' : '',
             'phonenumber' : '',
             'truename' : '',
             'detect_phonenumber' : '',
             'email' : '',
             'createTime' : ct,
             'userAccount' : '',
             'clientId' : PCCLIENTID,
             'appId' : 9999,
             'bindMobile' : '',
             'mac' : '',
             'idfa' : '',
             'imei' : '',
             'androidId' : '',
             'uuid' : '',
             'userId' : uid,
             "lang" : '',
             "country" : "",
             "signature" : "",
             "agreeAddFriend" : 1,
#              "aliveTime" :  ct,
#              "exp" : 0,
#              "charm" : 0,
#              "diamond" : 0,
#              "chip" : 3000,
#              "coin" : 0
             }
#     attrlist = []
#     valuelist = []
#     for k, v in datas.items() :
#         attrlist.append(k)
#         valuelist.append(v)

    ftlog.info('PCXQ_USER', 'creat new user of->', uid, snsId)
    # userdata._setAttrsForce(uid, datas)
    userdata.setAttrs(uid, datas)
    userchip.incrChip(uid, 3, 3000, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'SYSTEM_REPAIR', 0, PCCLIENTID)
    userchip.incrCoin(uid, 3, 0, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'SYSTEM_REPAIR', 0, PCCLIENTID)
    userchip.incrDiamond(uid, 3, 0, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'SYSTEM_REPAIR', 0, PCCLIENTID)
    userchip.incrCoupon(uid, 3, 0, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'SYSTEM_REPAIR', 0, PCCLIENTID)
    userdata.incrCharm(uid, 0)
    userdata.incrExp(uid, 0)
    
    ikey = 'item2:9999:' + str(uid)
    for k, v in itemdatas.items() :
        daobase.executeUserCmd(uid, 'hset', ikey, k, v)
    daobase._executeKeyMapCmd('set', 'snsidmap:' + str(snsId), uid)
    
    creat_gamedata(uid, chessExp, totalNum, winNum, loseNum, drawNum)
    


DATAKEYS = ('lastlogin', 'nslogin', 'loginsum', 'chessTitle',
            'chessWinrate', 'chessExp', 'dashifen', 'chessPlayTime',
            'unlockEndGameCount', 'lastIsFirst', 'chessRecord')
VALUES = [ 0, 0, 0, '六级棋士', 0, 1400, 0, 0, 0, 0, None]
        
def creat_gamedata(uid, chessExp, totalNum, winNum, loseNum, drawNum):
    rs = {"totalNum":totalNum, "winNum":winNum, "loseNum":loseNum, "drawNum":drawNum, "escapeNum":0, "singleWinNum":0, "singleLoseNum":0, "initiativeNum":0, "passiveNum":0, "initiativeWinNum":0, "passiveWinNum":0}
    VALUES[-1] = json.dumps(rs)
    ftlog.info('PCXQ_USER', 'creat new gamedata of->', uid, VALUES)
    gamedata.setGameAttrs(uid, 3, DATAKEYS, VALUES)


esnsids = []
sid = gdata.serverNum()
f = open('/home/tyhall/hall37/pcdatas/d'+str(int(sid)-1)+'.data', 'r')
x = 0
for l in f.readlines() :
    ftlog.info('PCXQ_USER readline ', x, l)
    x += 1
    if l :
        l = l.strip()
        snsid, chessExp, totalNum, winNum, loseNum, drawNum = l.split(' ')
        try:
            do_xq_user(snsid, int(chessExp), int(totalNum), int(winNum), int(loseNum), int(drawNum))
        except:
            ftlog.error()
            esnsids.append([snsid, chessExp, totalNum, winNum, loseNum, drawNum])
            break
ftlog.info('PCXQ_USER ERRSNSIDS=', esnsids)



