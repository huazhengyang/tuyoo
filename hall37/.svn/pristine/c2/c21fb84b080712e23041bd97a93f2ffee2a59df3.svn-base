# -*- coding:utf-8 -*-
'''
Created on 2016年2月4日

@author: zhaojiangang
'''

from datetime import datetime

import freetime.util.log as ftlog
from hall.entity import hallsubmember, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallsubmember import SubMemberStatus
from poker.entity.dao import userdata
import poker.util.timestamp as pktimestamp


userIds = [
157239873,
155269429,
156305698,
157109958,
89748918,
155523282,
157953334,
157418594,
148851962,
156830728,
123581099,
157635576,
155448354,
155194318,
120799597,
157256650,
155210754,
150390397,
157046818,
156073278,
153586180,
153893135,
156217715,
65710518,
155593309,
151313412,
134872055,
154918412,
156955418,
112352702,
121374512,
140610748,
77642667,
127080274,
151754099,
157343235,
155721145,
154604136,
134839521,
152363729,
156249914,
149146637,
153682999,
154940540,
148047929,
154527653,
152209669,
153427626,
155758143,
149387199,
64906875,
156950424,
155335366,
154983472,
157278089,
155020753,
156173205,
154162619,
125887562,
154731614,
154010215,
128246609,
74726859,
155876954,
154930997,
155908946,
155644171,
16299202,
155954648,
155899433,
124295284,
157266221,
153065108,
155850890,
157423459,
157380644,
155110326,
156602864,
97431494,
154616159,
80602130,
127670385,
155480552,
157865520,
157264322,
98442776,
155852730,
97664230,
155120549,
156209697,
39115676,
70777131,
153732643,
121017068,
155438865,
127981080,
156528052,
156445903,
105519020,
156047415,
157488110,
150938894,
144603568,
155211214,
137515116,
153518442,
155837982,
155839265,
157456641,
156211026,
155392373,
143389207,
152238505,
74810310,
155892100,
153537244,
147268386,
155871304,
158037251,
155217487,
145357506,
151368112,
156161819,
155683205,
71515788,
155295509,
152765276,
77709069,
76914931,
137917939,
85750045,
152697499,
155265013,
156218614,
134898542,
59540645,
49090258,
153621456,
138161468,
152200484,
152456735,
156986400,
155919425,
156403953,
156817313,
99088,
135704343,
134055852,
101406017,
128878907,
156778259,
155594313,
156655489,
157645137,
155255201,
157217409,
156751360,
155130861,
155612032,
91006503,
156653821,
156621668,
156424391,
156164957,
130844331,
152844505,
151663499,
157084613,
155274894,
153157760,
43330175,
156448279,
156762880,
157511755,
155386410,
156231560,
157312433,
155851960,
152247795,
137836687,
]
userIds = [155269429]
def addMember(userId):
    try:
        userdata.checkUserData(userId)
    except:
        ftlog.error('unsubmember_add.addMember NotFoundUser userId=', userId)
        return
    
    subStatus = hallsubmember.loadSubMemberStatus(userId)
    if not subStatus.isSub:
        ftlog.info('unsubmember_add.addMember NotSub userId=', userId,
                   'subDT=', subStatus.subDT,
                   'deliveryDT=', subStatus.deliveryDT,
                   'expiresDT=', subStatus.expiresDT)
        return
    
    if not subStatus.expiresDT:
        ftlog.info('unsubmember_add.addMember NotExpiresDT userId=', userId,
                   'subDT=', subStatus.subDT,
                   'deliveryDT=', subStatus.deliveryDT,
                   'expiresDT=', subStatus.expiresDT)
        return
    
    timestamp = pktimestamp.getCurrentTimestamp()
    # 检查用户是否是会员，如果不是会员则补偿用户
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    balance = userAssets.balance(HALL_GAMEID, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID, timestamp)
    if balance > 0:
        ftlog.info('unsubmember_add.addMember HaveMemberCard userId=', userId,
                   'subDT=', subStatus.subDT,
                   'deliveryDT=', subStatus.deliveryDT,
                   'expiresDT=', subStatus.expiresDT,
                   'balance=', balance)
        return
    
    nowDT = datetime.fromtimestamp(timestamp)
    expiresDT = SubMemberStatus.calcSubExpiresDT(nowDT, nowDT)
    nDays = (expiresDT.date() - nowDT.date()).days
    if nDays > 0:
        # 计算需要补偿30天
        _, count, final = userAssets.addAsset(HALL_GAMEID, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID,
                                              nDays, timestamp, 'GM_ADJUST', 0)
        ftlog.info('unsubmember_add.addMember OK userId=', userId,
                   'subDT=', subStatus.subDT,
                   'oldDeliveryDT=', subStatus.deliveryDT,
                   'oldExpiresDT=', subStatus.expiresDT,
                   'deliveryDT=', nowDT,
                   'balance=', balance,
                   'nDays=', nDays,
                   'count=', count,
                   'final=', final)
    else:
        ftlog.info('unsubmember_add.addMember EmptyNdays userId=', userId,
                   'subDT=', subStatus.subDT,
                   'oldDeliveryDT=', subStatus.deliveryDT,
                   'oldExpiresDT=', subStatus.expiresDT,
                   'deliveryDT=', nowDT,
                   'balance=', balance,
                   'nDays=', nDays,
                   'count=', count,
                   'final=', final)
    subStatus.expiresDT = expiresDT
    subStatus.deliveryDT = nowDT
    subStatus.subDT = nowDT
    hallsubmember._saveSubMemberStatus(userId, subStatus)
        
for userId in userIds:
    addMember(userId)
    
