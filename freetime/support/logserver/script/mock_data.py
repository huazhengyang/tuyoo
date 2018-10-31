# -*- coding: utf-8 -*-
import urllib2
import struct
import time
chip_mformat = '<IIqqqIIHHIBI'
game_mformat = '<IIIHIQQIqqqBB20s'
card_mformat = '<IIIHIQQIqqqBB20s'
login_mformat = '<IIIHHII32s40sBBH'
pay_mformat = '<IIIHHI14s6s25sHHBIIiH10s32s32s32sI11sBB'
etime = int(time.time())
uid = 83180761
chip = 0
tchip = 0
fchip = 0
eventid = 2
clientid = 0
gameid = 0
appid = 0
eparam = 0
chiptype = 0
itemid = 1
roomid = 601
tableid = 601001
roundid = 1
state = 1
cardlist = ''
ipaddr = 0
devid = ''
bindid = ''
phonetype = 1
province = 1
failreason = 1
orderid = ''
shortid = ''
deliver_orderid = ''
prodid = 10001
diamondid = 1
subevent = 1
prodprice = 6
chargeprice = 6
succprice = 6
paytype = 1
subpaytype = ''
thirdproid = ''
thirdorderid = ''
thirdappid = ''
mobile = ''
chip_mbody = struct.pack(chip_mformat, etime, uid, chip, tchip, fchip, eventid, clientid, gameid, appid, eparam, chiptype, itemid)
game_mbody = struct.pack(game_mformat, etime, eventid, uid, gameid, clientid, roomid, tableid, roundid, tchip, fchip, fchip, state, state, cardlist)
card_mbody = struct.pack(card_mformat, etime, eventid, uid, gameid, clientid, roomid, tableid, roundid, tchip, fchip, fchip, state, state, cardlist)
login_mbody = struct.pack(login_mformat, etime, eventid, uid, gameid, appid, clientid, ipaddr, devid, bindid, phonetype, province, failreason)
pay_mbody = struct.pack(pay_mformat, etime, eventid, uid, gameid, appid, clientid, orderid, shortid, deliver_orderid, prodid, diamondid, subevent, prodprice, chargeprice, succprice, paytype, subpaytype, thirdproid, thirdorderid, thirdappid, ipaddr, mobile, phonetype, province)
headerdata = {'log-type': 'chip', 'log-group': 'user1'}
requrl = 'http://10.3.13.251:10001'
ok = 0
error = 0
for i in xrange(0, 1):
    req = urllib2.Request(url=requrl, headers=headerdata, data=chip_mbody)
    try:
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        ok += 1
    except:
        error += 1
        print 'error'
print 'ok:', ok
print 'error:', error