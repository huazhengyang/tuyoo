# -*- coding:utf-8 -*-
'''
Created on 2018年04月13日

@author: zhaoliang
'''
import freetime.util.log as ftlog
from dizhu.entity.dizhuversion import SessionDizhuVersion
from poker.protocol import router
from dizhu.gametable.dizhu_sender import TimingMessageSender

def sendSmilesResOk(self, fromseat, member, toseat, price, smilie, self_charm, other_charm, tip, rcount=1):
    mo = self.createMsgPackRes('table_call', 'smilies')
    mo.setResult('fromseat', fromseat)
    mo.setResult('member', member)
    mo.setResult('toseat', toseat)
    mo.setResult('price', price)
    mo.setResult('smilies', smilie)
    mo.setResult('from_charm', self_charm)
    mo.setResult('to_charm', other_charm)
    mo.setResult('tip', tip)
    mo.setResult('count', rcount) # 新版本客户端才支持发送次数
    
    allplayers = []
    allplayers.extend(self.table.players)
    allplayers.extend(self.table.observers)
    oldclient_uids = [] # 使用老版本的uid
    newclient_uids = [] # 使用新版本的uid
    
    for p in allplayers :
        if p.userId <= 0 :
            continue
        dizhuver = SessionDizhuVersion.getVersionNumber(p.userId)
        if dizhuver >= 3.775:
            newclient_uids.append(int(p.userId))
        else:
            oldclient_uids.append(int(p.userId))
            
    ftlog.debug('sendSmilesResOk',
                'smilie=', smilie,
                'rcount=', rcount,
                'oldclient_uids=', oldclient_uids,
                'newclient_uids=', newclient_uids)

    # 新版本只发送一次协议
    for uid in newclient_uids:
        if uid <= 0:
            continue
        router.sendToUser(mo.pack(), uid)
    
    # 老版本发送多次协议，且将砖头转换为鸡蛋
    # 小游戏不存在兼容的问题
    for uid in oldclient_uids:
        if uid <= 0:
            continue
        for _ in xrange(rcount):
#                 if smilie == 'brick':
#                     mo.setResult('smilies', 'egg')
            router.sendToUser(mo.pack(), uid)
            TimingMessageSender.pushMessagePack(uid, mo.pack())
            
from dizhu.gametable.dizhu_sender import DizhuSender
DizhuSender.sendSmilesResOk = sendSmilesResOk
