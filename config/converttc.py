# -*- coding: utf-8 -*-

import os, json
import sys

converts = set(['dashifen.filter', 'upgrade_inc', 'upgrade_full', 'upgrade_diff'])
converts = set(['headpics'])
converts = set(['modules.switch'])

converts =['neituiguang2']
converts =['rename']
converts =['lottery']
converts =['fivestar']
# # gamelist  -- not use
converts =['pop.activity']
# # more.games -- not use
converts =['chargelead']
converts =['todotask.before.activity']
converts =['table.quickpay']
converts =['table.buyinall']
converts =['share']
converts =['room.pay']
converts =['hall.info']
converts =['free']


def convertByMod(gameid, mod):
    if mod not in converts :
        return
    p = './game/' + gameid + '/' + mod
    print 'convert->', p
    j0file = p + '/0.json'
    if not os.path.isfile(j0file) :
        print j0file, 'not found !'
        return
    else:
        print j0file
        # return
    rmfs = [j0file]
    tcdata = readJsonFile(j0file)
    writeJsonFile(p + '/tc.json', tcdata)

    vcdata = {'actual' : {}} 
    if 'default' in tcdata['templates'] :
        vcdata['default'] = 'default'
    
    cidfs = os.listdir(p)
    for cidf in cidfs :
        print cidf
        if cidf.endswith('.json') :
            try:
                cid = int(cidf[0:-5])
            except:
                print 'eascp json file->', p + '/' + cidf
                continue
            if cid > 0 :
                rmfs.append(p + '/' + cidf)
                ciddata = readJsonFile(p + '/' + cidf)
                tname = ciddata['template']
                vcdata['actual'][cid] = tname
    writeJsonFile(p + '/vc.json', vcdata)
    for rmf in rmfs :
        os.remove(rmf)
        pass
        

def convertByGameid(gameid):
    try:
        int(gameid)
    except:
        return
    mods = os.listdir('./game/' + gameid)
    for mod in mods :
        convertByMod(gameid, mod)


def main():
    gameids = os.listdir('./game')
    for gameid in gameids :
        convertByGameid(gameid)


def readJsonFile(fpath):
    fp = None
    try:
        fp = open(fpath, 'r')
        datas = json.load(fp)
        fp.close()
        return datas
    finally:
        try:
            fp.close()
        except:
            pass


def writeJsonFile(fpath, jsondata):
    jsondata = json.dumps(jsondata, indent=2, separators=(', ', ' : '), sort_keys=True, ensure_ascii=False)
    jsondata = jsondata.encode('utf-8')
    lines = jsondata.split('\n')
    for x in xrange(len(lines)) :
        lines[x] = lines[x].rstrip()
    jsondata = '\n'.join(lines)
    rfile = None
    try:
        rfile = open(fpath, 'wb+')
        rfile.write(jsondata)
        rfile.close()
    except:
        print repr(jsondata)
        raise
    finally:
        try:
            rfile.close()
        except:
            pass

if __name__ == '__main__' :
    main()

