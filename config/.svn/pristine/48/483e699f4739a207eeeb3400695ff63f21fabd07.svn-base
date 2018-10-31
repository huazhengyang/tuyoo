# -*- coding: utf-8 -*-
import os
import json
import sys
import datetime

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
    for x in xrange(len(lines)):
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

def convert(gameid, funconvert):
    gameid = str(gameid)
    ds = readJsonFile('./game/'+gameid+'/room/0.json')
    for rid, basedef in ds.items() :
        rdef = readJsonFile('./game/'+gameid+'/room/'+rid+'.json')
        if basedef['controlServerCount'] > 2 :
            basedef['controlServerCount'] = 2
        if basedef['gameServerCount'] > 2 :
            basedef['gameServerCount'] = 2
        if basedef['gameTableCount'] > 200 :
            basedef['gameTableCount'] = 200

        funconvert(rid, rdef)

        writeJsonFile('./game/'+gameid+'/room/'+rid+'.json', rdef)

    writeJsonFile('./game/'+gameid+'/room/0.json', ds)

