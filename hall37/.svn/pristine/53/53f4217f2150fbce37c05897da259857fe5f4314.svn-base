# -*- coding:utf-8 -*-

import time

# yd_balance.txt         1银豆=1金币
# jindou.qid.result.txt  10金豆=1钻石（取整）
# jifen.txt              2000盘数积分=1张参赛券（取整）
# menpiao.result.txt     1积分门票=10金币
# hlmj.jingyan.txt       4欢乐麻将等级经验值=1雀神分（取整）
# mjjingyan.txt          4血战麻将等级经验值=1雀神分（取整）
# xzmj.bk_balance.txt    1血战麻将贝壳=1金币

haserror = 0
basedir = '/home/tyhall/hall37/pcdatas/'

def load_file(fname, ukey, datas, mutil) :
    tc = time.time()
    fname = basedir + fname
    print 'load file->', fname, 'datas size=', len(datas)
    f = open(fname, 'r')
    ln = 0
    for l in f.readlines() :
        if l :
            ln = ln + 1
            try:
                if l.find('\t') > 0 :
                    snsid, val = l.split('\t')
                else:
                    snsid, val = l.split(' ')
                intsnsid = int(snsid)
                if intsnsid >= 1593010001 and intsnsid <= 1594994998 :
                    continue
                if intsnsid >= 1583000000 and intsnsid <= 1585000000 :
                    continue
                if snsid not in datas :
                    datas[snsid] = {}
                udata = datas[snsid]
                val = int(int(val) * mutil)
                if val < 0 :
                    val = 0
                if ukey not in udata :
                    udata[ukey] = val
                else:
                    udata[ukey] += val
            except:
                haserror = 1
                print 'data error !! file->', fname, 'line->', ln, 'data->', l
    f.close()
    print 'load', fname, 'done, time=%02f' % (time.time() - tc)


def main():
    pcusers = {}
    load_file('./txt/xq.jifen.txt', 'chessExp', pcusers, 1)
    load_file('./txt/xq.panshu.txt', 'totalNum', pcusers, 1)
    load_file('./txt/xq.sheng.txt', 'winNum', pcusers, 1)
    load_file('./txt/xq.fu.txt', 'loseNum', pcusers, 1)
    load_file('./txt/xq.he.txt', 'drawNum', pcusers, 1)

    print 'load data file done, size=', len(pcusers)
    if haserror :
        print 'some thing is error !! stop'
        return

    tc = time.time()
    fds = [open(basedir + 'datas/d0.data', 'w'),
           open(basedir + 'datas/d1.data', 'w'),
           open(basedir + 'datas/d2.data', 'w'),
           open(basedir + 'datas/d3.data', 'w'),
           open(basedir + 'datas/d4.data', 'w'),
           open(basedir + 'datas/d5.data', 'w'),
           open(basedir + 'datas/d6.data', 'w'),
           open(basedir + 'datas/d7.data', 'w')]
    x = 0
    for k, v in pcusers.items() :
        s = str(k) + ' ' + str(v.get('chessExp', 0)) + ' ' + str(v.get('totalNum', 0)) \
            + ' ' + str(v.get('winNum', 0)) + ' ' + str(v.get('loseNum', 0)) + ' ' + str(v.get('drawNum', 0)) + '\n'
        fds[x % len(fds)].write(s)
        x = x + 1
    for fd in fds :
        fd.close()
    print '========= save data end ===========, time=%02f' % (time.time() - tc)
    print 'the data size=', len(pcusers)

if __name__ == '__main__' :
    main()




